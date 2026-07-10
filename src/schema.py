from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TicketSchema:
    text_columns: list[str]
    category_column: str | None
    priority_column: str | None
    department_column: str | None
    language_column: str | None
    id_column: str | None


TEXT_CANDIDATES = [
    "ticket_text",
    "text",
    "description",
    "ticket_description",
    "message",
    "body",
    "content",
    "issue",
    "summary",
    "subject",
    "ticket_subject",
]

CATEGORY_CANDIDATES = ["category", "ticket_category", "ticket_type", "type", "issue_category"]
PRIORITY_CANDIDATES = ["priority", "ticket_priority", "urgency"]
DEPARTMENT_CANDIDATES = ["department", "assigned_department", "team", "support_department", "queue"]
LANGUAGE_CANDIDATES = ["language", "lang", "ticket_language"]
ID_CANDIDATES = ["ticket_id", "id", "case_id", "request_id"]


def _normalise(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def _find_column(columns: list[str], candidates: list[str]) -> str | None:
    normalised = {_normalise(column): column for column in columns}
    for candidate in candidates:
        if candidate in normalised:
            return normalised[candidate]
    return None


def infer_schema(df: pd.DataFrame) -> TicketSchema:
    columns = list(df.columns)
    text_columns = [
        column
        for column in columns
        if _normalise(column) in TEXT_CANDIDATES
    ]

    subject = _find_column(columns, ["ticket_subject", "subject", "summary"])
    description = _find_column(columns, ["ticket_description", "description", "message", "body", "content"])
    combined = [column for column in [subject, description] if column and column not in text_columns]
    if combined:
        text_columns = combined + text_columns

    return TicketSchema(
        text_columns=text_columns,
        category_column=_find_column(columns, CATEGORY_CANDIDATES),
        priority_column=_find_column(columns, PRIORITY_CANDIDATES),
        department_column=_find_column(columns, DEPARTMENT_CANDIDATES),
        language_column=_find_column(columns, LANGUAGE_CANDIDATES),
        id_column=_find_column(columns, ID_CANDIDATES),
    )
