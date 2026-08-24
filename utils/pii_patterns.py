"""
utils/pii_patterns.py
=====================
Rule-based PII detection and masking patterns.

All data processed by this system uses SYNTHETIC FICTIONAL cases.
PII masking is implemented here as a DEMONSTRATION of privacy-aware
architecture — showing how real names, phone numbers, addresses, and
identifiers would be handled if real data were processed.

In a real deployment, this module would be reviewed by a data protection
officer and supplemented with jurisdiction-specific requirements.
"""
from __future__ import annotations

import re
from typing import NamedTuple


class MaskResult(NamedTuple):
    masked_text: str
    redacted_item_types: list[str]  # types of PII found, NOT the actual values


# ── PII detection patterns ─────────────────────────────────────────────────────
# (label, regex_pattern, replacement_token)

PII_PATTERNS: list[tuple[str, str, str]] = [
    # Names — common patterns (first + last, or just a capitalized name sequence)
    ("PERSON_NAME", r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b", "[NAME REDACTED]"),

    # Phone numbers (international and local formats)
    ("PHONE_NUMBER", r"\b(\+?[\d\s\-\(\)]{7,15})\b", "[PHONE REDACTED]"),

    # Email addresses
    ("EMAIL_ADDRESS", r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b", "[EMAIL REDACTED]"),

    # Passport numbers (generic pattern)
    ("PASSPORT_NUMBER", r"\b[A-Z]{1,2}\d{6,9}\b", "[PASSPORT# REDACTED]"),

    # Street addresses
    ("STREET_ADDRESS",
     r"\b\d{1,5}\s+[A-Za-z\s]+(Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd)\b",
     "[ADDRESS REDACTED]"),

    # Dates of birth (common formats)
    ("DATE_OF_BIRTH",
     r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b",
     "[DOB/DATE REDACTED]"),

    # National ID / Social Security style numbers
    ("ID_NUMBER", r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b", "[ID# REDACTED]"),

    # Case/File reference numbers (in synthetic data: format SYN-XXXX)
    # NOTE: case_id is retained in masked form for traceability
]

# Fields that should NEVER be passed to the LLM, regardless of masking
LLM_BLOCKED_FIELDS = ["raw_narrative", "raw_intake_fields", "raw_case_id"]


def mask_text(text: str) -> MaskResult:
    """
    Apply PII masking patterns to a text string.

    Returns the masked text and a list of PII TYPE labels found
    (not the actual values — we never log what was removed).
    """
    if not text:
        return MaskResult("", [])

    masked = text
    found_types = []

    for label, pattern, replacement in PII_PATTERNS:
        new_text, count = re.subn(pattern, replacement, masked)
        if count > 0:
            found_types.append(label)
            masked = new_text

    return MaskResult(masked, found_types)


def mask_fields(fields: dict) -> tuple[dict, list[str]]:
    """
    Apply PII masking to all string values in a fields dict.

    Returns (masked_fields_dict, list_of_pii_types_found).
    """
    masked_fields = {}
    all_found_types = []

    for key, value in fields.items():
        if isinstance(value, str):
            result = mask_text(value)
            masked_fields[key] = result.masked_text
            all_found_types.extend(result.redacted_item_types)
        else:
            masked_fields[key] = value  # non-string fields passed through

    # Deduplicate types
    return masked_fields, list(set(all_found_types))
