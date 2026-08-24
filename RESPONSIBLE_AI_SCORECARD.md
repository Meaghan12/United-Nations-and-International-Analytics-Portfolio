# Responsible AI Scorecard
## Human Trafficking Risk & Referral Decision-Support System
**Author:** Meaghan Ryan | **Status:** Portfolio Prototype | **Version:** 2.0

> This scorecard traces each responsible AI principle to the specific code that implements it.
> It is not a certification or regulatory compliance document.
> This system has not been operationally, legally, or clinically validated.

---

## 1. Purpose Limitation

| Principle | Implementation |
|---|---|
| System purpose is narrowly defined | Identifies reported indicators, routes for human review, suggests referrals |
| Purpose is stated in every UI screen | Header, sidebar disclaimer, output panel, analytics panel |
| System explicitly states what it does NOT do | `ui/analysis_panel.py`, README, this document |

**What this system will NOT do:**
- Determine that trafficking has occurred
- Identify or accuse traffickers
- Predict criminality
- Make autonomous safeguarding decisions
- Generate a hidden numerical risk score
- Replace a trained human reviewer

---

## 2. Human Oversight

| Principle | Implementation |
|---|---|
| Human review is mandatory | `nodes/human_review.py` — `hitl_complete=False` until reviewer submits |
| Cannot be bypassed | `workflow/graph.py` — finalization phase blocked until `hitl_complete=True` |
| Reviewer controls: Approve, Edit, Escalate, Downgrade, More Info | `ui/human_review_panel.py` |
| Note required for escalation/override | Enforced in `ui/human_review_panel.py` |
| Reviewer decisions recorded in audit | `nodes/human_review.py` → `record_hitl_decision()` |
| Tests proving gate cannot be bypassed | `tests/test_human_review.py` |

---

## 3. Explainability

| Principle | Implementation |
|---|---|
| Each indicator shows supporting evidence | `indicator_hits[].evidence_quote` |
| Each indicator shows its detection source | `indicator_hits[].source` (structured_field / narrative / LLM) |
| Each indicator shows confidence level | `indicator_hits[].confidence` (REPORTED / POSSIBLE / INFERRED) |
| Routing rationale is shown in plain language | `routing_rationale` field, `ui/analysis_panel.py` |
| LLM is not the routing decision-maker | All routing in `workflow/router.py` — pure Python |
| Architecture is glass-box | All routing logic is inspectable in `nodes/` and `indicators/` |

---

## 4. Transparency

| Principle | Implementation |
|---|---|
| API mode vs demo mode is visible | Sidebar shows API status indicator |
| Web search calls are counted and shown | `web_search_calls_used / web_search_calls_max` displayed in UI |
| Sources retrieved are shown to reviewer | `ui/analysis_panel.py` — title, URL, relevance, jurisdiction |
| Audit trail is public-facing | `ui/audit_panel.py` — full execution trace |
| Disclaimer is prominent | Header and sidebar on every page |

---

## 5. PII and Data Minimisation

| Principle | Implementation |
|---|---|
| PII masking runs before any LLM call | `nodes/pii_mask.py` — regex masking before `indicator_analysis` |
| Masked version used for all LLM processing | `masked_narrative` passed to `services/llm_service.py` |
| Raw PII not sent to OpenAI | By design — only `masked_narrative` reaches API |
| Audit trail never logs raw PII | `AuditEntry.sensitive=True` items excluded from display |
| PII types logged, not values | `pii_redacted_items` stores category names only |
| Explicitly labelled prototype safeguard | UI panel, README, this document |
| Tests proving masking occurs | `tests/test_pii.py`, `tests/test_pii_masking.py` |

---

## 6. Profiling Resistance

| Principle | Implementation |
|---|---|
| Protected characteristics cannot trigger escalation | `validate_no_protected_characteristics()` in `indicators/framework.py` |
| Raises ValueError if characteristics appear in scoring input | Tested in `tests/test_indicator_framework.py` |
| CASE-008 demonstrates zero escalation for migrant worker | `data/synthetic_cases.json` |
| Dedicated profiling-resistance tests | `tests/test_false_positive_resistance.py`, `tests/test_profiling_resistance.py` |

**Protected characteristics that cannot trigger escalation:**
nationality, ethnicity, race, religion, immigration status, gender, sex,
sexual orientation, refugee status, migrant status

---

## 7. Uncertainty and Calibration

| Principle | Implementation |
|---|---|
| No numerical risk probability generated | No float score in any state field — categorical labels only |
| Confidence labels are descriptive | REPORTED / POSSIBLE / INFERRED — not numbers |
| Severity is categorical | NONE / LOW / MODERATE / HIGH / URGENT — not a score |
| System says "insufficient information" rather than guessing | NEED_INFO routing for vague cases |
| Evidence summaries use hedged language | `nodes/evidence_review.py`, LLM system prompt |
| Post-generation prohibited-term check | `nodes/evidence_review.py` — removes overconfident statements |

---

## 8. Model Boundaries

