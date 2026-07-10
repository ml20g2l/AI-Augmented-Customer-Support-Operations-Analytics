from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import DEFAULT_SAMPLE_SIZE, PROCESSED_DIR, RANDOM_STATE, TRUE_LABELS, ensure_directories


def create_classification_sample(
    cleaned: pd.DataFrame,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    stratify_by: str = TRUE_LABELS["category"],
) -> pd.DataFrame:
    ensure_directories()

    if len(cleaned) <= sample_size:
        sample = cleaned.copy()
    elif stratify_by in cleaned.columns:
        groups = []
        for _, group in cleaned.groupby(stratify_by, group_keys=False):
            group_sample_size = max(1, round(sample_size * len(group) / len(cleaned)))
            groups.append(group.sample(group_sample_size, random_state=RANDOM_STATE))
        sample = pd.concat(groups).sample(frac=1, random_state=RANDOM_STATE).head(sample_size).copy()
    else:
        sample = cleaned.sample(sample_size, random_state=RANDOM_STATE).copy()

    output_file = PROCESSED_DIR / "classification_sample.csv"
    sample.to_csv(output_file, index=False)
    return sample


def load_cleaned(path: str | Path = PROCESSED_DIR / "tickets_cleaned.csv") -> pd.DataFrame:
    return pd.read_csv(path)
