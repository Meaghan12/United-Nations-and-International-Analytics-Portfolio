"""
nodes/safety_check.py
=====================
Node 3 — Safety Check

PERMITTED: Apply deterministic rule-set to detect immediate danger; set routing flags.
PROHIBITED: Use LLM; make referral decisions; contact external systems; act autonomously.

This node runs BEFORE the LLM and uses ONLY rule-based pattern matching.
Even if immediate danger is detected, NO autonomous action is taken —
the system routes to URGENT_REVIEW for mandatory human confirmation.
"""
from __future__ import annotations

from indicators.rules import check_immediate_danger
from utils.audit_log import append_audit


def safety_check_node(state: dict) -> dict:
    """
    Scans the masked narrative and fields for immediate danger indicators.
    Sets immediate_danger_detected and danger_triggers.
    Does NOT autonomously escalate — routes to URGENT_REVIEW for human review.
    """
    masked_narrative = state.get("masked_narrative", "")
    masked_fields = state.get("masked_fields", {})

    # Combine text sources for scanning (masked content only)
    scan_text = masked_narrative + " " + " ".join(
        str(v) for v in masked_fields.values() if isinstance(v, str)
    )

    danger_detected, triggers = check_immediate_danger(scan_text)

    if danger_detected:
        event = f"Immediate danger indicators detected — triggers: {'; '.join(triggers)}"
    else:
        event = "Safety check complete — no immediate danger indicators detected"

    audit = append_audit(state, "safety_check", event)

    return {
        **state,
        "immediate_danger_detected": danger_detected,
        "danger_triggers": triggers,
        "audit_trail": audit,
    }
