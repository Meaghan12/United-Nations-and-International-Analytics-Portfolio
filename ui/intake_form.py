"""
ui/intake_form.py
=================
Case intake form — structured fields plus free-text narrative.
"""
from __future__ import annotations

import streamlit as st


def render_intake_form(prefill: dict | None = None) -> dict | None:
    """
    Renders the case intake form.
    If prefill is provided (from a synthetic case), fields are pre-populated.

    Returns:
        dict with raw_case_id, raw_narrative, raw_intake_fields
        or None if the form has not been submitted yet.
    """
    prefill_fields = prefill.get("intake_fields", {}) if prefill else {}
    prefill_narrative = prefill.get("narrative", "") if prefill else ""
    prefill_case_id = prefill.get("case_id", "") if prefill else ""

    st.markdown("#### Case Intake")
    st.caption(
        "Complete the fields below to begin analysis. "
        "Fields marked ★ are required to proceed to indicator analysis. "
        "All data processed by this demonstration uses **synthetic fictional cases only**."
    )

    with st.form("intake_form", clear_on_submit=False):
        col1, col2 = st.columns([1, 2])

        with col1:
            case_id = st.text_input(
                "Case Reference ID",
                value=prefill_case_id,
                placeholder="e.g. CASE-001",
                help="A reference identifier for this case record.",
            )

        with col2:
            employment_context = st.text_input(
                "Employment / Situational Context",
                value=prefill_fields.get("employment_context", ""),
                placeholder="Nature of work, recruitment channel, duration...",
            )

        reported_concerns = st.text_area(
            "Reported Concerns ★",
            value=prefill_fields.get("reported_concerns", ""),
            placeholder="Summarise the concerns reported by or on behalf of the individual...",
            height=80,
        )

        st.markdown("---")
        st.markdown("**Structured Indicator Fields**")
        st.caption("These fields directly inform indicator analysis. Provide as much detail as is known.")

        col_a, col_b = st.columns(2)

        with col_a:
            documentation_control = st.text_area(
                "Documentation Control",
                value=prefill_fields.get("documentation_control", ""),
                placeholder="Are personal documents in the individual's possession, or held by another party?",
                height=80,
            )
            freedom_of_movement = st.text_area(
                "Freedom of Movement",
                value=prefill_fields.get("freedom_of_movement", ""),
                placeholder="Is the individual free to come and go? Are there restrictions?",
                height=80,
            )
            wage_payment_concerns = st.text_area(
                "Wage / Payment Concerns",
                value=prefill_fields.get("wage_payment_concerns", ""),
                placeholder="Are wages paid as agreed? Any withholding, deductions, or irregularities?",
                height=80,
            )

        with col_b:
            coercion_or_threats = st.text_area(
                "Coercion or Threats",
                value=prefill_fields.get("coercion_or_threats", ""),
                placeholder="Have any threats been made to the individual or their family?",
                height=80,
            )
            recruitment_debt = st.text_area(
                "Recruitment / Placement Debt",
                value=prefill_fields.get("recruitment_debt", ""),
                placeholder="Were recruitment fees paid? Is debt being used as leverage?",
                height=80,
            )
            immediate_safety_concern = st.text_area(
                "Immediate Safety Concern",
                value=prefill_fields.get("immediate_safety_concern", ""),
                placeholder="Is there an immediate safety concern? Physical threats? Locked accommodation?",
                height=80,
            )

        st.markdown("---")
        narrative = st.text_area(
            "Full Case Narrative ★",
            value=prefill_narrative,
            placeholder=(
                "Provide the full narrative as reported by or on behalf of the individual. "
                "Do not include information that has not been reported."
            ),
            height=200,
        )

        st.caption(
            "⚠️ **Important:** Do not enter real personal information into this demonstration system. "
            "This system uses synthetic fictional data only. PII masking will be applied to the narrative "
            "before any further processing."
        )

        submitted = st.form_submit_button(
            "▶ Begin Analysis",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not reported_concerns.strip() and not narrative.strip():
                st.error("Please enter at least Reported Concerns or a Case Narrative to proceed.")
                return None

            return {
                "raw_case_id": case_id.strip() or "CASE-CUSTOM",
                "raw_narrative": narrative.strip(),
                "raw_intake_fields": {
                    "employment_context": employment_context.strip(),
                    "reported_concerns": reported_concerns.strip(),
                    "documentation_control": documentation_control.strip(),
                    "freedom_of_movement": freedom_of_movement.strip(),
                    "wage_payment_concerns": wage_payment_concerns.strip(),
                    "coercion_or_threats": coercion_or_threats.strip(),
                    "recruitment_debt": recruitment_debt.strip(),
                    "immediate_safety_concern": immediate_safety_concern.strip(),
                },
                "demo_mode": st.session_state.get("demo_mode", True),
            }

    return None
