"""
indicators/framework.py
=======================
Demonstration Indicator Framework

IMPORTANT DISCLAIMER:
This is a PROTOTYPE indicator framework designed to demonstrate responsible AI
architecture. It is NOT an official UN, IOM, ILO, or legal trafficking-
identification protocol. It is NOT validated for operational deployment.
Real trafficking identification requires trained professionals, survivor-informed
protocols, legal frameworks, and formal case-management processes.

This framework is deliberately designed to be replaceable — a validated
framework could be substituted by a subject-matter expert without changing
the surrounding architecture.

The 12 indicator categories below are inspired by publicly documented
trafficking awareness frameworks (e.g., ILO forced labour indicators,
Palermo Protocol definitions) but are simplified for prototype purposes
and carry NO legal or clinical authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ── Indicator category definitions ───────────────────────────────────────────

INDICATOR_CATEGORIES = {
    "coercion_threats": {
        "label": "Coercion / Threats",
        "description": "Verbal threats, threats to family members, threatened deportation or legal consequences.",
        "severity_weight": 3,
        "examples": [
            "threatened with deportation",
            "threatened with harm to family",
            "verbal threats from employer",
            "threatened if they refuse to comply",
            "warned not to speak to authorities",
        ],
    },
    "restriction_of_movement": {
        "label": "Restriction of Movement",
        "description": "Cannot leave workplace or accommodation; locked in; curfew enforced.",
        "severity_weight": 3,
        "examples": [
            "cannot leave freely",
            "locked in accommodation",
            "curfew enforced",
            "movement monitored",
            "not permitted to go out without supervision",
        ],
    },
    "document_confiscation": {
        "label": "Document Confiscation",
        "description": "Passport, identity documents, or work permits retained or withheld by employer or recruiter.",
        "severity_weight": 3,
        "examples": [
            "passport retained by employer",
            "identity documents withheld",
            "work permit held by recruiter",
            "unable to access own documents",
        ],
    },
    "debt_recruitment_pressure": {
        "label": "Debt / Recruitment Pressure",
        "description": "Excessive recruitment fees, ongoing debt bondage, debt used as control mechanism.",
        "severity_weight": 2,
        "examples": [
            "large recruitment fee incurred",
            "ongoing debt to employer or recruiter",
            "debt used to prevent leaving",
            "excessive deductions for accommodation or food",
        ],
    },
    "wage_control_withholding": {
        "label": "Wage Control / Withholding",
        "description": "Wages withheld, paid less than agreed, arbitrary fines deducted.",
        "severity_weight": 2,
        "examples": [
            "wages withheld",
            "paid less than agreed",
            "arbitrary fines applied",
            "wages given to third party",
            "unable to access own earnings",
        ],
    },
    "deception_regarding_work": {
        "label": "Deception Regarding Work",
        "description": "Job was materially different from what was described; false contract; misrepresented conditions.",
        "severity_weight": 2,
        "examples": [
            "job different from advertised",
            "working conditions misrepresented",
            "false contract presented",
            "nature of work was not disclosed",
        ],
    },
    "isolation": {
        "label": "Isolation",
        "description": "Contact with family or friends restricted; communications monitored; social isolation enforced.",
        "severity_weight": 2,
        "examples": [
            "contact with family restricted",
            "phone monitored or withheld",
            "not permitted to communicate freely",
            "kept away from community",
        ],
    },
    "dependency_control": {
        "label": "Dependency / Control",
        "description": "Housing, food, or basic needs controlled by employer as leverage.",
        "severity_weight": 2,
        "examples": [
            "housing controlled by employer",
            "food supply controlled",
            "basic needs dependent on employer compliance",
            "employer controls daily life",
        ],
    },
    "unsafe_accommodation": {
        "label": "Unsafe / Substandard Accommodation",
        "description": "Overcrowded, unsanitary, or employer-controlled premises used as accommodation.",
        "severity_weight": 1,
        "examples": [
            "overcrowded housing",
            "unsanitary living conditions",
            "sleeping at the worksite",
            "multiple workers in inadequate space",
        ],
    },
    "violence_threat_of_violence": {
        "label": "Violence / Threat of Violence",
        "description": "Physical harm reported or threatened; sexual violence reported or threatened.",
        "severity_weight": 4,  # highest weight — triggers URGENT regardless of count
        "examples": [
            "physical harm inflicted",
            "physical threats made",
            "sexual violence reported",
            "sexual coercion reported",
            "witnessed violence against others",
        ],
    },
    "inability_to_leave_employment": {
        "label": "Inability to Leave Employment",
        "description": "Cannot resign freely; threatened or penalised for attempting to leave.",
        "severity_weight": 3,
        "examples": [
            "cannot quit",
            "threatened for attempting to leave",
            "attempts to leave have been stopped",
            "told they must stay",
        ],
    },
    "exploitation_of_vulnerability": {
        "label": "Exploitation of Vulnerability",
        "description": "Employer or recruiter exploiting precarious immigration status, disability, or dependency.",
        "severity_weight": 2,
        "examples": [
            "immigration status used as leverage",
            "disability or health condition exploited",
            "desperate personal circumstances exploited",
            "limited language ability used to deceive",
        ],
    },
}


# ── Keyword matching for structured fields and narrative ─────────────────────

INDICATOR_KEYWORDS: dict[str, list[str]] = {
    "coercion_threats": [
        "threaten", "intimidat", "warn about deportation",
        "consequences if", "retaliat", "told they would be", "told i would be",
        "scared to leave", "afraid to leave", "frightened to leave",
    ],
    "restriction_of_movement": [
        "locked in", "locked up", "cannot leave", "can't leave", "not allowed to leave",
        "movement restricted", "confined", "curfew enforced",
        "not permitted to leave", "trapped", "no freedom to leave",
    ],
    "document_confiscation": [
        "passport retained", "passport taken", "passport held by",
        "identity document withheld", "id taken", "documents withheld",
        "documents kept by", "permit retained", "took my passport",
        "holding my documents", "won't return my documents",
        "passport confiscated",
    ],
    "debt_recruitment_pressure": [
        "recruitment fee", "debt bondage", "owe money to employer",
        "repay recruiter", "in debt to", "borrowed for job",
        "fee before departure", "advance that must be repaid",
        "debt used to prevent leaving",
    ],
    "wage_control_withholding": [
        "wages withheld", "not paid wages", "wages kept", "unpaid wages",
        "underpaid for agreed work", "no salary received",
        "deductions from wages", "fines taken from wages",
        "wages given to third party",
    ],
    "deception_regarding_work": [
        "different job than", "not what i was told", "misled about",
        "deceived about work", "false promise of", "different than advertised",
        "lied about the job", "false contract", "bait and switch",
    ],
    "isolation": [
        "cannot contact family", "phone taken", "not allowed to call",
        "isolated from", "no contact with family", "phone monitored",
        "communications monitored", "cannot speak freely",
    ],
    "dependency_control": [
        "employer controls housing", "boss controls", "controls my housing",
        "housing controlled by employer", "food controlled by",
        "dependent on employer for everything", "nowhere else to go",
    ],
    "unsafe_accommodation": [
        "overcrowded housing", "sleeping at work", "unsanitary conditions",
        "dirty accommodation", "unsafe housing", "sharing with many others",
        "no privacy in accommodation",
    ],
    "violence_threat_of_violence": [
        "hit by", "beaten by", "assault", "physically abused",
        "sexual violence", "sexually abused", "sexually assaulted",
        "physical threat", "threatened with violence",
        "threatened to harm", "will hurt",
    ],
    "inability_to_leave_employment": [
        "cannot quit", "can't quit", "not allowed to quit",
        "trapped in job", "forced to stay", "threatened if i leave",
        "must stay or", "no choice but to stay",
    ],
    "exploitation_of_vulnerability": [
        "immigration status used", "visa used as leverage", "status exploited",
        "exploiting disability", "took advantage of desperate",
        "manipulated because of", "exploiting their situation",
        "threatened with deportation",
    ],
}



# ── Protected characteristics — EXPLICITLY EXCLUDED from severity scoring ────
# This guard is documented here and enforced in indicator_analysis.py.
# If any of these fields are passed to severity calculation, an error is raised.

PROTECTED_CHARACTERISTICS = [
    "nationality",
    "ethnicity",
    "race",
    "religion",
    "gender",
    "sex",
    "sexual_orientation",
    "disability",
    "age_category",       # age as demographic, not operational context
    "immigration_status",  # can be DISPLAYED contextually but MUST NOT increase score
    "country_of_origin",
]

# NOTE ON IMMIGRATION_STATUS:
# Immigration precarity can be relevant operational context for a human reviewer
# (e.g., to understand referral pathways). However, immigration status alone —
# or demographic combinations that proxy for it — must not increase risk scoring.
# The system flags "exploitation_of_vulnerability" only when the narrative
# contains evidence that someone is ACTIVELY EXPLOITING the status,
# not merely when the status is present.


def validate_no_protected_characteristics(scoring_input: dict) -> None:
    """
    Guard function. Raises ValueError if protected characteristics are
    present in scoring input. Called before any indicator calculation.
    """
    violations = [k for k in scoring_input if k in PROTECTED_CHARACTERISTICS]
    if violations:
        raise ValueError(
            f"ARCHITECTURE VIOLATION: Protected characteristic(s) {violations} "
            f"were passed to indicator scoring. These must never affect risk calculation. "
            f"Remove them from the scoring input."
        )


def get_severity_from_hits(indicator_hits: list[dict]) -> str:
    """
    Deterministic severity calculation from indicator hits.
    Returns a categorical label — NO numeric score is produced.

    Logic:
    - Any violence/threat-of-violence hit → URGENT
    - Any restriction_of_movement + (coercion OR document_confiscation) → URGENT
    - 3+ hits with severity_weight >= 3 → HIGH
    - 2+ hits any categories → MODERATE
    - 1 hit → LOW
    - 0 hits → NONE
    """
    if not indicator_hits:
        return "NONE"

    categories_hit = set(h["category"] for h in indicator_hits)

    # Immediate URGENT triggers
    if "violence_threat_of_violence" in categories_hit:
        return "URGENT"

    if "restriction_of_movement" in categories_hit and (
        "coercion_threats" in categories_hit
        or "document_confiscation" in categories_hit
        or "inability_to_leave_employment" in categories_hit
    ):
        return "URGENT"

    # Count high-weight indicators
    high_weight_count = sum(
        1 for h in indicator_hits
        if INDICATOR_CATEGORIES.get(h["category"], {}).get("severity_weight", 0) >= 3
    )

    total_count = len(indicator_hits)

    if high_weight_count >= 3:
        return "HIGH"
    if total_count >= 2:
        return "MODERATE"
    if total_count >= 1:
        return "LOW"
    return "NONE"


def get_routing_from_severity(
    severity: str,
    validation_complete: bool,
    indicator_count: int,
) -> tuple[str, str]:
    """
    Maps severity + validation state to a routing recommendation.
    Returns (routing_state, rationale).
    """
    if not validation_complete:
        return (
            "NEED_INFO",
            "Required information is missing. Clarifying questions have been generated "
            "before a substantive assessment can proceed.",
        )

    if severity == "URGENT":
        return (
            "URGENT_REVIEW",
            "Immediate safety concern detected based on reported indicators. "
            "Urgent human safeguarding review is required. "
            "The system has not determined that trafficking has occurred.",
        )

    if severity == "HIGH":
        return (
            "PRIORITY_REVIEW",
            "Multiple serious indicators are present across several risk categories. "
            "Priority human review is required before any action.",
        )

    if severity in ("MODERATE", "LOW") and indicator_count >= 1:
        return (
            "READY_FOR_REVIEW",
            f"{indicator_count} indicator(s) identified. Human review is recommended. "
            "The system has not concluded that trafficking has occurred.",
        )

    if severity == "NONE" and indicator_count == 0:
        return (
            "NO_ACTION_RECOMMENDED",
            "No substantive trafficking indicators were identified in the reported information. "
            "This does not exclude the possibility of unreported concerns. "
            "Human reviewer should confirm and close or escalate as appropriate.",
        )

    # Fallback
    return (
        "READY_FOR_REVIEW",
        "Analysis complete. Human review recommended.",
    )
