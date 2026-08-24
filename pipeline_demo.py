"""
pipeline_demo.py
================
Human Trafficking Risk & Referral Decision-Support System
— End-to-End Pipeline Demonstration —

Author: Meaghan Ryan

PURPOSE:
    This script runs all 8 synthetic cases through the complete LangGraph
    pipeline (without the Streamlit UI) and produces:

      1. Colour-coded console output showing each node executing per case
      2. A full indicator analysis summary per case
      3. Four matplotlib charts saved to output/ and displayed inline:
           a) Routing state distribution (pie)
           b) Indicator category frequency (horizontal bar)
           c) Severity distribution (bar)
           d) Per-case indicator heatmap (colour matrix)

    This file is intended to be opened in PyCharm or any Python IDE.
    Run it directly:  python pipeline_demo.py

    All data is SYNTHETIC FICTIONAL — no real individuals or cases.

REQUIREMENTS:
    pip install langgraph langchain-core python-dotenv matplotlib numpy
"""

import os
import sys
import json
import time
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

# ── External dependencies ─────────────────────────────────────────────────────
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠  matplotlib not installed — charts will be skipped.")
    print("   Run: pip install matplotlib numpy\n")

# ── Internal imports ──────────────────────────────────────────────────────────
from workflow.graph import run_automated_phase
from indicators.framework import INDICATOR_CATEGORIES
from referrals.categories import REFERRAL_CATEGORIES
from workflow.state import ROUTING_STATES
from utils.audit_log import public_audit_trail

