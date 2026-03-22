"""Rastreamento de metadados de coleta — quando cada fonte foi atualizada."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

METADATA_FILE = "collection_metadata.json"


def _get_metadata_path(data_dir: Path) -> Path:
    return data_dir / "processed" / METADATA_FILE


def load_metadata(data_dir: Path) -> dict[str, dict[str, str]]:
    """Carrega metadados de coleta."""
    path = _get_metadata_path(data_dir)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data: dict[str, dict[str, str]] = json.load(f)
            return data
    return {}


def save_collection_metadata(
    data_dir: Path,
    source: str,
    records: int,
    notes: str = "",
) -> None:
    """Registra que uma coleta foi realizada."""
    metadata = load_metadata(data_dir)
    metadata[source] = {
        "last_collected": datetime.now(tz=UTC).isoformat(),
        "records": str(records),
        "notes": notes,
    }
    path = _get_metadata_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    logger.info("Metadata atualizado: %s = %d registros", source, records)
