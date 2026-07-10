from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.config import PROCESSED_DIR, TABLES_DIR, ensure_directories


DEFAULT_MANUAL_TRIAGE_MINUTES = 5.0
DEFAULT_AI_ASSISTED_TRIAGE_MINUTES = 1.0
DEFAULT_HOURLY_COST_GBP = 18.0
DEFAULT_AI_ASSISTED_RATES = (0.0, 0.25, 0.50, 0.75)


def build_efficiency_scenarios(
    ticket_count: int,
    manual_triage_minutes: float = DEFAULT_MANUAL_TRIAGE_MINUTES,
    ai_assisted_triage_minutes: float = DEFAULT_AI_ASSISTED_TRIAGE_MINUTES,
    hourly_cost_gbp: float = DEFAULT_HOURLY_COST_GBP,
    ai_assisted_rates: tuple[float, ...] = DEFAULT_AI_ASSISTED_RATES,
) -> pd.DataFrame:
    """Build transparent time-and-cost scenarios without using model predictions."""
    if ticket_count < 0:
        raise ValueError("ticket_count must not be negative.")
    if manual_triage_minutes <= 0 or ai_assisted_triage_minutes < 0 or hourly_cost_gbp < 0:
        raise ValueError("Scenario assumptions must be non-negative, with manual triage above zero.")

    baseline_minutes = ticket_count * manual_triage_minutes
    rows = []
    for ai_assisted_rate in ai_assisted_rates:
        if not 0 <= ai_assisted_rate <= 1:
            raise ValueError("Each AI-assisted rate must be between 0 and 1.")

        ai_assisted_tickets = round(ticket_count * ai_assisted_rate)
        manual_only_tickets = ticket_count - ai_assisted_tickets
        estimated_minutes = (
            ai_assisted_tickets * ai_assisted_triage_minutes
            + manual_only_tickets * manual_triage_minutes
        )
        minutes_saved = baseline_minutes - estimated_minutes
        rows.append({
            "scenario": f"{ai_assisted_rate:.0%} AI-assisted triage",
            "ai_assisted_rate_assumption": ai_assisted_rate,
            "total_tickets": ticket_count,
            "ai_assisted_tickets": ai_assisted_tickets,
            "manual_only_tickets": manual_only_tickets,
            "baseline_triage_hours": baseline_minutes / 60,
            "estimated_triage_hours": estimated_minutes / 60,
            "estimated_hours_saved": minutes_saved / 60,
            "estimated_cost_saved_gbp": minutes_saved / 60 * hourly_cost_gbp,
            "manual_triage_minutes_assumption": manual_triage_minutes,
            "ai_assisted_triage_minutes_assumption": ai_assisted_triage_minutes,
            "hourly_cost_gbp_assumption": hourly_cost_gbp,
        })
    return pd.DataFrame(rows)


def export_efficiency_scenarios(
    cleaned_file: str | Path = PROCESSED_DIR / "tickets_cleaned.csv",
) -> pd.DataFrame:
    ensure_directories()
    ticket_count = len(pd.read_csv(cleaned_file))
    scenarios = build_efficiency_scenarios(ticket_count)
    scenarios.to_csv(TABLES_DIR / "operational_efficiency_scenarios.csv", index=False)

    assumptions = pd.DataFrame([
        {"assumption": "Manual triage time per ticket", "value": DEFAULT_MANUAL_TRIAGE_MINUTES, "unit": "minutes"},
        {"assumption": "AI-assisted triage time per ticket", "value": DEFAULT_AI_ASSISTED_TRIAGE_MINUTES, "unit": "minutes"},
        {"assumption": "Fully loaded support cost", "value": DEFAULT_HOURLY_COST_GBP, "unit": "GBP per hour"},
        {"assumption": "Dataset scope", "value": ticket_count, "unit": "English tickets"},
    ])
    assumptions.to_csv(TABLES_DIR / "operational_efficiency_assumptions.csv", index=False)
    return scenarios


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(PROCESSED_DIR / "tickets_cleaned.csv"))
    args = parser.parse_args()

    scenarios = export_efficiency_scenarios(args.input)
    print(f"Exported {len(scenarios)} operational efficiency scenarios.")


if __name__ == "__main__":
    main()
