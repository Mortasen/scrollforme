import json
from pathlib import Path

from scrollforme.config import parse_settings
from scrollforme.digest import build_digest, rerender, unused_modules


def _write_module(modules_dir: Path, domain: str, body: str) -> None:
	package = modules_dir / domain
	package.mkdir(parents=True)
	(package / "__init__.py").write_text(body)


def _settings(tmp_path: Path, modules: list[str]):
	sources = [{"module": module, "description": f"use {module}"} for module in modules]
	return parse_settings({"sources": sources}, base_dir=tmp_path)


def _fake_modules(tmp_path: Path) -> None:
	modules_dir = tmp_path / "modules"
	_write_module(
		modules_dir,
		"good.com",
		"def browse(description):\n\treturn {'seen': description}\n",
	)
	_write_module(
		modules_dir, "broken.com", "def browse(description):\n\traise OSError('offline')\n"
	)
	_write_module(modules_dir, "spare.com", "def browse(description):\n\treturn {}\n")


def test_build_digest_runs_each_source_and_records_failures(tmp_path):
	_fake_modules(tmp_path)
	html_path = build_digest(_settings(tmp_path, ["good.com", "broken.com"]))
	record = json.loads((html_path.parent / "digest.json").read_text())
	results = {result["module"]: result for result in record["results"]}
	assert results["good.com"]["data"] == {"seen": "use good.com"}
	assert results["broken.com"]["error"] == "offline"
	assert "Could not read this site: offline" in html_path.read_text()


def test_rerender_rebuilds_html_from_json(tmp_path):
	_fake_modules(tmp_path)
	html_path = build_digest(_settings(tmp_path, ["good.com"]))
	html_path.unlink()
	assert rerender(html_path.with_suffix(".json")) == html_path
	assert "use good.com" in html_path.read_text()


def test_modules_without_a_source_are_reported(tmp_path):
	_fake_modules(tmp_path)
	assert unused_modules(_settings(tmp_path, ["good.com"])) == ["broken.com", "spare.com"]


def test_progress_is_reported_before_each_source(tmp_path):
	_fake_modules(tmp_path)
	seen = []
	build_digest(
		_settings(tmp_path, ["good.com", "broken.com"]), lambda i, s: seen.append((i, s.module))
	)
	assert seen == [(0, "good.com"), (1, "broken.com")]
