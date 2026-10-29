"""Check, without spending anything, that the machine has what a run needs.

These are PATH checks only: they cannot tell whether the browser has remote
debugging switched on or whether the Claude credential works.
"""

import shutil
from pathlib import Path

from scrollforme.config import BrowserSettings, resolve_dir

BROWSER_PROGRAMS = {"chrome": ["google-chrome", "google-chrome-stable"], "firefox": ["firefox"]}
MCP_PROGRAMS = {"chrome": "npx", "firefox": "firefox-devtools-mcp"}


def check_environment(raw: dict, base_dir: Path) -> list[dict]:
	"""One entry per check: its name, whether it passed, and a detail for the user."""
	kind = BrowserSettings(**raw.get("browser", {})).kind
	browser = next(filter(shutil.which, BROWSER_PROGRAMS[kind]), None)
	mcp = MCP_PROGRAMS[kind]
	return [
		_check(f"Your {kind}", browser is not None, browser or " or ".join(BROWSER_PROGRAMS[kind])),
		_check(f"{kind} DevTools MCP launcher", shutil.which(mcp) is not None, mcp),
		_check("Modules folder", resolve_dir(raw, "modules_dir", base_dir).is_dir(), "modules/"),
	]


def _check(name: str, ok: bool, detail: str) -> dict:
	return {"name": name, "ok": ok, "detail": detail}
