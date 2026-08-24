"""
nodes/indicator_analysis.py
============================
Identifies trafficking-related indicators from a case submission.

Three-pass approach:
1. Deterministic field matching (structured intake fields)
2. Deterministic keyword matching (narrative text)
3. LLM extraction via services/llm_service.py (structured JSON schema output)
   — only called when API is available; gracefully skipped in demo mode.

The LLM is used for extraction only.
All routing decisions are made by deterministic Python.

Protected-characteristics guard runs before any scoring.
PII masking has already occurred upstream (pii_mask node).
"""
from __future__ import annotations

import re
from utils.audit_log import append_audit
from indicators.framework import (
    INDICATOR_CATEGORIES,
    INDICATOR_KEYWORDS,
    get_severity_from_hits,
    validate_no_protected_characteristics,
)
from utils.config import is_demo_mode


# ── Protected characteristics (never used as escalation triggers) ─────────────
PROTECTED_CHARACTERISTICS = [
    "nationality", "ethnicity", "race", "religion", "immigration_status",
    "gender", "sex", "sexual_orientation", "refugee_status", "migrant_status",
]


# ── Negative denial detection ─────────────────────────────────────────────────

def _is_negative_denial(text: str) -> bool:
    """
    Return True if the field value clearly states the indicator is ABSENT.
    Prevents false positives where 'No threats, no coercion reported' is
    flagged as a threat indicator.
    """
    text = text.lower().strip()

    # Pure negatives
    if text in {"no", "none", "n/a", "not applicable", "not reported", "false", "0", "no concerns"}:
        return True

    NEGATIVE_PREFIXES = [
        "no ", "none ", "not ", "no-", "no—", "none reported",
        "no threats", "no coercion", "no pressure", "no fees",
        "no debt", "no recruitment", "free to", "freely",
        "wages paid as agreed", "paid as agreed", "paid on time",
        "holds their own", "individual holds", "in their own possession",
        "no irregularities", "no concerns",
        # Ambiguous / uncertain — not strong enough to flag as confirmed indicator
        "possibly", "potential", "may ", "perhaps", "unclear", "unknown",
        "not provided", "not known",
    ]
    for prefix in NEGATIVE_PREFIXES:
        if text.startswith(prefix):
            return True

    # Systematic negative: multiple "no " occurrences
    if text.count("no ") >= 2:
        return True

    return False


# ── Field matching ────────────────────────────────────────────────────────────

FIELD_CATEGORY_MAP = {
    "documentation_control":    "document_confiscation",
    "freedom_of_movement":      "restriction_of_movement",
    "wage_payment_concerns":    "wage_control_withholding",
    "coercion_or_threats":      "coercion_threats",
    "recruitment_debt":         "debt_recruitment_pressure",
    "immediate_safety_concern": "violence_threat_of_violence",
    "work_conditions":          "unsafe_accommodation",
    "isolation_indicators":     "isolation",
    "employment_exit":          "inability_to_leave_employment",
}


def _field_match(fields: dict) -> list[dict]:
    hits = []
    seen_categories = set()

    for field_key, category in FIELD_CATEGORY_MAP.items():
        value = fields.get(field_key, "")
        if not value or not isinstance(value, str):
            continue
        if _is_negative_denial(value):
            continue
        if category not in seen_categories:
            cat_meta = INDICATOR_CATEGORIES.get(category, {})
            hits.append({
                "category":       category,
                "label":          cat_meta.get("label", category),
                "source":         "structured_field",
                "confidence":     "REPORTED",
                "evidence_quote": value[:120],
            })
            seen_categories.add(category)

    return hits


# ── Keyword matching ──────────────────────────────────────────────────────────

def _keyword_match(narrative: str) -> list[dict]:
    if not narrative:
        return []

    text_lower = narrative.lower()
    hits = []
    seen_categories = set()

    for category, keywords in INDICATOR_KEYWORDS.items():
        if category in seen_categories:
            continue
        for kw in keywords:
            if kw.lower() in text_lower:
                cat_meta = INDICATOR_CATEGORIES.get(category, {})
                hits.append({
                    "category":       category,
                    "label":          cat_meta.get("label", category),
                    "source":         "narrative_extraction",
                    "confidence":     "POSSIBLE",
                    "evidence_quote": kw,
                })
                seen_categories.add(category)
                break

    return hits


