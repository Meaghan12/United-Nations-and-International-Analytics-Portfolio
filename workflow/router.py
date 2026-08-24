"""
workflow/router.py
==================
Deterministic routing logic for LangGraph conditional edges.

ALL routing decisions are made by Python code, not the LLM.
This ensures routing is fully auditable and explainable.
"""
from __future__ import annotations


def route_after_safety_check(state: dict) -> str:
    """
    After safety_check: if immediate danger detected → fast-path to referral_options
    (skipping validate and indicator_analysis in favour of speed, but still
    passing through human_review).

    In the current design we DO still run validate and indicator_analysis
    even for urgent cases, so the reviewer has full context.
    The URGENT flag is set and displayed prominently.
    """
    if state.get("immediate_danger_detected", False):
        # We still want full analysis — urgency is displayed prominently in UI
        return "validate"
    return "validate"


def route_after_validate(state: dict) -> str:
    """
    After validate: if incomplete → NEED_INFO terminal display (still hits human_review).
    If complete → proceed to indicator_analysis.
    """
    if state.get("validation_status") == "INCOMPLETE":
        return "need_info"
    return "indicator_analysis"


def route_after_human_review(state: dict) -> str:
    """
    After human_review: always proceed to finalize.
    The HITL gate cannot be bypassed — even in urgent cases.
    """
    return "finalize"
