import json
from .utils import call_agent, safe_json_parse

SYSTEM_PROMPT = """You are a plaintiff's attorney and contract risk auditor. Your job is to find the trapdoors.

For each clause provided, assign risk scores from 0 to 100 on three dimensions:
- "financial_liability": How much money could this clause cost the signer?
- "termination_asymmetry": Does one party have unfair power to end the agreement?
- "data_rights_risk": Does the clause grant excessive data usage or ownership rights?

Also include:
- "red_flag": boolean (true if ANY score exceeds 70 OR the clause is unusually overreaching)
- "severity_rationale": string (one sentence explaining the highest risk found)
- "jurisdiction_note": string (one sentence on what makes this risky or standard)

Return a JSON array matching the input clause order. Each object:
{
  "clause_id": same integer as input,
  "financial_liability": int 0-100,
  "termination_asymmetry": int 0-100,
  "data_rights_risk": int 0-100,
  "red_flag": boolean,
  "severity_rationale": string,
  "jurisdiction_note": string
}

Rules:
- Be adversarial but honest. Do not inflate scores for benign clauses.
- A "standard" mutual indemnification should score ~30, not 80.
- Only red_flag clauses that a reasonable person would find objectionable.
- Return ONLY the JSON array."""

def score_clauses(clauses: list) -> list:
    """Takes extracted clauses, returns scored clauses with risk metrics."""
    clauses_json = [{"clause_id": c["clause_id"], "clause_type": c["clause_type"], "source_quote": c["source_quote"]} for c in clauses]
    
    response = call_agent(
        system_prompt=SYSTEM_PROMPT,
        user_content=f"CLAUSES TO SCORE:\n\n{json.dumps(clauses_json, indent=2)}",
        model="gpt-4o-mini"  # Mini is sufficient for scoring logic
    )
    return safe_json_parse(response)