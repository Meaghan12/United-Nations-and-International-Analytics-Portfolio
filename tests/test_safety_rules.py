"""
tests/test_safety_rules.py
===========================
Tests for the deterministic safety trigger rules.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from indicators.rules import check_immediate_danger


class TestImmediateDangerRules:
    def test_physical_violence_triggers(self):
        text = "The individual reports being hit by their employer on multiple occasions."
        detected, triggers = check_immediate_danger(text)
        assert detected is True
        assert len(triggers) > 0

    def test_locked_accommodation_triggers(self):
        text = "The individual is locked in the house and cannot leave."
        detected, triggers = check_immediate_danger(text)
        assert detected is True

    def test_sexual_violence_triggers(self):
        text = "The individual reports being sexually assaulted by the employer."
        detected, triggers = check_immediate_danger(text)
        assert detected is True

    def test_explicit_threat_triggers(self):
        text = "Threatened to kill the individual if they attempt to leave."
        detected, triggers = check_immediate_danger(text)
        assert detected is True

    def test_no_false_positive_on_normal_employment(self):
        text = "The individual is employed as a factory worker and receives wages on time."
        detected, triggers = check_immediate_danger(text)
        assert detected is False
        assert len(triggers) == 0

    def test_no_false_positive_on_debt(self):
        text = "The individual incurred a recruitment fee of $3,000 and is repaying it monthly."
        detected, triggers = check_immediate_danger(text)
        assert detected is False

    def test_multiple_triggers_collected(self):
        text = "The individual was hit by the employer and is locked in the accommodation."
        detected, triggers = check_immediate_danger(text)
        assert detected is True
        assert len(triggers) >= 2

    def test_case_insensitive(self):
        text = "LOCKED IN THE HOUSE AND CANNOT LEAVE"
        detected, _ = check_immediate_danger(text)
        assert detected is True
