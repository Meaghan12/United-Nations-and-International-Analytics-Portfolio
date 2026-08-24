"""
utils/display_helpers.py
========================
Streamlit display utilities for consistent UI formatting.
"""
from __future__ import annotations

import streamlit as st
from workflow.state import ROUTING_STATES
from referrals.categories import REFERRAL_CATEGORIES
from indicators.framework import INDICATOR_CATEGORIES


# ── Colour / semantic tokens ───────────────────────────────────────────────────

SEVERITY_COLORS = {
    "URGENT": "#C0392B",
    "HIGH": "#E67E22",
    "MODERATE": "#2980B9",
    "LOW": "#27AE60",
    "NONE": "#95A5A6",
}

ROUTING_COLORS = {
    "URGENT_REVIEW": "#C0392B",
    "PRIORITY_REVIEW": "#E67E22",
    "READY_FOR_REVIEW": "#2980B9",
    "NEED_INFO": "#F39C12",
    "OTHER_SUPPORT": "#8E44AD",
    "NO_ACTION_RECOMMENDED": "#7F8C8D",
    "HUMAN_OVERRIDE": "#27AE60",
    "REFERRED": "#27AE60",
}


def routing_badge(routing_state: str) -> str:
    """Return styled HTML badge for a routing state."""
    info = ROUTING_STATES.get(routing_state, {})
    label = info.get("label", routing_state)
    emoji = info.get("emoji", "⚪")
    color = ROUTING_COLORS.get(routing_state, "#7F8C8D")
    return (
        f'<span style="background-color:{color};color:white;padding:4px 12px;'
        f'border-radius:4px;font-weight:600;font-size:0.9rem;">'
        f'{emoji} {label}</span>'
    )


def severity_badge(severity: str) -> str:
    """Return styled HTML badge for severity level."""
    color = SEVERITY_COLORS.get(severity, "#95A5A6")
    return (
        f'<span style="background-color:{color};color:white;padding:3px 10px;'
        f'border-radius:4px;font-weight:600;font-size:0.85rem;">'
        f'{severity}</span>'
    )


def node_step_display(node_name: str, status: str = "pending") -> str:
    """Return a formatted workflow step indicator."""
    status_map = {
        "complete": ("✅", "#27AE60"),
        "active": ("⚙️", "#2980B9"),
        "pending": ("○", "#BDC3C7"),
        "skipped": ("—", "#BDC3C7"),
    }
    icon, color = status_map.get(status, ("○", "#BDC3C7"))
    label = node_name.replace("_", " ").title()
    return f'<span style="color:{color};font-weight:500;">{icon} {label}</span>'


def indicator_category_label(category_key: str) -> str:
    """Return human-readable label for an indicator category key."""
    return INDICATOR_CATEGORIES.get(category_key, {}).get("label", category_key.replace("_", " ").title())


def referral_label(referral_key: str) -> str:
    """Return human-readable label for a referral category key."""
    return REFERRAL_CATEGORIES.get(referral_key, {}).get("label", referral_key.replace("_", " ").title())
