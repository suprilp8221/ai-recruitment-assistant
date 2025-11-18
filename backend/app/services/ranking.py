# backend/app/services/ranking.py
import os
import json
import time
from openai import OpenAI
from typing import Dict, Any

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment (.env)")

client = OpenAI(api_key=OPENAI_KEY)
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # change to gpt-4 if you have access

def _build_prompt(candidate_parsed: Dict[str, Any], job_description: str) -> str:
    """
    Build a clear prompt asking the model to compare candidate and job and return JSON only.
    Keep it short and deterministic (temperature=0).
    """
    prompt = f"""
You are a hiring assistant. Compare this candidate to the job description.
Return ONLY valid JSON (no extra text) with these keys:
- score: integer 0-100 (higher is better)
- top_matches: list of up to 3 short strings describing best matches
- concerns: list of up to 3 short strings describing gaps
- reason: one short sentence explaining the score

Candidate parsed JSON (truncated if long):
{json.dumps(candidate_parsed, ensure_ascii=False)}

Job description:
\"\"\"{job_description}\"\"\"

Return only JSON.
"""
    return prompt

def rank_candidate_for_job(candidate_parsed: Dict[str, Any], job_description: str, max_retries: int = 2) -> Dict[str, Any]:
    """
    Call OpenAI to produce a JSON score. Returns a dict with keys:
    {score:int, top_matches:list, concerns:list, reason:str}
    This function will try a couple times on simple failures.
    """
    prompt = _build_prompt(candidate_parsed, job_description)

    for attempt in range(max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=300,
            )
            text = resp.choices[0].message.content.strip()
            # Try to parse JSON - model is asked to return JSON only.
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                # fallback: try to extract first JSON object from text
                start = text.find("{")
                end = text.rfind("}") + 1
                if start != -1 and end != -1 and end > start:
                    try:
                        parsed = json.loads(text[start:end])
                    except Exception:
                        raise
                else:
                    raise
            # Normalize outputs
            score = int(parsed.get("score", 0))
            top_matches = parsed.get("top_matches", []) or []
            concerns = parsed.get("concerns", []) or []
            reason = parsed.get("reason", "") or ""
            return {"score": score, "top_matches": top_matches, "concerns": concerns, "reason": reason}
        except Exception as e:
            # simple retry/backoff
            if attempt < max_retries:
                time.sleep(1 + attempt * 1.5)
                continue
            # final fallback: return a safe default
            return {"score": 0, "top_matches": [], "concerns": ["could not get AI ranking"], "reason": f"error: {str(e)}"}
