from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import PROCESSED_DIR, TABLES_DIR, TRUE_LABELS, ensure_directories
from src.efficiency_model import export_efficiency_scenarios
from src.evaluation import empirical_accuracy_by_category


def export_distribution_tables(cleaned_file: str | Path = PROCESSED_DIR / "tickets_cleaned.csv") -> None:
    ensure_directories()
    df = pd.read_csv(cleaned_file)
    for label_name, column in TRUE_LABELS.items():
        if column not in df.columns:
            continue
        table = (
            df[column]
            .fillna("missing")
            .value_counts()
            .rename_axis(label_name)
            .reset_index(name="ticket_count")
        )
        table["ticket_share"] = table["ticket_count"] / table["ticket_count"].sum()
        table.to_csv(TABLES_DIR / f"{label_name}_distribution.csv", index=False)


def export_routing_scenarios(
    predictions_file: str | Path = PROCESSED_DIR / "gemini_predictions.csv",
    minutes_manual_triage: float = 5.0,
    minutes_ai_review: float = 1.0,
    hourly_cost: float = 18.0,
) -> pd.DataFrame:
    ensure_directories()
    accuracy = empirical_accuracy_by_category(predictions_file)
    if accuracy.empty:
        return accuracy

    rows = []
    for threshold in [round(value / 100, 2) for value in range(50, 100, 5)]:
        auto_route = accuracy[accuracy["empirical_accuracy"] >= threshold]
        automated_tickets = int(auto_route["ticket_count"].sum())
        total_tickets = int(accuracy["ticket_count"].sum())
        automation_rate = automated_tickets / total_tickets if total_tickets else 0
        estimated_errors = int(
            (auto_route["ticket_count"] * (1 - auto_route["empirical_accuracy"])).sum()
        )
        manual_minutes_before = total_tickets * minutes_manual_triage
        manual_minutes_after = (
            automated_tickets * minutes_ai_review
            + (total_tickets - automated_tickets) * minutes_manual_triage
        )
        minutes_saved = manual_minutes_before - manual_minutes_after
        rows.append({
            "accuracy_threshold": threshold,
            "total_sample_tickets": total_tickets,
            "automated_tickets": automated_tickets,
            "automation_rate": automation_rate,
            "estimated_auto_route_errors": estimated_errors,
            "minutes_saved_sample": minutes_saved,
            "estimated_cost_saved_sample": minutes_saved / 60 * hourly_cost,
        })

    scenarios = pd.DataFrame(rows)
    scenarios.to_csv(TABLES_DIR / "routing_threshold_scenarios.csv", index=False)
    return scenarios


def export_root_cause_table(
    predictions_file: str | Path = PROCESSED_DIR / "gemini_predictions.csv",
) -> pd.DataFrame:
    ensure_directories()
    predictions = pd.read_csv(predictions_file)
    if "root_cause" not in predictions.columns:
        return pd.DataFrame()

    table = (
        predictions["root_cause"]
        .fillna("unknown")
        .astype(str)
        .str.strip()
        .str.lower()
        .value_counts()
        .rename_axis("root_cause")
        .reset_index(name="ticket_count")
    )
    table["ticket_share"] = table["ticket_count"] / table["ticket_count"].sum()
    table.to_csv(TABLES_DIR / "root_cause_distribution.csv", index=False)
    return table


def export_all_powerbi_tables() -> None:
    export_distribution_tables()
    export_efficiency_scenarios()
    predictions_file = PROCESSED_DIR / "gemini_predictions.csv"
    if predictions_file.exists():
        export_routing_scenarios(predictions_file)
        export_root_cause_table(predictions_file)
