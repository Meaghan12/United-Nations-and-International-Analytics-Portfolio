"""
nodes/validate.py
=================
Node 4 — Validation

PERMITTED: Check field completeness; generate clarifying questions.
PROHIBITED: Assume missing data; make risk assessments; call LLM.

If required fields are absent, the system returns NEED_INFO with specific
clarifying questions rather than proceeding with incomplete information.
This prevents the model from hallucinating conclusions from sparse input.
"""
from __future__ import annotations

from utils.audit_log import append_audit

# Minimum fields required to proceed to indicator analysis.
# If any of these are missing or empty, NEED_INFO is returned.
REQUIRED_FIELDS = [
    "reported_concerns",
    "narrative",
]

# Fields that are highly useful but not strictly required.
# Their absence generates additional clarifying questions.
RECOMMENDED_FIELDS_WITH_QUESTIONS = {
    "employment_context": (
        "Can you describe the nature of the work or employment situation?"
    ),
    "documentation_control": (
        "Are the individual's personal documents (passport, ID, work permit) "
        "in their own possession, or are they held by someone else?"
    ),
    "freedom_of_movement": (
        "Is the individual free to come and go as they choose, "
        "or are there restrictions on their movement?"
    ),
    "wage_payment_concerns": (
        "Are wages being paid as agreed? Are there any deductions, "
        "withholdings, or payment irregularities?"
    ),
    "coercion_or_threats": (
        "Have any threats been made — to the individual or their family — "
        "by an employer, recruiter, or other party?"
    ),
    "recruitment_debt": (
        "Did the individual incur any fees or debts related to recruitment, "
        "travel, or placement? If so, approximately what amount?"
    ),
}


def validate_node(state: dict) -> dict:
    """
    Checks whether minimum required information is present.
    Generates targeted clarifying questions for missing information.
    """
    fields = state.get("masked_fields", {})
    narrative = state.get("masked_narrative", "")

    missing = []
    clarifying = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        value = fields.get(field, "").strip() if isinstance(fields.get(field), str) else ""
        if not value and not narrative.strip():
            missing.append(field)

    # Generate questions for recommended-but-missing fields
    for field, question in RECOMMENDED_FIELDS_WITH_QUESTIONS.items():
        value = fields.get(field, "")
        if not value or (isinstance(value, str) and value.strip().lower() in ["", "unknown", "n/a", "not provided"]):
            clarifying.append(question)

    # Check narrative length — very short narratives cannot be meaningfully assessed
    MIN_NARRATIVE_LENGTH = 50
    if len(narrative.strip()) < MIN_NARRATIVE_LENGTH and not any(
        fields.get(f, "").strip() for f in REQUIRED_FIELDS
    ):
        missing.append("narrative (too brief for assessment)")

    if missing:
        status = "INCOMPLETE"
        event = f"Validation failed — required fields missing or insufficient: {', '.join(missing)}"
    elif clarifying:
        status = "COMPLETE"
        event = f"Validation passed — {len(clarifying)} clarifying question(s) generated for enhanced assessment"
    else:
        status = "COMPLETE"
        event = "Validation passed — all fields present"

    audit = append_audit(state, "validate", event)

    return {
        **state,
        "validation_status": status,
        "missing_fields": missing,
        "clarifying_questions": clarifying,
        "audit_trail": audit,
    }
