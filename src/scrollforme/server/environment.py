"""Check, without spending anything, that the machine has what a run needs.

These are filesystem checks only: they cannot tell whether a site is still
logged in or whether the Claude credential works.
"""

import shutil
from pathlib import Path

from scrollforme.config import parse_browser, parse_mcp, resolve_dir


def check_environment(raw: dict, base_dir: Path) -> list[dict]:
	"""One entry per check: its name, whether it passed, and a detail for the user."""
	browser = parse_browser(raw.get("browser", {}), base_dir)
	mcp = parse_mcp(raw.get("mcp", {}))
	server_script = Path(mcp.args[0]) if mcp.args else Path()
	return [
		_check("Chrome", shutil.which(browser.chrome_binary) is not None, browser.chrome_binary),
		_check("stealth-browser-mcp Python", Path(mcp.command).is_file(), mcp.command),
		_check("stealth-browser-mcp server", server_script.is_file(), str(server_script)),
		_check("Modules folder", resolve_dir(raw, "modules_dir", base_dir).is_dir(), "modules/"),
		_check("Browser profile", browser.profile_dir.is_dir(), str(browser.profile_dir)),
	]


def _check(name: str, ok: bool, detail: str) -> dict:
	return {"name": name, "ok": ok, "detail": detail}
