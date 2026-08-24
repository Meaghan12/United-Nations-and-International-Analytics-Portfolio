"""
nodes/referral_options.py
=========================
Node 7 — Referral Options

PERMITTED: Map indicator categories to fictional referral types using logic table.
PROHIBITED: Select referrals based on demographics; contact real agencies;
            make autonomous referrals; bypass human review.

All referral options are presented to the human reviewer — they are
RECOMMENDATIONS only, not actions.
"""
from __future__ import annotations

from referrals.categories import get_referrals_for_indicators, REFERRAL_CATEGORIES
from indicators.framework import get_routing_from_severity
from utils.audit_log import append_audit


def referral_options_node(state: dict) -> dict:
    """
    Maps detected indicators to relevant referral categories.
    Applies routing logic to determine the recommended routing state.
    """
    indicator_categories = state.get("indicator_categories", {})
    indicator_hits = state.get("indicator_hits", [])
    severity = state.get("indicator_severity", "NONE")
    validation_status = state.get("validation_status", "COMPLETE")
    immediate_danger = state.get("immediate_danger_detected", False)
    danger_triggers = state.get("danger_triggers", [])

    # Override severity to URGENT if safety_check fired
    effective_severity = "URGENT" if immediate_danger else severity

    # Determine referral options
    referral_map = get_referrals_for_indicators(indicator_categories)

    # Convert to list of keys + rationale dict
    referral_keys = list(referral_map.keys())
    referral_rationale = referral_map

    # Determine routing state
    validation_complete = (validation_status == "COMPLETE")
    indicator_count = len(indicator_hits)

    # Check for labour-only indicators (OTHER_SUPPORT case)
    high_weight_cats = {
        "coercion_threats", "restriction_of_movement", "document_confiscation",
        "violence_threat_of_violence", "inability_to_leave_employment"
    }
    detected_cats = set(k for k, v in indicator_categories.items() if v > 0)
    has_serious_indicators = bool(detected_cats & high_weight_cats)
    labour_only_cats = {
        "wage_control_withholding", "deception_regarding_work",
        "unsafe_accommodation", "debt_recruitment_pressure"
    }
    is_labour_only = (
        indicator_count > 0
        and not has_serious_indicators
        and bool(detected_cats & labour_only_cats)
        and effective_severity in ("LOW", "NONE")
    )

    if immediate_danger:
        routing_state = "URGENT_REVIEW"
        routing_rationale = (
            "Immediate safety concern identified by deterministic rule check. "
            f"Triggers: {'; '.join(danger_triggers)}. "
            "Urgent human safeguarding review is required. "
            "This system has not determined that trafficking has occurred."
        )
    elif is_labour_only:
        routing_state = "OTHER_SUPPORT"
        routing_rationale = (
            "Labour and employment concerns are present. "
            "However, indicators of coercion, physical confinement, "
            "or document confiscation are not reported at this time. "
            "Human review is recommended. Trafficking indicators insufficient "
            "for higher-priority routing. Labour rights support may be appropriate."
        )
    elif indicator_count == 0 and state.get("clarifying_questions"):
        # No indicators found, but there are unanswered clarifying questions —
        # insufficient information to rule out concerns; request more details
        routing_state = "NEED_INFO"
        routing_rationale = (
            "No substantive indicators were identified from the information provided. "
            "However, key contextual questions remain unanswered. "
            "The absence of detected indicators does not confirm the absence of concern. "
            "A human reviewer should consider whether to gather additional information "
            "before closing this case."
        )
    else:
        routing_state, routing_rationale = get_routing_from_severity(
            effective_severity, validation_complete, indicator_count
        )

    event = (
        f"Referral options identified: {len(referral_keys)} pathway(s) — "
        f"routing recommendation: {routing_state}"
    )
    audit = append_audit(state, "referral_options", event)

    return {
        **state,
        "referral_categories": referral_keys,
        "referral_rationale": referral_rationale,
        "routing_state": routing_state,
        "routing_rationale": routing_rationale,
        "audit_trail": audit,
    }
