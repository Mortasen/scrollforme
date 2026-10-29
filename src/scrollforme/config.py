"""Load the user's scrollforme.toml into typed settings.

The file names the sites to visit (by module domain) and what the user uses each
for, the dedicated browser profile that holds the user's logins, how to launch
the stealth-browser MCP server, and the agent's model and spending limits.

Module `browse(description)` calls take no settings argument, so the active
settings live here: `use_settings` sets them, `get_settings` reads them.
"""

import tomllib
from pathlib import Path
from dataclasses import asdict, dataclass, field

import tomli_w

DEFAULT_CONFIG_PATH = Path("scrollforme.toml")
DEFAULT_MCP_ROOT = Path.home() / ".local/src/stealth-browser-mcp"


@dataclass(frozen=True)
class Source:
	"""One site to visit: its module's domain and what the user uses the site for."""

	module: str
	description: str


@dataclass(frozen=True)
class BrowserSettings:
	"""The persistent Chrome profile the agent browses with."""

	profile_dir: Path
	chrome_binary: str = "google-chrome"
	headless: bool = False


@dataclass(frozen=True)
class McpSettings:
	"""How to start the stealth-browser MCP server as a stdio subprocess."""

	command: str = str(DEFAULT_MCP_ROOT / ".venv/bin/python")
	args: list[str] = field(default_factory=lambda: [str(DEFAULT_MCP_ROOT / "src/server.py")])


@dataclass(frozen=True)
class AgentSettings:
	"""Model choice and the per-visit limits that stop a run from going on forever."""

	model: str = "claude-opus-5-5"
	effort: str = "medium"
	max_turns: int = 60
	max_budget_usd: float = 1.0


@dataclass(frozen=True)
class Settings:
	"""Everything a run needs."""

	sources: list[Source]
	browser: BrowserSettings
	mcp: McpSettings
	agent: AgentSettings
	output_dir: Path
	modules_dir: Path


_active_settings: Settings | None = None


def use_settings(settings: Settings) -> None:
	"""Make `settings` the ones every module's browse() runs with."""
	global _active_settings
	_active_settings = settings


def get_settings() -> Settings:
	"""The settings passed to `use_settings`, else those in the default config file."""
	if _active_settings is None:
		use_settings(load_settings())
	return _active_settings


def default_raw_config() -> dict:
	"""A config with every setting at its default and no sources yet, as TOML data."""
	return {
		"output_dir": "output",
		"modules_dir": "modules",
		"browser": {"profile_dir": "profile", "chrome_binary": "google-chrome", "headless": False},
		"mcp": asdict(McpSettings()),
		"agent": asdict(AgentSettings()),
		"sources": [],
	}


def read_raw_config(path: Path = DEFAULT_CONFIG_PATH) -> dict:
	"""The config file's TOML data as written, without resolving any paths."""
	with path.open("rb") as file:
		return tomllib.load(file)


def save_raw_config(raw: dict, path: Path = DEFAULT_CONFIG_PATH) -> Settings:
	"""Validate `raw` and write it to `path`; raise ValueError or TypeError if invalid."""
	settings = parse_settings(raw, base_dir=path.parent)
	path.write_text(tomli_w.dumps(raw))
	return settings


def load_settings(path: Path = DEFAULT_CONFIG_PATH) -> Settings:
	"""Read and validate the TOML file at `path`."""
	return parse_settings(read_raw_config(path), base_dir=path.parent)


def parse_settings(raw: dict, base_dir: Path) -> Settings:
	"""Build settings from parsed TOML; relative paths resolve against `base_dir`."""
	sources = [Source(**entry) for entry in raw.get("sources", [])]
	if not sources:
		raise ValueError("config defines no [[sources]]")
	_reject_blank_descriptions(sources)
	return Settings(
		sources=sources,
		browser=parse_browser(raw.get("browser", {}), base_dir),
		mcp=parse_mcp(raw.get("mcp", {})),
		agent=AgentSettings(**raw.get("agent", {})),
		output_dir=resolve_dir(raw, "output_dir", base_dir),
		modules_dir=resolve_dir(raw, "modules_dir", base_dir),
	)


def resolve_dir(raw: dict, key: str, base_dir: Path) -> Path:
	"""The absolute path of the `output_dir` or `modules_dir` setting."""
	defaults = {"output_dir": "output", "modules_dir": "modules"}
	return (base_dir / Path(raw.get(key, defaults[key])).expanduser()).resolve()


def _reject_blank_descriptions(sources: list[Source]) -> None:
	blank = [source.module for source in sources if not source.description.strip()]
	if blank:
		raise ValueError(f"sources without a description: {blank}")


def parse_browser(raw: dict, base_dir: Path) -> BrowserSettings:
	"""Browser settings from a `[browser]` table; the profile path resolves against `base_dir`."""
	options = {key: value for key, value in raw.items() if key != "profile_dir"}
	profile_dir = Path(raw.get("profile_dir", "profile")).expanduser()
	return BrowserSettings(profile_dir=(base_dir / profile_dir).resolve(), **options)


def parse_mcp(raw: dict) -> McpSettings:
	"""MCP launch settings from an `[mcp]` table, with `~` expanded."""
	expanded = {key: _expand_home(value) for key, value in raw.items()}
	return McpSettings(**expanded)


def _expand_home(value: str | list[str]) -> str | list[str]:
	if isinstance(value, list):
		return [str(Path(item).expanduser()) for item in value]
	return str(Path(value).expanduser())
