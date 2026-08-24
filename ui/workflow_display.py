"""
ui/workflow_display.py
======================
Workflow node-by-node progress visualization.
"""
from __future__ import annotations

import streamlit as st

WORKFLOW_NODES = [
    ("intake", "Intake"),
    ("pii_mask", "PII Mask"),
    ("safety_check", "Safety Check"),
    ("validate", "Validate"),
    ("indicator_analysis", "Indicator Analysis"),
    ("evidence_review", "Evidence Review"),
    ("referral_options", "Referral Options"),
    ("human_review", "Human Review ★"),
    ("finalize", "Finalize"),
    ("audit", "Audit"),
]


def render_workflow_progress(completed_nodes: list[str], active_node: str | None = None):
    """
    Renders the workflow progress bar showing which nodes have completed.

    Args:
        completed_nodes: List of node names that have finished processing.
        active_node: The currently active node name (if any).
    """
    st.markdown("#### Workflow Path")

    node_cols = st.columns(len(WORKFLOW_NODES))

    for i, (node_key, node_label) in enumerate(WORKFLOW_NODES):
        with node_cols[i]:
            if node_key in completed_nodes:
                st.markdown(
                    f"<div style='text-align:center;padding:6px 2px;background:#EBF5FB;"
                    f"border-radius:6px;border:1px solid #2980B9;'>"
                    f"<span style='color:#2980B9;font-size:1.1rem;'>✅</span><br>"
                    f"<span style='font-size:0.65rem;color:#2C3E50;font-weight:600;'>{node_label}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            elif node_key == active_node:
                st.markdown(
                    f"<div style='text-align:center;padding:6px 2px;background:#FEF9E7;"
                    f"border-radius:6px;border:2px solid #F39C12;'>"
                    f"<span style='font-size:1.1rem;'>⚙️</span><br>"
                    f"<span style='font-size:0.65rem;color:#E67E22;font-weight:700;'>{node_label}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='text-align:center;padding:6px 2px;background:#F8F9FA;"
                    f"border-radius:6px;border:1px solid #DEE2E6;'>"
                    f"<span style='font-size:1.1rem;color:#BDC3C7;'>○</span><br>"
                    f"<span style='font-size:0.65rem;color:#95A5A6;'>{node_label}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
