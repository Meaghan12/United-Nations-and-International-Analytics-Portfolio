"""
ui/analysis_panel.py
====================
Analysis results panel — indicators, evidence summary, routing recommendation.
"""
from __future__ import annotations

import streamlit as st
from utils.display_helpers import routing_badge, severity_badge, indicator_category_label, referral_label
from workflow.state import ROUTING_STATES
from referrals.categories import REFERRAL_CATEGORIES
from indicators.framework import INDICATOR_CATEGORIES


def render_analysis_panel(state: dict):
    """
    Renders the full analysis results panel after automated processing.
    """
    routing_state = state.get("routing_state", "READY_FOR_REVIEW")
    indicator_hits = state.get("indicator_hits", [])
    indicator_categories = state.get("indicator_categories", {})
    severity = state.get("indicator_severity", "NONE")
    routing_rationale = state.get("routing_rationale", "")
    evidence_summary = state.get("evidence_summary", "")
    referral_categories = state.get("referral_categories", [])
    referral_rationale = state.get("referral_rationale", {})
    missing_fields = state.get("missing_fields", [])
    clarifying_questions = state.get("clarifying_questions", [])
    pii_redacted_items = state.get("pii_redacted_items", [])
    immediate_danger = state.get("immediate_danger_detected", False)
    danger_triggers = state.get("danger_triggers", [])

    # ── Routing recommendation header ────────────────────────────────────────
    st.markdown("---")

    if immediate_danger:
        st.error(
            "🔴 **URGENT SAFEGUARDING REVIEW FLAGGED**\n\n"
            f"Immediate danger triggers detected: {'; '.join(danger_triggers)}\n\n"
            "**Human review is required before any action is taken. "
            "This system has not determined that trafficking has occurred.**"
        )
    elif routing_state == "NEED_INFO":
        st.warning(
            "🟡 **INFORMATION REQUIRED**\n\n"
            "Insufficient information to proceed with full analysis. "
            "Clarifying questions have been generated for the reviewer."
        )

    st.markdown("#### System Recommendation")
    st.markdown(routing_badge(routing_state), unsafe_allow_html=True)
    st.markdown("")
    st.info(routing_rationale)

    st.caption(
        "**This is a decision-support recommendation only.** "
        "It does not constitute a legal determination, clinical assessment, "
        "or confirmation that trafficking has occurred. "
        "Human review is required before any action."
    )

    st.markdown("---")

    # ── Two-column layout: indicators + missing info ──────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown(f"#### Observed Indicators ({len(indicator_hits)})")

        if pii_redacted_items:
            st.success(
                f"🔒 **PII masking applied** — types detected and redacted: "
                f"{', '.join(pii_redacted_items)}"
            )

        if not indicator_hits:
            st.markdown(
                "*No substantive indicators identified in the information provided.*"
            )
        else:
            # Group by category
            cats_hit = {}
            for hit in indicator_hits:
                cats_hit.setdefault(hit["category"], []).append(hit)

            for cat_key, hits in cats_hit.items():
                cat_label = indicator_category_label(cat_key)
                cat_desc = INDICATOR_CATEGORIES.get(cat_key, {}).get("description", "")
                with st.expander(f"**{cat_label}**", expanded=True):
                    for hit in hits:
                        conf_colors = {
                            "REPORTED": "🔴",
                            "POSSIBLE": "🟠",
                            "INFERRED": "🟡",
                        }
                        conf_icon = conf_colors.get(hit["confidence"], "⚪")
                        source_label = hit["source"].replace("_", " ").title()
                        st.markdown(
                            f"{conf_icon} **{hit['label']}**  \n"
                            f"<span style='font-size:0.8rem;color:#7F8C8D;'>"
                            f"Confidence: {hit['confidence']} · Source: {source_label}</span>",
                            unsafe_allow_html=True,
                        )
                    st.caption(cat_desc)

        # Severity
        st.markdown("**Severity Assessment**")
        st.markdown(severity_badge(severity), unsafe_allow_html=True)
        st.caption(
            "Severity is a categorical label only — no numerical score is generated. "
            "Severity does not constitute a trafficking determination."
        )

    with col_right:
        st.markdown("#### Information Still Missing")
        if not clarifying_questions and not missing_fields:
            st.success("All required fields were provided.")
        else:
            if missing_fields:
                st.error(f"**Required fields missing:** {', '.join(missing_fields)}")
            if clarifying_questions:
                st.markdown(
                    "*The following questions would strengthen the assessment:*"
                )
                for q in clarifying_questions:
                    st.markdown(f"• {q}")

        st.markdown("---")
        st.markdown("#### Potential Referral Pathways")
        st.caption(
            "These are **fictional prototype referral categories**. "
            "They do not represent real services."
        )
        if not referral_categories:
            st.markdown("*No specific referral pathways identified.*")
        else:
            for ref_key in referral_categories:
                ref_label = referral_label(ref_key)
                rationale = referral_rationale.get(ref_key, "")
                ref_desc = REFERRAL_CATEGORIES.get(ref_key, {}).get("description", "")
                with st.expander(f"**{ref_label}**"):
                    st.markdown(rationale)
                    st.caption(ref_desc)

    st.markdown("---")

    # ── Evidence summary ──────────────────────────────────────────────────────
    st.markdown("#### AI-Generated Evidence Summary")
    st.caption(
        "Generated by a language model with strictly constrained instructions. "
        "Uses hedged, qualified language only. "
        "Does not constitute a determination of trafficking or any legal conclusion. "
        "Human review is required before any action."
    )
    if evidence_summary:
        st.markdown(
            f"<div style='background:#F8F9FA;border-left:4px solid #2980B9;"
            f"padding:16px 20px;border-radius:0 8px 8px 0;line-height:1.7;'>"
            f"{evidence_summary}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("*Evidence summary not available.*")
