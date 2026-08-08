# ⚖️ Adverse Insight

**AI-Powered Contract Risk Triage**

Built for the [Codex Creator Challenge](https://codexcreator.com), this app chains three AI agents to analyze any contract in seconds.

## 🎯 Live Demo

🔗 **[adverse-insight.streamlit.app](https://adverse-insight.streamlit.app)**

---

## 🤖 How It Works

| Agent | Model | Function |
|---|---|---|
| **Agent 1: Extractor** | GPT-4o-mini | Reads the contract and extracts every clause into structured JSON |
| **Agent 2: Red-Team Scorer** | GPT-4o-mini | Adversarial risk scoring on financial liability, termination asymmetry, and data rights (0-100 scale) |
| **Agent 3: Negotiator** | GPT-4o | Drafts plain-English negotiation scripts for every red-flagged clause |

---

## 📊 Features

- Upload PDF or TXT contracts
- Radar chart visualizing risk vs. market standards
- Clause-by-clause breakdown with source quotes
- One-click download of negotiation scripts
- Built with cybersecurity threat-modeling methodology

---

## 🛠 Tech Stack

- **Frontend:** Streamlit
- **AI Orchestration:** OpenAI API (GPT-4o-mini + GPT-4o)
- **PDF Processing:** PDFPlumber
- **Visualization:** Plotly
- **Deployment:** Streamlit Community Cloud

---

## 🚀 Run Locally

git clone https://github.com/chima-ukachukwu-sec/adverse-insight.git
cd adverse-insight
pip install -r requirements.txt
streamlit run app.py

Set your OpenAI API key in a `.env` file:

OPENAI_API_KEY=sk-your-key-here

---

## ⚠️ Disclaimer

Adverse Insight provides AI-generated educational content intended to help users understand contracts better. It is **NOT legal advice**. Always consult a qualified legal professional before making decisions based on contract terms.

---

## 👤 Author

**Chima Anthony Ukachukwu**

Master's in Cybersecurity | Class of 2025

---

## Running it

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...      # live analysis needs a key
streamlit run app.py
```

Without a key the app still loads and the **Load a sample analysis** button
works. That sample is a real saved run against `samples/one-sided-contract.txt`,
not hand-written output, so the interface can be explored without spending
anything on a demo.

## Layout

```
app.py                    presentation only: flow, layout, what gets shown
ui/theme.py               palette, CSS, risk bands, the meter and pipeline widgets
agents/                   the chain itself. extractor -> scorer -> negotiator
samples/analysis.json     one real saved run, used by the sample button
```

`app.py` never decides what a clause is worth. Scoring lives entirely in
`agents/`, which keeps the write-up of the chain's behaviour valid when the
interface changes.

## Known limits

- Scores are a model's judgement and move between runs. The same contract has
  scored 100/100 and 90/100 on consecutive runs.
- The market-standard baseline on the radar chart is a fixed reference, not a
  measured benchmark.
- Nothing here detects prompt injection. The extraction step happens to drop
  instructions aimed at the reviewer, but that is a side effect of emitting
  short verbatim quotes, not a control. There is a write-up of that testing at
  [chimaukachukwu.com](https://chimaukachukwu.com/portfolio/case-studies/adverse-insight.html).
- Not legal advice.
