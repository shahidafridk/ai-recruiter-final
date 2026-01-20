# app/schema.py

"""
Output Schema Validation
------------------------
Validates the STRUCTURE of AI output only.

This module:
- Does NOT judge correctness
- Does NOT override AI decisions
- Does NOT apply business rules

It exists solely to ensure the AI output
is complete, well-formed, and renderable.
"""

from typing import Dict, Any, Tuple


# -------------------
# REQUIRED STRUCTURE
# --------------------

REQUIRED_TOP_LEVEL_FIELDS = {
    "decision": str,
    "ats_score": (int, float),
    "decision_summary": str,
    "detailed_explanation": str,
    "strengths": list,
    "gaps": list,
    "keyword_analysis": dict,
    "improvement_suggestions": list,
}

KEYWORD_ANALYSIS_FIELDS = {
    "important_keywords_from_jd": list,
    "clearly_present_in_resume": list,
    "weak_or_implicit_in_resume": list,
    "missing_from_resume": list,
}


# ------------------
# PUBLIC VALIDATOR
# ------------------

def validate_ai_output(output: Dict) -> Tuple[bool, str]:
    """
    Validates the STRUCTURE of the AI recruiter output.

    Returns:
        (True, "OK") if valid
        (False, human-readable error message) if invalid
    """

    if not isinstance(output, dict):
        return False, "AI output must be a JSON object"

    # ------------------
    # Top-level fields
    # ------------------
    for field, expected_type in REQUIRED_TOP_LEVEL_FIELDS.items():
        if field not in output:
            return False, f"Missing required field: '{field}'"

        if not isinstance(output[field], expected_type):
            return False, (
                f"Field '{field}' must be of type "
                f"{_type_name(expected_type)}"
            )

    # ----------------
    # Decision sanity 
    # ----------------
    if output["decision"] not in {"PASS", "BORDERLINE", "REJECT"}:
        return False, (
            "Field 'decision' must be one of: PASS, BORDERLINE, REJECT"
        )

    if not (0 <= output["ats_score"] <= 100):
        return False, "Field 'ats_score' must be between 0 and 100"

    # ------------------
    # Explanation depth 
    # -----------------
    explanation = output["detailed_explanation"].strip()
    if len(explanation) < 200:
        return False, (
            "Detailed explanation is too short. "
            "It must clearly explain the decision using resume and JD content."
        )

    # -----------------------------
    # Strengths / Gaps structure
    # -----------------------------
    if not _validate_list_of_dicts(output["strengths"]):
        return False, "Field 'strengths' must be a list of objects"

    if not _validate_list_of_dicts(output["gaps"]):
        return False, "Field 'gaps' must be a list of objects"

    # -----------------------------
    # Keyword analysis structure
    # -----------------------------
    ka = output["keyword_analysis"]
    if not isinstance(ka, dict):
        return False, "Field 'keyword_analysis' must be an object"

    for field, expected_type in KEYWORD_ANALYSIS_FIELDS.items():
        if field not in ka:
            return False, (
                f"Missing keyword_analysis field: '{field}'"
            )
        if not isinstance(ka[field], expected_type):
            return False, (
                f"keyword_analysis.{field} must be a list"
            )

    # -----------------------------
    # Improvement suggestions
    # -----------------------------
    if not _validate_list_of_dicts(output["improvement_suggestions"]):
        return False, (
            "Field 'improvement_suggestions' must be a list of objects"
        )

    return True, "OK"


# -------------------------
# HELPERS (STRUCTURE ONLY)
# --------------------------

def _validate_list_of_dicts(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    return all(isinstance(item, dict) for item in value)


def _type_name(t: Any) -> str:
    if isinstance(t, tuple):
        return " or ".join(x.__name__ for x in t)
    return t.__name__

