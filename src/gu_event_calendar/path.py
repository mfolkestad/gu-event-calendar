from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
DOCS_DIR = PROJECT_ROOT / "docs"

EVENT_API = (
    "https://www.gu.se/api/search/rest/apps/"
    "external_web/searchers/event_en"
)