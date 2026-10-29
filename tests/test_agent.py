from pathlib import Path
from dataclasses import replace

from scrollforme.config import BrowserSettings, load_settings
from scrollforme.agent import (
	BROWSER_BACKENDS,
	SiteTask,
	build_options,
	build_prompt,
	decode_nested_json,
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
	expected = BROWSER_BACKENDS["chrome"]["tools"]
	assert options.allowed_tools == [f"mcp__browser__{name}" for name in expected]
	for backend in BROWSER_BACKENDS.values():
		assert {"click", "fill", "evaluate_script", "close_page"}.isdisjoint(backend["tools"])


def test_chrome_attaches_to_the_running_browser():
	server = build_options(SETTINGS).mcp_servers["browser"]
	assert "--autoConnect" in server["args"]


def test_firefox_attaches_over_marionette():
	firefox = replace(SETTINGS, browser=BrowserSettings(kind="firefox", marionette_port=2829))
	server = build_options(firefox).mcp_servers["browser"]
	assert server["command"] == "firefox-devtools-mcp"
	assert server["args"][-2:] == ["--marionettePort", "2829"]


def test_prompt_carries_profile_site_and_purpose():
	task = SiteTask("reddit.com", "https://www.reddit.com/", "new open models", "skip promos")
	prompt = build_prompt(task, SETTINGS)
	assert "user's own running chrome" in prompt
	assert "stay on reddit.com" in prompt
	assert "new open models" in prompt
	assert "skip promos" in prompt


def test_output_is_any_json_object():
	assert build_options(SETTINGS).output_format["schema"]["type"] == "object"


def test_json_encoded_nested_values_are_decoded():
	raw = {"status": "ok", "posts": '[{"title": "x", "tags": "[\\"a\\"]"}]', "note": "[draft] text"}
	assert decode_nested_json(raw) == {
		"status": "ok",
		"posts": [{"title": "x", "tags": ["a"]}],
		"note": "[draft] text",
	}
