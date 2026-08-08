"""
Visual layer for Adverse Insight.

Kept separate from app.py so the page file stays readable: app.py should show
the flow of the agent chain, not three hundred lines of CSS. The palette is
the same one used on chimaukachukwu.com, so the demo and the case study that
describes it look like they belong to each other.
"""

# Palette, mirroring the portfolio's design tokens.
BG          = "#0a0e14"
BG_CARD     = "#161c24"
BG_RAISED   = "#1a2230"
BORDER      = "#1e293b"
BORDER_HOVER= "#2d3a4a"
TEXT        = "#e6edf3"
TEXT_MUTED  = "#8a94a0"
ACCENT      = "#00d4aa"
DANGER      = "#ff5f56"
WARN        = "#ffbd2e"
OK          = "#27c93f"

# Risk bands. One definition, used by the meters, the badges and the summary,
# so a clause cannot be amber in one place and red in another.
def risk_band(score: int) -> tuple:
    """Return (label, colour) for a 0-100 risk score."""
    if score >= 70:
        return "high", DANGER
    if score >= 40:
        return "elevated", WARN
    return "low", OK


CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&family=JetBrains+Mono:wght@400;500&display=swap');

  .stApp {{ background: {BG}; }}

  /* Streamlit's own chrome adds nothing here and costs vertical space. */
  #MainMenu, footer, header {{ visibility: hidden; }}
  .block-container {{ padding-top: 2.5rem; padding-bottom: 4rem; max-width: 1180px; }}

  html, body, [class*="css"], .stMarkdown, p, span, div, li {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      color: {TEXT};
  }}
  code, .mono {{ font-family: 'JetBrains Mono', monospace; }}

  /* ---- hero ---- */
  .ai-eyebrow {{
      font-family: 'JetBrains Mono', monospace; font-size: .72rem; letter-spacing: .18em;
      text-transform: uppercase; color: {ACCENT}; margin-bottom: .6rem;
  }}
  .ai-title {{
      font-size: 2.6rem; font-weight: 800; letter-spacing: -.02em;
      line-height: 1.1; margin: 0 0 .6rem 0; color: {TEXT};
  }}
  .ai-sub {{ font-size: 1.02rem; color: {TEXT_MUTED}; max-width: 62ch; line-height: 1.6; }}

  /* ---- agent pipeline ---- */
  .pipe {{ display: flex; gap: .5rem; margin: 1.6rem 0 .4rem 0; flex-wrap: wrap; }}
  .pipe-step {{
      flex: 1 1 180px; border: 1px solid {BORDER}; border-radius: 10px;
      padding: .8rem .9rem; background: {BG_CARD}; position: relative;
      transition: border-color .2s ease, background .2s ease;
  }}
  .pipe-step .n {{
      font-family: 'JetBrains Mono', monospace; font-size: .68rem;
      letter-spacing: .12em; color: {TEXT_MUTED}; text-transform: uppercase;
  }}
  .pipe-step .t {{ font-weight: 600; font-size: .95rem; margin-top: .18rem; }}
  .pipe-step .d {{ font-size: .78rem; color: {TEXT_MUTED}; margin-top: .2rem; line-height: 1.45; }}
  .pipe-step.done {{ border-color: {ACCENT}; }}
  .pipe-step.done .n {{ color: {ACCENT}; }}
  .pipe-step.active {{ border-color: {ACCENT}; background: {BG_RAISED}; }}

  /* ---- metric tiles ---- */
  .tiles {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: .7rem; margin: .4rem 0 1.4rem 0; }}
  .tile {{ border: 1px solid {BORDER}; border-radius: 10px; padding: 1rem 1.1rem; background: {BG_CARD}; }}
  .tile .k {{
      font-family: 'JetBrains Mono', monospace; font-size: .66rem; letter-spacing: .12em;
      text-transform: uppercase; color: {TEXT_MUTED};
  }}
  .tile .v {{ font-size: 1.9rem; font-weight: 800; letter-spacing: -.02em; margin-top: .3rem; line-height: 1; }}
  .tile .c {{ font-size: .74rem; color: {TEXT_MUTED}; margin-top: .35rem; }}

  /* ---- clause card ---- */
  .clause {{
      border: 1px solid {BORDER}; border-left: 3px solid {BORDER};
      border-radius: 10px; padding: 1rem 1.15rem; background: {BG_CARD}; margin-bottom: .65rem;
  }}
  .clause.flag {{ border-left-color: {DANGER}; }}
  .clause.clean {{ border-left-color: {OK}; }}
  .clause-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; flex-wrap: wrap; }}
  .clause-type {{ font-weight: 600; font-size: 1rem; }}
  .clause-id {{ font-family: 'JetBrains Mono', monospace; font-size: .7rem; color: {TEXT_MUTED}; }}
  .badge {{
      font-family: 'JetBrains Mono', monospace; font-size: .64rem; letter-spacing: .1em;
      text-transform: uppercase; padding: .2rem .5rem; border-radius: 4px; border: 1px solid;
  }}
  .badge.high {{ color: {DANGER}; border-color: {DANGER}33; background: {DANGER}14; }}
  .badge.low  {{ color: {OK};     border-color: {OK}33;     background: {OK}14; }}

  .quote {{
      font-family: 'JetBrains Mono', monospace; font-size: .78rem; line-height: 1.6;
      color: {TEXT_MUTED}; border-left: 2px solid {BORDER_HOVER};
      padding: .5rem .8rem; margin: .7rem 0; background: {BG}; border-radius: 0 6px 6px 0;
  }}
  .plain {{ font-size: .9rem; line-height: 1.6; margin: .5rem 0 .8rem 0; }}

  /* ---- risk meters ---- */
  .meters {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: .6rem; margin-top: .5rem; }}
  .meter .ml {{ display: flex; justify-content: space-between; font-size: .74rem; color: {TEXT_MUTED}; margin-bottom: .28rem; }}
  .meter .mv {{ font-family: 'JetBrains Mono', monospace; color: {TEXT}; }}
  .track {{ height: 5px; background: {BG}; border-radius: 3px; overflow: hidden; }}
  .fill {{ height: 100%; border-radius: 3px; }}

  .rationale {{ font-size: .84rem; color: {TEXT_MUTED}; line-height: 1.6; margin-top: .8rem; }}
  .rationale b {{ color: {TEXT}; font-weight: 600; }}
  .juris {{
      font-size: .8rem; color: {TEXT_MUTED}; line-height: 1.6; margin-top: .5rem;
      padding-top: .5rem; border-top: 1px dashed {BORDER};
  }}

  /* ---- script card ---- */
  .script {{
      border: 1px solid {BORDER}; border-left: 3px solid {ACCENT}; border-radius: 10px;
      padding: 1rem 1.15rem; background: {BG_CARD}; margin-bottom: .65rem;
  }}
  .script .sh {{ font-weight: 600; margin-bottom: .45rem; }}
  .script .sb {{ font-size: .92rem; line-height: 1.65; color: {TEXT}; }}

  .note {{ font-size: .78rem; color: {TEXT_MUTED}; line-height: 1.6; }}

  /* ---- streamlit widget overrides ---- */
  [data-testid="stFileUploaderDropzone"] {{
      background: {BG_CARD}; border: 1px dashed {BORDER_HOVER}; border-radius: 10px;
  }}
  .stButton > button {{
      background: {ACCENT}; color: {BG}; border: none; border-radius: 8px;
      font-weight: 600; padding: .6rem 1.1rem; transition: filter .15s ease;
  }}
  .stButton > button:hover {{ filter: brightness(1.08); color: {BG}; }}
  .stDownloadButton > button {{
      background: transparent; color: {ACCENT}; border: 1px solid {ACCENT}55;
      border-radius: 8px; font-weight: 500;
  }}
  [data-testid="stSidebar"] {{ background: {BG_CARD}; border-right: 1px solid {BORDER}; }}
  .stTabs [data-baseweb="tab-list"] {{ gap: 1.4rem; border-bottom: 1px solid {BORDER}; }}
  .stTabs [data-baseweb="tab"] {{ background: transparent; color: {TEXT_MUTED}; font-weight: 500; }}
  .stTabs [aria-selected="true"] {{ color: {ACCENT}; }}

  /* Respect the same accessibility rule the portfolio follows. */
  @media (prefers-reduced-motion: reduce) {{
      * {{ transition: none !important; animation: none !important; }}
  }}
