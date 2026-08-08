"""
Adverse Insight: a three-agent chain that reads a contract, scores every clause
for hidden risk, and drafts the counter-proposal.

The agent chain in agents/ is deliberately untouched by this file. This is the
presentation layer only: it decides what to show and in what order, never what
a clause is worth. Keeping that line clean is what lets the case study describe
the chain's behaviour without the write-up going stale every time the UI moves.
"""

import html
import json
import os
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from ui.theme import (ACCENT, BG, BG_CARD, BORDER, DANGER, OK, TEXT,
                      TEXT_MUTED, CSS, meter, pipeline, risk_band)

st.set_page_config(
    page_title="Adverse Insight | AI Contract Risk Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(CSS, unsafe_allow_html=True)

AXES = [
    ("financial_liability", "Financial liability"),
    ("termination_asymmetry", "Termination asymmetry"),
    ("data_rights_risk", "Data rights"),
]
SAMPLE = Path(__file__).parent / "samples" / "analysis.json"


def esc(v) -> str:
    return html.escape(str(v if v is not None else ""))


def peak(scored: dict) -> int:
    """
    Highest score across all three axes.

    The previous build read financial_liability alone while labelling the result
    "Highest Risk Score", so a contract whose worst problem was a one-sided
    termination clause reported a lower peak than it had.
    """
    return max(int(scored.get(k) or 0) for k, _ in AXES)


# ── state ─────────────────────────────────────────────────────────────────
for key in ("clauses", "scored", "scripts", "stage", "source"):
    st.session_state.setdefault(key, None)
st.session_state.setdefault("stage", 0)
st.session_state.setdefault("only_flagged", False)


# ── hero ──────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="ai-eyebrow">Three-agent chain · contract risk triage</div>'
    '<h1 class="ai-title">Adverse Insight</h1>'
    '<p class="ai-sub">Upload a contract. One agent splits it into clauses, a second '
    'scores each clause adversarially on three axes, and a third drafts the language '
    'you would send back. The clauses that hurt are rarely the hostile-sounding ones; '
    'they are the buried ones.</p>',
    unsafe_allow_html=True,
)

col_up, col_demo = st.columns([3, 2])
with col_up:
    uploaded = st.file_uploader("Contract (PDF or TXT)", type=["pdf", "txt"],
                                label_visibility="collapsed")
with col_demo:
    use_sample = st.button("Load a sample analysis", use_container_width=True,
                           help="A saved run against a deliberately one-sided "
                                "contract. Costs nothing and makes no API call.")

has_key = bool(os.getenv("OPENAI_API_KEY"))
if not has_key and not st.session_state.scored:
    st.markdown(
        f'<p class="note">No API key is configured on this instance, so live analysis '
        f'is unavailable. The sample run below is a real saved result and shows exactly '
        f'what the chain produces.</p>', unsafe_allow_html=True)


# ── sample path: a real saved run, no API call ────────────────────────────
if use_sample and SAMPLE.exists():
    data = json.loads(SAMPLE.read_text())
    st.session_state.clauses = data["clauses"]
    st.session_state.scored = data["scored"]
    st.session_state.scripts = data["scripts"]
    st.session_state.source = "sample"
    st.session_state.stage = 3


# ── live path ─────────────────────────────────────────────────────────────
if uploaded is not None:
    import pdfplumber
    if uploaded.type == "application/pdf":
        with pdfplumber.open(uploaded) as pdf:
            text = "\n".join(p.extract_text() or "" for p in pdf.pages)
    else:
        text = uploaded.read().decode("utf-8", errors="replace")

    if len(text.strip()) < 100:
        st.error("Could not extract enough text. A scanned image will not work; "
                 "this needs a text-based PDF or a .txt file.")
        st.stop()

    st.markdown(f'<p class="note">{len(text.split()):,} words extracted from '
                f'<code>{esc(uploaded.name)}</code>.</p>', unsafe_allow_html=True)

    if st.button("Run the agent chain", type="primary", disabled=not has_key):
        slot = st.empty()
        try:
            # Imported here rather than at module scope: agents/utils.py builds
            # the OpenAI client on import, which raises when no key is set. A
            # keyless instance should still load and still show the sample.
            from agents import (draft_negotiation_points, extract_clauses,
                                score_clauses)
            slot.markdown(pipeline(0), unsafe_allow_html=True)
            clauses = extract_clauses(text)

            slot.markdown(pipeline(1), unsafe_allow_html=True)
            scored = score_clauses(clauses)

            flagged = [s for s in scored if s.get("red_flag")]
            scripts = []
            if flagged:
                slot.markdown(pipeline(2), unsafe_allow_html=True)
                by_id = {c["clause_id"]: c for c in clauses}
                scripts = draft_negotiation_points([
                    {
                        "clause_id": s["clause_id"],
                        "clause_type": s.get("clause_type")
                        or by_id.get(s["clause_id"], {}).get("clause_type", "Clause"),
                        "source_quote": by_id.get(s["clause_id"], {}).get("source_quote", ""),
                        "severity_rationale": s.get("severity_rationale", ""),
                    }
                    for s in flagged
                ])
            slot.markdown(pipeline(3), unsafe_allow_html=True)
            st.session_state.update(clauses=clauses, scored=scored,
                                    scripts=scripts, stage=3, source="live")
        except Exception as exc:  # noqa: BLE001 - surfaced to the user deliberately
            slot.empty()
            st.error(f"The chain stopped: {type(exc).__name__}. "
                     f"Nothing was saved. Detail: {exc}")


