"""
nodes/human_review.py
=====================
Node 8 — Human Review (HITL Gate)

PERMITTED: Present system output to reviewer; accept reviewer input;
           record override decisions in audit trail.
PROHIBITED: Be skipped; auto-approve; alter audit trail; reverse human decisions.

This node does not process logic — it is a PAUSE POINT.
In the Streamlit architecture, this node stores the pre-review state
and signals to the UI that human input is required.
The UI then presents the review panel and collects the reviewer's decision,
which is written back to state via st.session_state before finalize runs.

This node CANNOT be bypassed even in URGENT_REVIEW mode.
Urgency changes how prominently the UI presents information — not whether
human review occurs.
"""
from __future__ import annotations

from utils.audit_log import append_audit


def human_review_node(state: dict) -> dict:
    """
    Marks the case as awaiting human review.
    The actual reviewer interaction happens in the Streamlit UI layer.
    This node signals the pause and records the entry to the audit trail.
    """
    routing_state = state.get("routing_state", "READY_FOR_REVIEW")
    indicator_count = len(state.get("indicator_hits", []))

    event = (
        f"Case submitted for human review — "
        f"system recommendation: {routing_state} — "
        f"{indicator_count} indicator(s) presented to reviewer"
    )
    audit = append_audit(state, "human_review", event)

    return {
        **state,
        "hitl_complete": False,  # UI sets this to True after reviewer submits
        "audit_trail": audit,
    }


def record_hitl_decision(state: dict, decision: str, note: str = "", reviewer_note: str = "", edits: dict = None) -> dict:
    """
    Called by the Streamlit UI after the reviewer submits their decision.
    Records the human decision and override details to the audit trail.

    Args:
        state: Current case state
        decision: One of APPROVED | EDITED | ESCALATED | DOWNGRADED | MORE_INFO
        note: Free-text reviewer note
        edits: Dict of any fields the reviewer changed
    """
    # Accept both `note` and `reviewer_note` (alias) for backward compatibility
    effective_note = reviewer_note or note or ""
    if edits is None:
        edits = {}

    event = f"Human reviewer decision: {decision}"
    if effective_note:
        event += f" — note recorded"
    if edits:
        event += f" — {len(edits)} field(s) overridden"

    audit = append_audit(state, "human_review", event)

    # Determine if this is a human override (reviewer changed the recommendation)
    is_override = decision in ("EDITED", "ESCALATED", "DOWNGRADED")

    return {
        **state,
        "hitl_decision": decision,
        "reviewer_note": effective_note,
        "reviewer_edits": edits,
        "hitl_complete": True,
        "audit_trail": audit,
        # If the reviewer escalated or downgraded, routing_state changes
        "routing_state": _apply_reviewer_routing(state.get("routing_state", ""), decision, edits),
    }


def _apply_reviewer_routing(current_routing: str, decision: str, edits: dict) -> str:
    """
    Applies reviewer routing changes. Called only for ESCALATED/DOWNGRADED decisions.
    APPROVED and MORE_INFO retain the current routing.
    EDITED uses whatever the reviewer specified in edits.
    """
    if decision == "ESCALATED":
        return "URGENT_REVIEW"
    if decision == "DOWNGRADED":
        return "OTHER_SUPPORT"
    if decision == "EDITED" and "routing_state" in edits:
        return edits["routing_state"]
    return current_routing
