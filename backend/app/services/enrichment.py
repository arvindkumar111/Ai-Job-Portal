import json
import time
import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.gemini_api_key)

ENRICHMENT_PROMPT = """You are analyzing a job description to extract structured information.
Return ONLY valid JSON, no other text, in exactly this format:
{{
  "skills": ["skill1", "skill2"],
  "role_category": "short role name like 'Backend Engineer' or 'Data Analyst'",
  "experience_level": "one of: Fresher, 0-2 years, 2-5 years, 5+ years, Not specified"
}}

Job Title: {title}
Job Description: {description}
"""

# Ordered by preference: try the first, fall back to the next if it fails.
MODEL_FALLBACK_CHAIN = [
    "gemini-3.6-flash",
    "gemini-3.7-flash",   # newest/most rate-limited, kept as last resort
]

def _call_model(model_name: str, prompt: str) -> str:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text.strip()

def _parse_json_response(raw_text: str) -> dict:
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`").replace("json\n", "", 1)
    return json.loads(raw_text)

def enrich_job(title: str, description: str) -> dict:
    """Tries each model in MODEL_FALLBACK_CHAIN in order. Falls back to the
    next model on failure (rate limit, timeout, bad response). If every
    model fails, returns safe defaults rather than crashing ingestion."""
    prompt = ENRICHMENT_PROMPT.format(title=title, description=description[:3000])

    for attempt, model_name in enumerate(MODEL_FALLBACK_CHAIN):
        try:
            raw_text = _call_model(model_name, prompt)
            parsed = _parse_json_response(raw_text)

            return {
                "tags": parsed.get("skills", []),
                "role_category": parsed.get("role_category", "Not specified"),
                "experience_required": parsed.get("experience_level", "Not specified"),
            }

        except Exception as e:
            print(f"[{model_name}] enrichment failed for '{title}': {e}")
            if attempt < len(MODEL_FALLBACK_CHAIN) - 1:
                time.sleep(1)  # brief pause before trying next model
                continue

    # every model in the chain failed
    return {
        "tags": [],
        "role_category": "Not specified",
        "experience_required": "Not specified",
    }