"""Persist workflow run artifacts with a rolling file limit."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Union


def save_workflow_result(
    result: dict[str, Any],
    output_dir: Union[str, Path] = "output",
    max_files: int = 3,
    prefix: str = "sales_workflow",
) -> Path:
    """Write JSON results and keep at most `max_files` by recency."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    payload = dict(result)
    payload["saved_at"] = datetime.now(timezone.utc).isoformat()

    file_path = output_path / f"{prefix}_{datetime.now():%Y%m%d_%H%M%S}.json"
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)

    existing = sorted(
        output_path.glob(f"{prefix}_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for old_file in existing[max_files:]:
        old_file.unlink()

    return file_path
