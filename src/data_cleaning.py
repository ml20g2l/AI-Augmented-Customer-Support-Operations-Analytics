from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.config import PROCESSED_DIR, TEXT_COLUMN, TRUE_LABELS, ensure_directories
from src.schema import TicketSchema, infer_schema


def load_raw_data(raw_file: str | Path) -> pd.DataFrame:
    raw_path = Path(raw_file)
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw file not found: {raw_path}")
    return pd.read_csv(raw_path)


def _is_english(value: object) -> bool:
    if pd.isna(value):
        return False
    text = str(value).strip().lower()
    return text in {"en", "eng", "english"}


def _build_ticket_text(df: pd.DataFrame, schema: TicketSchema) -> pd.Series:
    if not schema.text_columns:
        raise ValueError(
            "No ticket text column found. Expected one of: text, description, "
            "ticket_description, message, subject, or ticket_subject."
        )
    return (
        df[schema.text_columns]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


def clean_tickets(raw_file: str | Path) -> tuple[pd.DataFrame, dict]:
    ensure_directories()
    raw = load_raw_data(raw_file)
    schema = infer_schema(raw)

    df = raw.copy()
    starting_rows = len(df)

    if schema.language_column:
        df = df[df[schema.language_column].map(_is_english)].copy()

    rows_after_language_filter = len(df)
    df[TEXT_COLUMN] = _build_ticket_text(df, schema)
    df = df[df[TEXT_COLUMN].str.len() > 0].copy()
    rows_after_text_filter = len(df)

    duplicate_subset = [TEXT_COLUMN]
    if schema.id_column:
        duplicate_subset = [schema.id_column]
    df = df.drop_duplicates(subset=duplicate_subset).copy()

    if schema.id_column and schema.id_column != "ticket_id":
        df = df.rename(columns={schema.id_column: "ticket_id"})
    elif not schema.id_column:
        df.insert(0, "ticket_id", range(1, len(df) + 1))

    rename_map = {}
    if schema.category_column:
        rename_map[schema.category_column] = TRUE_LABELS["category"]
    if schema.priority_column:
        rename_map[schema.priority_column] = TRUE_LABELS["priority"]
    if schema.department_column:
        rename_map[schema.department_column] = TRUE_LABELS["department"]
    df = df.rename(columns=rename_map)

    for column in TRUE_LABELS.values():
        if column in df.columns:
            df[column] = df[column].astype(str).str.strip()

    summary = {
        "raw_file": str(raw_file),
        "starting_rows": int(starting_rows),
        "rows_after_language_filter": int(rows_after_language_filter),
        "rows_after_text_filter": int(rows_after_text_filter),
        "final_rows": int(len(df)),
        "removed_rows_total": int(starting_rows - len(df)),
        "detected_text_columns": schema.text_columns,
        "detected_language_column": schema.language_column,
        "detected_category_column": schema.category_column,
        "detected_priority_column": schema.priority_column,
        "detected_department_column": schema.department_column,
    }

    output_file = PROCESSED_DIR / "tickets_cleaned.csv"
    summary_file = PROCESSED_DIR / "cleaning_summary.json"
    df.to_csv(output_file, index=False)
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return df, summary
