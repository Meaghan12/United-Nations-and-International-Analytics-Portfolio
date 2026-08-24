"""
ui/human_review_panel.py
========================
Human-in-the-Loop review panel.

This is the HITL gate. The reviewer sees the full system recommendation
and has controls to approve, edit, escalate, downgrade, or request more info.
This panel CANNOT be bypassed — even in urgent cases.
"""
from __future__ import annotations

import streamlit as st
from utils.display_helpers import routing_badge
from workflow.state import ROUTING_STATES


def render_human_review_panel(state: dict) -> dict | None:
    """
    Renders the human review panel.

    Returns:
        dict with hitl_decision, reviewer_note, reviewer_edits
        or None if the reviewer has not yet submitted.
    """
    routing_state = state.get("routing_state", "READY_FOR_REVIEW")
    indicator_hits = state.get("indicator_hits", [])
    referral_categories = state.get("referral_categories", [])

    st.markdown("---")
    st.markdown("## 👤 Human Review")

    # Banner emphasizing HITL cannot be bypassed
    if routing_state == "URGENT_REVIEW":
        st.error(
            "🔴 **URGENT SAFEGUARDING REVIEW REQUIRED**\n\n"
            "This case has been flagged for urgent review. "
            "**A qualified human reviewer must confirm all actions. "
            "This system will not take any autonomous action.**"
        )
    else:
        st.info(
            "**Human review is required before this case can be finalised.** "
            "Review the system analysis above and use the controls below to record your decision. "
            "Your decision will be logged in the audit trail."
        )

    st.markdown(
        f"**System Recommendation:** {routing_badge(routing_state)}",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"**Indicators identified:** {len(indicator_hits)} | "
        f"**Referral pathways suggested:** {len(referral_categories)}"
    )

    st.markdown("---")

    with st.form("human_review_form"):
        st.markdown("#### Reviewer Decision")

        decision_options = {
            "APPROVED": "✅  Approve — Accept the system recommendation as presented",
            "EDITED": "✏️  Edit — Modify the recommendation before finalising",
            "ESCALATED": "🔴  Escalate — Elevate to URGENT SAFEGUARDING REVIEW",
            "DOWNGRADED": "⬇️  Downgrade — Lower priority to OTHER SUPPORT / NO ACTION",
            "MORE_INFO": "❓  Request More Information — Return to NEED_INFO status",
        }

        selected_decision = st.radio(
            "Select your decision:",
            options=list(decision_options.keys()),
            format_func=lambda k: decision_options[k],
            key="hitl_decision_radio",
        )

        st.markdown("---")

        # Show edit fields if EDITED is selected
        edited_routing = None
        edited_referrals = None

        if selected_decision == "EDITED":
            st.markdown("#### Edit Recommendation")
            routing_choices = list(ROUTING_STATES.keys())
            edited_routing = st.selectbox(
                "Change routing state to:",
                options=routing_choices,
                index=routing_choices.index(routing_state) if routing_state in routing_choices else 0,
                key="edited_routing",
            )

        reviewer_note = st.text_area(
            "Reviewer Note (required for Escalate, Downgrade, or Edit):",
            placeholder="Record your reasoning, observations, or any additional context...",
            height=100,
            key="reviewer_note",
        )

        # Validate: note required for non-standard decisions
        st.caption(
            "Your decision and note will be recorded in the immutable audit trail. "
            "This record cannot be altered after submission."
        )

        submitted = st.form_submit_button(
            "📋 Submit Reviewer Decision",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if selected_decision in ("ESCALATED", "DOWNGRADED", "EDITED") and not reviewer_note.strip():
                st.error("A reviewer note is required for Escalate, Downgrade, or Edit decisions.")
                return None

            edits = {}
            if edited_routing and edited_routing != routing_state:
                edits["routing_state"] = edited_routing
            if edited_referrals:
                edits["referral_categories"] = edited_referrals

            return {
                "hitl_decision": selected_decision,
                "reviewer_note": reviewer_note.strip(),
                "reviewer_edits": edits,
            }

    return None
