"""
utils/audit_log.py
==================
Append-only audit trail management.

The audit trail provides an immutable record of every processing step.
Sensitive fields are flagged and excluded from the public-facing display.
The full audit trail is retained in state for authorized internal review.
"""
from __future__ import annotations

from datetime import datetime, timezone


def make_audit_entry(
    node: str,
    event: str,
    sensitive: bool = False,
) -> dict:
    """
    Create a single audit trail entry.

    Args:
        node: The node name (e.g. "intake", "pii_mask")
        event: Plain-language description of what occurred
        sensitive: If True, this entry is excluded from the UI display trace.
                   Used when the event description might reference sensitive content.

    Returns:
        AuditEntry dict
    """
    return {
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "node": node,
        "event": event,
        "sensitive": sensitive,
    }


def append_audit(state: dict, node: str, event: str, sensitive: bool = False) -> list:
    """
    Return a new audit trail list with the new entry appended.

    NOTE: We return a new list rather than mutating in place
    to respect LangGraph's state immutability expectations.
    """
    existing = state.get("audit_trail", [])
    new_entry = make_audit_entry(node, event, sensitive)
    return existing + [new_entry]


def public_audit_trail(audit_trail: list) -> list:
    """
    Filter the audit trail for public/UI display.
    Removes entries marked sensitive=True.
    """
    return [entry for entry in audit_trail if not entry.get("sensitive", False)]
