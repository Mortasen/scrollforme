"""Command-line entry point: `login`, `run` and `render`.

A run writes `<output_dir>/<timestamp>/digest.json` and `digest.html`; `render`
rebuilds the HTML from a saved JSON record without touching the browser.
"""

import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

from loguru import logger

from scrollforme.agent import collect_source
from scrollforme.render import render_digest
from scrollforme.browser import open_profile_for_login
from scrollforme.config import DEFAULT_CONFIG_PATH, Settings, Source, load_settings
from scrollforme.models import SourceDigest, digest_from_dict, digest_to_dict


def main() -> None:
	"""Parse arguments and dispatch to a subcommand."""
	args = _build_parser().parse_args()
	args.handler(args)


def _build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="scrollforme", description=__doc__)
	parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
	commands = parser.add_subparsers(required=True)
	commands.add_parser("login", help="open the browser profile to log in").set_defaults(
		handler=_login
	)
	commands.add_parser("run", help="read every source and write a digest").set_defaults(
		handler=_run
	)
	render = commands.add_parser("render", help="rebuild HTML from a saved digest.json")
	render.add_argument("digest_json", type=Path)
	render.set_defaults(handler=_render)
	return parser


def _login(args: argparse.Namespace) -> None:
	settings = load_settings(args.config)
	open_profile_for_login(settings.browser, [source.url for source in settings.sources])


def _run(args: argparse.Namespace) -> None:
	settings = load_settings(args.config)
	started_at = datetime.now()
	digests = asyncio.run(_collect_all(settings))
	run_dir = settings.output_dir / started_at.strftime("%Y-%m-%d_%H%M%S")
	html_path = _write_run(run_dir, digests, started_at)
	logger.info("Digest written to {}", html_path)


async def _collect_all(settings: Settings) -> list[SourceDigest]:
	"""Read sources one at a time: they share one browser profile, which Chrome locks."""
	return [await _collect_or_record_error(source, settings) for source in settings.sources]


async def _collect_or_record_error(source: Source, settings: Settings) -> SourceDigest:
	try:
		return await collect_source(source, settings)
	except Exception as error:
		logger.exception("Failed to read {}", source.name)
		return SourceDigest(source.name, source.url, items=[], error=str(error))


def _write_run(run_dir: Path, digests: list[SourceDigest], started_at: datetime) -> Path:
	run_dir.mkdir(parents=True, exist_ok=True)
	record = {
		"generated_at": started_at.isoformat(),
		"digests": [digest_to_dict(d) for d in digests],
	}
	(run_dir / "digest.json").write_text(json.dumps(record, indent="\t", ensure_ascii=False))
	html_path = run_dir / "digest.html"
	html_path.write_text(render_digest(digests, started_at))
	return html_path


def _render(args: argparse.Namespace) -> None:
	record = json.loads(args.digest_json.read_text())
	digests = [digest_from_dict(data) for data in record["digests"]]
	html_path = args.digest_json.with_suffix(".html")
	html_path.write_text(render_digest(digests, datetime.fromisoformat(record["generated_at"])))
	logger.info("Digest written to {}", html_path)
