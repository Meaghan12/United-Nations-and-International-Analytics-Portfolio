"""
services/referral_service.py
=============================
Maps indicator categories to referral resource categories.
Extracted from referrals/categories.py into a dedicated service layer.
"""
from __future__ import annotations

REFERRAL_CATEGORY_MAP: dict[str, dict] = {
    "specialized_trafficking_support": {
        "label": "Specialized Trafficking Support",
        "description": "Specialized support organizations for trafficking-related concerns.",
        "relevant_indicators": [
            "coercion_threats", "restriction_of_movement", "document_confiscation",
            "violence_threat_of_violence", "inability_to_leave_employment",
        ],
    },
    "emergency_safeguarding": {
        "label": "Emergency Safeguarding Review",
        "description": "Immediate safeguarding escalation where physical danger is indicated.",
        "relevant_indicators": ["violence_threat_of_violence", "coercion_threats"],
    },
    "legal_assistance": {
        "label": "Legal Assistance",
        "description": "Legal aid, rights advice, immigration law support.",
        "relevant_indicators": [
            "document_confiscation", "debt_recruitment_pressure",
            "restriction_of_movement", "inability_to_leave_employment",
        ],
    },
    "immigration_legal_status": {
        "label": "Immigration / Legal Status Assistance",
        "description": "Immigration status advice, visa assistance, legal residency support.",
        "relevant_indicators": [
            "document_confiscation", "exploitation_of_vulnerability",
            "debt_recruitment_pressure",
        ],
    },
    "housing_shelter": {
        "label": "Housing / Shelter Support",
        "description": "Emergency or transitional housing and shelter services.",
        "relevant_indicators": [
            "restriction_of_movement", "unsafe_accommodation",
            "inability_to_leave_employment",
        ],
    },
    "healthcare": {
        "label": "Healthcare",
        "description": "Medical care, physical health services, trauma-informed care.",
        "relevant_indicators": ["violence_threat_of_violence", "unsafe_accommodation"],
    },
    "psychosocial_support": {
        "label": "Psychosocial Support",
        "description": "Mental health, counselling, and psychosocial wellbeing support.",
        "relevant_indicators": [
            "coercion_threats", "isolation", "dependency_control",
            "violence_threat_of_violence",
        ],
    },
    "labour_rights": {
        "label": "Labour Rights Support",
        "description": "Employment rights, wage claims, labour standards agencies.",
        "relevant_indicators": [
            "wage_control_withholding", "deception_regarding_work",
            "debt_recruitment_pressure", "unsafe_accommodation",
        ],
    },
    "financial_assistance": {
        "label": "Financial Assistance",
        "description": "Emergency financial support, debt relief, income assistance.",
        "relevant_indicators": ["wage_control_withholding", "debt_recruitment_pressure"],
    },
    "case_management": {
        "label": "Case Management Follow-Up",
        "description": "Ongoing case coordination and support service navigation.",
        "relevant_indicators": [],  # always available
    },
}


def get_referrals_for_indicators(detected_categories: list[str]) -> list[dict]:
    """
    Return the appropriate referral categories for the given detected indicators.
    Always includes case management. Always returns prototype-only disclaimer.
    """
    matched = set()

    for key, meta in REFERRAL_CATEGORY_MAP.items():
        if key == "case_management":
            matched.add(key)
            continue
        if any(ind in meta["relevant_indicators"] for ind in detected_categories):
            matched.add(key)

    return [
        {
            "key": key,
            "label": REFERRAL_CATEGORY_MAP[key]["label"],
            "description": REFERRAL_CATEGORY_MAP[key]["description"],
        }
        for key in REFERRAL_CATEGORY_MAP
        if key in matched
    ]
