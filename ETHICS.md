# ETHICS.md — Responsible AI Design Document

**Human Trafficking Risk & Referral Decision-Support System**  
Author: Meaghan Ryan · Portfolio Prototype

---

## Purpose of This Document

This document explains the ethical design principles embedded in this system — not as aspirational statements, but as implemented architectural decisions. A reader should be able to trace each principle to specific code.

---

## 1. The System Cannot Determine That Trafficking Occurred

**Principle:** The system may never output a statement equivalent to "this person has been trafficked," "trafficking is confirmed," or any other factual or legal determination.

**Implementation:**
- `models/prompts.py`: `PROHIBITED_TERMS` list in the evidence review system prompt explicitly forbids these phrases
- `nodes/evidence_review.py`: `_sanitize_summary()` applies post-generation replacement of prohibited language
- `workflow/state.py`: No field in `CaseState` stores a trafficking determination — only indicator hits and routing states
- Routing state labels (e.g., `PRIORITY_REVIEW`) describe the review priority, not a trafficking conclusion

---

## 2. Human Review Cannot Be Bypassed

**Principle:** No case can be finalized without a human reviewer explicitly submitting a decision.

**Implementation:**
- `workflow/graph.py`: The LangGraph graph includes `human_review` as a mandatory node before `finalize`
- `workflow/state.py`: `hitl_complete` field is initialized to `False` by `human_review_node` and set to `True` only by `record_hitl_decision()`
- `nodes/human_review.py`: `record_hitl_decision()` is only called after reviewer form submission
- `app.py`: `run_finalization_phase()` only executes after reviewer input is collected and written to state
- In `URGENT_REVIEW` cases: the UI presents an urgent red banner. The reviewer must still click "Submit Reviewer Decision" to proceed.

---

## 3. Protected Characteristics Cannot Drive Risk Classification

**Principle:** Nationality, ethnicity, race, religion, gender, sex, sexual orientation, disability, immigration status, and country of origin must not increase a person's risk classification.

**Implementation:**
- `indicators/framework.py`: `PROTECTED_CHARACTERISTICS` list defines all excluded fields
- `indicators/framework.py`: `validate_no_protected_characteristics()` raises `ValueError` if these fields appear in scoring input
- `nodes/indicator_analysis.py`: `validate_no_protected_characteristics(scoring_input)` is called before any indicator scoring
- `indicators/framework.py`: `exploitation_of_vulnerability` is only triggered by evidence of active exploitation — not by the presence of a vulnerable status alone
- Test: `tests/test_false_positive_resistance.py` verifies that Case 8 (migrant worker, no indicators) routes to `NO_ACTION_RECOMMENDED`

---

## 4. PII Must Not Appear in LLM Input or Logs

**Principle:** Sensitive identifying information must be removed before any LLM call. Logs must record PII types, not values.

**Implementation:**
- `nodes/pii_mask.py` runs before any LLM node in the graph
- `models/llm_client.py` and the node implementations: only `masked_narrative` and `masked_fields` are passed to LLM calls
- `utils/pii_patterns.py`: `mask_text()` returns `MaskResult.redacted_item_types` — a list of type labels only
- `nodes/pii_mask.py`: audit event logs `"types detected: PERSON_NAME, PHONE_NUMBER"` — never the actual values
- `utils/audit_log.py`: `AuditEntry.sensitive` flag allows filtering sensitive entries from public display

---

## 5. The LLM Has Constrained Responsibilities

**Principle:** The language model performs extraction and synthesis only. It makes no routing decisions, no legal assessments, and no referral decisions.

**Implementation:**
- `models/prompts.py`: `INDICATOR_EXTRACTION_SYSTEM` — explicitly prohibits concluding trafficking, assessing guilt, making recommendations
- `models/prompts.py`: `EVIDENCE_REVIEW_SYSTEM` — explicitly prohibits using words like "victim", "trafficker", "confirmed", "guilty"
- `workflow/router.py`: All routing functions are pure Python deterministic functions — no LLM calls
- `indicators/framework.py`: Severity and routing logic is pure Python — no LLM
- Only `indicator_analysis.py` (extraction) and `evidence_review.py` (synthesis) call `get_llm_response()`
- Temperature is set to 0 for all LLM calls — deterministic output

