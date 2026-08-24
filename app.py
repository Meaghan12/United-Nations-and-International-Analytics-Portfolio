"""
app.py
======
Human Trafficking Risk & Referral Decision-Support System
Streamlit entry point — API-enabled version

Deployment: Streamlit Community Cloud
Repository: Meaghan12/United-Nations-and-International-Analytics-Portfolio
Branch: main
Entry point: app.py (this file)

Architecture:
- LangGraph stateful workflow (workflow/graph.py)
- Two-phase execution: automated → human review → finalization
- OpenAI Responses API (services/llm_service.py + services/web_retrieval.py)
- Graceful demo mode when API key is absent
- All routing deterministic Python — LLM assists extraction/synthesis only
"""

import os
import json
import streamlit as st
from datetime import datetime

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Human Trafficking Risk & Referral Decision-Support System",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Internal imports ──────────────────────────────────────────────────────────
from utils.config import is_demo_mode, is_api_available, get_openai_model, get_max_web_searches
from workflow.graph import run_automated_phase, run_finalization_phase
from nodes.human_review import record_hitl_decision
from workflow.state import ROUTING_STATES
from utils.display_helpers import routing_badge, routing_badge_html
from utils.audit_log import public_audit_trail

# ── Load synthetic cases ──────────────────────────────────────────────────────
_CASES_PATH = os.path.join(os.path.dirname(__file__), "data", "synthetic_cases.json")
with open(_CASES_PATH) as _f:
    CASES: dict = json.load(_f)

_ANALYTICS_PATH = os.path.join(os.path.dirname(__file__), "data", "synthetic_analytics.json")
with open(_ANALYTICS_PATH) as _f:
    ANALYTICS: dict = json.load(_f)

