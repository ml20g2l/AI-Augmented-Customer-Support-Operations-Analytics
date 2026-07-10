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

from src.config import PROCESSED_DIR, TEXT_COLUMN, ensure_directories


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


def classify_sample(
    input_file: str | Path = PROCESSED_DIR / "classification_sample.csv",
    output_file: str | Path = PROCESSED_DIR / "gemini_predictions.csv",
    model: str = "gemini-2.0-flash",
    sleep_seconds: float = 1.0,
) -> pd.DataFrame:
    ensure_directories()
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("Set GEMINI_API_KEY or GOOGLE_API_KEY before running Gemini classification.")

    sample = pd.read_csv(input_file)
    if TEXT_COLUMN not in sample.columns:
        raise ValueError(f"Input file must contain {TEXT_COLUMN!r}.")

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
    parser.add_argument("--model", default="gemini-2.0-flash")
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    args = parser.parse_args()

    classify_sample(args.input, args.output, args.model, args.sleep_seconds)


if __name__ == "__main__":
    main()
