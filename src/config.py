from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"
TABLES_DIR = OUTPUTS_DIR / "tables"


DEFAULT_SAMPLE_SIZE = 500
RANDOM_STATE = 42
FREE_TIER_MODEL = "gemini-2.5-flash-lite"
FREE_TIER_MAX_REQUESTS = 500

TEXT_COLUMN = "ticket_text"

TRUE_LABELS = {
    "category": "actual_category",
    "priority": "actual_priority",
    "department": "actual_department",
}

PREDICTED_LABELS = {
    "category": "predicted_category",
    "priority": "predicted_priority",
    "department": "predicted_department",
}


def ensure_directories() -> None:
    for path in [RAW_DIR, PROCESSED_DIR, CHARTS_DIR, TABLES_DIR]:
        path.mkdir(parents=True, exist_ok=True)
