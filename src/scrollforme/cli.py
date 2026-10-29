"""Command-line entry point: `serve`, `run` and `render`.

`serve` starts the local web app (setup wizard and dashboard). `run` builds a
digest of every configured source and `render` rebuilds the HTML from a saved
digest.json; both are thin wrappers over `scrollforme.digest`.
"""

import argparse
from pathlib import Path

import uvicorn
from loguru import logger

from scrollforme.digest import build_digest, rerender
from scrollforme.server.app import create_app
from scrollforme.server.context import AppContext
from scrollforme.config import DEFAULT_CONFIG_PATH, load_settings

DEFAULT_PORT = 8765
DEFAULT_WEB_DIR = Path(__file__).resolve().parents[2] / "web" / "build"


def main() -> None:
	"""Parse arguments and dispatch to a subcommand."""
	args = _build_parser().parse_args()
	args.handler(args)


def _build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="scrollforme", description=__doc__)
	parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
	commands = parser.add_subparsers(required=True)
	serve = commands.add_parser("serve", help="start the local web app")
	serve.add_argument("--port", type=int, default=DEFAULT_PORT)
	serve.add_argument("--web-dir", type=Path, default=DEFAULT_WEB_DIR)
	serve.set_defaults(handler=_serve)
	commands.add_parser("run", help="browse every configured site and write a digest").set_defaults(
		handler=_run
	)
	render = commands.add_parser("render", help="rebuild HTML from a saved digest.json")
	render.add_argument("digest_json", type=Path)
	render.set_defaults(handler=_render)
	return parser


def _serve(args: argparse.Namespace) -> None:
	web_dir = args.web_dir if (args.web_dir / "index.html").is_file() else None
	if web_dir is None:
		logger.error(
			"No frontend build in {}; run `pnpm --dir web build`. Serving the API only.",
			args.web_dir,
		)
	app = create_app(AppContext(args.config.resolve()), web_dir)
	logger.info("Open http://127.0.0.1:{}/", args.port)
	uvicorn.run(app, host="127.0.0.1", port=args.port)


def _run(args: argparse.Namespace) -> None:
	html_path = build_digest(load_settings(args.config))
	logger.info("Digest written to {}", html_path)


def _render(args: argparse.Namespace) -> None:
	logger.info("Digest written to {}", rerender(args.digest_json))
