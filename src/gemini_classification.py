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
    ensure_directories,
)


PROMPT_TEMPLATE = """
You are classifying customer support tickets for an operations analytics project.

Return only valid JSON with this schema:
{{
  "category": "short category label",
  "priority": "low|medium|high|critical",
  "department": "best routing department",
  "confidence": 0.0,
  "root_cause": "short recurring issue label"
}}

Ticket:
{ticket_text}
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


def classify_ticket(client: genai.Client, model: str, ticket_text: str) -> dict:
    response = client.models.generate_content(
        model=model,
        contents=PROMPT_TEMPLATE.format(ticket_text=ticket_text[:5000]),
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

    client = genai.Client(api_key=api_key)
    rows = []

    for _, row in tqdm(sample.iterrows(), total=len(sample), desc="Classifying tickets"):
        try:
            prediction = classify_ticket(client, model, str(row[TEXT_COLUMN]))
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
        if sleep_seconds:
            time.sleep(sleep_seconds)

    predictions = pd.DataFrame(rows)
    predictions.to_csv(output_file, index=False)
    return predictions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(PROCESSED_DIR / "classification_sample.csv"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / "gemini_predictions.csv"))
    parser.add_argument("--model", default=FREE_TIER_MODEL)
    parser.add_argument("--sleep-seconds", type=float, default=4.0)
    args = parser.parse_args()

    classify_sample(args.input, args.output, args.model, args.sleep_seconds)


if __name__ == "__main__":
    main()