# ── Output directory ──────────────────────────────────────────────────────────
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Terminal colour helpers ───────────────────────────────────────────────────
class C:
    """ANSI colour codes for terminal output."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    ORANGE  = "\033[93m"
    BLUE    = "\033[94m"
    GREEN   = "\033[92m"
    CYAN    = "\033[96m"
    GREY    = "\033[90m"
    PURPLE  = "\033[95m"
    YELLOW  = "\033[93m"
    WHITE   = "\033[97m"


ROUTING_COLOURS = {
    "URGENT_REVIEW":        C.RED,
    "PRIORITY_REVIEW":      C.ORANGE,
    "READY_FOR_REVIEW":     C.BLUE,
    "NEED_INFO":            C.YELLOW,
    "OTHER_SUPPORT":        C.PURPLE,
    "NO_ACTION_RECOMMENDED": C.GREY,
}

ROUTING_EMOJIS = {
    "URGENT_REVIEW":        "🔴",
    "PRIORITY_REVIEW":      "🟠",
    "READY_FOR_REVIEW":     "🔵",
    "NEED_INFO":            "🟡",
    "OTHER_SUPPORT":        "🟣",
    "NO_ACTION_RECOMMENDED": "⚪",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def print_header(text: str, width: int = 72):
    print(f"\n{C.BOLD}{C.WHITE}{'─' * width}")
    print(f"  {text}")
    print(f"{'─' * width}{C.RESET}\n")


def print_case_header(case_id: str, title: str, expected: str):
    print(f"\n{C.BOLD}{'━' * 72}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {case_id}  ·  {title}{C.RESET}")
    print(f"  Expected route: {ROUTING_EMOJIS.get(expected, '⚪')} {expected}")
    print(f"{C.BOLD}{'━' * 72}{C.RESET}")


def print_node_event(node: str, event: str):
    print(f"  {C.GREY}  ⟶ {node:<22}{C.RESET} {event}")


def print_routing_result(routing_state: str, rationale: str):
    colour = ROUTING_COLOURS.get(routing_state, C.GREY)
    emoji  = ROUTING_EMOJIS.get(routing_state, "⚪")
    label  = ROUTING_STATES.get(routing_state, {}).get("label", routing_state)
    print(f"\n  {colour}{C.BOLD}  {emoji}  ROUTING: {label}{C.RESET}")
    # Wrap rationale
    words = rationale.split()
    line = "     "
    for word in words:
        if len(line) + len(word) > 70:
            print(f"  {C.GREY}{line}{C.RESET}")
            line = "     " + word + " "
        else:
            line += word + " "
    if line.strip():
        print(f"  {C.GREY}{line}{C.RESET}")


def print_indicators(hits: list):
    if not hits:
        print(f"  {C.GREY}  No indicators identified.{C.RESET}")
        return
    for hit in hits:
        conf_colour = {
            "REPORTED": C.RED,
            "POSSIBLE": C.ORANGE,
            "INFERRED": C.YELLOW,
        }.get(hit["confidence"], C.GREY)
        source_label = hit["source"].replace("_", " ").title()
        print(
            f"  {conf_colour}  ◆ {hit['label']:<45}{C.RESET}"
            f"{C.GREY}[{hit['confidence']} · {source_label}]{C.RESET}"
        )


def print_audit_trail(audit_trail: list):
    print(f"\n  {C.BOLD}Execution Trace:{C.RESET}")
    for entry in public_audit_trail(audit_trail):
        ts   = entry.get("timestamp", "--:--:--")
        node = entry.get("node", "?").ljust(20)
        evt  = entry.get("event", "")
        print(f"  {C.GREY}  {ts}  |  {node}  |  {evt}{C.RESET}")


# ── Load synthetic cases ──────────────────────────────────────────────────────

def load_cases() -> dict:
    cases_path = ROOT / "data" / "synthetic_cases.json"
    with open(cases_path) as f:
        return json.load(f)


# ── Run a single case through the pipeline ────────────────────────────────────

def run_case(case_data: dict) -> dict:
    """
    Build initial state from a synthetic case dict and run the
    automated phase of the LangGraph pipeline.
    Returns the resulting CaseState dict.
    """
    initial_state = {
        "raw_case_id":       case_data["case_id"],
        "raw_narrative":     case_data["narrative"],
        "raw_intake_fields": case_data["intake_fields"],
        "demo_mode":         True,   # use pre-computed LLM responses
    }
    return run_automated_phase(initial_state)


# ── Chart 1: Routing distribution ─────────────────────────────────────────────

def chart_routing_distribution(results: list[dict]):
    """Pie chart of routing states across all 8 cases."""
    from collections import Counter

    counts = Counter(r["routing_state"] for r in results)
    labels = []
    sizes  = []
    colors = []

    colour_map = {
        "URGENT_REVIEW":        "#C0392B",
        "PRIORITY_REVIEW":      "#E67E22",
        "READY_FOR_REVIEW":     "#2980B9",
        "NEED_INFO":            "#F39C12",
        "OTHER_SUPPORT":        "#8E44AD",
        "NO_ACTION_RECOMMENDED": "#95A5A6",
    }

    for state, count in sorted(counts.items(), key=lambda x: -x[1]):
        label = ROUTING_STATES.get(state, {}).get("label", state)
        labels.append(f"{label}\n(n={count})")
        sizes.append(count)
        colors.append(colour_map.get(state, "#BDC3C7"))

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.0f%%",
        startangle=140,
        pctdistance=0.75,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
    )
    for text in texts:
        text.set_fontsize(9)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    ax.set_title(
        "Case Routing Distribution\n(Synthetic Demonstration Dataset — n=8)",
        fontsize=13, fontweight="bold", pad=20
    )
    fig.text(
        0.5, 0.01,
        "SYNTHETIC DATA ONLY · Not real case statistics",
        ha="center", fontsize=8, color="#95A5A6", style="italic"
    )
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_routing_distribution.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"  ✅ Saved: {out}")
    plt.show()
    plt.close()


# ── Chart 2: Indicator category frequency ─────────────────────────────────────

def chart_indicator_frequency(results: list[dict]):
    """Horizontal bar chart of how often each indicator category appeared."""
    from collections import Counter

    category_counts: Counter = Counter()
    for r in results:
        for hit in r.get("indicator_hits", []):
            category_counts[hit["category"]] += 1

    sorted_cats = sorted(
        INDICATOR_CATEGORIES.keys(),
        key=lambda c: category_counts.get(c, 0),
        reverse=True,
    )
    labels = [INDICATOR_CATEGORIES[c]["label"] for c in sorted_cats]
    values = [category_counts.get(c, 0) for c in sorted_cats]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(labels, values, color="#2980B9", edgecolor="white")

    # Colour bars by value
    max_val = max(values) if values else 1
    for bar, val in zip(bars, values):
        intensity = 0.3 + 0.7 * (val / max_val)
        bar.set_color(plt.cm.Blues(intensity))
        if val > 0:
            ax.text(
                val + 0.05, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=9, color="#2C3E50"
            )

    ax.set_xlabel("Frequency (number of synthetic cases)", fontsize=10)
    ax.set_title(
        "Indicator Category Frequency\n(Synthetic Demonstration Dataset — n=8 cases)",
        fontsize=13, fontweight="bold"
    )
    ax.set_xlim(0, max_val + 1)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor("#FAFAFA")
    fig.text(
        0.5, 0.01,
        "SYNTHETIC DATA ONLY · Not real indicator prevalence data",
        ha="center", fontsize=8, color="#95A5A6", style="italic"
    )
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_indicator_frequency.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"  ✅ Saved: {out}")
    plt.show()
    plt.close()


# ── Chart 3: Severity distribution ────────────────────────────────────────────

def chart_severity_distribution(results: list[dict]):
    """Bar chart of severity levels across all cases."""
    from collections import Counter

    severity_order  = ["URGENT", "HIGH", "MODERATE", "LOW", "NONE"]
    severity_colors = ["#C0392B", "#E67E22", "#2980B9", "#27AE60", "#95A5A6"]
    counts = Counter(r.get("indicator_severity", "NONE") for r in results)
    values = [counts.get(s, 0) for s in severity_order]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(severity_order, values, color=severity_colors, edgecolor="white", linewidth=1.5)
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
            str(val), ha="center", va="bottom", fontsize=11, fontweight="bold",
            color="#2C3E50"
        )

    ax.set_ylabel("Number of Cases", fontsize=10)
    ax.set_title(
        "Severity Level Distribution\n(Categorical — No Numerical Scores Generated)",
        fontsize=12, fontweight="bold"
    )
    ax.set_ylim(0, max(values) + 1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_facecolor("#FAFAFA")
    fig.text(
        0.5, 0.01,
        "SYNTHETIC DATA ONLY · Severity is categorical only — not a probability score",
        ha="center", fontsize=8, color="#95A5A6", style="italic"
    )
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_severity_distribution.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"  ✅ Saved: {out}")
    plt.show()
    plt.close()


# ── Chart 4: Per-case indicator heatmap ───────────────────────────────────────

def chart_indicator_heatmap(cases: dict, results: list[dict]):
    """
    Colour matrix: rows = indicator categories, columns = cases.
    Cell colour indicates whether indicator was detected in that case.
    Source is encoded by colour intensity:
      - structured_field: darkest
      - narrative_extraction: medium
      - llm_extracted: lighter
    """
    case_ids = [r["raw_case_id"] for r in results]
    category_keys = list(INDICATOR_CATEGORIES.keys())
    category_labels = [INDICATOR_CATEGORIES[k]["label"] for k in category_keys]

    # Build presence matrix (0=absent, 1=llm, 2=narrative, 3=field)
    source_rank = {"llm_extracted": 1, "narrative_extraction": 2, "structured_field": 3}
    matrix = np.zeros((len(category_keys), len(case_ids)), dtype=int)

    for col, result in enumerate(results):
        for hit in result.get("indicator_hits", []):
            if hit["category"] in category_keys:
                row = category_keys.index(hit["category"])
                rank = source_rank.get(hit["source"], 1)
                matrix[row, col] = max(matrix[row, col], rank)

    # Short case labels
    case_labels = [cid.replace("CASE-", "C") for cid in case_ids]

    fig, ax = plt.subplots(figsize=(11, 7))

    # Custom colormap: white → light blue → medium blue → dark blue
    cmap = plt.cm.Blues
    img = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0, vmax=3)

    ax.set_xticks(range(len(case_ids)))
    ax.set_xticklabels(case_labels, fontsize=9)
    ax.set_yticks(range(len(category_keys)))
    ax.set_yticklabels(category_labels, fontsize=8)

    # Add routing state annotation on top
    routing_short = {
        "URGENT_REVIEW": "URGENT",
        "PRIORITY_REVIEW": "PRIORITY",
        "READY_FOR_REVIEW": "READY",
        "NEED_INFO": "NEED INFO",
        "OTHER_SUPPORT": "OTHER",
        "NO_ACTION_RECOMMENDED": "NO ACTION",
    }
    for col, result in enumerate(results):
        rs = result.get("routing_state", "")
        label = routing_short.get(rs, rs)
        colour_map_txt = {
            "URGENT_REVIEW": "#C0392B",
            "PRIORITY_REVIEW": "#E67E22",
            "READY_FOR_REVIEW": "#2980B9",
            "NEED_INFO": "#F39C12",
            "OTHER_SUPPORT": "#8E44AD",
            "NO_ACTION_RECOMMENDED": "#95A5A6",
        }
        ax.text(
            col, -0.7, label,
            ha="center", va="bottom", fontsize=7, fontweight="bold",
            color=colour_map_txt.get(rs, "#2C3E50"), rotation=30
        )

    # Grid lines
    ax.set_xticks(np.arange(-0.5, len(case_ids), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(category_keys), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    # Legend
    patches = [
        mpatches.Patch(color=cmap(0.0), label="Not detected"),
        mpatches.Patch(color=cmap(0.35), label="LLM extracted"),
        mpatches.Patch(color=cmap(0.65), label="Narrative keyword"),
        mpatches.Patch(color=cmap(0.95), label="Structured field"),
    ]
    ax.legend(
        handles=patches, loc="lower right", fontsize=8,
        bbox_to_anchor=(1.0, -0.25), ncol=4, frameon=False
    )

    ax.set_title(
        "Per-Case Indicator Detection Matrix\n(Synthetic Demonstration Dataset)",
        fontsize=12, fontweight="bold", pad=25
    )
    ax.set_xlabel("Case", fontsize=10, labelpad=10)
    ax.set_ylabel("Indicator Category", fontsize=10)

    fig.text(
        0.5, -0.03,
        "SYNTHETIC DATA ONLY · Colour intensity = detection source confidence",
        ha="center", fontsize=8, color="#95A5A6", style="italic"
    )
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_indicator_heatmap.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"  ✅ Saved: {out}")
    plt.show()
    plt.close()


# ── Main demo runner ──────────────────────────────────────────────────────────

def main():
    print(f"\n{C.BOLD}{C.WHITE}")
    print("  ╔══════════════════════════════════════════════════════════════════╗")
    print("  ║  Human Trafficking Risk & Referral Decision-Support System       ║")
    print("  ║  Pipeline Demonstration — End-to-End Run                         ║")
    print("  ║  Author: Meaghan Ryan · Synthetic Demonstration Data Only        ║")
    print("  ╚══════════════════════════════════════════════════════════════════╝")
    print(f"{C.RESET}")

    cases = load_cases()
    results = []

    print_header("PHASE 1 — RUNNING ALL 8 SYNTHETIC CASES THROUGH PIPELINE")

    for case_id, case_data in cases.items():
        print_case_header(case_id, case_data["title"], case_data["expected_routing"])

        # Run pipeline
        t0 = time.time()
        state = run_case(case_data)
        elapsed = time.time() - t0

        # Show audit trail (node sequence)
        audit = state.get("audit_trail", [])
        for entry in public_audit_trail(audit):
            print_node_event(entry["node"], entry["event"])

        # PII masking result
        pii_types = state.get("pii_redacted_items", [])
        if pii_types:
            print(f"\n  {C.GREEN}🔒 PII masked: {', '.join(pii_types)}{C.RESET}")
        else:
            print(f"\n  {C.GREY}🔒 PII check: no direct identifiers detected in text{C.RESET}")

        # Indicators
        hits = state.get("indicator_hits", [])
        severity = state.get("indicator_severity", "NONE")
        print(f"\n  {C.BOLD}Indicators detected ({len(hits)}) · Severity: {severity}{C.RESET}")
        print_indicators(hits)

        # Routing
        routing_state = state.get("routing_state", "UNKNOWN")
        routing_rationale = state.get("routing_rationale", "")
        print_routing_result(routing_state, routing_rationale)

        # Validation check
        expected = case_data["expected_routing"]
        match_symbol = "✅" if routing_state == expected else "⚠️ "
        print(
            f"\n  {match_symbol}  Routed to {routing_state} "
            f"(expected: {expected}) — {elapsed:.2f}s"
        )

        state["raw_case_id"] = case_id  # ensure ID is preserved for charts
        results.append(state)

    # ── Summary table ─────────────────────────────────────────────────────────
    print_header("PHASE 2 — PIPELINE SUMMARY TABLE")
    print(f"  {'CASE':<12} {'TITLE':<42} {'ROUTING':<25} {'INDICATORS'}")
    print(f"  {'─'*12} {'─'*42} {'─'*25} {'─'*10}")
    for case_id, case_data in cases.items():
        result = next((r for r in results if r.get("raw_case_id") == case_id), {})
        routing = result.get("routing_state", "?")
        n_hits  = len(result.get("indicator_hits", []))
        severity = result.get("indicator_severity", "?")
        colour  = ROUTING_COLOURS.get(routing, C.GREY)
        title_short = case_data["title"][:41]
        print(
            f"  {case_id:<12} {title_short:<42} "
            f"{colour}{routing:<25}{C.RESET} {n_hits} ({severity})"
        )

    # ── Architecture notes ────────────────────────────────────────────────────
    print_header("PHASE 3 — ARCHITECTURE NOTES")
    print(f"  {C.BOLD}LangGraph nodes executed per case:{C.RESET}")
    print(f"  intake → pii_mask → safety_check → validate →")
    print(f"  indicator_analysis → evidence_review → referral_options → human_review")
    print()
    print(f"  {C.BOLD}LLM calls:{C.RESET}")
    print(f"  • indicator_analysis : extraction only (masked text, JSON output, temp=0)")
    print(f"  • evidence_review    : synthesis only (hedged language, prohibited terms filtered)")
    print(f"  • All routing        : deterministic Python — NO LLM involvement")
    print()
    print(f"  {C.BOLD}Key safeguards active:{C.RESET}")
    print(f"  ✅ Protected characteristics guard — validate_no_protected_characteristics()")
    print(f"  ✅ PII masking before every LLM call")
    print(f"  ✅ Post-generation prohibited-term sanitization in evidence_review")
    print(f"  ✅ HITL gate cannot be bypassed (hitl_complete=False until reviewer submits)")
    print(f"  ✅ Categorical severity labels only — no numerical risk scores")

    # ── Charts ────────────────────────────────────────────────────────────────
    if MATPLOTLIB_AVAILABLE:
        print_header("PHASE 4 — GENERATING CHARTS")

        print(f"\n  Chart 1/4: Routing Distribution")
        chart_routing_distribution(results)

        print(f"\n  Chart 2/4: Indicator Category Frequency")
        chart_indicator_frequency(results)

        print(f"\n  Chart 3/4: Severity Distribution")
        chart_severity_distribution(results)

        print(f"\n  Chart 4/4: Per-Case Indicator Heatmap")
        chart_indicator_heatmap(cases, results)

        print(f"\n  {C.GREEN}{C.BOLD}All charts saved to: {OUTPUT_DIR}/{C.RESET}")

    # ── Final footer ──────────────────────────────────────────────────────────
    print(f"\n{C.BOLD}{C.WHITE}")
    print("  ┌──────────────────────────────────────────────────────────────────┐")
    print("  │  Pipeline demo complete.                                         │")
    print("  │  All cases use SYNTHETIC FICTIONAL data only.                    │")
    print("  │  This is a portfolio prototype — not an operational system.      │")
    print("  └──────────────────────────────────────────────────────────────────┘")
    print(f"{C.RESET}\n")


if __name__ == "__main__":
    main()
