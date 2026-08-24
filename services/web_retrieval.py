"""
services/web_retrieval.py
==========================
Controlled authoritative web search via the OpenAI Responses API built-in
web_search_preview tool.

Design constraints (from system requirements):
- Maximum TWO web-search tool calls per case analysis.
  This is enforced programmatically, not just by convention.
- Jurisdiction is ALWAYS reviewer-supplied — never inferred from IP/VPN/device.
- Search is for REFERRAL RESOURCE GROUNDING only — not for deciding
  whether trafficking occurred.
- Retrieved sources are exposed to the reviewer (title, URL, relevance, jurisdiction).
- If search fails or returns untrustworthy results, the system says so clearly.
  It does NOT fabricate fallback agencies.
- Search failure must NOT crash the case workflow.
- The web_search_preview tool is the OpenAI built-in — no external search APIs needed.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from models.schemas import RetrievedSource, WebGroundingResult
from utils.config import get_openai_key, get_openai_model, get_max_web_searches, is_demo_mode

logger = logging.getLogger(__name__)

MAX_SEARCHES = get_max_web_searches()  # = 2


@dataclass
class WebSearchSession:
    """
    Tracks web-search usage for a single case analysis.
    The call counter is the enforcement mechanism for the 2-call maximum.
    """
    calls_used: int = 0
    max_calls: int = MAX_SEARCHES
    results: list[WebGroundingResult] = field(default_factory=list)

    @property
    def calls_remaining(self) -> int:
        return max(0, self.max_calls - self.calls_used)

    @property
    def limit_reached(self) -> bool:
        return self.calls_used >= self.max_calls

    def all_sources(self) -> list[RetrievedSource]:
        sources = []
        for r in self.results:
            sources.extend(r.sources)
        return sources

    def display_counter(self) -> str:
        return f"Web grounding calls used: {self.calls_used} / {self.max_calls}"


def _build_search_query(
    indicator_categories: list[str],
    jurisdiction: str,
    search_type: str = "support_resources",
) -> str:
    """
    Build a focused search query for authoritative referral resources.
    The query targets resource-finding, not trafficking classification.
    """
    jurisdiction_part = f"in {jurisdiction}" if jurisdiction and jurisdiction.strip() else ""

    if search_type == "support_resources":
        indicators_readable = ", ".join(
            cat.replace("_", " ") for cat in indicator_categories[:4]
        )
        return (
            f"official support services trafficking exploitation "
            f"{indicators_readable} {jurisdiction_part} "
            f"government legal aid shelter hotline"
        ).strip()

    elif search_type == "legal_resources":
        return (
            f"legal aid immigration rights labour law "
            f"trafficking support {jurisdiction_part} official government"
        ).strip()

    return f"trafficking support resources {jurisdiction_part} official".strip()


def _parse_web_search_output(
    output_items: list,
    search_query: str,
    jurisdiction: str,
) -> WebGroundingResult:
    """
    Parse the Responses API output for web_search_preview tool results.
    Extracts sources from the API response structure.
    """
    sources = []

    for item in output_items:
        # The Responses API returns web search results in message output items
        if hasattr(item, "type") and item.type == "message":
            # Extract citations/annotations from the message content
            if hasattr(item, "content"):
                for content_block in item.content:
                    if hasattr(content_block, "annotations"):
                        for ann in content_block.annotations:
                            if hasattr(ann, "url") and ann.url:
                                title = getattr(ann, "title", ann.url)
                                sources.append(
                                    RetrievedSource(
                                        title=title[:200] if title else ann.url,
                                        url=ann.url,
                                        relevance=(
                                            f"Retrieved as authoritative resource for "
                                            f"this case context."
                                        ),
                                        jurisdiction=jurisdiction or "Not specified",
                                    )
                                )

    return WebGroundingResult(
        sources=sources[:8],  # cap at 8 sources per call
        search_query=search_query,
        search_successful=True,
    )


def run_web_search(
    session: WebSearchSession,
    indicator_categories: list[str],
    jurisdiction: str,
    search_type: str = "support_resources",
) -> WebGroundingResult | None:
    """
    Perform one web-search tool call via the OpenAI Responses API.

    Returns a WebGroundingResult, or None if the limit is reached.
    On any failure, returns a WebGroundingResult with search_successful=False.
    Never raises — failure is always handled gracefully.

    Args:
        session: The WebSearchSession tracking calls for this case.
        indicator_categories: Which indicator categories to ground resources for.
        jurisdiction: Reviewer-supplied jurisdiction string (NEVER inferred from IP).
        search_type: "support_resources" or "legal_resources".
    """
    # Enforce hard limit
    if session.limit_reached:
        logger.info("Web search limit reached (%d/%d). Skipping call.", session.calls_used, session.max_calls)
        return None

    if is_demo_mode():
        session.calls_used += 1
        demo_result = WebGroundingResult(
            sources=[
                RetrievedSource(
                    title="Demo Mode — Web search not active",
                    url="https://example.org",
                    relevance=(
                        "Web search requires an OpenAI API key. "
                        "Configure OPENAI_API_KEY to retrieve live authoritative resources."
                    ),
                    jurisdiction=jurisdiction or "Not specified",
                )
            ],
            search_query=_build_search_query(indicator_categories, jurisdiction, search_type),
            search_successful=False,
            failure_reason="Demo mode — API key not configured.",
        )
        session.results.append(demo_result)
        return demo_result

    key = get_openai_key()
    if not key:
        session.calls_used += 1
        failed = WebGroundingResult(
            sources=[],
            search_query=_build_search_query(indicator_categories, jurisdiction, search_type),
            search_successful=False,
            failure_reason="No API key configured.",
        )
        session.results.append(failed)
        return failed

    search_query = _build_search_query(indicator_categories, jurisdiction, search_type)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        model = get_openai_model()

        instructions = (
            "You are retrieving authoritative support resources for a human case reviewer. "
            "Find official government, NGO, or recognized institutional resources. "
            "Do NOT speculate about whether trafficking occurred. "
            "Return URLs and titles of trustworthy referral resources only."
        )

        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=search_query,
            tools=[{"type": "web_search_preview"}],
            temperature=0,
        )

        session.calls_used += 1
        result = _parse_web_search_output(response.output, search_query, jurisdiction)
        session.results.append(result)
        return result

    except Exception as exc:
        session.calls_used += 1
        logger.warning("Web search failed: %s", type(exc).__name__)
        failed = WebGroundingResult(
            sources=[],
            search_query=search_query,
            search_successful=False,
            failure_reason=(
                f"Reliable current resources could not be confirmed "
                f"({type(exc).__name__}). The reviewer should consult known "
                f"local service directories directly."
            ),
        )
        session.results.append(failed)
        return failed


def get_grounded_resources(
    indicator_categories: list[str],
    jurisdiction: str,
    routing_state: str,
) -> tuple[WebSearchSession, list[RetrievedSource]]:
    """
    High-level entry point: perform up to two targeted web searches
    and return all sources found.

    Call 1: Support / referral resources for the given indicators + jurisdiction.
    Call 2 (if indicators suggest it): Legal / immigration resources.

    Returns (session, sources_list).
    """
    session = WebSearchSession()

    if not jurisdiction or not jurisdiction.strip():
        # No jurisdiction supplied — web search cannot be meaningfully targeted
        return session, []

    # Call 1 — general support resources
    run_web_search(session, indicator_categories, jurisdiction, "support_resources")

    # Call 2 — legal/immigration resources, only if case has relevant indicators
    legal_relevant_categories = {
        "document_confiscation", "debt_recruitment_pressure",
        "restriction_of_movement", "inability_to_leave_employment",
        "exploitation_of_vulnerability",
    }
    has_legal_indicators = bool(set(indicator_categories) & legal_relevant_categories)
    urgent_or_priority = routing_state in ("URGENT_REVIEW", "PRIORITY_REVIEW")

    if has_legal_indicators or urgent_or_priority:
        run_web_search(session, indicator_categories, jurisdiction, "legal_resources")

    return session, session.all_sources()
