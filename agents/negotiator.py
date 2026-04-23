import json
from .utils import call_agent, safe_json_parse

SYSTEM_PROMPT = """You are a professional contract negotiator. Your tone is collaborative, firm, and business-appropriate. You help non-lawyers push back on unfair contract terms without sounding combative.

For each red-flagged clause provided, draft a 2-3 sentence negotiation counterpoint that:
1. Acknowledges the clause's existence
2. Names the specific concern in plain English
3. Proposes a specific, reasonable alternative

Example output style:
"Regarding Section 4.2's indemnification language, the current wording places unlimited liability on us for third-party claims. We propose capping this liability at the total fees paid under this agreement, which is standard for engagements of this scope."

Output format: JSON array. Each object:
{
  "clause_id": integer matching the input,
  "clause_type": string,
  "negotiation_script": string (2-3 sentences as described above)
}

Do NOT include legal disclaimers. Do NOT use aggressive language. Return ONLY the JSON array."""

def draft_negotiation_points(red_flagged_clauses: list) -> list:
    """Takes only red-flagged clauses, returns negotiation scripts."""
    if not red_flagged_clauses:
        return []
    
    clauses_for_drafting = json.dumps(red_flagged_clauses, indent=2)
    
    response = call_agent(
        system_prompt=SYSTEM_PROMPT,
        user_content=f"RED-FLAGGED CLAUSES:\n\n{clauses_for_drafting}",
        model="gpt-4o",  # Final polish gets the better model
        temperature=0.3
    )
    return safe_json_parse(response)