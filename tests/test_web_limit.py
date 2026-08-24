"""
tests/test_web_limit.py
========================
Verifies the two-web-search-call limit is enforced programmatically.
"""
import pytest
from services.web_retrieval import WebSearchSession, run_web_search, MAX_SEARCHES


def test_max_searches_constant_is_two():
    assert MAX_SEARCHES == 2


def test_session_starts_at_zero():
    session = WebSearchSession()
    assert session.calls_used == 0
    assert session.calls_remaining == 2
    assert not session.limit_reached


def test_limit_reached_after_two_calls():
    session = WebSearchSession()
    # Force two calls in demo mode (no API key needed)
    import os
    os.environ["DEMO_MODE"] = "true"
    run_web_search(session, ["coercion_threats"], "Test Jurisdiction")
    run_web_search(session, ["document_confiscation"], "Test Jurisdiction")
    assert session.calls_used == 2
    assert session.limit_reached
    assert session.calls_remaining == 0


def test_third_call_returns_none():
    """A third web search call must return None — not raise, not execute."""
    session = WebSearchSession()
    import os
    os.environ["DEMO_MODE"] = "true"
    run_web_search(session, ["coercion_threats"], "Test Jurisdiction")
    run_web_search(session, ["document_confiscation"], "Test Jurisdiction")
    result = run_web_search(session, ["isolation"], "Test Jurisdiction")
    assert result is None
    assert session.calls_used == 2  # still 2, not 3


def test_display_counter_format():
    session = WebSearchSession()
    import os
    os.environ["DEMO_MODE"] = "true"
    run_web_search(session, ["coercion_threats"], "Test Jurisdiction")
    counter = session.display_counter()
    assert "1" in counter and "2" in counter


def test_no_jurisdiction_no_calls():
    """If no jurisdiction is supplied, web search should not run."""
    from services.web_retrieval import get_grounded_resources
    import os
    os.environ["DEMO_MODE"] = "true"
    session, sources = get_grounded_resources(["coercion_threats"], "", "URGENT_REVIEW")
    assert session.calls_used == 0
    assert sources == []
