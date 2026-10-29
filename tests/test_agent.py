from pathlib import Path

from scrollforme.config import load_settings
from scrollforme.agent import (
	READ_ONLY_BROWSER_TOOLS,
	WRITING_BROWSER_TOOLS,
	build_options,
	build_prompt,
)

SETTINGS = load_settings(Path(__file__).parent.parent / "scrollforme.example.toml")


def test_agent_has_no_builtin_tools_and_denies_unlisted_calls():
	options = build_options(SETTINGS)
	assert options.tools == []
	assert options.permission_mode == "dontAsk"
	assert options.setting_sources == []


def test_no_mcp_server_but_the_browser_can_load():
	options = build_options(SETTINGS)
	assert list(options.mcp_servers) == ["browser"]
	assert options.strict_mcp_config is True
	assert options.env["ENABLE_CLAUDEAI_MCP_SERVERS"] == "false"


def test_only_read_only_browser_tools_are_allowed():
	options = build_options(SETTINGS)
	assert options.allowed_tools == [f"mcp__browser__{name}" for name in READ_ONLY_BROWSER_TOOLS]
	assert options.disallowed_tools == [f"mcp__browser__{name}" for name in WRITING_BROWSER_TOOLS]
	assert set(WRITING_BROWSER_TOOLS).isdisjoint(READ_ONLY_BROWSER_TOOLS)


def test_server_starts_with_unused_sections_disabled():
	args = build_options(SETTINGS).mcp_servers["browser"]["args"]
	assert "--disable-network-debugging" in args
	assert "--disable-browser-management" not in args
	assert "--disable-element-interaction" not in args


def test_prompt_names_the_profile_and_item_cap():
	source = SETTINGS.sources[0]
	prompt = build_prompt(source, SETTINGS)
	assert str(SETTINGS.browser.profile_dir) in prompt
	assert f"up to {source.max_items} items" in prompt
