"""
nodes/evidence_review.py
=========================
Generates a hedged, neutral evidence summary for the human reviewer.

Uses services/llm_service.py with structured JSON schema output.
In demo mode, generates a safe deterministic summary.

The LLM may assist with synthesis — it does NOT make the routing decision.
Post-generation prohibited-term check as belt-and-suspenders.
"""
from __future__ import annotations

from utils.audit_log import append_audit
from utils.config import is_demo_mode


def evidence_review_node(state: dict) -> dict:
    """
    LangGraph node: Evidence Review

    Reads:  masked_narrative, indicator_hits, routing_state, demo_mode
    Writes: evidence_summary, missing_information, llm_model_version, api_mode
    """
    masked_narrative = state.get("masked_narrative", "")
    indicator_hits   = state.get("indicator_hits", [])
    routing_state    = state.get("routing_state", "UNKNOWN")
    demo             = state.get("demo_mode", False) or is_demo_mode()

    api_mode = not demo
    model_version = "demo-mode"
    missing_info: list[str] = []

    if demo:
        n = len(indicator_hits)
        case_id = state.get("raw_case_id", "")
        # Try to get pre-computed demo summary
        summary = None
        try:
            import json, os
            demo_path = os.path.join(
                os.path.dirname(__file__), "..", "data", "demo_llm_responses.json"
            )
            with open(demo_path) as f:
                demo_data = json.load(f)
            summary = demo_data.get(case_id, {}).get("evidence_summary", None)
        except Exception:
            pass

        if not summary:
            summary = (
                f"Demo mode: {n} indicator category(ies) identified through "
                f"deterministic matching. Routing recommendation: "
                f"{routing_state.replace('_', ' ')}. "
                "This is decision-support only — not a trafficking determination. "
                "Configure an OpenAI API key for live evidence synthesis."
            )
    else:
        try:
            from services.llm_service import generate_evidence_summary
            from utils.config import get_openai_model
            result = generate_evidence_summary(masked_narrative, indicator_hits, routing_state)
            summary = result.summary
            missing_info = result.missing_information
            model_version = get_openai_model()
            api_mode = True
        except Exception as exc:
            n = len(indicator_hits)
            summary = (
                f"{n} indicator category(ies) identified. "
                f"Routing: {routing_state.replace('_', ' ')}. "
                "Evidence summary unavailable — API error. "
                "Human reviewer should assess the reported indicators directly."
            )
            model_version = f"error:{type(exc).__name__}"
            api_mode = False

    # Post-generation safety check — belt-and-suspenders
    _PROHIBITED = [
        "confirmed trafficking", "is a trafficker", "is guilty",
        "has been trafficked", "trafficking confirmed", "is trafficking",
    ]
    for term in _PROHIBITED:
        if term.lower() in summary.lower():
            summary = summary.replace(term, "[term removed]")

    event = (
        f"Evidence synthesis complete — {len(indicator_hits)} indicator(s) "
        f"summarised in hedged language"
        + (" [API]" if api_mode else " [demo/deterministic]")
    )
    audit = append_audit(state, "evidence_review", event)

    return {
        **state,
        "evidence_summary":    summary,
        "missing_information": missing_info,
        "llm_model_version":   model_version,
        "api_mode":            api_mode,
        "audit_trail":         audit,
    }
