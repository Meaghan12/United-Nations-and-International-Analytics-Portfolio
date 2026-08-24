"""
nodes/pii_mask.py
=================
Node 2 — PII Masking

PERMITTED: Apply regex + rule-based PII patterns; log TYPES of redaction.
PROHIBITED: Log actual PII values; call LLM on raw data; modify case assessments.

This node creates the masked working copies of the narrative and fields.
All downstream LLM nodes receive ONLY the masked copies.
"""
from __future__ import annotations

from utils.pii_patterns import mask_text, mask_fields
from utils.audit_log import append_audit


def pii_mask_node(state: dict) -> dict:
    """
    Masks PII in the raw narrative and raw intake fields.
    Produces masked_narrative and masked_fields for downstream use.

    Logs the TYPES of PII detected (not the actual values).
    """
    raw_narrative = state.get("raw_narrative", "")
    raw_fields = state.get("raw_intake_fields", {})

    # Mask narrative
    narrative_result = mask_text(raw_narrative)

    # Mask structured fields
    masked_fields_dict, field_pii_types = mask_fields(raw_fields)

    # Combine all PII types found
    all_pii_types = list(set(narrative_result.redacted_item_types + field_pii_types))

    # Audit: log PII types found, never values
    if all_pii_types:
        event = f"PII masking applied — types detected: {', '.join(all_pii_types)}"
    else:
        event = "PII masking applied — no direct identifiers detected in text"

    audit = append_audit(state, "pii_mask", event)

    return {
        **state,
        "masked_narrative": narrative_result.masked_text,
        "masked_fields": masked_fields_dict,
        "pii_redacted_items": all_pii_types,
        "audit_trail": audit,
    }
