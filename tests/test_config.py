import tomllib
from pathlib import Path

import pytest

from scrollforme.config import load_settings, parse_settings

EXAMPLE_CONFIG = Path(__file__).parent.parent / "scrollforme.example.toml"


def test_example_config_loads():
	settings = load_settings(EXAMPLE_CONFIG)
	assert [source.name for source in settings.sources] == ["r/LocalLLaMA", "Instagram following"]
	assert settings.browser.profile_dir.is_absolute()
	assert "~" not in settings.mcp.command
	assert all("~" not in arg for arg in settings.mcp.args)


def test_relative_paths_resolve_against_config_dir(tmp_path):
	raw = {"sources": [{"name": "a", "url": "https://example.com"}]}
	settings = parse_settings(raw, base_dir=tmp_path)
	assert settings.browser.profile_dir == tmp_path / "profile"
	assert settings.output_dir == tmp_path / "output"


def test_config_without_sources_is_rejected(tmp_path):
	with pytest.raises(ValueError, match="no \\[\\[sources\\]\\]"):
		parse_settings({}, base_dir=tmp_path)


def test_duplicate_source_names_are_rejected(tmp_path):
	source = {"name": "a", "url": "https://example.com"}
	with pytest.raises(ValueError, match="duplicate"):
		parse_settings({"sources": [source, source]}, base_dir=tmp_path)


def test_unknown_source_key_is_rejected(tmp_path):
	raw = tomllib.loads('[[sources]]\nname = "a"\nurl = "https://x"\nmax_itmes = 3\n')
	with pytest.raises(TypeError):
		parse_settings(raw, base_dir=tmp_path)