# ── results ───────────────────────────────────────────────────────────────
clauses, scored = st.session_state.clauses, st.session_state.scored
if clauses and scored:
    by_id = {c["clause_id"]: c for c in clauses}
    flagged = [s for s in scored if s.get("red_flag")]
    worst = max((peak(s) for s in scored), default=0)
    band, band_colour = risk_band(worst)

    st.markdown(pipeline(3), unsafe_allow_html=True)
    if st.session_state.source == "sample":
        st.markdown('<p class="note">Showing a saved sample run. No API call was made.</p>',
                    unsafe_allow_html=True)

    st.markdown(
        f'<div class="tiles">'
        f'<div class="tile"><div class="k">Clauses</div><div class="v">{len(clauses)}</div>'
        f'<div class="c">extracted verbatim</div></div>'
        f'<div class="tile"><div class="k">Red flagged</div>'
        f'<div class="v" style="color:{DANGER if flagged else OK}">{len(flagged)}</div>'
        f'<div class="c">{round(100 * len(flagged) / max(1, len(scored)))}% of the contract</div></div>'
        f'<div class="tile"><div class="k">Peak risk</div>'
        f'<div class="v" style="color:{band_colour}">{worst}<span style="font-size:.9rem;'
        f'color:{TEXT_MUTED}">/100</span></div>'
        f'<div class="c">worst single axis, {band}</div></div>'
        f'<div class="tile"><div class="k">Scripts</div>'
        f'<div class="v">{len(st.session_state.scripts or [])}</div>'
        f'<div class="c">ready to send</div></div>'
        f'</div>', unsafe_allow_html=True)

    tab_over, tab_clauses, tab_scripts = st.tabs(
        ["Risk profile", f"Clauses ({len(clauses)})",
         f"Negotiation ({len(st.session_state.scripts or [])})"])

    # ---- overview ----
    with tab_over:
        avg = {k: sum(int(s.get(k) or 0) for s in scored) / len(scored) for k, _ in AXES}
        labels = [lbl for _, lbl in AXES]
        mine = [round(avg[k]) for k, _ in AXES]
        market = [30, 25, 20]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=market + market[:1], theta=labels + labels[:1], fill="toself",
            name="Market standard", line=dict(color=OK, width=2),
            fillcolor="rgba(39,201,63,0.12)"))
        fig.add_trace(go.Scatterpolar(
            r=mine + mine[:1], theta=labels + labels[:1], fill="toself",
            name="This contract", line=dict(color=DANGER, width=2),
            fillcolor="rgba(255,95,86,0.18)"))
        fig.update_layout(
            polar=dict(
                bgcolor=BG_CARD,
                radialaxis=dict(visible=True, range=[0, 100], gridcolor=BORDER,
                                tickfont=dict(color=TEXT_MUTED, size=10), linecolor=BORDER),
                angularaxis=dict(gridcolor=BORDER, tickfont=dict(color=TEXT, size=12),
                                 linecolor=BORDER)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color=TEXT),
            legend=dict(orientation="h", y=-0.12, x=.5, xanchor="center",
                        font=dict(color=TEXT_MUTED, size=11)),
            margin=dict(l=70, r=70, t=30, b=50), height=420)

        c1, c2 = st.columns([3, 2])
        with c1:
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})
        with c2:
            st.markdown('<div style="padding-top:1.2rem">', unsafe_allow_html=True)
            for key, label in AXES:
                st.markdown(meter(label, round(avg[key])), unsafe_allow_html=True)
                st.markdown('<div style="height:.7rem"></div>', unsafe_allow_html=True)
            st.markdown(
                f'<p class="note">Averaged across every clause, against a market-standard '
                f'baseline. Anything above 70 on a single clause is worth negotiating or '
                f'refusing. The baseline is a fixed reference, not a measured benchmark.</p>'
                '</div>', unsafe_allow_html=True)

    # ---- clauses ----
    with tab_clauses:
        st.session_state.only_flagged = st.toggle(
            "Red-flagged only", value=st.session_state.only_flagged)
        rows = sorted(scored, key=peak, reverse=True)
        if st.session_state.only_flagged:
            rows = [s for s in rows if s.get("red_flag")]
        st.markdown(f'<p class="note">Sorted by worst axis, highest first. '
                    f'Showing {len(rows)} of {len(scored)}.</p>', unsafe_allow_html=True)

        for s in rows:
            src = by_id.get(s["clause_id"], {})
            flag = bool(s.get("red_flag"))
            ctype = esc(s.get("clause_type") or src.get("clause_type") or "Clause")
            body = [
                f'<div class="clause {"flag" if flag else "clean"}">',
                f'<div class="clause-head"><div><span class="clause-type">{ctype}</span> '
                f'<span class="clause-id">clause {esc(s.get("clause_id"))}</span></div>'
                f'<span class="badge {"high" if flag else "low"}">'
                f'{"red flag" if flag else "clear"}</span></div>',
            ]
            if src.get("source_quote"):
                body.append(f'<div class="quote">{esc(src["source_quote"])}</div>')
            if src.get("plain_english_summary"):
                body.append(f'<div class="plain">{esc(src["plain_english_summary"])}</div>')
            body.append('<div class="meters">'
                        + "".join(meter(lbl, int(s.get(k) or 0)) for k, lbl in AXES)
                        + "</div>")
            if s.get("severity_rationale"):
                body.append(f'<div class="rationale"><b>Why:</b> '
                            f'{esc(s["severity_rationale"])}</div>')
            # Surfaced deliberately: the scorer has always produced this and the
            # previous UI dropped it on the floor.
            if s.get("jurisdiction_note"):
                body.append(f'<div class="juris">{esc(s["jurisdiction_note"])}</div>')
            body.append("</div>")
            st.markdown("".join(body), unsafe_allow_html=True)

    # ---- scripts ----
    with tab_scripts:
        scripts = st.session_state.scripts or []
        if not scripts:
            st.markdown('<p class="note">Nothing was red-flagged, so there is nothing '
                        'to push back on. That is a result, not an empty state.</p>',
                        unsafe_allow_html=True)
        else:
            st.download_button(
                "Download all scripts (.txt)",
                data="\n\n---\n\n".join(
                    f"Re: {n.get('clause_type', 'Clause')} (clause {n.get('clause_id')})\n"
                    f"{n.get('negotiation_script', '')}" for n in scripts),
                file_name="adverse-insight-negotiation-points.txt", mime="text/plain")
            st.markdown('<div style="height:.9rem"></div>', unsafe_allow_html=True)
            for n in scripts:
                st.markdown(
                    f'<div class="script"><div class="sh">{esc(n.get("clause_type", "Clause"))} '
                    f'<span class="clause-id">clause {esc(n.get("clause_id"))}</span></div>'
                    f'<div class="sb">{esc(n.get("negotiation_script", ""))}</div></div>',
                    unsafe_allow_html=True)

    st.markdown(
        f'<div style="margin-top:2rem;padding-top:1rem;border-top:1px solid {BORDER}">'
        f'<p class="note"><b style="color:{TEXT}">Not legal advice.</b> This is '
        f'AI-generated analysis to help you read a contract more carefully, not a '
        f'substitute for a lawyer. Scores are a model\'s judgement and will vary '
        f'between runs.</p></div>', unsafe_allow_html=True)

else:
    st.markdown(pipeline(0), unsafe_allow_html=True)
    st.markdown(
        f'<p class="note" style="margin-top:1rem">Built in 48 hours for the Codex '
        f'Creator Challenge. Source on '
        f'<a href="https://github.com/chima-ukachukwu-sec/adverse-insight" '
        f'style="color:{ACCENT}">GitHub</a>, and a write-up of how it was built and '
        f'how it holds up under prompt injection at '
        f'<a href="https://chimaukachukwu.com/portfolio/case-studies/adverse-insight.html" '
        f'style="color:{ACCENT}">chimaukachukwu.com</a>.</p>', unsafe_allow_html=True)
