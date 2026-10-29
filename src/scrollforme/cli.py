"""Command-line entry point: `login`, `run` and `render`.

`run` builds a digest of every configured source and `render` rebuilds the HTML
from a saved digest.json; both are thin wrappers over `scrollforme.digest`.
"""

import argparse
from pathlib import Path

from loguru import logger

from scrollforme.digest import build_digest, rerender
from scrollforme.browser import open_profile_for_login
from scrollforme.config import DEFAULT_CONFIG_PATH, load_settings


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
	commands.add_parser("run", help="browse every configured site and write a digest").set_defaults(
		handler=_run
	)
	render = commands.add_parser("render", help="rebuild HTML from a saved digest.json")
	render.add_argument("digest_json", type=Path)
	render.set_defaults(handler=_render)
	return parser


def _login(args: argparse.Namespace) -> None:
	settings = load_settings(args.config)
	urls = [f"https://www.{source.module}/" for source in settings.sources]
	open_profile_for_login(settings.browser, list(dict.fromkeys(urls)))


def _run(args: argparse.Namespace) -> None:
	html_path = build_digest(load_settings(args.config))
	logger.info("Digest written to {}", html_path)


def _render(args: argparse.Namespace) -> None:
	logger.info("Digest written to {}", rerender(args.digest_json))
