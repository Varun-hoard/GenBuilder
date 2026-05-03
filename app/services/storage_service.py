"""
GenBuilder — Local Storage Service

Saves generated design parameter sets as JSON files to a local output
directory. Designed as a drop-in replacement for S3 — the interface is
intentionally similar so cloud storage can be swapped in later.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Default output directory (configurable via env)
OUTPUT_DIR = Path(
    os.environ.get("GENBUILDER_OUTPUT_DIR", "./outputs")
).resolve()


def _ensure_output_dir() -> Path:
    """Create the output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def save_result(
    request_id: str,
    project_name: str,
    data: dict,
) -> str:
    """
    Save a design result as a JSON file.

    Returns the local file path (analogous to an S3 URI).
    """
    _ensure_output_dir()

    # Build a filename: project-name_request-id.json
    safe_name = project_name.replace(" ", "-").lower()
    filename = f"{safe_name}_{request_id}.json"
    filepath = OUTPUT_DIR / filename

    # Add metadata
    payload = {
        "request_id": request_id,
        "project_name": project_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "parameters": data,
    }

    filepath.write_text(json.dumps(payload, indent=2, default=str))
    logger.info("Saved result to %s", filepath)

    return str(filepath)


def get_result(request_id: str) -> Optional[dict]:
    """
    Retrieve a previously generated result by its request ID.

    Scans the output directory for a file containing the request_id.
    """
    _ensure_output_dir()

    for filepath in OUTPUT_DIR.glob("*.json"):
        if request_id in filepath.name:
            return json.loads(filepath.read_text())

    return None


def list_results(limit: int = 50) -> list[dict]:
    """
    List all saved results, newest first.

    Returns lightweight summaries (no full parameter data) for browsing.
    """
    _ensure_output_dir()
    results = []

    json_files = sorted(
        OUTPUT_DIR.glob("*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    for filepath in json_files[:limit]:
        try:
            data = json.loads(filepath.read_text())
            results.append({
                "request_id": data.get("request_id", "unknown"),
                "project_name": data.get("project_name", "unknown"),
                "generated_at": data.get("generated_at", "unknown"),
                "filename": filepath.name,
                "size_bytes": filepath.stat().st_size,
            })
        except (json.JSONDecodeError, KeyError):
            continue

    return results


def delete_result(request_id: str) -> bool:
    """Delete a saved result by request ID. Returns True if deleted."""
    _ensure_output_dir()

    for filepath in OUTPUT_DIR.glob("*.json"):
        if request_id in filepath.name:
            filepath.unlink()
            logger.info("Deleted result %s", filepath)
            return True

    return False
