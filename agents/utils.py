import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def safe_json_parse(response_text: str) -> dict:
    """
    Handles the #1 failure mode: OpenAI returns JSON wrapped in markdown code blocks
    or with trailing commas. This parser survives both.
    """
    text = response_text.strip()
    
    # Strip markdown ```json ... ``` wrappers
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json) and last line (```)
        text = "\n".join(lines[1:-1])
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Last resort: try to fix trailing commas
        import re
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        return json.loads(text)

def call_agent(system_prompt: str, user_content: str, model: str = "gpt-4o-mini", temperature: float = 0.1) -> str:
    """
    Single point of contact for all OpenAI calls.
    Low temperature = deterministic, reproducible results. Critical for contract analysis.
    """
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    )
    return response.choices[0].message.content