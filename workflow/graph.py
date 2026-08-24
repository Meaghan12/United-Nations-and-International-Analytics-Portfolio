"""
workflow/graph.py
=================
LangGraph StateGraph assembly for the HT Decision-Support System.

The graph runs all automated nodes (intake → pii_mask → safety_check →
validate → indicator_analysis → evidence_review → referral_options →
human_review) in sequence, then pauses.

In the Streamlit integration, human_review sets hitl_complete=False and
the UI collects reviewer input via st.session_state. Once the reviewer
submits, finalize → audit run to close the case.

For the Streamlit session-state pattern, we split the workflow into
two callable phases:
  - run_automated_phase(state): intake through human_review
  - run_finalization_phase(state): finalize + audit
"""
from __future__ import annotations

from langgraph.graph import StateGraph, END

from workflow.state import CaseState
from workflow.router import route_after_validate
from nodes.intake import intake_node
from nodes.pii_mask import pii_mask_node
from nodes.safety_check import safety_check_node
from nodes.validate import validate_node
from nodes.indicator_analysis import indicator_analysis_node
from nodes.evidence_review import evidence_review_node
from nodes.referral_options import referral_options_node
from nodes.human_review import human_review_node
from nodes.finalize import finalize_node
from nodes.audit import audit_node


def build_automated_graph():
    """
    Builds and compiles the automated phase graph (intake → human_review).
    This runs without user interaction and produces the pre-review state.
    """
    graph = StateGraph(dict)  # using dict for flexibility with TypedDict subtype

    # Add nodes
    graph.add_node("intake", intake_node)
    graph.add_node("pii_mask", pii_mask_node)
    graph.add_node("safety_check", safety_check_node)
    graph.add_node("validate", validate_node)
    graph.add_node("need_info", _need_info_passthrough)
    graph.add_node("indicator_analysis", indicator_analysis_node)
    graph.add_node("evidence_review", evidence_review_node)
    graph.add_node("referral_options", referral_options_node)
    graph.add_node("human_review", human_review_node)

    # Set entry point
    graph.set_entry_point("intake")

    # Linear edges (no branching needed here — routing state is set in state dict)
    graph.add_edge("intake", "pii_mask")
    graph.add_edge("pii_mask", "safety_check")
    graph.add_edge("safety_check", "validate")

    # Branch after validate: INCOMPLETE → need_info, COMPLETE → indicator_analysis
    graph.add_conditional_edges(
        "validate",
        route_after_validate,
        {
            "need_info": "need_info",
            "indicator_analysis": "indicator_analysis",
        },
    )

    graph.add_edge("need_info", "human_review")
    graph.add_edge("indicator_analysis", "evidence_review")
    graph.add_edge("evidence_review", "referral_options")
    graph.add_edge("referral_options", "human_review")
    graph.add_edge("human_review", END)

    return graph.compile()


def build_finalization_graph():
    """
    Builds and compiles the finalization phase graph (finalize → audit).
    Runs after the human reviewer submits their decision.
    """
    graph = StateGraph(dict)

    graph.add_node("finalize", finalize_node)
    graph.add_node("audit", audit_node)

    graph.set_entry_point("finalize")
    graph.add_edge("finalize", "audit")
    graph.add_edge("audit", END)

    return graph.compile()


def _need_info_passthrough(state: dict) -> dict:
    """
    Passthrough node for NEED_INFO cases.
    Sets routing_state to NEED_INFO and routes to human_review.
    Human reviewer can add a note or request specific information.
    """
    from utils.audit_log import append_audit

    missing = state.get("missing_fields", [])
    clarifying = state.get("clarifying_questions", [])
    event = (
        f"Routed to NEED_INFO — "
        f"{len(missing)} required field(s) missing — "
        f"{len(clarifying)} clarifying question(s) generated"
    )
    audit = append_audit(state, "routing", event)

    return {
        **state,
        "routing_state": "NEED_INFO",
        "routing_rationale": (
            "Insufficient information was provided to proceed with indicator analysis. "
            f"{len(clarifying)} clarifying question(s) have been generated. "
            "A human reviewer should review and determine how to proceed."
        ),
        "indicator_hits": state.get("indicator_hits", []),
        "indicator_categories": state.get("indicator_categories", {}),
        "indicator_severity": state.get("indicator_severity", "NONE"),
        "evidence_summary": (
            "Insufficient information was provided for an evidence summary. "
            "Please review the clarifying questions and gather additional information."
        ),
        "referral_categories": state.get("referral_categories", ["case_management_follow_up"]),
        "referral_rationale": state.get("referral_rationale", {}),
        "audit_trail": audit,
    }


# ── Convenience functions for Streamlit integration ──────────────────────────

_automated_graph = None
_finalization_graph = None


def get_automated_graph():
    global _automated_graph
    if _automated_graph is None:
        _automated_graph = build_automated_graph()
    return _automated_graph


def get_finalization_graph():
    global _finalization_graph
    if _finalization_graph is None:
        _finalization_graph = build_finalization_graph()
    return _finalization_graph


def run_automated_phase(initial_state: dict) -> dict:
    """Run the automated analysis phase and return the pre-review state."""
    graph = get_automated_graph()
    result = graph.invoke(initial_state)
    return result


def run_finalization_phase(state: dict) -> dict:
    """Run the finalization phase after human review is complete."""
    graph = get_finalization_graph()
    result = graph.invoke(state)
    return result
