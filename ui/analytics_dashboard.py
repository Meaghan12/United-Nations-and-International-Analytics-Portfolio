"""
ui/analytics_dashboard.py
==========================
Synthetic dataset analytics dashboard.

CLEARLY LABELED: SYNTHETIC DEMONSTRATION DATASET ONLY.
These figures are from 8 fictional cases and have no epidemiological meaning.
The dashboard exists to demonstrate programme analytics and monitoring capabilities.
"""
from __future__ import annotations

import json
import os

import streamlit as st

try:
    import plotly.graph_objects as go
    import plotly.express as px
    _plotly_available = True
except ImportError:
    _plotly_available = False


ROUTING_COLORS_MAP = {
    "URGENT_REVIEW": "#C0392B",
    "PRIORITY_REVIEW": "#E67E22",
    "READY_FOR_REVIEW": "#2980B9",
    "NEED_INFO": "#F39C12",
    "OTHER_SUPPORT": "#8E44AD",
    "NO_ACTION_RECOMMENDED": "#7F8C8D",
}

ROUTING_LABELS = {
    "URGENT_REVIEW": "Urgent Review",
    "PRIORITY_REVIEW": "Priority Review",
    "READY_FOR_REVIEW": "Ready for Review",
    "NEED_INFO": "Need Information",
    "OTHER_SUPPORT": "Other Support",
    "NO_ACTION_RECOMMENDED": "No Action Recommended",
}


def render_analytics_dashboard():
    """Renders the synthetic dataset analytics dashboard."""
    st.markdown("---")
    st.markdown("## 📊 Analytics Dashboard")

    st.error(
        "**⚠ SYNTHETIC DEMONSTRATION DATASET ONLY**\n\n"
        "All figures below are derived from 8 entirely fictional cases. "
        "They do not represent real caseloads, real populations, or real outcomes. "
        "This dashboard demonstrates programme analytics and monitoring capabilities "
        "that could be applied to real data in an operational context after "
        "appropriate validation, governance review, and expert oversight."
    )

    # Load analytics data
    analytics_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "synthetic_analytics.json"
    )
    try:
        with open(analytics_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        st.error("Analytics data file not found.")
        return

    # ── Summary statistics ─────────────────────────────────────────────────
    st.markdown("### Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Cases (Synthetic)", data.get("total_cases", 0))
    with col2:
        st.metric(
            "Avg. Indicators / Case",
            f"{data.get('average_indicators_per_case', 0):.1f}"
        )
    with col3:
        n_need_info = data.get("cases_requiring_additional_information", 0)
        total = data.get("total_cases", 1)
        st.metric("Requiring More Info", f"{n_need_info}/{total}")
    with col4:
        st.metric(
            "Demo Override Rate",
            f"{data.get('human_override_rate_demo', 0):.0%}"
        )

    if not _plotly_available:
        st.warning("Install plotly for interactive charts: `pip install plotly`")
        return

    st.markdown("---")

    # ── Two charts side by side ────────────────────────────────────────────
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("#### Cases by Routing State")
        routing_dist = data.get("routing_distribution", {})
        labels = [ROUTING_LABELS.get(k, k) for k in routing_dist.keys()]
        values = list(routing_dist.values())
        colors = [ROUTING_COLORS_MAP.get(k, "#95A5A6") for k in routing_dist.keys()]

        fig_pie = go.Figure(
            go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors),
                textinfo="label+value",
                hole=0.35,
            )
        )
        fig_pie.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=300,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        st.markdown("#### Severity Distribution")
        severity_dist = data.get("severity_distribution", {})
        sev_order = ["URGENT", "HIGH", "MODERATE", "LOW", "NONE"]
        sev_colors = ["#C0392B", "#E67E22", "#2980B9", "#27AE60", "#95A5A6"]
        sev_values = [severity_dist.get(s, 0) for s in sev_order]

        fig_sev = go.Figure(
            go.Bar(
                x=sev_order,
                y=sev_values,
                marker_color=sev_colors,
                text=sev_values,
                textposition="outside",
            )
        )
        fig_sev.update_layout(
            xaxis_title="Severity Level",
            yaxis_title="Number of Cases",
            margin=dict(t=10, b=40, l=40, r=10),
            height=300,
            plot_bgcolor="white",
            yaxis=dict(gridcolor="#F0F0F0"),
        )
        st.plotly_chart(fig_sev, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Most Frequently Observed Indicator Categories")

    indicator_freq = data.get("indicator_category_frequency", {})
    sorted_indicators = sorted(indicator_freq.items(), key=lambda x: x[1], reverse=True)
    ind_labels = [k.replace("_", " ").title() for k, v in sorted_indicators]
    ind_values = [v for k, v in sorted_indicators]

    fig_ind = go.Figure(
        go.Bar(
            x=ind_values,
            y=ind_labels,
            orientation="h",
            marker_color="#2980B9",
            text=ind_values,
            textposition="outside",
        )
    )
    fig_ind.update_layout(
        xaxis_title="Frequency (synthetic cases)",
        margin=dict(t=10, b=40, l=220, r=60),
        height=400,
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#F0F0F0"),
    )
    st.plotly_chart(fig_ind, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Referral Pathways Recommended")
    st.caption("Number of synthetic cases for which each referral pathway was suggested.")

    referral_freq = data.get("referral_categories_frequency", {})
    sorted_referrals = sorted(referral_freq.items(), key=lambda x: x[1], reverse=True)
    ref_labels = [k.replace("_", " ").title() for k, v in sorted_referrals]
    ref_values = [v for k, v in sorted_referrals]

    fig_ref = go.Figure(
        go.Bar(
            x=ref_values,
            y=ref_labels,
            orientation="h",
            marker_color="#8E44AD",
            text=ref_values,
            textposition="outside",
        )
    )
    fig_ref.update_layout(
        xaxis_title="Frequency (synthetic cases)",
        margin=dict(t=10, b=40, l=260, r=60),
        height=400,
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#F0F0F0"),
    )
    st.plotly_chart(fig_ref, use_container_width=True)

    st.caption(
        "In an operational context, this dashboard could support programme managers in "
        "monitoring caseload patterns, identifying resource needs, tracking human override rates, "
        "and reporting to funders — with appropriate governance and data protection frameworks in place."
    )