</style>
"""


def meter(label: str, score: int) -> str:
    """One labelled risk bar. Colour comes from the shared band function."""
    _, colour = risk_band(score)
    return (
        f'<div class="meter"><div class="ml"><span>{label}</span>'
        f'<span class="mv">{score}</span></div>'
        f'<div class="track"><div class="fill" style="width:{max(0, min(100, score))}%;'
        f'background:{colour}"></div></div></div>'
    )


def pipeline(stage: int) -> str:
    """
    Renders the three-agent chain with stages 0..3 completed.
    Showing the chain is the point: the architecture is the thing worth seeing.
    """
    steps = [
        ("Agent 01", "Extractor", "Splits the document into clauses, verbatim."),
        ("Agent 02", "Adversarial scorer", "Scores each clause on three risk axes."),
        ("Agent 03", "Negotiator", "Drafts counter-language for what got flagged."),
    ]
    out = ['<div class="pipe">']
    for i, (n, t, d) in enumerate(steps):
        cls = "done" if i < stage else ("active" if i == stage else "")
        mark = "✓ " if i < stage else ""
        out.append(
            f'<div class="pipe-step {cls}"><div class="n">{mark}{n}</div>'
            f'<div class="t">{t}</div><div class="d">{d}</div></div>'
        )
    out.append("</div>")
    return "".join(out)
