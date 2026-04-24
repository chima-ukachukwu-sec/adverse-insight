import streamlit as st
import pdfplumber
import plotly.graph_objects as go
from agents import extract_clauses, score_clauses, draft_negotiation_points

# ──────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────
st.set_page_config(
    page_title="Adverse Insight | AI Contract Risk Analyzer",
    page_icon="⚖️",
    layout="wide"
)

# ──────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────
with st.sidebar:
    st.title("⚖️ Adverse Insight")
    st.caption("AI-Powered Contract Risk Triage")
    st.divider()
    st.markdown("""
    **How it works:**
    1. Upload any contract (PDF/TXT)
    2. AI extracts every clause
    3. Each clause is scored for financial, termination, and data risk
    4. Red-flagged clauses get negotiation scripts
    """)
    st.divider()
    st.caption("Built for the Codex Creator Challenge")
    st.markdown("[GitHub Repo](https://github.com/chima-ukachukwu-sec/adverse-insight)")
    
    st.divider()
    st.markdown("### Sample Contracts")
    st.markdown("Need a contract to test?")
    st.markdown("- [Any Terms of Service](https://tosdr.org)")
    st.markdown("- [Sample Employment Agreement](https://www.lawdepot.com)")
    st.markdown("- Your own job offer letter")

# ──────────────────────────────────────
# MAIN CONTENT
# ──────────────────────────────────────
st.title("Adverse Insight")
st.subheader("AI Agent Chain for Contract Risk Analysis")

uploaded_file = st.file_uploader(
    "Upload a contract (PDF or TXT)",
    type=["pdf", "txt"],
    help="Your document is processed locally. No data is stored."
)

