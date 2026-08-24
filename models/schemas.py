"""
models/schemas.py
=================
Pydantic schemas for structured LLM output validation.

The OpenAI Responses API supports JSON Schema-constrained output.
These schemas define exactly what the LLM is allowed to return,
making extraction machine-validated rather than prompt-dependent.
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


# ── Indicator extraction schema ───────────────────────────────────────────────

VALID_CATEGORIES = Literal[
    "coercion_threats",
    "restriction_of_movement",
    "document_confiscation",
    "debt_recruitment_pressure",
    "wage_control_withholding",
    "deception_regarding_work",
    "isolation",
    "dependency_control",
    "unsafe_accommodation",
    "violence_threat_of_violence",
    "inability_to_leave_employment",
    "exploitation_of_vulnerability",
]

VALID_CONFIDENCE = Literal["REPORTED", "POSSIBLE", "INFERRED"]


class ExtractedIndicator(BaseModel):
    """A single indicator extracted from case narrative by the LLM."""
    category: VALID_CATEGORIES = Field(
        description="Indicator category from the Demonstration Indicator Framework"
    )
    evidence_quote: str = Field(
        description="Direct or paraphrased supporting text from the narrative (≤120 chars)",
        max_length=200,
    )
    confidence: VALID_CONFIDENCE = Field(
        description="Confidence level: REPORTED=explicitly stated, POSSIBLE=implied, INFERRED=contextual"
    )


class IndicatorExtractionResult(BaseModel):
    """Full structured output from the indicator extraction LLM call."""
    indicators: list[ExtractedIndicator] = Field(
        description="List of trafficking-related indicators found in the narrative. Empty list if none.",
        default_factory=list,
    )
    ambiguities: list[str] = Field(
        description="List of aspects that are ambiguous or require clarification (≤3 items, ≤80 chars each)",
        default_factory=list,
        max_length=3,
    )
    note: str = Field(
        description="Optional brief note about the extraction (≤200 chars). Do NOT conclude trafficking occurred.",
        default="",
        max_length=200,
    )


# ── Evidence review schema ────────────────────────────────────────────────────

class EvidenceSummaryResult(BaseModel):
    """Structured output from the evidence review LLM call."""
    summary: str = Field(
        description=(
            "Hedged, neutral summary of reported indicators for the human reviewer. "
            "Use 'individual', not 'victim'. Do NOT state trafficking has occurred. "
            "Do NOT name perpetrators. Do NOT give a probability. ≤400 chars."
        ),
        max_length=600,
    )
    missing_information: list[str] = Field(
        description="Key information gaps that would help the reviewer. ≤5 items.",
        default_factory=list,
        max_length=5,
    )


# ── Web search source schema ──────────────────────────────────────────────────

class RetrievedSource(BaseModel):
    """A single authoritative source returned from web grounding."""
    title: str = Field(description="Page or organization title")
    url: str = Field(description="Full URL of the resource")
    relevance: str = Field(
        description="Brief explanation of why this source is relevant to this case (≤150 chars)",
        max_length=200,
    )
    jurisdiction: str = Field(
        description="Jurisdiction or geographic scope of the resource",
        default="Not specified",
    )


class WebGroundingResult(BaseModel):
    """Result of one web-search tool call."""
    sources: list[RetrievedSource] = Field(
        description="Authoritative sources found",
        default_factory=list,
    )
    search_query: str = Field(description="The query that was used")
    search_successful: bool = Field(default=True)
    failure_reason: str = Field(default="")
