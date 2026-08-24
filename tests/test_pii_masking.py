"""
tests/test_pii_masking.py
=========================
Tests for PII detection and masking.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.pii_patterns import mask_text, mask_fields


class TestPIIMasking:
    def test_name_masked(self):
        text = "The individual, Maria Santos, contacted the service."
        result = mask_text(text)
        assert "Maria Santos" not in result.masked_text
        assert "[NAME REDACTED]" in result.masked_text
        assert "PERSON_NAME" in result.redacted_item_types

    def test_email_masked(self):
        text = "Contact them at worker.anon@example.com for follow-up."
        result = mask_text(text)
        assert "worker.anon@example.com" not in result.masked_text
        assert "[EMAIL REDACTED]" in result.masked_text

    def test_pii_values_never_in_type_list(self):
        """Critical: redacted_item_types must contain TYPE labels, not values."""
        text = "Her name is Jane Doe and her number is 555-1234."
        result = mask_text(text)
        # Types should be generic labels, not the actual values
        for item_type in result.redacted_item_types:
            assert "Jane" not in item_type
            assert "Doe" not in item_type
            assert "555" not in item_type

    def test_empty_text_handled(self):
        result = mask_text("")
        assert result.masked_text == ""
        assert result.redacted_item_types == []

    def test_no_pii_no_redaction(self):
        text = "The individual works in agricultural employment and is concerned about wages."
        result = mask_text(text)
        # No PII patterns should match
        assert "[NAME REDACTED]" not in result.masked_text
        assert "[EMAIL REDACTED]" not in result.masked_text

    def test_mask_fields_dict(self):
        fields = {
            "employment_context": "Works for employer Maria Santos at the farm",
            "freedom_of_movement": "Cannot leave freely",
        }
        masked, pii_types = mask_fields(fields)
        assert "Maria Santos" not in masked["employment_context"]
        assert "Cannot leave freely" == masked["freedom_of_movement"]  # no PII here

    def test_non_string_fields_passed_through(self):
        fields = {"count": 5, "active": True, "narrative": "Normal text"}
        masked, _ = mask_fields(fields)
        assert masked["count"] == 5
        assert masked["active"] is True
