"""
tests/test_indicator_framework.py
===================================
Tests for indicator severity logic and protected characteristic guard.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from indicators.framework import (
    get_severity_from_hits,
    get_routing_from_severity,
    validate_no_protected_characteristics,
    INDICATOR_CATEGORIES,
)


class TestSeverityLogic:
    def test_violence_always_urgent(self):
        hits = [{"category": "violence_threat_of_violence", "label": "Hit", "source": "reported", "confidence": "REPORTED"}]
        assert get_severity_from_hits(hits) == "URGENT"

    def test_restriction_plus_coercion_urgent(self):
        hits = [
            {"category": "restriction_of_movement", "label": "Locked in", "source": "field", "confidence": "REPORTED"},
            {"category": "coercion_threats", "label": "Threatened", "source": "field", "confidence": "REPORTED"},
        ]
        assert get_severity_from_hits(hits) == "URGENT"

    def test_three_high_weight_indicators_is_high(self):
        hits = [
            {"category": "coercion_threats", "label": "Threatened", "source": "field", "confidence": "REPORTED"},
            {"category": "document_confiscation", "label": "Passport taken", "source": "field", "confidence": "REPORTED"},
            {"category": "inability_to_leave_employment", "label": "Cannot quit", "source": "field", "confidence": "REPORTED"},
        ]
        severity = get_severity_from_hits(hits)
        assert severity == "HIGH"

    def test_single_indicator_low(self):
        hits = [{"category": "debt_recruitment_pressure", "label": "Debt", "source": "field", "confidence": "REPORTED"}]
        assert get_severity_from_hits(hits) == "LOW"

    def test_no_indicators_none(self):
        assert get_severity_from_hits([]) == "NONE"

    def test_two_indicators_moderate(self):
        hits = [
            {"category": "wage_control_withholding", "label": "Wages withheld", "source": "field", "confidence": "REPORTED"},
            {"category": "debt_recruitment_pressure", "label": "High debt", "source": "field", "confidence": "REPORTED"},
        ]
        assert get_severity_from_hits(hits) == "MODERATE"


class TestRoutingLogic:
    def test_urgent_routes_to_urgent_review(self):
        routing, _ = get_routing_from_severity("URGENT", True, 2)
        assert routing == "URGENT_REVIEW"

    def test_high_routes_to_priority_review(self):
        routing, _ = get_routing_from_severity("HIGH", True, 3)
        assert routing == "PRIORITY_REVIEW"

    def test_incomplete_validation_routes_to_need_info(self):
        routing, _ = get_routing_from_severity("MODERATE", False, 2)
        assert routing == "NEED_INFO"

    def test_none_severity_no_action(self):
        routing, _ = get_routing_from_severity("NONE", True, 0)
        assert routing == "NO_ACTION_RECOMMENDED"

    def test_rationale_is_not_empty(self):
        _, rationale = get_routing_from_severity("HIGH", True, 3)
        assert len(rationale) > 20


class TestProtectedCharacteristicsGuard:
    def test_nationality_raises_error(self):
        with pytest.raises(ValueError, match="ARCHITECTURE VIOLATION"):
            validate_no_protected_characteristics({"nationality": "Fictional"})

    def test_ethnicity_raises_error(self):
        with pytest.raises(ValueError, match="ARCHITECTURE VIOLATION"):
            validate_no_protected_characteristics({"ethnicity": "Fictional"})

    def test_immigration_status_raises_error(self):
        with pytest.raises(ValueError, match="ARCHITECTURE VIOLATION"):
            validate_no_protected_characteristics({"immigration_status": "undocumented"})

    def test_legitimate_fields_do_not_raise(self):
        # Should not raise
        validate_no_protected_characteristics({
            "employment_context": "Agricultural work",
            "documentation_control": "Passport retained",
        })

    def test_empty_dict_does_not_raise(self):
        validate_no_protected_characteristics({})
