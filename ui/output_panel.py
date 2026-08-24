"""
ui/output_panel.py
==================
Final decision support output panel.
"""
from __future__ import annotations

import streamlit as st
from utils.display_helpers import routing_badge, referral_label
from workflow.state import ROUTING_STATES
from referrals.categories import REFERRAL_CATEGORIES


def render_output_panel(state: dict):
    """Renders the finalised case output."""
    st.markdown("---")
    st.markdown("## ✅ Final Decision Support Output")

    final_routing = state.get("final_routing_state", "UNKNOWN")
    hitl_decision = state.get("hitl_decision", "UNKNOWN")
    reviewer_note = state.get("reviewer_note", "")
    final_referrals = state.get("final_referral_categories", [])
    session_id = state.get("session_id", "")
    timestamp_start = state.get("timestamp_start", "")
    timestamp_end = state.get("timestamp_end", "")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Status", ROUTING_STATES.get(final_routing, {}).get("label", final_routing))
    with col2:
        st.metric("Reviewer Decision", hitl_decision)
    with col3:
        st.metric("Session", session_id)

    st.markdown(routing_badge(final_routing), unsafe_allow_html=True)
    st.markdown("")

    if reviewer_note:
        st.markdown("**Reviewer Note:**")
        st.markdown(
            f"<blockquote style='border-left:4px solid #27AE60;padding:10px 16px;"
            f"background:#EAFAF1;border-radius:0 6px 6px 0;'>{reviewer_note}</blockquote>",
            unsafe_allow_html=True,
        )

    if final_referrals:
        st.markdown("**Confirmed Referral Pathways:**")
        for ref_key in final_referrals:
            label = referral_label(ref_key)
            desc = REFERRAL_CATEGORIES.get(ref_key, {}).get("description", "")
            st.markdown(f"• **{label}** — *{desc}*")

    st.warning(
        "**IMPORTANT LIMITATIONS:**\n\n"
        "This output is a decision-support record only. It does not constitute a legal determination, "
        "clinical assessment, or confirmation that trafficking has occurred. "
        "All referral categories are fictional prototypes. "
        "Actions should only be taken by qualified human practitioners following appropriate protocols. "
        "This system is not affiliated with or endorsed by any United Nations organization."
    )
