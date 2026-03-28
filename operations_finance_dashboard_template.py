"""
Operations Finance Executive Dashboard Template

Reusable template for decision-oriented executive reporting with placeholder
structures for budget, actuals, operational metrics, and revenue/profitability.

Dependencies:
    - pandas
    - matplotlib

Usage:
    python operations_finance_dashboard_template.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd


# -----------------------------
# 1) Placeholder input datasets
# -----------------------------
# Replace these with your actual data pipelines / ERP exports / BI extracts.
# Keep column names to preserve compatibility with the calculations below.

# Budget vs actual financials by business unit/category/period.
# BUDGET DATA GOES HERE: columns like planned spend, planned revenue, planned profit.
# ACTUAL COST DATA GOES HERE: columns like actual spend, actual revenue, actual profit.
def load_placeholder_finance_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "period": ["P1", "P1", "P1", "P2", "P2", "P2"],
            "business_unit": ["Unit_A", "Unit_B", "Unit_C", "Unit_A", "Unit_B", "Unit_C"],
            "opex_budget": [120_000, 95_000, 88_000, 130_000, 97_000, 90_000],
            "opex_actual": [125_500, 90_500, 92_200, 128_800, 101_300, 91_100],
            "revenue_budget": [250_000, 180_000, 140_000, 260_000, 185_000, 145_000],
            "revenue_actual": [248_400, 176_500, 149_200, 272_200, 188_500, 142_800],
            "gross_profit_actual": [98_200, 72_000, 59_800, 112_900, 75_500, 56_400],
            "operating_profit_actual": [52_700, 38_600, 27_900, 59_800, 40_100, 24_500],
        }
    )


# Operational metric placeholders.
# OPERATIONAL METRICS GO HERE: planned throughput/utilization/service-level and actual values.
def load_placeholder_operational_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "period": ["P1", "P2", "P3", "P4"],
            "planned_operational_rate": [0.88, 0.90, 0.92, 0.91],
            "actual_operational_rate": [0.84, 0.89, 0.86, 0.93],
            "planned_cycle_time_min": [48, 47, 46, 46],
            "actual_cycle_time_min": [50, 48, 49, 45],
        }
    )


# Risk threshold configuration placeholders.
# EARLY WARNING THRESHOLDS GO HERE: values can be tuned by leadership policy.
def load_placeholder_thresholds() -> Dict[str, float]:
    return {
        "max_opex_variance_pct": 0.05,           # Alert if OPEX actual exceeds budget by >5%
        "min_operating_margin_pct": 0.12,        # Alert if operating margin falls below 12%
        "min_operational_rate_attainment": 0.95, # Alert if actual/planned operational rate <95%
    }


@dataclass
class DashboardOutputs:
    kpi_table: pd.DataFrame
    opex_variance_detail: pd.DataFrame
    profitability_detail: pd.DataFrame
    revenue_contribution: pd.DataFrame
    operational_efficiency: pd.DataFrame
    warnings: List[str]


# -----------------------------
# 2) KPI calculation engine
# -----------------------------
def calculate_dashboard_kpis(
    finance_df: pd.DataFrame,
    operations_df: pd.DataFrame,
    thresholds: Dict[str, float],
) -> DashboardOutputs:
    df = finance_df.copy()

    # --- Core KPI formulas ---
    # Budget variance (€) = Actual - Budget
    df["opex_variance_eur"] = df["opex_actual"] - df["opex_budget"]

    # Budget variance (%) = (Actual - Budget) / Budget
    df["opex_variance_pct"] = df["opex_variance_eur"] / df["opex_budget"]

    # Margin % (gross) = Gross profit / Revenue actual
    df["gross_margin_pct"] = df["gross_profit_actual"] / df["revenue_actual"]

    # Margin % (operating) = Operating profit / Revenue actual
    df["operating_margin_pct"] = df["operating_profit_actual"] / df["revenue_actual"]

    # Revenue contribution % = Unit revenue actual / Total revenue actual
    total_revenue_actual = df["revenue_actual"].sum()
    df["revenue_contribution_pct"] = df["revenue_actual"] / total_revenue_actual

    # Aggregate KPI card dataset.
    kpi_table = pd.DataFrame(
        {
            "kpi": [
                "Total Budget (OPEX)",
                "Total Actual (OPEX)",
                "Budget Variance (€)",
                "Budget Variance (%)",
                "Total Gross Profit",
                "Total Operating Profit",
                "Gross Margin %",
                "Operating Margin %",
            ],
            "value": [
                df["opex_budget"].sum(),
                df["opex_actual"].sum(),
                df["opex_variance_eur"].sum(),
                df["opex_variance_eur"].sum() / df["opex_budget"].sum(),
                df["gross_profit_actual"].sum(),
                df["operating_profit_actual"].sum(),
                df["gross_profit_actual"].sum() / total_revenue_actual,
                df["operating_profit_actual"].sum() / total_revenue_actual,
            ],
        }
    )

    # OPEX variance analysis table (management drill-down).
    opex_variance_detail = (
        df.groupby(["period", "business_unit"], as_index=False)
        .agg(
            opex_budget=("opex_budget", "sum"),
            opex_actual=("opex_actual", "sum"),
            opex_variance_eur=("opex_variance_eur", "sum"),
            opex_variance_pct=("opex_variance_pct", "mean"),
        )
        .sort_values(["period", "opex_variance_eur"], ascending=[True, False])
    )

    # Profitability analysis table.
    profitability_detail = (
        df.groupby(["period", "business_unit"], as_index=False)
        .agg(
            revenue_actual=("revenue_actual", "sum"),
            gross_profit_actual=("gross_profit_actual", "sum"),
            operating_profit_actual=("operating_profit_actual", "sum"),
        )
    )
    profitability_detail["gross_margin_pct"] = (
        profitability_detail["gross_profit_actual"] / profitability_detail["revenue_actual"]
    )
    profitability_detail["operating_margin_pct"] = (
        profitability_detail["operating_profit_actual"]
        / profitability_detail["revenue_actual"]
    )

    # Revenue summary with contribution.
    revenue_contribution = (
        df.groupby("business_unit", as_index=False)
        .agg(
            revenue_budget=("revenue_budget", "sum"),
            revenue_actual=("revenue_actual", "sum"),
        )
        .sort_values("revenue_actual", ascending=False)
    )
    revenue_contribution["revenue_variance_eur"] = (
        revenue_contribution["revenue_actual"] - revenue_contribution["revenue_budget"]
    )
    revenue_contribution["revenue_contribution_pct"] = (
        revenue_contribution["revenue_actual"] / revenue_contribution["revenue_actual"].sum()
    )

    # Operational efficiency analysis.
    operational_efficiency = operations_df.copy()

    # Actual vs planned operational rate = actual_rate / planned_rate
    operational_efficiency["operational_rate_attainment"] = (
        operational_efficiency["actual_operational_rate"]
        / operational_efficiency["planned_operational_rate"]
    )

    # Early warning signal logic.
    warnings: List[str] = []

    if (df["opex_variance_pct"] > thresholds["max_opex_variance_pct"]).any():
        warnings.append(
            "OPEX variance exceeded threshold in at least one business unit/period."
        )

    if (profitability_detail["operating_margin_pct"] < thresholds["min_operating_margin_pct"]).any():
        warnings.append(
            "Operating margin dropped below minimum threshold in at least one segment."
        )

    if (
        operational_efficiency["operational_rate_attainment"]
        < thresholds["min_operational_rate_attainment"]
    ).any():
        warnings.append(
            "Operational rate attainment below threshold in at least one period."
        )

    return DashboardOutputs(
        kpi_table=kpi_table,
        opex_variance_detail=opex_variance_detail,
        profitability_detail=profitability_detail,
        revenue_contribution=revenue_contribution,
        operational_efficiency=operational_efficiency,
        warnings=warnings,
    )


# -----------------------------
# 3) Dashboard rendering
# -----------------------------
def render_dashboard(outputs: DashboardOutputs) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle("Operations Finance Executive Dashboard (Template)", fontsize=15)

    # KPI Cards (visualized as bar chart for template simplicity)
    kpis_to_plot = outputs.kpi_table.head(6)
    axes[0, 0].bar(kpis_to_plot["kpi"], kpis_to_plot["value"])
    axes[0, 0].set_title("KPI Cards")
    axes[0, 0].tick_params(axis="x", rotation=40)

    # OPEX variance analysis
    opex_plot = (
        outputs.opex_variance_detail.groupby("business_unit", as_index=False)["opex_variance_eur"].sum()
    )
    axes[0, 1].bar(opex_plot["business_unit"], opex_plot["opex_variance_eur"])
    axes[0, 1].set_title("OPEX Variance Analysis (€)")

    # Profitability analysis (operating margin by unit)
    profit_plot = (
        outputs.profitability_detail.groupby("business_unit", as_index=False)["operating_margin_pct"].mean()
    )
    axes[1, 0].plot(profit_plot["business_unit"], profit_plot["operating_margin_pct"], marker="o")
    axes[1, 0].set_title("Profitability Analysis (Operating Margin %) ")

    # Operational efficiency: actual vs planned rate
    ops_plot = outputs.operational_efficiency
    axes[1, 1].plot(ops_plot["period"], ops_plot["planned_operational_rate"], label="Planned")
    axes[1, 1].plot(ops_plot["period"], ops_plot["actual_operational_rate"], label="Actual")
    axes[1, 1].set_title("Operational Efficiency (Actual vs Planned)")
    axes[1, 1].legend()

    plt.tight_layout()
    plt.show()


# -----------------------------
# 4) Executive summary builder
# -----------------------------
def generate_executive_summary(outputs: DashboardOutputs) -> str:
    total_opex_variance = float(
        outputs.kpi_table.loc[
            outputs.kpi_table["kpi"] == "Budget Variance (€)", "value"
        ].iloc[0]
    )
    operating_margin = float(
        outputs.kpi_table.loc[
            outputs.kpi_table["kpi"] == "Operating Margin %", "value"
        ].iloc[0]
    )

    risk_text = (
        " | ".join(outputs.warnings)
        if outputs.warnings
        else "No threshold breaches detected in current template data."
    )

    return (
        "Executive Summary:\n"
        f"- Current OPEX variance totals: {total_opex_variance:,.2f}.\n"
        f"- Current operating margin: {operating_margin:.2%}.\n"
        "- Revenue and profitability should be reviewed by business unit contribution table.\n"
        f"- Early warning signals: {risk_text}"
    )


# -----------------------------
# 5) Script entry point
# -----------------------------
def main() -> None:
    finance_df = load_placeholder_finance_data()
    operations_df = load_placeholder_operational_data()
    thresholds = load_placeholder_thresholds()

    outputs = calculate_dashboard_kpis(finance_df, operations_df, thresholds)

    print(generate_executive_summary(outputs))
    print("\n=== KPI TABLE ===")
    print(outputs.kpi_table)
    print("\n=== REVENUE SUMMARY ===")
    print(outputs.revenue_contribution)
    print("\n=== RISK / EARLY WARNING SIGNALS ===")
    print(outputs.warnings if outputs.warnings else "No warnings")

    render_dashboard(outputs)


if __name__ == "__main__":
    main()
