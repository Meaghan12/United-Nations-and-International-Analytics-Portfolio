"""
tests/test_false_positive_resistance.py
========================================
CRITICAL TEST: The profiling resistance test.

Case 8 (CASE-008) is a migrant worker with NO trafficking indicators.
The system MUST route this to NO_ACTION_RECOMMENDED, not a risk state.

This test validates that demographic characteristics do not drive risk
classification even when they might be associated with migration vulnerability.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nodes.indicator_analysis import _field_match, _keyword_match
from indicators.framework import get_severity_from_hits, get_routing_from_severity, validate_no_protected_characteristics


class TestProfilingResistance:
    """
    Tests that ensure the system resists demographic profiling.
    Case 8 scenario: Migrant worker, legally employed, no indicators.
    """

    CASE_008_FIELDS = {
        "employment_context": "Seasonal agricultural worker, legally employed under a temporary work visa programme",
        "reported_concerns": "Individual came to the advice centre to ask about their employment rights in general",
        "documentation_control": "Individual holds their own passport and work permit",
        "freedom_of_movement": "Free to move. Lives independently. Travels freely in the community.",
        "wage_payment_concerns": "Wages paid as agreed. No irregularities reported.",
        "coercion_or_threats": "No threats, no pressure, no coercion reported",
        "recruitment_debt": "No recruitment fees paid",
        "immediate_safety_concern": "No",
    }

    CASE_008_NARRATIVE = (
        "A seasonal agricultural worker came to the advice centre to understand their general "
        "employment rights while working in the country on a temporary visa. They arrived legally "
        "through a government-regulated seasonal worker programme. They hold their own passport "
        "and permit. They live in accommodation they arranged independently. They are free to come "
        "and go as they choose. Wages are paid on time and as agreed. There are no threats, no debt, "
        "and no pressure of any kind. They have regular contact with their family. They simply want "
        "to understand what their rights are as a temporary worker."
    )

    def test_no_field_indicators_from_safe_case(self):
        """Structured fields from Case 8 should produce zero indicator hits."""
        hits = _field_match(self.CASE_008_FIELDS)
        assert len(hits) == 0, (
            f"Expected 0 indicator hits for Case 8 (profiling resistance), "
            f"but got {len(hits)}: {hits}"
        )

    def test_no_keyword_indicators_from_safe_narrative(self):
        """Case 8 narrative should produce zero keyword indicator hits."""
        hits = _keyword_match(self.CASE_008_NARRATIVE)
        assert len(hits) == 0, (
            f"Expected 0 keyword hits for Case 8, but got {len(hits)}: {hits}"
        )

    def test_severity_is_none_with_no_indicators(self):
        """Zero indicators must produce NONE severity."""
        severity = get_severity_from_hits([])
        assert severity == "NONE"

    def test_routing_is_no_action_with_none_severity(self):
        """NONE severity + complete validation must route to NO_ACTION_RECOMMENDED."""
        routing, _ = get_routing_from_severity("NONE", True, 0)
        assert routing == "NO_ACTION_RECOMMENDED", (
            f"Expected NO_ACTION_RECOMMENDED but got {routing}. "
            f"Demographic characteristics must not drive risk routing."
        )

    def test_protected_characteristics_guard_fires(self):
        """
        Validate that if someone accidentally passes demographic fields
        to the scoring pipeline, the architecture guard raises an error.
        """
        with pytest.raises(ValueError):
            validate_no_protected_characteristics({
                "nationality": "Fictional Country",
                "employment_context": "Agricultural",
            })

    def test_immigration_status_alone_does_not_trigger(self):
        """
        Immigration status references in context should not trigger
        exploitation_of_vulnerability unless exploitation is explicitly described.
        """
        safe_text = "The individual is on a temporary work visa and is legally employed."
        hits = _keyword_match(safe_text)
        # Should not flag exploitation_of_vulnerability just from mentioning status
        exploitation_hits = [h for h in hits if h["category"] == "exploitation_of_vulnerability"]
        assert len(exploitation_hits) == 0, (
            "Mentioning immigration status without exploitation context "
            "should NOT trigger exploitation_of_vulnerability indicator."
        )
