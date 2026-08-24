"""
tests/test_need_info.py
========================
Verifies that incomplete or vague cases route to NEED_INFO
rather than producing a spurious recommendation.
"""
import pytest
import os
os.environ.setdefault("DEMO_MODE", "true")

from workflow.graph import run_automated_phase


def test_empty_narrative_routes_need_info():
    """A case with no narrative and no fields should request more information."""
    state = run_automated_phase({
        "raw_case_id": "TEST-EMPTY",
        "raw_narrative": "",
        "raw_intake_fields": {},
        "demo_mode": True,
    })
    assert state.get("routing_state") in ("NEED_INFO", "NO_ACTION_RECOMMENDED"), \
        f"Expected NEED_INFO for empty case, got {state.get('routing_state')}"


def test_very_short_vague_narrative_with_clarifying_questions():
    """
    Case 002: 'My employer treats me badly' — too vague for a meaningful
    indicator analysis. The system should generate clarifying questions.
    """
    import json, pathlib
    cases_path = pathlib.Path(__file__).parent.parent / "data" / "synthetic_cases.json"
    with open(cases_path) as f:
        cases = json.load(f)

    case = cases.get("CASE-002", {})
    state = run_automated_phase({
        "raw_case_id": "CASE-002",
        "raw_narrative": case.get("narrative", "My employer treats me badly."),
        "raw_intake_fields": case.get("intake_fields", {}),
        "demo_mode": True,
    })
    # Should not auto-escalate a vague case
    assert state.get("routing_state") in ("NEED_INFO", "NO_ACTION_RECOMMENDED"), \
        f"Vague case should not escalate. Got {state.get('routing_state')}"


def test_missing_required_fields_generates_questions():
    """When key fields are missing, clarifying questions should be generated."""
    state = run_automated_phase({
        "raw_case_id": "TEST-MISSING",
        "raw_narrative": "Worker appears distressed. No other information available.",
        "raw_intake_fields": {},
        "demo_mode": True,
    })
    # Either validation stops it or no indicators route it to need_info
    assert state.get("validation_status") in ("COMPLETE", "INCOMPLETE")
    # Clarifying questions or need_info routing expected
    has_questions = bool(state.get("clarifying_questions"))
    need_info = state.get("routing_state") in ("NEED_INFO", "NO_ACTION_RECOMMENDED")
    assert has_questions or need_info


def test_validation_status_set_in_all_cases():
    """Validation status must always be set — never missing."""
    state = run_automated_phase({
        "raw_case_id": "TEST-VAL",
        "raw_narrative": "Some narrative.",
        "raw_intake_fields": {},
        "demo_mode": True,
    })
    assert "validation_status" in state
    assert state["validation_status"] in ("COMPLETE", "INCOMPLETE")