# ── Session state initialisation ──────────────────────────────────────────────
def _init_session():
    defaults = {
        "phase": "intake",         # intake | analysis | review | final | analytics
        "case_state": None,
        "hitl_submitted": False,
        "web_session": None,
        "web_sources": [],
        "web_calls_used": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_session()

# ── Routing badge colours ─────────────────────────────────────────────────────
BADGE_COLOURS = {
    "URGENT_REVIEW":       ("#7f1d1d", "#fca5a5"),
    "PRIORITY_REVIEW":     ("#78350f", "#fcd34d"),
    "READY_FOR_REVIEW":    ("#1e3a5f", "#93c5fd"),
    "NEED_INFO":           ("#713f12", "#fef08a"),
    "OTHER_SUPPORT":       ("#4a1d96", "#c4b5fd"),
    "NO_ACTION_RECOMMENDED": ("#374151", "#d1d5db"),
    "HUMAN_OVERRIDE":      ("#14532d", "#86efac"),
    "REFERRED":            ("#14532d", "#86efac"),
}


def _routing_badge(state_key: str) -> str:
    meta = ROUTING_STATES.get(state_key, {})
    bg, fg = BADGE_COLOURS.get(state_key, ("#374151", "#d1d5db"))
    emoji = meta.get("emoji", "⚪")
    label = meta.get("label", state_key.replace("_", " "))
    return (
        f'<span style="background:{bg};color:{fg};padding:6px 14px;'
        f'border-radius:6px;font-weight:bold;font-size:0.95rem;">'
        f'{emoji} {label}</span>'
    )

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="background:#263b4d;padding:28px 32px;border-radius:12px;margin-bottom:8px">
  <h1 style="color:white;margin:0 0 6px 0">🔵 Human Trafficking Risk &amp; Referral Decision-Support System</h1>
  <p style="color:#c9d5df;margin:0 0 4px 0">Human-in-the-Loop &nbsp;·&nbsp; PII Protection &nbsp;·&nbsp; Explainable Risk Indicators &nbsp;·&nbsp; Safeguarding Escalation &nbsp;·&nbsp; Auditable Decisions</p>
  <p style="color:#7fc4ea;margin:0;font-size:0.9rem">Portfolio Prototype &nbsp;·&nbsp; Meaghan Ryan &nbsp;·&nbsp; Synthetic Demonstration Data Only &nbsp;·&nbsp; Not affiliated with any UN organization</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.error("⚠️ **SYNTHETIC DEMONSTRATION DATA ONLY**\n\nNo real individuals, cases, or organizations are represented.")

    # API / Demo mode indicator
    api_ok = is_api_available()
    if api_ok:
        st.success(f"✅ **API Mode Active**\nModel: `{get_openai_model()}`")
    else:
        st.info("🔵 **Demo Mode**\nNo API key configured.\nDeterministic analysis active.\nAll 8 cases fully functional.")

    st.markdown("---")

    # Case selector
    case_options = list(CASES.keys())
    selected_key = st.selectbox("📂 Load sample case:", case_options)
    case_data = CASES[selected_key]

    expected = case_data.get("expected_routing", "")
    if expected:
        meta = ROUTING_STATES.get(expected, {})
        st.caption(f"Expected route: {meta.get('emoji','⚪')} `{expected}`")

    st.markdown("---")

    # Jurisdiction field — reviewer-supplied only, never inferred from IP
    st.markdown("**📍 Jurisdiction / Location**")
    st.caption("Reviewer-supplied only. Never inferred from your IP address or VPN.")
    jurisdiction = st.text_input(
        "Jurisdiction",
        placeholder="e.g. Halifax, Nova Scotia, Canada",
        label_visibility="collapsed",
    )

    # Web grounding toggle
    st.markdown("**🌐 Authoritative Web Grounding**")
    web_enabled = st.toggle(
        "Enable web search for referral resources",
        value=bool(jurisdiction and api_ok),
        disabled=not jurisdiction,
        help="Requires jurisdiction to be entered. Uses up to 2 web search calls.",
    )

    # Web search counter
    calls_used = st.session_state.get("web_calls_used", 0)
    max_calls = get_max_web_searches()
    st.caption(f"Web grounding calls used: {calls_used} / {max_calls}")

    if not jurisdiction and web_enabled:
        st.warning("Enter a jurisdiction above to enable web grounding.")

    st.markdown("---")

    # Navigation
    st.markdown("**Navigate**")
    if st.button("🔄 Start New Case", use_container_width=True):
        for k in ["phase", "case_state", "hitl_submitted", "web_session", "web_sources", "web_calls_used"]:
            st.session_state[k] = {"phase": "intake"}.get(k, None) if k == "phase" else None if k != "web_calls_used" else 0
        st.session_state["phase"] = "intake"
        st.rerun()

    if st.button("📊 Analytics Dashboard", use_container_width=True):
        st.session_state["phase"] = "analytics"
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSIBLE AI PRINCIPLES
# ═══════════════════════════════════════════════════════════════════════════════

with st.expander("⚖️ Responsible AI Design Principles", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### This system is designed **NOT** to:")
        st.markdown("""
- Determine that trafficking has occurred
- Predict criminality or identify perpetrators
- Make autonomous safeguarding decisions
- Use demographic characteristics to inflate risk
- Bypass human review
- Generate a hidden numerical risk score
- Infer your location from IP address or VPN
""")
    with col_b:
        st.markdown("### This system **IS** designed to:")
        st.markdown("""
- Identify reported indicators transparently
- Route cases for human review
- Require reviewer confirmation before consequential action
- Mask PII before model-facing processing
- Maintain an auditable execution trace
- Say "insufficient information" rather than guess
- Retrieve authoritative resources with reviewer-supplied jurisdiction
- Enforce a maximum of two web search calls per case
""")

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state["phase"] == "analytics":
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd

    st.markdown("## 📊 Programme Analytics Dashboard")
    st.warning(
        "**SYNTHETIC DEMONSTRATION DATA ONLY.** "
        "These statistics are derived from 8 entirely fictional cases. "
        "They do not represent real case outcomes, real organizations, "
        "or real trafficking prevalence."
    )

    analytics = ANALYTICS

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Synthetic Cases", analytics.get("total_cases", 8))
    m2.metric("Avg Indicators per Case", analytics.get("avg_indicators", "—"))
    m3.metric("Cases Needing More Info", analytics.get("need_info_count", "—"))
    m4.metric("Human Override Rate", analytics.get("override_rate", "0%"))

    c1, c2 = st.columns(2)

    with c1:
        # Routing distribution
        routing_data = analytics.get("routing_distribution", {})
        if routing_data:
            labels = [ROUTING_STATES.get(k, {}).get("label", k) for k in routing_data]
            values = list(routing_data.values())
            colours = ["#C0392B","#E67E22","#2980B9","#F39C12","#8E44AD","#95A5A6","#27AE60","#27AE60"]
            fig = go.Figure(data=[go.Pie(
                labels=labels, values=values,
                hole=0.5, marker_colors=colours[:len(labels)],
            )])
            fig.update_layout(title="Case Routing Distribution", height=350, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Indicator frequency
        ind_data = analytics.get("indicator_frequency", {})
        if ind_data:
            df = pd.DataFrame(list(ind_data.items()), columns=["Category", "Frequency"])
            df = df.sort_values("Frequency", ascending=True)
            fig = px.bar(df, x="Frequency", y="Category", orientation="h",
                         title="Indicator Category Frequency",
                         color="Frequency", color_continuous_scale="Blues")
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        # Severity distribution
        sev_data = analytics.get("severity_distribution", {})
        if sev_data:
            sev_colours = {"URGENT":"#C0392B","HIGH":"#E67E22","MODERATE":"#2980B9","LOW":"#27AE60","NONE":"#95A5A6"}
            df_s = pd.DataFrame(list(sev_data.items()), columns=["Severity","Count"])
            fig = px.bar(df_s, x="Severity", y="Count",
                         title="Severity Distribution",
                         color="Severity", color_discrete_map=sev_colours)
            fig.update_layout(height=320, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        # Referral frequency
        ref_data = analytics.get("referral_frequency", {})
        if ref_data:
            df_r = pd.DataFrame(list(ref_data.items()), columns=["Referral","Count"])
            df_r = df_r.sort_values("Count", ascending=True)
            fig = px.bar(df_r, x="Count", y="Referral", orientation="h",
                         title="Referral Pathway Frequency",
                         color="Count", color_continuous_scale="Greens")
            fig.update_layout(height=320, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.info(
        "With validated, governed real-world data, similar analytics could potentially support: "
        "programme monitoring, resource planning, evaluation, quality assurance, "
        "operational decision support, and reporting."
    )
    st.caption("Analytics methodology: synthetic counts derived from the 8 demonstration scenarios only.")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# INTAKE PHASE
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state["phase"] == "intake":
    st.markdown("## Case Intake")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        case_id_input = st.text_input(
            "Case Reference ID",
            value=selected_key.split(":")[0].strip(),
        )
        narrative_input = st.text_area(
            "Full Case Narrative ★",
            value=case_data.get("narrative", ""),
            height=180,
            help="Describe the situation in as much detail as is known.",
        )

    with col_right:
        st.markdown("**Structured Indicator Fields**")
        st.caption("Complete as many fields as available.")
        intake_fields = case_data.get("intake_fields", {})

        doc_control = st.text_area(
            "Documentation control",
            value=intake_fields.get("documentation_control", ""),
            height=68,
            placeholder="Is the individual in possession of their own documents?",
        )
        movement = st.text_area(
            "Freedom of movement",
            value=intake_fields.get("freedom_of_movement", ""),
            height=68,
            placeholder="Can the individual come and go freely?",
        )
        wages = st.text_area(
            "Wage payment",
            value=intake_fields.get("wage_payment_concerns", ""),
            height=68,
            placeholder="Are wages paid as agreed?",
        )
        coercion = st.text_area(
            "Coercion / threats",
            value=intake_fields.get("coercion_or_threats", ""),
            height=68,
            placeholder="Any threats made?",
        )
        safety = st.text_area(
            "Immediate safety concern",
            value=intake_fields.get("immediate_safety_concern", ""),
            height=68,
            placeholder="Any immediate physical danger?",
        )

    if st.button("▶ Begin Analysis", use_container_width=True, type="primary"):
        # Build initial state
        built_fields = {
            "documentation_control":    doc_control,
            "freedom_of_movement":      movement,
            "wage_payment_concerns":    wages,
            "coercion_or_threats":      coercion,
            "immediate_safety_concern": safety,
        }
        # Add original intake fields as fallback
        for k, v in intake_fields.items():
            if k not in built_fields:
                built_fields[k] = v

        with st.spinner("Running automated analysis pipeline…"):
            initial_state = {
                "raw_case_id":           case_id_input or selected_key.split(":")[0].strip(),
                "raw_narrative":         narrative_input,
                "raw_intake_fields":     built_fields,
                "demo_mode":             not api_ok,
                "reviewer_jurisdiction": jurisdiction,
                "web_grounding_enabled": web_enabled and bool(jurisdiction),
                "web_search_calls_max":  get_max_web_searches(),
            }

            result_state = run_automated_phase(initial_state)

            # Web grounding (up to 2 calls) if enabled
            web_sources = []
            web_calls = 0
            if web_enabled and jurisdiction and jurisdiction.strip():
                from services.web_retrieval import get_grounded_resources
                detected_cats = [h["category"] for h in result_state.get("indicator_hits", [])]
                routing = result_state.get("routing_state", "READY_FOR_REVIEW")
                try:
                    web_session, web_sources = get_grounded_resources(
                        detected_cats, jurisdiction, routing
                    )
                    web_calls = web_session.calls_used
                except Exception:
                    web_sources = []
                    web_calls = 0

            result_state["web_sources"] = web_sources
            result_state["web_search_calls_used"] = web_calls
            st.session_state["web_calls_used"] = web_calls
            st.session_state["case_state"] = result_state
            st.session_state["phase"] = "analysis"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS PHASE
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state["phase"] == "analysis":
    state = st.session_state["case_state"]
    routing = state.get("routing_state", "UNKNOWN")
    severity = state.get("indicator_severity", "NONE")
    hits = state.get("indicator_hits", [])
    summary = state.get("evidence_summary", "")
    missing_info = state.get("missing_information", [])
    clarifying = state.get("clarifying_questions", [])
    referrals = state.get("referral_categories", [])
    rationale = state.get("routing_rationale", "")
    web_sources = state.get("web_sources", [])
    calls_used = state.get("web_search_calls_used", 0)
    api_used = state.get("api_mode", False)
    llm_used = state.get("llm_extraction_used", False)

    # ── Routing banner ────────────────────────────────────────────────────────
    if routing == "URGENT_REVIEW":
        st.error("🔴 **URGENT SAFEGUARDING REVIEW FLAGGED**\n\nHuman review is required before any action. This system has not determined that trafficking has occurred.")
    elif routing == "PRIORITY_REVIEW":
        st.warning("🟠 **PRIORITY REVIEW RECOMMENDED**\n\nMultiple indicators present. Human review required.")
    elif routing == "NEED_INFO":
        st.warning("🟡 **MORE INFORMATION REQUIRED**\n\nInsufficient information for full assessment. Clarifying questions generated.")
    elif routing == "NO_ACTION_RECOMMENDED":
        st.success("⚪ **NO TRAFFICKING INDICATORS IDENTIFIED**\n\nNo escalation indicators detected. Human reviewer should confirm and close or escalate if appropriate.")
    else:
        st.info(f"System recommendation: **{ROUTING_STATES.get(routing,{}).get('label', routing)}**")

    st.markdown(f"**Routing Rationale:** {rationale}", unsafe_allow_html=False)
    st.caption(f"Source: {'LLM-assisted' if llm_used else 'Deterministic'} | API mode: {'Active' if api_used else 'Demo'} | Severity: {severity}")

    st.markdown("---")

    # ── Workflow path ─────────────────────────────────────────────────────────
    with st.expander("🔄 Workflow Path", expanded=False):
        nodes = ["intake","pii_mask","safety_check","validate","indicator_analysis",
                 "evidence_review","referral_options","human_review","finalize","audit"]
        cols = st.columns(len(nodes))
        for i, (col, node) in enumerate(zip(cols, nodes)):
            col.markdown(f"<div style='text-align:center;font-size:0.72rem;padding:4px;background:#f0f4f8;border-radius:4px'>{node.replace('_','<br>')}</div>", unsafe_allow_html=True)

    # ── Indicators + Referrals ────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(f"### Observed Indicators ({len(hits)})")
        if hits:
            for hit in hits:
                source_label = hit.get("source","?").replace("_"," ").title()
                conf = hit.get("confidence","?")
                conf_color = {"REPORTED":"🔴","POSSIBLE":"🟠","INFERRED":"🟡"}.get(conf,"⚪")
                with st.expander(f"{conf_color} {hit.get('label', hit.get('category','?'))}", expanded=False):
                    st.markdown(f"**Category:** `{hit.get('category','?')}`")
                    st.markdown(f"**Confidence:** {conf}")
                    st.markdown(f"**Detection source:** {source_label}")
                    quote = hit.get("evidence_quote","")
                    if quote:
                        st.markdown(f"**Supporting text:** *\"{quote[:150]}\"*")
        else:
            st.success("No trafficking-related indicator categories identified from the submitted information.")

        if clarifying:
            st.markdown("### Missing Information")
            st.caption("The following questions would assist the human reviewer:")
            for q in clarifying:
                st.markdown(f"- {q}")

        if missing_info:
            st.markdown("### Information Gaps (AI-identified)")
            for gap in missing_info:
                st.markdown(f"- {gap}")

    with col_right:
        st.markdown("### Potential Referral Pathways")
        st.caption("Prototype categories only — not a real service directory.")
        if referrals:
            from services.referral_service import REFERRAL_CATEGORY_MAP
            for ref_key in referrals:
                meta = REFERRAL_CATEGORY_MAP.get(ref_key, {})
                label = meta.get("label", ref_key)
                desc = meta.get("description", "")
                with st.expander(label):
                    st.write(desc)
        else:
            st.info("No specific referral pathways indicated.")

    # ── AI Evidence Summary ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### AI-Generated Evidence Summary")
    st.caption("Hedged, neutral summary for the human reviewer. This is decision-support only.")
    st.info(summary if summary else "No summary generated.")

    # ── Web-Grounded Resources ────────────────────────────────────────────────
    jur = state.get("reviewer_jurisdiction", "")
    st.markdown("---")
    st.markdown(f"### 🌐 Source-Grounded Resources")
    st.caption(
        f"Web grounding calls used: **{calls_used} / {get_max_web_searches()}** "
        + (f"| Jurisdiction: {jur}" if jur else "| No jurisdiction entered")
    )

    if web_sources:
        for src in web_sources:
            with st.expander(f"📄 {getattr(src,'title',src.get('title','Resource') if isinstance(src,dict) else 'Resource')}"):
                url = getattr(src,'url',src.get('url','') if isinstance(src,dict) else '')
                relevance = getattr(src,'relevance',src.get('relevance','') if isinstance(src,dict) else '')
                src_jur = getattr(src,'jurisdiction',src.get('jurisdiction','') if isinstance(src,dict) else '')
                if url:
                    st.markdown(f"**URL:** [{url}]({url})")
                if relevance:
                    st.markdown(f"**Relevance:** {relevance}")
                if src_jur:
                    st.markdown(f"**Jurisdiction:** {src_jur}")
    elif not jur:
        st.caption("Enter a jurisdiction in the sidebar to retrieve authoritative referral resources.")
    elif not web_enabled:
        st.caption("Web grounding was disabled for this analysis.")
    else:
        st.caption("No authoritative resources could be confirmed for this search. The reviewer should consult known local service directories directly.")

    # ── Proceed to Human Review ───────────────────────────────────────────────
    st.markdown("---")
    if st.button("👤 Proceed to Human Review", use_container_width=True, type="primary"):
        st.session_state["phase"] = "review"
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# HUMAN REVIEW PHASE
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state["phase"] == "review":
    state = st.session_state["case_state"]
    routing = state.get("routing_state", "UNKNOWN")
    hits = state.get("indicator_hits", [])

    st.markdown("## 👤 Human Review")
    st.caption(
        "The system has not made a final determination. "
        "A human reviewer must confirm, edit, escalate, downgrade, or request more information."
    )

    # Show context
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**System Recommendation:** {ROUTING_STATES.get(routing,{}).get('label', routing)}")
        st.markdown(f"**Indicators Presented:** {len(hits)}")
        st.markdown(f"**Severity:** {state.get('indicator_severity','NONE')}")
    with col_b:
        jur = state.get("reviewer_jurisdiction","")
        st.markdown(f"**Jurisdiction:** {jur if jur else 'Not entered'}")
        st.markdown(f"**Evidence Summary:** {state.get('evidence_summary','')[:120]}…")

    st.markdown("---")

    decision = st.radio(
        "Reviewer Decision:",
        ["Approve", "Edit", "Escalate", "Downgrade", "Request More Information"],
        horizontal=True,
    )
    note = st.text_area(
        "Reviewer Note",
        placeholder="Add a note. Required for escalation or downgrade.",
        help="Notes are recorded in the audit trail.",
    )

    # Enforce note for escalation/downgrade
    requires_note = decision in ("Escalate", "Downgrade")
    if requires_note and not note.strip():
        st.warning(f"A reviewer note is required when selecting **{decision}**.")

    can_submit = not requires_note or bool(note.strip())

    if st.button("📋 Submit Reviewer Decision", use_container_width=True, type="primary", disabled=not can_submit):
        decision_map = {
            "Approve": "APPROVED",
            "Edit": "EDITED",
            "Escalate": "ESCALATED",
            "Downgrade": "DOWNGRADED",
            "Request More Information": "MORE_INFO",
        }
        updated = record_hitl_decision(
            state,
            decision_map[decision],
            reviewer_note=note,
        )

        with st.spinner("Finalising case…"):
            final = run_finalization_phase(updated)
            st.session_state["case_state"] = final
            st.session_state["phase"] = "final"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL OUTPUT PHASE
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state["phase"] == "final":
    state = st.session_state["case_state"]
    final_routing = state.get("final_routing_state", state.get("routing_state","?"))
    decision = state.get("hitl_decision","?")
    note = state.get("reviewer_note","")
    audit = state.get("audit_trail",[])

    st.markdown("## ✅ Case Review Complete")
    st.success(
        f"**Final Routing:** {ROUTING_STATES.get(final_routing,{}).get('label', final_routing)}\n\n"
        f"**Reviewer Decision:** {decision}\n\n"
        f"**Limitations:** This prototype output is for demonstration purposes only. "
        "It does not constitute a professional safeguarding determination."
    )

    if note:
        st.markdown(f"**Reviewer Note:** {note}")

    # ── Audit Trace ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Execution Trace (Audit Trail)")
    st.caption("Non-sensitive metadata only. Raw PII is never logged.")

    public_entries = public_audit_trail(audit)
    if public_entries:
        audit_lines = [
            f"{e.get('timestamp','?')} | {e.get('node','?'):<22} | {e.get('event','?')}"
            for e in public_entries
        ]
        st.code("\n".join(audit_lines), language=None)
    else:
        st.code("No audit entries recorded.", language=None)

    st.markdown("---")
    if st.button("🔄 Analyse Another Case", use_container_width=True):
        st.session_state["phase"] = "intake"
        st.session_state["case_state"] = None
        st.session_state["web_calls_used"] = 0
        st.rerun()
