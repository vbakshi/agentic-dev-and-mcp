"""Save benchmark results to disk with a rolling file limit."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Union


def _serialize_results(results: dict) -> dict:
    """Make results JSON-serializable."""
    serialized = dict(results)
    config = dict(serialized.get("config", {}))
    if "answerers" in config:
        config["answerers"] = [list(pair) for pair in config["answerers"]]
    serialized["config"] = config
    serialized["saved_at"] = datetime.now(timezone.utc).isoformat()
    return serialized


def save_benchmark_results(
    results: dict,
    output_dir: Union[str, Path] = "output",
    max_files: int = 3,
) -> Path:
    """
    Write results to output_dir and keep at most max_files by recency.

    Returns the path to the newly written file.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = output_path / f"benchmark_{timestamp}.json"

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(_serialize_results(results), f, indent=2, ensure_ascii=False)

    existing = sorted(
        output_path.glob("benchmark_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old_file in existing[max_files:]:
        old_file.unlink()

    return file_path

