"""
nodes/finalize.py
=================
Node 9 — Finalize

PERMITTED: Compose final output from human-approved content; set final routing state.
PROHIBITED: Reverse human decisions; add conclusions not approved by reviewer;
            alter audit trail; call LLM.
"""
from __future__ import annotations

from workflow.state import ROUTING_STATES
from referrals.categories import REFERRAL_CATEGORIES
from utils.audit_log import append_audit


def finalize_node(state: dict) -> dict:
    """
    Composes the final decision-support output from human-reviewed content.
    The final routing state reflects the human reviewer's decision, not
    the system's original recommendation (if they differ).
    """
    hitl_decision = state.get("hitl_decision", "APPROVED")
    routing_state = state.get("routing_state", "READY_FOR_REVIEW")
    reviewer_edits = state.get("reviewer_edits", {})
    reviewer_note = state.get("reviewer_note", "")

    # Determine final routing state
    if hitl_decision in ("EDITED", "ESCALATED", "DOWNGRADED"):
        final_routing = routing_state  # already updated by human_review.record_hitl_decision
        is_override = True
    elif hitl_decision == "APPROVED":
        final_routing = routing_state
        is_override = False
    elif hitl_decision == "MORE_INFO":
        final_routing = "NEED_INFO"
        is_override = False
    else:
        final_routing = routing_state
        is_override = False

    # If reviewer changed routing, mark as HUMAN_OVERRIDE unless they approved urgent escalation
    if is_override and final_routing not in ("URGENT_REVIEW",):
        final_routing_display = "HUMAN_OVERRIDE"
    elif hitl_decision == "APPROVED" and routing_state in ("PRIORITY_REVIEW", "READY_FOR_REVIEW", "OTHER_SUPPORT"):
        final_routing_display = "REFERRED"
    else:
        final_routing_display = final_routing

    # Final referral categories: use reviewer edits if provided, else system recommendation
    if "referral_categories" in reviewer_edits:
        final_referrals = reviewer_edits["referral_categories"]
    else:
        final_referrals = state.get("referral_categories", [])

    # Compose final recommendation text
    routing_info = ROUTING_STATES.get(final_routing_display, ROUTING_STATES.get(final_routing, {}))
    routing_label = routing_info.get("label", final_routing_display)

    recommendation_parts = [
        f"Case Status: {routing_label}",
        "",
        f"Human Reviewer Decision: {hitl_decision}",
    ]
    if reviewer_note:
        recommendation_parts.append(f"Reviewer Note: {reviewer_note}")
    if final_referrals:
        referral_labels = [
            REFERRAL_CATEGORIES.get(r, {}).get("label", r) for r in final_referrals
        ]
        recommendation_parts.append(
            f"Recommended Pathways: {'; '.join(referral_labels)}"
        )
    recommendation_parts += [
        "",
        "IMPORTANT: This output is a decision-support record. It does not constitute "
        "a legal determination, clinical assessment, or confirmation that trafficking "
        "has occurred. All actions require qualified human judgment.",
    ]

    final_recommendation = "\n".join(recommendation_parts)

    event = f"Case finalised — final status: {final_routing_display} — reviewer decision: {hitl_decision}"
    audit = append_audit(state, "finalize", event)

    return {
        **state,
        "final_routing_state": final_routing_display,
        "final_recommendation": final_recommendation,
        "final_referral_categories": final_referrals,
        "audit_trail": audit,
    }
