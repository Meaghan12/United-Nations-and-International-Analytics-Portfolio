"""
indicators/rules.py
===================
Deterministic safety trigger rules for the safety_check node.

These rules run BEFORE any LLM call and are purely rule-based.
No model output influences these decisions.

A trigger fires when keyword patterns match the intake narrative or
structured fields. Firing immediately sets routing to URGENT_REVIEW.
"""
from __future__ import annotations

import re

# ── Immediate danger trigger patterns ─────────────────────────────────────────
# Each entry: (rule_label, list_of_keyword_patterns)
# Any match in masked_narrative or masked_fields triggers the rule.

IMMEDIATE_DANGER_RULES: list[tuple[str, list[str]]] = [
    (
        "Physical violence reported",
        [
            r"\b(hit|beaten|beat|assault|attacked|struck|physically abused)\b",
            r"\bphysical (harm|violence|abuse)\b",
        ],
    ),
    (
        "Sexual violence or coercion reported",
        [
            r"\b(raped|rape|sexual assault|sexually assault\w*|sexually abused|sexually coerced)\b",
            r"\bforced (to have sex|into sex|sexual)\b",
        ],
    ),
    (
        "Locked or physically confined",
        [
            r"\b(locked in|locked up|physically confined|cannot leave|can't leave)\b",
            r"\b(door locked|locked room|locked house|locked accommodation)\b",
        ],
    ),
    (
        "Explicit threat of serious harm",
        [
            r"\b(threatened to kill|will kill|death threat|kill me|hurt me|harm me)\b",
            r"\b(threatened with (weapon|knife|gun|violence))\b",
        ],
    ),
    (
        "Person reporting immediate danger",
        [
            r"\b(in danger now|currently in danger|help me now|emergency|unsafe right now)\b",
            r"\b(need help immediately|please help|I am scared)\b",
        ],
    ),
    (
        "Confirmed movement restriction with threats",
        [
            r"\b(not allowed to leave).{0,80}(threat|scared|afraid|force)\b",
            r"\b(threat).{0,80}(not allowed to leave|cannot leave|can't leave)\b",
        ],
    ),
]


def check_immediate_danger(text: str) -> tuple[bool, list[str]]:
    """
    Scans text for immediate danger indicators using deterministic rules.

    Args:
        text: Masked narrative or concatenated masked fields.

    Returns:
        (danger_detected: bool, triggered_rule_labels: list[str])
    """
    text_lower = text.lower()
    triggered = []

    for label, patterns in IMMEDIATE_DANGER_RULES:
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                triggered.append(label)
                break  # one match per rule is enough

    return bool(triggered), triggered
