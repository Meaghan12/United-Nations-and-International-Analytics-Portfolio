"""
workflow/state.py
=================
Central state schema for the HT Decision-Support System.

Every LangGraph node reads from and writes to a CaseState instance.
Each node is permitted to write ONLY its designated fields
(enforced by convention and documented in the node permission model).

This file contains no business logic — only type definitions.
"""
from __future__ import annotations

from typing import TypedDict, Optional


class IndicatorHit(TypedDict):
    """A single matched risk indicator."""
    category: str        # e.g. "document_confiscation"
    label: str           # human-readable indicator description
    source: str          # "structured_field" | "narrative_extraction" | "llm_extracted"
    confidence: str      # "REPORTED" | "POSSIBLE" | "INFERRED"
                         # Never a decimal score — keeps output interpretable


class AuditEntry(TypedDict):
    """One immutable entry in the execution trace."""
    timestamp: str
    node: str
    event: str           # plain-language description of what occurred
    sensitive: bool      # if True, excluded from public-facing display trace


class CaseState(TypedDict, total=False):
    """
    The single source of truth flowing through the LangGraph pipeline.

    Fields are grouped by the node that owns them. Nodes may READ any field
    but should WRITE only their designated fields to avoid coupling.

    total=False allows partial initialization at intake; all fields are
    optional at the TypedDict level but required by their owning node.
    """

    # ── Session ──────────────────────────────────────────────────────────
    session_id: str
    timestamp_start: str
    timestamp_end: str

    # ── Raw input (pre-masking) — NEVER passed to LLM ──────────────────
    raw_case_id: str
    raw_narrative: str
    raw_intake_fields: dict          # structured form fields as submitted

    # ── Masked working copy — LLM-safe ──────────────────────────────────
    masked_narrative: str
    masked_fields: dict
    pii_redacted_items: list         # types of PII removed (not values)

    # ── Safety check ─────────────────────────────────────────────────────
    immediate_danger_detected: bool
    danger_triggers: list            # rule labels that fired (not raw text)

    # ── Validation ───────────────────────────────────────────────────────
    validation_status: str           # "COMPLETE" | "INCOMPLETE"
    missing_fields: list             # field names missing
    clarifying_questions: list       # questions to ask the practitioner

    # ── Indicator analysis ───────────────────────────────────────────────
    indicator_hits: list             # list of IndicatorHit dicts
    indicator_categories: dict       # category → count
    indicator_severity: str          # "NONE" | "LOW" | "MODERATE" | "HIGH" | "URGENT"
    # NOTE: No numeric score is stored. Categorical labels only.

    # ── Routing ──────────────────────────────────────────────────────────
    routing_state: str               # pre-human-review routing recommendation
    routing_rationale: str           # plain-English explanation of routing

    # ── LLM evidence synthesis ───────────────────────────────────────────
    evidence_summary: str            # hedged, qualified human-readable text
    llm_model_version: str           # logged for reproducibility/auditability
    demo_mode: bool                  # True = using pre-computed responses (no API key needed)

    # ── Referral options ─────────────────────────────────────────────────
    referral_categories: list        # list of referral type strings
    referral_rationale: dict         # referral_type → rationale string

    # ── Human review (HITL gate) ─────────────────────────────────────────
    hitl_decision: str               # "APPROVED" | "EDITED" | "ESCALATED" | "DOWNGRADED" | "MORE_INFO"
    reviewer_note: str
    reviewer_edits: dict             # what the reviewer changed vs. system recommendation
    hitl_complete: bool              # True only after reviewer submits

    # ── Final output ─────────────────────────────────────────────────────
    final_routing_state: str
    final_recommendation: str
    final_referral_categories: list

    # ── Audit trail ──────────────────────────────────────────────────────────
    audit_trail: list                # list of AuditEntry dicts (append-only)

    # ── Web grounding ─────────────────────────────────────────────────────────
    # Jurisdiction is ALWAYS reviewer-supplied — never inferred from IP/VPN.
    reviewer_jurisdiction: str       # e.g. "Halifax, Nova Scotia, Canada"
    web_grounding_enabled: bool      # True if reviewer enabled web search
    web_search_calls_used: int       # current counter (max = 2)
    web_search_calls_max: int        # always 2
    web_sources: list                # list of RetrievedSource dicts
    web_grounding_note: str          # human-readable status / failure message

    # ── API mode ──────────────────────────────────────────────────────────────
    api_mode: bool                   # True = real OpenAI API; False = demo mode
    llm_extraction_used: bool        # True if LLM was called for indicator extraction
    missing_information: list        # from LLM evidence review structured output


# ── Routing state constants ───────────────────────────────────────────────────
# Centralised here so every module uses the same strings.

ROUTING_STATES = {
    "URGENT_REVIEW": {
        "label": "URGENT SAFEGUARDING REVIEW",
        "color": "red",
        "emoji": "🔴",
        "description": "Immediate safety concern detected. Human review required urgently.",
    },
    "PRIORITY_REVIEW": {
        "label": "PRIORITY REVIEW",
        "color": "orange",
        "emoji": "🟠",
        "description": "Multiple serious indicators present. Human review required.",
    },
    "READY_FOR_REVIEW": {
        "label": "READY FOR REVIEW",
        "color": "blue",
        "emoji": "🔵",
        "description": "Analysis complete. Moderate indicators present. Human review recommended.",
    },
    "NEED_INFO": {
        "label": "INFORMATION REQUIRED",
        "color": "yellow",
        "emoji": "🟡",
        "description": "Insufficient information to complete assessment. Clarifying questions generated.",
    },
    "OTHER_SUPPORT": {
        "label": "OTHER SUPPORT INDICATED",
        "color": "purple",
        "emoji": "🟣",
        "description": "Welfare or labour concerns identified. Trafficking indicators insufficient. Human review recommended.",
    },
    "NO_ACTION_RECOMMENDED": {
        "label": "NO TRAFFICKING INDICATORS IDENTIFIED",
        "color": "gray",
        "emoji": "⚪",
        "description": "No substantive indicators present. Human review confirms and closes case.",
    },
    "HUMAN_OVERRIDE": {
        "label": "HUMAN OVERRIDE RECORDED",
        "color": "green",
        "emoji": "🟢",
        "description": "Reviewer changed the system recommendation. Override recorded in audit trail.",
    },
    "REFERRED": {
        "label": "REFERRED",
        "color": "green",
        "emoji": "🟢",
        "description": "Review completed. Referral decision confirmed by human reviewer.",
    },
}

INDICATOR_SEVERITY_LEVELS = ["NONE", "LOW", "MODERATE", "HIGH", "URGENT"]
