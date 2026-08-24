"""
referrals/categories.py
=======================
Fictional referral category definitions for the prototype.

IMPORTANT:
These are FICTIONAL general referral categories. This system does NOT
contain real emergency numbers, named shelters, real police agencies,
or actual victim services directories.

The referral logic is intended to DEMONSTRATE workflow architecture —
not to serve as an operational referral resource. Any real deployment
would require integration with verified, jurisdiction-specific resources
reviewed by subject-matter experts.
"""
from __future__ import annotations

# ── Fictional referral category definitions ───────────────────────────────────

REFERRAL_CATEGORIES = {
    "specialized_trafficking_support": {
        "label": "Specialized Trafficking Support Service",
        "description": (
            "Referral to a specialist service equipped to assess and support "
            "individuals who may have experienced trafficking. "
            "[PROTOTYPE — not a real service directory]"
        ),
        "indicator_categories": [
            "coercion_threats",
            "restriction_of_movement",
            "document_confiscation",
            "inability_to_leave_employment",
            "violence_threat_of_violence",
        ],
    },
    "emergency_safeguarding_review": {
        "label": "Emergency Safeguarding Review",
        "description": (
            "Immediate escalation to a senior human safeguarding officer for urgent review. "
            "This is an internal escalation pathway, not an autonomous action. "
            "[PROTOTYPE — internal workflow step]"
        ),
        "indicator_categories": [
            "violence_threat_of_violence",
            "restriction_of_movement",
            "coercion_threats",
        ],
    },
    "legal_assistance": {
        "label": "Legal Assistance",
        "description": (
            "Access to legal advice regarding rights, contracts, and employment law. "
            "[PROTOTYPE — not a real legal service]"
        ),
        "indicator_categories": [
            "document_confiscation",
            "deception_regarding_work",
            "wage_control_withholding",
            "debt_recruitment_pressure",
        ],
    },
    "immigration_legal_status": {
        "label": "Immigration / Legal Status Assistance",
        "description": (
            "Support with immigration status concerns, documentation, and legal residency. "
            "[PROTOTYPE — not a real immigration service]"
        ),
        "indicator_categories": [
            "exploitation_of_vulnerability",
            "document_confiscation",
        ],
    },
    "housing_shelter_support": {
        "label": "Housing / Shelter Support",
        "description": (
            "Safe alternative accommodation support, particularly where employer controls current housing. "
            "[PROTOTYPE — not a real shelter directory]"
        ),
        "indicator_categories": [
            "restriction_of_movement",
            "dependency_control",
            "unsafe_accommodation",
        ],
    },
    "healthcare": {
        "label": "Healthcare",
        "description": (
            "Access to physical and/or mental health services. "
            "[PROTOTYPE — not a real healthcare directory]"
        ),
        "indicator_categories": [
            "violence_threat_of_violence",
            "unsafe_accommodation",
        ],
    },
    "psychosocial_support": {
        "label": "Psychosocial Support",
        "description": (
            "Counselling and psychological support services. "
            "[PROTOTYPE — not a real counselling directory]"
        ),
        "indicator_categories": [
            "isolation",
            "coercion_threats",
            "violence_threat_of_violence",
        ],
    },
    "labour_rights_support": {
        "label": "Labour Rights Support",
        "description": (
            "Information and advocacy relating to employment rights, unpaid wages, and working conditions. "
            "[PROTOTYPE — not a real labour support service]"
        ),
        "indicator_categories": [
            "wage_control_withholding",
            "deception_regarding_work",
            "debt_recruitment_pressure",
            "unsafe_accommodation",
        ],
    },
    "financial_assistance": {
        "label": "Financial Assistance",
        "description": (
            "Emergency financial support where wages have been withheld or debt is being used as control. "
            "[PROTOTYPE — not a real financial service]"
        ),
        "indicator_categories": [
            "wage_control_withholding",
            "debt_recruitment_pressure",
        ],
    },
    "case_management_follow_up": {
        "label": "Case Management Follow-Up",
        "description": (
            "Ongoing structured case management and follow-up for continued support and monitoring. "
            "[PROTOTYPE — internal workflow step]"
        ),
        "indicator_categories": [],  # always available as a baseline option
    },
}


def get_referrals_for_indicators(indicator_categories: dict) -> dict[str, str]:
    """
    Maps detected indicator categories to relevant referral types.

    Args:
        indicator_categories: dict mapping category_key → count

    Returns:
        dict mapping referral_key → rationale_string
    """
    detected_cats = set(k for k, v in indicator_categories.items() if v > 0)
    result = {}

    for ref_key, ref_data in REFERRAL_CATEGORIES.items():
        matching = detected_cats & set(ref_data["indicator_categories"])
        if matching or ref_key == "case_management_follow_up":
            if matching:
                indicator_labels = [
                    k.replace("_", " ").title() for k in matching
                ]
                rationale = (
                    f"Recommended based on detected indicators: "
                    f"{', '.join(indicator_labels)}."
                )
            else:
                rationale = "Recommended as standard case-management follow-up."
            result[ref_key] = rationale

    return result
