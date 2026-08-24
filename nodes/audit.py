"""
nodes/audit.py
==============
Node 10 — Audit

PERMITTED: Append immutable structured log entries; mask sensitive fields;
           record timestamps and session closure.
PROHIBITED: Expose PII; be writable after finalization; modify prior entries.
"""
from __future__ import annotations

from datetime import datetime, timezone

from utils.audit_log import append_audit


def audit_node(state: dict) -> dict:
    """
    Closes the case processing session and writes the final audit entry.
    The audit trail is now complete and should be treated as immutable.
    """
    timestamp_end = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    session_id = state.get("session_id", "UNKNOWN")
    final_routing = state.get("final_routing_state", "UNKNOWN")
    hitl_decision = state.get("hitl_decision", "UNKNOWN")

    event = (
        f"Session closed — session: {session_id} — "
        f"final status: {final_routing} — "
        f"reviewer decision: {hitl_decision}"
    )
    audit = append_audit(state, "audit", event)

    return {
        **state,
        "timestamp_end": timestamp_end,
        "audit_trail": audit,
    }
