# app/ai_recruiter_evaluator.py

from dotenv import load_dotenv
load_dotenv()

"""
AI Recruiter Evaluator
----------------------
Pure AI-driven recruiter simulation.

Guarantees:
- Uses a model that respects JSON contracts (Llama 3.3 70B)
- Always returns a normalized dict
- No rule-based logic
- No business decisions in code
"""

import os
import json
from typing import Dict, Any
from groq import Groq

from app.prompts import (
    RECRUITER_SYSTEM_PROMPT,
    RECRUITER_USER_PROMPT_TEMPLATE,
)


# --------------------------------------------------
# CONFIGURATION (CRITICAL)
# --------------------------------------------------

# UPDATED: Replaced deprecated 3.1 model with 3.3
DEFAULT_MODEL = "llama-3.3-70b-versatile"
MODEL_NAME = os.getenv("GROQ_MODEL", DEFAULT_MODEL)


# --------------------------------------------------
# INTERNAL HELPERS
# --------------------------------------------------

def _call_groq(client: Groq, resume_text: str, job_description_text: str) -> str:
    """
    Single Groq call.
    Enables JSON mode to ensure valid output.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": RECRUITER_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": RECRUITER_USER_PROMPT_TEMPLATE.format(
                    resume=resume_text.strip(),
                    job_description=job_description_text.strip(),
                ),
            },
        ],
        # --------------------------------------------------
        # CRITICAL FIX: ENABLE JSON MODE
        # --------------------------------------------------
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=3000,
        timeout=60,
    )

    return response.choices[0].message.content.strip()


def _normalize_keys(obj: Any) -> Any:
    """
    Recursively normalize JSON keys.
    Strips whitespace and quotes to prevent KeyError.
    """
    if isinstance(obj, dict):
        return {
            str(k).strip().strip('"').strip(): _normalize_keys(v)
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [_normalize_keys(item) for item in obj]

    return obj


def _extract_json(text: str) -> Dict:
    """
    Extract and parse JSON object from model output.
    Handles Markdown fences if present, but relies on JSON mode.
    """
    # 1. Remove markdown code blocks if the model adds them despite JSON mode
    cleaned = text.replace("```json", "").replace("```", "").strip()

    # 2. Locate the JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end <= start:
        # In JSON mode, sometimes the whole string is just the JSON
        # If brackets aren't found via find/rfind, try parsing the whole thing
        try:
            parsed = json.loads(cleaned)
            return _normalize_keys(parsed)
        except json.JSONDecodeError:
            raise ValueError(
                "Model did not return a valid JSON object.\n\n"
                f"Raw output:\n{cleaned}"
            )

    # 3. Parse the substring
    json_str = cleaned[start:end + 1]
    
    try:
        parsed = json.loads(json_str)
        return _normalize_keys(parsed)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON Parsing Failed: {str(e)}\nContent: {json_str}")


# --------------------------------------------------
# PUBLIC API
# --------------------------------------------------

def evaluate_resume_with_ai(
    *,
    resume_text: str,
    job_description_text: str,
) -> Dict:
    """
    Authoritative evaluation entrypoint.
    """

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    client = Groq(api_key=api_key)

    raw = _call_groq(client, resume_text, job_description_text)

    try:
        return _extract_json(raw)

    except Exception as e:
        # One retry only — if this fails, stop.
        # Often a retry fixes a random JSON syntax glitch.
        retry = _call_groq(client, resume_text, job_description_text)
        try:
            return _extract_json(retry)
        except Exception:
            raise ValueError(
                "AI failed to return valid JSON after retry.\n"
                f"Error: {str(e)}"
            ) from e