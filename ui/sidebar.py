"""
ui/sidebar.py
=============
Sidebar component — project identity, sample cases, responsible-AI notice.
"""
from __future__ import annotations

import json
import os

import streamlit as st


def render_sidebar() -> dict | None:
    """
    Renders the sidebar and returns the selected case dict if a sample case
    is chosen, or None if the user wants to enter a custom case.
    """
    with st.sidebar:
        st.markdown("## 🔵 Decision-Support System")
        st.markdown("**Human Trafficking Risk & Referral**")
        st.divider()

        # Prominent synthetic data warning
        st.error(
            "**⚠ SYNTHETIC DEMONSTRATION DATA ONLY**\n\n"
            "All cases in this system are entirely fictional. "
            "No real individuals, real cases, or real organizations "
            "are represented."
        )
        st.divider()

        st.markdown("### Sample Cases")
        st.caption(
            "Select a pre-built synthetic case to explore the system, "
            "or scroll down to enter a custom case."
        )

        # Load synthetic cases
        cases_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "synthetic_cases.json"
        )
        try:
            with open(cases_path) as f:
                cases = json.load(f)
        except FileNotFoundError:
            st.warning("Synthetic cases file not found.")
            return None

        case_options = {"— Enter a custom case —": None}
        for case_id, case_data in cases.items():
            label = f"{case_id}: {case_data['title']}"
            case_options[label] = case_data

        selected_label = st.selectbox(
            "Load sample case:",
            options=list(case_options.keys()),
            key="sidebar_case_select",
        )

        selected_case = case_options.get(selected_label)

        if selected_case:
            st.info(f"**Expected route:** `{selected_case.get('expected_routing', 'N/A')}`")
            st.caption(selected_case.get("description", ""))

        st.divider()
        st.markdown("### ⚖️ Responsible AI Notice")
        st.caption(
            "This system is a **portfolio prototype** only. It does not constitute "
            "a clinical, legal, or criminal assessment. It cannot determine that "
            "trafficking has occurred. All outputs require human review before any "
            "action. Demographic characteristics do not affect risk routing. "
            "This system is not affiliated with or endorsed by any United Nations "
            "organization."
        )

        st.divider()
        st.markdown("### ℹ️ About")
        st.caption(
            "Developed by **Meaghan Ryan** as a portfolio project exploring "
            "responsible AI architecture for humanitarian decision-support contexts."
        )

        return selected_case