| Principle | Implementation |
|---|---|
| LLM scope strictly limited | LLM called in exactly 2 nodes: indicator extraction + evidence summary |
| LLM does NOT make routing decisions | All routing in pure Python |
| LLM does NOT trigger urgent safety escalation | `nodes/safety_check.py` — deterministic rules only |
| LLM does NOT bypass human review | `workflow/graph.py` — HITL gate is independent of LLM output |
| Temperature = 0 for all LLM calls | `services/llm_service.py` |
| Structured JSON schema output | Pydantic schemas in `models/schemas.py` — LLM cannot return freeform text |

---

## 9. Deterministic Safeguards

These controls run in pure Python regardless of LLM availability:

| Safeguard | Node |
|---|---|
| Urgent safety detection (physical violence, locked accommodation, explicit threats) | `nodes/safety_check.py` + `indicators/rules.py` |
| Required-field validation | `nodes/validate.py` |
| PII masking | `nodes/pii_mask.py` + `utils/pii.py` |
| Human review gate | `nodes/human_review.py` |
| Protected-characteristics guard | `indicators/framework.py` |
| Web search call limit (max 2) | `services/web_retrieval.py` |
| Prohibited-term post-processing | `nodes/evidence_review.py` |
| Audit trail creation | `nodes/audit.py` + `utils/audit.py` |

---

## 10. Auditability

| Principle | Implementation |
|---|---|
| Every node produces an audit event | All 10 nodes call `append_audit()` |
| Audit includes: timestamp, node, event, decision source | `AuditEntry` TypedDict |
| Human override recorded with reviewer note | `record_hitl_decision()` |
| Public audit trace is displayed in UI | `ui/audit_panel.py` |
| Sensitive entries excluded from public display | `AuditEntry.sensitive=True` |

---

## 11. Web Source Governance

| Principle | Implementation |
|---|---|
| Maximum 2 web searches per case | `services/web_retrieval.py` — hard limit enforced |
| Jurisdiction is reviewer-supplied only | Never inferred from IP, VPN, or browser location |
| Sources shown to reviewer (title, URL, relevance, jurisdiction) | `ui/analysis_panel.py` |
| No sources fabricated on failure | Returns failure message — does not invent agencies |
| Web search failure does not crash workflow | Try/except in `services/web_retrieval.py` |
| Tests for call limit | `tests/test_web_limit.py` |

---

## 12. Synthetic Data Limitations

- All 8 demonstration cases are entirely fictional
- No real individuals, organizations, or outcomes are represented
- Indicator keywords and framework categories are illustrative, not clinically validated
- Analytics are synthetic — not derived from real case data
- Routing logic has not been validated against expert-reviewed cases
- The system is not calibrated to real-world base rates of trafficking

---

## 13. Bias and Fairness Considerations

- **Known limitation:** Keyword matching may have higher false-positive rates for certain narrative styles or phrasings
- **Known limitation:** The indicator framework has not been reviewed by trafficking survivors, frontline practitioners, or domain experts
- **Mitigation:** Protected-characteristics guard prevents demographic escalation
- **Mitigation:** CASE-008 profiling-resistance case is a continuous test
- **Future requirement:** Expert review of indicator categories and keyword lists
- **Future requirement:** Disproportionate-impact testing across demographic groups

---

## 14. Misuse Risks

| Risk | Mitigation |
|---|---|
| Used as a final determination tool | Prominent disclaimers; HITL gate enforced in code |
| Used to justify discriminatory screening | Protected-characteristics guard; profiling-resistance tests |
| API key exposed | Key never logged, never in GitHub; `st.secrets` used on Cloud |
| Real case data entered | Prominent synthetic-data warning; no data retention in prototype |
| Results presented as UN-validated | Explicit disclaimer in header and README |

---

## 15. Deployment Limitations

This system is **not** suitable for operational use without:

- Review of indicator categories by certified anti-trafficking experts
- Validation of routing logic against expert-reviewed real cases
- Assessment by social work, legal, and psychological professionals
- Survivor consultation
- Ethics review by an independent IRB or equivalent
- Data governance framework for any real case data
- Security audit
- Accessibility audit
- Ongoing monitoring for disparate impact

---

## 16. Testing

| Test coverage | File |
|---|---|
| Safety rules | `tests/test_safety.py` / `test_safety_rules.py` |
| Routing logic | `tests/test_routing.py` |
| PII masking | `tests/test_pii.py` / `test_pii_masking.py` |
| Profiling resistance | `tests/test_profiling_resistance.py` / `test_false_positive_resistance.py` |
| NEED_INFO routing | `tests/test_need_info.py` |
| Human review gate | `tests/test_human_review.py` |
| API fallback / demo mode | `tests/test_api_fallback.py` |
| Web search limit | `tests/test_web_limit.py` |
| Indicator framework | `tests/test_indicator_framework.py` |

---

## 17. Secrets Handling

| Principle | Implementation |
|---|---|
| API key never committed to GitHub | `.gitignore` excludes `.env` and `.streamlit/secrets.toml` |
| Key never logged or printed | `utils/config.py` — key returned but never displayed |
| Key never returned to UI | No UI element reads or shows the key |
| Streamlit Cloud key loaded via `st.secrets` | `utils/config.py` priority chain |
| `.env.example` contains placeholder only | `OPENAI_API_KEY=your_key_here` |

---

*This scorecard was authored by Meaghan Ryan as part of a portfolio prototype.*
*It does not constitute legal, ethical, or operational certification.*
*Last updated: August 2026.*
