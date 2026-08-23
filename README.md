# Human Trafficking Risk & Referral Decision-Support System

**Live Interactive Demo:**  
https://united-nations-and-international-analytics-portfolio-7ex3qtsvw.streamlit.app/

**Designed and developed by Meaghan Ryan**

A portfolio prototype exploring responsible AI architecture for trafficking-related safeguarding and referral decision support.

This project demonstrates how machine learning, agentic AI, behavioural science, analytics, and human-centred decision support can be combined to support complex safeguarding workflows.

> **Important:** All cases and data currently demonstrated in this project are entirely synthetic. No real individuals, cases, organizations, or outcomes are represented. This project is not affiliated with or endorsed by the United Nations or Eyes Open International.

## Purpose

The system is designed to help a human reviewer organize reported information, identify potentially relevant trafficking-related indicators, recognize missing information, consider appropriate referral pathways, and document the reasoning process behind a case review.

The system is designed to:

- identify reported trafficking-related risk indicators transparently;
- recognize insufficient or missing information rather than guess;
- protect personally identifiable information before model-facing processing;
- suggest relevant referral categories;
- route cases according to transparent safeguarding logic;
- require human review before consequential action;
- maintain an auditable execution trace; and
- support programme-level analytics and monitoring.

The system is **not** designed to:

- determine that trafficking has occurred;
- predict criminality or identify perpetrators;
- make autonomous referral or safeguarding decisions;
- use demographic characteristics to inflate risk;
- bypass human review;
- or generate a hidden numerical risk score.

## Demonstration

The interactive prototype contains eight fictional scenarios designed to demonstrate different system behaviours, including:

- urgent safeguarding review;
- higher- and moderate-priority concerns;
- cases requiring additional information;
- lower-priority employment concerns;
- and profiling-resistance scenarios in which demographic or migration characteristics alone do not trigger escalation.

One example involves a fictional domestic worker reporting document confiscation, restriction of movement, physical threats, wage withholding, isolation, and inability to leave employment.

The system identifies the reported indicators, explains the basis for the recommendation, suggests possible support categories, and then requires a human reviewer to approve, edit, escalate, downgrade, or request additional information.

## Human-in-the-Loop Decision Support

The system is intentionally designed so that AI does not make the final safeguarding decision.

A human reviewer remains responsible for consequential action and can:

- approve the system recommendation;
- edit it;
- escalate a case;
- downgrade the priority;
- request more information; and
- record reviewer reasoning.

The resulting decision becomes part of the audit trail.

## Explainable / Glass-Box Architecture

The project uses a glass-box approach rather than an opaque prediction model.

The reviewer can see:

- which indicators were identified;
- what information supported them;
- the resulting routing recommendation;
- potential referral pathways;
- the evidence summary;
- the human review decision; and
- the sequence of processing steps recorded in the execution trace.

Core safeguarding and routing behaviour is designed to remain governed by transparent logic rather than an unexplained model score.

## Responsible AI Design

Responsible-AI safeguards demonstrated by the project include:

- human-in-the-loop decision making;
- PII protection;
- explainable indicator reasoning;
- deterministic safety and routing controls;
- uncertainty and missing-information handling;
- profiling resistance;
- constrained language-model use;
- safeguarding escalation;
- auditability; and
- separation between decision support and final human judgment.

An accompanying Responsible AI / Ethics Scorecard is being prepared for the project.

## AI and Language-Model Role

The language model is deliberately limited to natural-language tasks where it adds value, particularly:

- extracting relevant indicators from narrative text;
- synthesizing reported evidence;
- producing concise, qualified case summaries; and
- assisting with information retrieval in the API-enabled version.

Safety checks, validation, routing logic, and human-review requirements are designed to remain governed independently of the language model.

## API-Enabled and Web-Grounded Version

The full version is being configured to support API-enabled analysis and controlled retrieval of current information from authoritative web sources.

A reviewer will be able to explicitly provide a relevant jurisdiction — for example, Halifax, Nova Scotia or Ohio — rather than the system inferring location from an IP address or VPN.

The retrieval layer is intended to support access to current, location-appropriate information such as:

- official legal and labour-rights guidance;
- specialized trafficking-support resources;
- healthcare resources;
- psychosocial support;
- immigration or legal-status information;
- housing or shelter resources; and
- other verified referral information.

The system is designed to expose the supporting sources so that retrieved information remains reviewable rather than functioning as an unexplained recommendation.

## Analytics

The prototype also includes a programme-level analytics layer demonstrating how aggregated case information could be used to examine:

- routing states;
- severity distributions;
- frequently observed indicator categories;
- cases requiring additional information;
- human-review and override patterns; and
- referral-pathway demand.

With appropriately governed and validated real-world data, a similar analytics layer could support programme monitoring, resource planning, quality assurance, evaluation, operational decision support, and reporting.

## Technical Stack

The project is built in Python and incorporates:

- **Streamlit** — interactive user interface;
- **LangGraph** — workflow orchestration in the full modular implementation;
- **OpenAI API** — constrained language-model functionality;
- **Plotly** — analytics and visualization;
- **Pytest** — testing and validation;
- **Pandas** — data handling and analytics; and
- **deterministic Python logic** — safeguarding rules, validation, routing, and human-review controls.

## Workflow

The intended end-to-end workflow is:

`Intake → PII Mask → Safety Check → Validate → Indicator Analysis → Evidence Review → Referral Options → Human Review → Finalize → Audit`

This architecture separates model-assisted natural-language processing from deterministic safeguards and human decision authority.

## Current Deployment Status

The public Streamlit application currently provides an immediately accessible demonstration using synthetic cases and deterministic prototype logic.

The repository is being expanded with the full modular architecture, API-enabled analysis, governed web retrieval, testing suite, responsible-AI documentation, and additional technical materials.

The public Streamlit URL can remain the same as the implementation is upgraded.

## Portfolio Context

This project was developed to demonstrate applied capabilities across:

- machine learning and AI;
- behavioural and psychological analysis;
- human-centred system design;
- programme analytics;
- responsible AI governance;
- decision-support systems;
- data visualization;
- and applied problem solving in complex human-impact environments.

The underlying architecture is transferable beyond trafficking-related safeguarding to other areas requiring transparent, human-supervised decision support, such as healthcare, programme evaluation, public-sector operations, humanitarian services, financial controls, and social-impact analytics.
