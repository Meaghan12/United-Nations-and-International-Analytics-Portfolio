# United-Nations-and-International-Analytics-Portfolio
Portfolio of responsible AI, agentic systems, machine learning, healthcare, financial and human-impact analytics for international and United Nations roles, best suited for me
# Human Trafficking Risk & Referral Decision-Support System

A portfolio prototype exploring responsible AI architecture for trafficking-related safeguarding and referral decision support.

Designed and developed by Meaghan Ryan.

## Purpose

This project demonstrates how machine learning, agentic AI, behavioural science, analytics, and human-centred decision support can be combined to assist with complex safeguarding workflows.

The system is designed to:

- identify reported trafficking-related risk indicators transparently;
- recognize insufficient or missing information;
- protect personally identifiable information before LLM processing;
- suggest relevant referral categories;
- route cases according to deterministic safeguarding logic;
- require human review before consequential action;
- maintain an auditable execution trace; and
- support programme-level analytics and monitoring.

It is **not** designed to determine that trafficking has occurred, identify perpetrators, predict criminality, or autonomously make safeguarding decisions.

## Demonstration

All current demonstration cases are entirely synthetic. No real individuals or cases are represented.

The prototype includes eight fictional scenarios spanning urgent safeguarding concerns, incomplete-information cases, lower-priority concerns, and profiling-resistance testing.

## Architecture

The prototype is built in Python and incorporates:

- Streamlit — interactive application interface
- LangGraph — workflow orchestration
- OpenAI API — constrained natural-language analysis
- Plotly — analytics and visualisation
- Pytest — testing and responsible-AI validation
- Deterministic Python rules — validation, safety checks, routing, and human-review requirements

The LLM is deliberately limited to natural-language tasks where it adds value. Core safety and routing decisions remain governed by transparent deterministic logic.

## Live API & Web-Grounded Version

The live version is being configured to support API-enabled analysis of newly entered synthetic cases and controlled web retrieval from authoritative sources.

The planned retrieval layer allows the reviewer to explicitly provide a relevant jurisdiction and use limited web-search calls to retrieve current, location-appropriate official guidance and verified referral resources.

The system does not infer jurisdiction from a user's IP address or VPN.

## Responsible AI

The project uses a glass-box approach emphasizing:

- explainability;
- human-in-the-loop decision making;
- PII protection;
- uncertainty handling;
- profiling resistance;
- deterministic safeguarding controls; and
- auditability.

An accompanying Responsible AI / Ethics scorecard and full technical documentation are being added to this repository.

## Project Status

**Portfolio prototype — active development.**

The complete source code, technical documentation, live Streamlit deployment, and API-enabled retrieval layer are being added to this repository.
