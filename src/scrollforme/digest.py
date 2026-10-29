"""Build a digest: run every configured source's module and compile the results.

A run calls each `[[sources]]` entry's module `browse(description)` in turn,
then writes `<output_dir>/<timestamp>/digest.json` (the raw dicts) and
`digest.html` (rendered from them). `rerender` rebuilds the HTML from a saved
JSON record without touching the browser.
"""

import json
from pathlib import Path
from datetime import datetime
from collections.abc import Callable

from loguru import logger

from scrollforme.render import render_digest
from scrollforme.config import Settings, Source, use_settings
from scrollforme.site_modules import available_domains, load_browse
from scrollforme.models import SourceResult, result_from_dict, result_to_dict

SourceStarted = Callable[[int, Source], None]
"""Called with a source's position and the source just before it is browsed."""


def _ignore_progress(index: int, source: Source) -> None:
	pass


def build_digest(settings: Settings, on_source_start: SourceStarted = _ignore_progress) -> Path:
	"""Run all sources with `settings` and return the path of the HTML digest."""
	use_settings(settings)
	_warn_about_unused_modules(settings)
	started_at = datetime.now()
	results = collect_results(settings, on_source_start)
	run_dir = settings.output_dir / started_at.strftime("%Y-%m-%d_%H%M%S")
	return write_run(run_dir, results, started_at)


def collect_results(
	settings: Settings, on_source_start: SourceStarted = _ignore_progress
) -> list[SourceResult]:
	"""Browse every source, one at a time: they share one browser profile, which Chrome locks."""
	results = []
	for index, source in enumerate(settings.sources):
		on_source_start(index, source)
		results.append(_browse_or_record_error(source, settings))
	return results


def write_run(run_dir: Path, results: list[SourceResult], generated_at: datetime) -> Path:
	"""Save the results as digest.json and digest.html in `run_dir`; return the HTML path."""
	run_dir.mkdir(parents=True, exist_ok=True)
	record = {
		"generated_at": generated_at.isoformat(),
		"results": [result_to_dict(result) for result in results],
	}
	(run_dir / "digest.json").write_text(json.dumps(record, indent="\t", ensure_ascii=False))
	html_path = run_dir / "digest.html"
	html_path.write_text(render_digest(results, generated_at))
	return html_path


def rerender(digest_json: Path) -> Path:
	"""Rebuild the HTML next to a saved digest.json; return its path."""
	record = json.loads(digest_json.read_text())
	results = [result_from_dict(data) for data in record["results"]]
	html_path = digest_json.with_suffix(".html")
	html_path.write_text(render_digest(results, datetime.fromisoformat(record["generated_at"])))
	return html_path


def unused_modules(settings: Settings) -> list[str]:
	"""Module domains in modules_dir that no source uses."""
	used = {source.module for source in settings.sources}
	return [domain for domain in available_domains(settings.modules_dir) if domain not in used]


def _warn_about_unused_modules(settings: Settings) -> None:
	for domain in unused_modules(settings):
		logger.warning("Module {} has no [[sources]] entry, so it is skipped", domain)


def _browse_or_record_error(source: Source, settings: Settings) -> SourceResult:
	try:
		data = load_browse(settings.modules_dir, source.module)(source.description)
		return SourceResult(source.module, source.description, data=data)
	except Exception as error:
		logger.exception("Failed to browse {}", source.module)
		return SourceResult(source.module, source.description, error=str(error))