if uploaded_file:
    # ── TEXT EXTRACTION ──
    with st.spinner("📄 Extracting text from document..."):
        if uploaded_file.type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                contract_text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        else:
            contract_text = uploaded_file.read().decode("utf-8")
        
        # Pre-flight guard: prevent garbage-in
        if len(contract_text.strip()) < 100:
            st.error("⚠️ Could not extract sufficient text. The document may be a scanned image or empty. Please upload a text-based PDF or TXT file.")
            st.stop()
        
        word_count = len(contract_text.split())
        st.success(f"✅ Extracted {word_count} words from document.")
    
    # ── AGENT CHAIN EXECUTION ──
    if "clauses" not in st.session_state:
        st.session_state.clauses = None
        st.session_state.scored_clauses = None
        st.session_state.negotiation_points = None
    
    if st.button("🔍 Analyze Contract", type="primary", use_container_width=True):
        # Agent 1: Extract
        with st.spinner("🤖 Agent 1: Extracting clauses..."):
            st.session_state.clauses = extract_clauses(contract_text)
            st.success(f"Extracted {len(st.session_state.clauses)} clauses.")
        
        # Agent 2: Score
        with st.spinner("🔴 Agent 2: Scoring risk..."):
            st.session_state.scored_clauses = score_clauses(st.session_state.clauses)
            red_flags = [c for c in st.session_state.scored_clauses if c.get("red_flag")]
            st.success(f"Identified {len(red_flags)} red-flagged clauses.")
        
        # Agent 3: Negotiate
        if red_flags:
            with st.spinner("📝 Agent 3: Drafting negotiation points..."):
                red_flagged_input = []
                for scored in red_flags:
                    original = next((c for c in st.session_state.clauses if c["clause_id"] == scored["clause_id"]), None)
                    if original:
                        red_flagged_input.append({
                            "clause_id": scored["clause_id"],
                            "clause_type": scored.get("clause_type", original.get("clause_type")),
                            "source_quote": original.get("source_quote", ""),
                            "severity_rationale": scored.get("severity_rationale", "")
                        })
                st.session_state.negotiation_points = draft_negotiation_points(red_flagged_input)
                st.success(f"Drafted {len(st.session_state.negotiation_points)} negotiation scripts.")
    
    # ── RESULTS DISPLAY ──
    if st.session_state.scored_clauses:
        st.divider()
        
        # Tab layout for organized viewing
        tab1, tab2, tab3 = st.tabs(["📊 Risk Dashboard", "📋 Clause Details", "📝 Negotiation Scripts"])
        
        with tab1:
            st.subheader("Risk Overview")
            
            # Calculate averages for radar chart
            avg_financial = sum(c.get("financial_liability", 0) for c in st.session_state.scored_clauses) / len(st.session_state.scored_clauses)
            avg_termination = sum(c.get("termination_asymmetry", 0) for c in st.session_state.scored_clauses) / len(st.session_state.scored_clauses)
            avg_data = sum(c.get("data_rights_risk", 0) for c in st.session_state.scored_clauses) / len(st.session_state.scored_clauses)
            
            # Radar chart
            categories = ['Financial Liability', 'Termination Asymmetry', 'Data Rights Risk']
            contract_values = [avg_financial, avg_termination, avg_data]
            market_values = [30, 25, 20]  # Market standard benchmarks
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=contract_values + [contract_values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name='This Contract',
                line_color='red'
            ))
            fig.add_trace(go.Scatterpolar(
                r=market_values + [market_values[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name='Market Standard',
                line_color='green'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                margin=dict(l=80, r=80, t=40, b=40),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.metric("Total Clauses", len(st.session_state.clauses))
                red_count = len([c for c in st.session_state.scored_clauses if c.get("red_flag")])
                st.metric("Red-Flagged Clauses", red_count, delta=f"{red_count} critical" if red_count > 0 else None, delta_color="inverse")
                st.metric("Highest Risk Score", f"{max(c.get('financial_liability', 0) for c in st.session_state.scored_clauses)}/100")
                st.caption("Scores above 70 indicate clauses you should negotiate or reject.")
        
        with tab2:
            st.subheader("Clause-by-Clause Analysis")
            
            for scored in st.session_state.scored_clauses:
                original = next((c for c in st.session_state.clauses if c["clause_id"] == scored["clause_id"]), None)
                
                if scored.get("red_flag"):
                    expander_label = f"🔴 Clause {scored['clause_id']}: {original.get('clause_type', 'Unknown')} — HIGH RISK"
                else:
                    expander_label = f"🟢 Clause {scored['clause_id']}: {original.get('clause_type', 'Unknown')}"
                
                with st.expander(expander_label):
                    if original:
                        st.caption("**Source Quote:**")
                        st.info(original.get("source_quote", "N/A"))
                        st.caption("**Plain English:**")
                        st.write(original.get("plain_english_summary", "N/A"))
                    
                    st.divider()
                    st.caption("**Risk Assessment:**")
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Financial Risk", f"{scored.get('financial_liability', 'N/A')}/100")
                    col_b.metric("Termination Risk", f"{scored.get('termination_asymmetry', 'N/A')}/100")
                    col_c.metric("Data Rights Risk", f"{scored.get('data_rights_risk', 'N/A')}/100")
                    st.write(f"**Rationale:** {scored.get('severity_rationale', 'N/A')}")
        
        with tab3:
            st.subheader("Auto-Generated Negotiation Scripts")
            
            if st.session_state.negotiation_points:
                # Single download button for all scripts
                all_scripts = "\n\n---\n\n".join([
                    f"**Re: {n.get('clause_type', 'Clause')} (Clause {n.get('clause_id', 'N/A')})**\n{n.get('negotiation_script', '')}"
                    for n in st.session_state.negotiation_points
                ])
                
                st.download_button(
                    label="📧 Download Negotiation Scripts (.txt)",
                    data=all_scripts,
                    file_name="adverse_insight_negotiation_points.txt",
                    mime="text/plain"
                )
                
                st.divider()
                
                for n in st.session_state.negotiation_points:
                    st.markdown(f"### {n.get('clause_type', 'Clause')} (Clause {n.get('clause_id', 'N/A')})")
                    st.success(n.get('negotiation_script', 'N/A'))
            else:
                st.info("No red-flagged clauses detected. This contract appears balanced. No negotiation points needed.")
        
        # ── DISCLAIMER ──
        st.divider()
        st.caption("⚠️ **Disclaimer:** Adverse Insight provides AI-generated educational content intended to help you understand contracts better. It is NOT legal advice. Always consult a qualified legal professional before making decisions based on contract terms.")

else:
    # ── EMPTY STATE ──
    st.info("👆 Upload a contract to begin analysis.")
    
    st.divider()
    st.markdown("""
    ### What this tool does:
    - **Extracts** every clause from your document
    - **Scores** each clause on financial, termination, and data risk
    - **Flags** problematic clauses in red
    - **Drafts** negotiation scripts you can use immediately
    
    Built with a **3-agent AI chain** — extraction, adversarial scoring, and negotiation drafting — all orchestrated through Codex and the OpenAI API.
    """)