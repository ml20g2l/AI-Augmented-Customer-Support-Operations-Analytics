from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai
from tqdm import tqdm

from src.config import (
    FREE_TIER_MAX_REQUESTS,
    FREE_TIER_MODEL,
    PROCESSED_DIR,
    TEXT_COLUMN,
    TRUE_LABELS,
    ensure_directories,
)


PROMPT_TEMPLATE = """
You are classifying customer support tickets for an operations analytics project.

Return only valid JSON with this schema:
{{
  "category": "one allowed category value exactly",
  "priority": "one allowed priority value exactly",
  "department": "one allowed department value exactly",
  "confidence": 0.0,
  "root_cause": "short recurring issue label"
}}

Ticket:
{ticket_text}

Allowed category values: {category_options}
Allowed priority values: {priority_options}
Allowed department values: {department_options}
""".strip()


def _extract_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model response: {text[:200]}")
    return json.loads(cleaned[start:end + 1])


def classify_ticket(
    client: genai.Client,
    model: str,
    ticket_text: str,
    category_options: list[str],
    priority_options: list[str],
    department_options: list[str],
) -> dict:
    response = client.models.generate_content(
        model=model,
        contents=PROMPT_TEMPLATE.format(
            ticket_text=ticket_text[:5000],
            category_options=json.dumps(category_options),
            priority_options=json.dumps(priority_options),
            department_options=json.dumps(department_options),
        ),
    )
    parsed = _extract_json(response.text or "")
    return {
        "predicted_category": parsed.get("category"),
        "predicted_priority": parsed.get("priority"),
        "predicted_department": parsed.get("department"),
        "llm_confidence": parsed.get("confidence"),
        "root_cause": parsed.get("root_cause"),
    }


def _validate_free_tier_settings(model: str, sample_size: int) -> None:
    """Prevent accidental use of a paid model or an oversized free-tier run."""
    if os.getenv("GEMINI_FREE_TIER_ONLY", "").strip().lower() != "true":
        raise EnvironmentError(
            "Set GEMINI_FREE_TIER_ONLY=true only after confirming that the API key belongs "
            "to a Free Tier project in Google AI Studio."
        )
    if model != FREE_TIER_MODEL:
        raise ValueError(
            f"This project is restricted to the free-tier model {FREE_TIER_MODEL!r}."
        )
    if sample_size > FREE_TIER_MAX_REQUESTS:
        raise ValueError(
            f"Free-tier runs are capped at {FREE_TIER_MAX_REQUESTS} tickets; received {sample_size}."
        )


def classify_sample(
    input_file: str | Path = PROCESSED_DIR / "classification_sample.csv",
    output_file: str | Path = PROCESSED_DIR / "gemini_predictions.csv",
    model: str = FREE_TIER_MODEL,
    sleep_seconds: float = 4.0,
    max_tickets: int | None = None,
) -> pd.DataFrame:
    ensure_directories()
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("Set GEMINI_API_KEY or GOOGLE_API_KEY before running Gemini classification.")

    sample = pd.read_csv(input_file)
    if TEXT_COLUMN not in sample.columns:
        raise ValueError(f"Input file must contain {TEXT_COLUMN!r}.")
    _validate_free_tier_settings(model, len(sample))
    output_path = Path(output_file)

    existing_predictions = pd.DataFrame()
    if output_path.exists():
        existing_predictions = pd.read_csv(output_path)
        if "ticket_id" not in existing_predictions.columns:
            raise ValueError("Existing prediction file must contain 'ticket_id' to resume safely.")
        if "classification_error" in existing_predictions.columns:
            existing_predictions = existing_predictions[
                existing_predictions["classification_error"].isna()
                | existing_predictions["classification_error"].astype(str).str.strip().eq("")
            ].copy()

    completed_ids = set(existing_predictions.get("ticket_id", pd.Series(dtype=object)).dropna())
    pending = sample[~sample["ticket_id"].isin(completed_ids)].copy()
    if max_tickets is not None:
        pending = pending.head(max_tickets).copy()

    category_options = sorted(sample[TRUE_LABELS["category"]].dropna().astype(str).unique())
    priority_options = sorted(sample[TRUE_LABELS["priority"]].dropna().astype(str).unique())
    department_options = sorted(sample[TRUE_LABELS["department"]].dropna().astype(str).unique())

    client = genai.Client(api_key=api_key)
    rows = existing_predictions.to_dict(orient="records")

    for _, row in tqdm(pending.iterrows(), total=len(pending), desc="Classifying tickets"):
        try:
            prediction = classify_ticket(
                client,
                model,
                str(row[TEXT_COLUMN]),
                category_options,
                priority_options,
                department_options,
            )
            prediction["classification_error"] = None
        except Exception as exc:
            prediction = {
                "predicted_category": None,
                "predicted_priority": None,
                "predicted_department": None,
                "llm_confidence": None,
                "root_cause": None,
                "classification_error": str(exc),
            }
        rows.append({**row.to_dict(), **prediction})
        pd.DataFrame(rows).to_csv(output_path, index=False)
        if sleep_seconds:
            time.sleep(sleep_seconds)

    predictions = pd.DataFrame(rows)
    predictions.to_csv(output_path, index=False)
    return predictions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(PROCESSED_DIR / "classification_sample.csv"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / "gemini_predictions.csv"))
    parser.add_argument("--model", default=FREE_TIER_MODEL)
    parser.add_argument("--sleep-seconds", type=float, default=4.0)
    parser.add_argument("--max-tickets", type=int)
    args = parser.parse_args()

    classify_sample(args.input, args.output, args.model, args.sleep_seconds, args.max_tickets)


if __name__ == "__main__":
    main()