# ── LLM extraction ────────────────────────────────────────────────────────────

def _llm_extract(masked_narrative: str, state: dict) -> list[dict]:
    """
    Use the LLM service for structured extraction.
    Falls back gracefully if API is unavailable or demo mode is active.
    """
    # Use demo pre-computed data if available and in demo mode
    if state.get("demo_mode", False) or is_demo_mode():
        case_id = state.get("raw_case_id", "")
        try:
            import json, os
            demo_path = os.path.join(
                os.path.dirname(__file__), "..", "data", "demo_llm_responses.json"
            )
            with open(demo_path) as f:
                demo = json.load(f)
            case_data = demo.get(case_id, {})
            return [
                {**h, "source": h.get("source", "llm_extracted")}
                for h in case_data.get("indicators", [])
            ]
        except Exception:
            return []

    # Real API call via the LLM service
    try:
        from services.llm_service import extract_indicators_llm
        result = extract_indicators_llm(masked_narrative)
        hits = []
        for ind in result.indicators:
            cat_meta = INDICATOR_CATEGORIES.get(ind.category, {})
            hits.append({
                "category":       ind.category,
                "label":          cat_meta.get("label", ind.category),
                "source":         "llm_extracted",
                "confidence":     ind.confidence,
                "evidence_quote": ind.evidence_quote,
            })
        return hits
    except Exception:
        return []


# ── Main node ─────────────────────────────────────────────────────────────────

def indicator_analysis_node(state: dict) -> dict:
    """
    LangGraph node: Indicator Analysis

    Reads:  masked_narrative, masked_fields, demo_mode, raw_case_id
    Writes: indicator_hits, indicator_categories, indicator_severity,
            llm_extraction_used
    """
    masked_narrative = state.get("masked_narrative", "")
    masked_fields    = state.get("masked_fields", {})

    # Protected characteristics guard — raises ValueError if triggered
    validate_no_protected_characteristics(masked_fields)

    # 1. Deterministic field matching
    field_hits   = _field_match(masked_fields)

    # 2. Deterministic keyword matching on narrative
    keyword_hits = _keyword_match(masked_narrative)

    # 3. LLM extraction
    api_available = not (state.get("demo_mode", False) or is_demo_mode())
    llm_hits = _llm_extract(masked_narrative, state)
    llm_used = api_available and bool(llm_hits)

    # Merge: deduplicate by category, prefer structured_field > narrative > llm
    source_priority = {"structured_field": 3, "narrative_extraction": 2, "llm_extracted": 1}
    all_hits_by_category: dict[str, dict] = {}
    for hit in llm_hits + keyword_hits + field_hits:
        if "source" not in hit:
            hit = {**hit, "source": "llm_extracted"}
        cat = hit["category"]
        existing = all_hits_by_category.get(cat)
        if not existing or source_priority.get(hit["source"], 0) > source_priority.get(existing.get("source", "llm_extracted"), 0):
            all_hits_by_category[cat] = hit

    final_hits = list(all_hits_by_category.values())

    # Count by category
    category_counts = {cat: 0 for cat in INDICATOR_CATEGORIES}
    for hit in final_hits:
        category_counts[hit["category"]] = category_counts.get(hit["category"], 0) + 1

    # Severity (categorical only — no numeric score)
    severity = get_severity_from_hits(final_hits)

    n_cats = sum(1 for v in category_counts.values() if v > 0)
    event = (
        f"Indicator analysis complete — {len(final_hits)} indicator(s) identified "
        f"across {n_cats} category/categories — severity: {severity}"
        + (" [LLM-assisted]" if llm_used else " [deterministic]")
    )
    audit = append_audit(state, "indicator_analysis", event)

    return {
        **state,
        "indicator_hits":       final_hits,
        "indicator_categories": category_counts,
        "indicator_severity":   severity,
        "llm_extraction_used":  llm_used,
        "audit_trail":          audit,
    }
