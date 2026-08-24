"""
ui/audit_panel.py
=================
Execution trace / audit trail display.
"""
from __future__ import annotations

import streamlit as st
from utils.audit_log import public_audit_trail


def render_audit_panel(state: dict):
    """Renders the public-facing execution trace."""
    st.markdown("---")
    st.markdown("#### Execution Trace (Audit Trail)")
    st.caption(
        "This trace shows the sequence of processing steps. "
        "Sensitive entries are excluded from this display. "
        "A full internal audit record is retained in the session state."
    )

    audit_trail = state.get("audit_trail", [])
    public_entries = public_audit_trail(audit_trail)

    if not public_entries:
        st.markdown("*No audit entries available yet.*")
        return

    trace_lines = []
    for entry in public_entries:
        ts = entry.get("timestamp", "--:--:--")
        node = entry.get("node", "unknown").ljust(20)
        event = entry.get("event", "")
        trace_lines.append(f"{ts}  |  {node}  |  {event}")

    st.code("\n".join(trace_lines), language=None)
