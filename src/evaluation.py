from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from src.config import CHARTS_DIR, PREDICTED_LABELS, PROCESSED_DIR, TRUE_LABELS, ensure_directories


def _normalise_label(series: pd.Series) -> pd.Series:
    return series.fillna("missing").astype(str).str.strip().str.lower()


def _save_confusion_matrix(y_true: pd.Series, y_pred: pd.Series, label_name: str) -> None:
    labels = sorted(set(y_true.unique()) | set(y_pred.unique()))
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    matrix_df = pd.DataFrame(matrix, index=labels, columns=labels)
    matrix_df.to_csv(PROCESSED_DIR / f"confusion_matrix_{label_name}.csv")

    plt.figure(figsize=(10, 7))
    sns.heatmap(matrix_df, annot=True, fmt="d", cmap="Blues")
    plt.title(f"Confusion Matrix: {label_name.title()}")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / f"confusion_matrix_{label_name}.png", dpi=150)
    plt.close()


def evaluate_predictions(
    predictions_file: str | Path = PROCESSED_DIR / "gemini_predictions.csv",
) -> dict:
    ensure_directories()
    predictions = pd.read_csv(predictions_file)
    metrics: dict[str, object] = {}

    for label_name, actual_column in TRUE_LABELS.items():
        predicted_column = PREDICTED_LABELS[label_name]
        if actual_column not in predictions.columns or predicted_column not in predictions.columns:
            continue

        valid = predictions[[actual_column, predicted_column]].dropna()
        if valid.empty:
            continue

        y_true = _normalise_label(valid[actual_column])
        y_pred = _normalise_label(valid[predicted_column])
        metrics[label_name] = {
            "accuracy": accuracy_score(y_true, y_pred),
            "classification_report": classification_report(y_true, y_pred, output_dict=True, zero_division=0),
        }
        _save_confusion_matrix(y_true, y_pred, label_name)

    metrics_file = PROCESSED_DIR / "classification_metrics.json"
    metrics_file.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def empirical_accuracy_by_category(
    predictions_file: str | Path = PROCESSED_DIR / "gemini_predictions.csv",
) -> pd.DataFrame:
    predictions = pd.read_csv(predictions_file)
    actual = TRUE_LABELS["category"]
    predicted = PREDICTED_LABELS["category"]
    if actual not in predictions.columns or predicted not in predictions.columns:
        return pd.DataFrame()

    df = predictions.dropna(subset=[actual, predicted]).copy()
    df["category_match"] = _normalise_label(df[actual]) == _normalise_label(df[predicted])
    accuracy = (
        df.groupby(actual)
        .agg(ticket_count=("category_match", "size"), empirical_accuracy=("category_match", "mean"))
        .reset_index()
        .rename(columns={actual: "category"})
        .sort_values(["empirical_accuracy", "ticket_count"], ascending=[False, False])
    )
    accuracy.to_csv(PROCESSED_DIR / "empirical_accuracy_by_category.csv", index=False)
    return accuracy
