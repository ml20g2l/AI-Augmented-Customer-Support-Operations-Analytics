from __future__ import annotations

import argparse
from pathlib import Path
from shutil import copy2

import kagglehub

from src.config import RAW_DIR, ensure_directories


DATASET_HANDLE = "tobiasbueck/multilingual-customer-support-tickets"


def download_dataset(copy_csv_to_raw: bool = True) -> Path:
    ensure_directories()
    dataset_path = Path(kagglehub.dataset_download(DATASET_HANDLE))

    if copy_csv_to_raw:
        csv_files = sorted(dataset_path.glob("*.csv"))
        for csv_file in csv_files:
            copy2(csv_file, RAW_DIR / csv_file.name)

    return dataset_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-copy", action="store_true", help="Download only; do not copy CSV files to data/raw.")
    args = parser.parse_args()

    path = download_dataset(copy_csv_to_raw=not args.no_copy)
    print(f"Path to dataset files: {path}")


if __name__ == "__main__":
    main()