---

## 6. The System Must Be Able to Say "Insufficient Information"

**Principle:** The system should return `NEED_INFO` rather than force a classification when key information is absent.

**Implementation:**
- `nodes/validate.py`: Required fields check; if absent, `validation_status = "INCOMPLETE"`
- `workflow/router.py`: `route_after_validate()` routes to `"need_info"` when `validation_status == "INCOMPLETE"`
- `workflow/graph.py`: `_need_info_passthrough()` sets `routing_state = "NEED_INFO"` and generates clarifying questions
- Test: `tests/test_indicator_framework.py` verifies that `NONE` severity + incomplete validation → `NEED_INFO`

---

## 7. No Numeric Risk Score Is Produced

**Principle:** Categorical severity labels are used. Numerical scores create false precision and can be misinterpreted as probabilistic trafficking determinations.

**Implementation:**
- `workflow/state.py`: `indicator_severity` field accepts only: `"NONE" | "LOW" | "MODERATE" | "HIGH" | "URGENT"`
- `indicators/framework.py`: `get_severity_from_hits()` returns a string label, never a float
- `models/prompts.py`: Extraction prompt states "Do not assign decimal probability scores"
- No UI component displays a numerical score

---

## 8. Survivor-Centred Language

**Principle:** Language should be professional, neutral, and non-stigmatizing.

**Implementation:**
- `models/prompts.py`: Evidence review system prompt requires use of "individual", "person", "reported indicators" — prohibits "victim" in the sense of a trafficking label
- `nodes/evidence_review.py`: `_sanitize_summary()` replaces prohibited terms post-generation
- `referrals/categories.py`: Referral labels use professional terminology
- `workflow/state.py`: `ROUTING_STATES` labels use language like "Immediate Safety Concern" rather than "Trafficking Confirmed"
- This document and the README use careful language throughout

---

## 9. Referral Categories Are Fictional

**Principle:** The prototype must not misrepresent itself as an operational referral service. Real emergency numbers, named organizations, or real victim services must not be included.

**Implementation:**
- `referrals/categories.py`: All referral descriptions include `"[PROTOTYPE — not a real service directory]"`
- README and ETHICS.md: Explicitly state that referral categories are fictional
- No phone numbers, URLs to real services, or named organizations appear in the codebase

---

## 10. The Audit Trail Is Immutable After Completion

**Principle:** The record of processing steps cannot be modified after case finalization.

**Implementation:**
- `utils/audit_log.py`: `append_audit()` returns a new list rather than mutating in place
- `nodes/audit.py`: Final audit entry recorded; no subsequent nodes write to audit trail
- `utils/audit_log.py`: `public_audit_trail()` filters `sensitive=True` entries for display — it does not delete them from the internal state

---

## 11. What Would Be Needed for Real Deployment

This section is included to honestly communicate the gap between this prototype and a deployable system:

- **Survivor input and co-design** — people with lived experience of trafficking should be involved in designing any real system
- **Subject-matter expert review** — anti-trafficking practitioners, social workers, legal professionals
- **Formal indicator framework** — validated against a recognized legal/clinical standard (e.g., ILO forced labour indicators, Palermo Protocol)
- **Jurisdictional legal review** — varying legal definitions and obligations across countries
- **Data protection assessment** — GDPR, national data protection laws, sector-specific requirements
- **Security review** — penetration testing, access controls, data residency
- **Bias and fairness audit** — formal evaluation against real case data
- **Multilingual support** — most affected populations may not speak English
- **Operational governance** — policies, training, accountability frameworks
- **Ongoing monitoring** — human override rates, routing patterns, model drift

---

*This document is part of a portfolio project. It is not a compliance document for any real system.*
