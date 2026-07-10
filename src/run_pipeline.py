from __future__ import annotations

import argparse
from pathlib import Path

from src.config import DEFAULT_SAMPLE_SIZE, PROCESSED_DIR, ensure_directories
from src.data_cleaning import clean_tickets
from src.evaluation import evaluate_predictions, empirical_accuracy_by_category
from src.powerbi_exports import export_all_powerbi_tables
from src.sampling import create_classification_sample, load_cleaned


def run_clean_and_sample(raw_file: str | Path, sample_size: int) -> None:
    cleaned, summary = clean_tickets(raw_file)
    create_classification_sample(cleaned, sample_size=sample_size)
    export_all_powerbi_tables()
    print("Cleaning complete.")
    print(f"Final cleaned rows: {summary['final_rows']}")
    print("Sample saved to data/processed/classification_sample.csv")


def run_evaluation() -> None:
    predictions_file = PROCESSED_DIR / "gemini_predictions.csv"
    if not predictions_file.exists():
        raise FileNotFoundError(
            "Gemini predictions not found. Run src.gemini_classification first."
        )
    evaluate_predictions(predictions_file)
    empirical_accuracy_by_category(predictions_file)
    export_all_powerbi_tables()
    print("Evaluation complete.")
    print("Metrics saved to data/processed and Power BI tables saved to outputs/tables.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-file", help="Path to the raw Kaggle CSV file.")
    parser.add_argument("--sample-size", type=int, default=DEFAULT_SAMPLE_SIZE)
    parser.add_argument("--evaluate-only", action="store_true")
    args = parser.parse_args()

    ensure_directories()
    if args.evaluate_only:
        run_evaluation()
        return

    if args.raw_file:
        run_clean_and_sample(args.raw_file, args.sample_size)
        return

    cleaned_file = PROCESSED_DIR / "tickets_cleaned.csv"
    if cleaned_file.exists():
        cleaned = load_cleaned(cleaned_file)
        create_classification_sample(cleaned, sample_size=args.sample_size)
        export_all_powerbi_tables()
        print("Sample regenerated from existing cleaned data.")
        return

    raise ValueError("Provide --raw-file, or run with --evaluate-only after predictions exist.")


if __name__ == "__main__":
    main()
