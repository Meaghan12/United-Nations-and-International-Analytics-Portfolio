"""
nodes/intake.py
===============
Node 1 — Intake

PERMITTED: Structure raw input; assign session ID; initialize audit trail.
PROHIBITED: Modify content; make assessments; call LLM.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from utils.audit_log import append_audit


def intake_node(state: dict) -> dict:
    """
    Initialises the case processing session.
    Assigns a session ID, records start time, and opens the audit trail.
    Raw input fields are carried forward untouched.
    """
    session_id = f"SESSION-{uuid.uuid4().hex[:8].upper()}"
    timestamp_start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    audit = append_audit({}, "intake", "Case received and session initialised")

    return {
        **state,
        "session_id": session_id,
        "timestamp_start": timestamp_start,
        "audit_trail": audit,
    }
