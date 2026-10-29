"""List and read the runs saved in the output directory.

A run's ID is its folder name. IDs come from the URL, so they are checked to name
a direct child of the output directory before any file is opened.
"""

import re
import json
from pathlib import Path

RUN_ID_PATTERN = re.compile(r"[\w-]+")


class UnknownRun(Exception):
	"""No saved run has this ID."""


def list_runs(output_dir: Path) -> list[dict]:
	"""Summaries of every saved run, newest first."""
	if not output_dir.is_dir():
		return []
	records = sorted(output_dir.glob("*/digest.json"), reverse=True)
	return [_summarise(path.parent.name, _read(path)) for path in records]


def read_run(output_dir: Path, run_id: str) -> dict:
	"""The full digest.json record of one run."""
	return _read(run_file(output_dir, run_id, "digest.json"))


def run_file(output_dir: Path, run_id: str, name: str) -> Path:
	"""The path of `name` inside run `run_id`; raise UnknownRun if there is none."""
	if not RUN_ID_PATTERN.fullmatch(run_id):
		raise UnknownRun(run_id)
	path = output_dir / run_id / name
	if not path.is_file():
		raise UnknownRun(run_id)
	return path


def _read(path: Path) -> dict:
	return json.loads(path.read_text())


def _summarise(run_id: str, record: dict) -> dict:
	results = record.get("results", [])
	failed = [result["module"] for result in results if result.get("error")]
	return {
		"id": run_id,
		"generated_at": record.get("generated_at", ""),
		"sites": [result["module"] for result in results],
		"failed": failed,
	}
