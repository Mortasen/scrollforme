import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scrollforme.server.app import create_app
from scrollforme.server.runs import RunManager
from scrollforme.server.context import AppContext
from scrollforme.config import default_raw_config

LOCAL = "http://127.0.0.1:8765"


def _fake_build(settings, on_source_start):
	run_dir = settings.output_dir / "2026-10-29_200000"
	run_dir.mkdir(parents=True)
	(run_dir / "digest.json").write_text(json.dumps({"generated_at": "x", "results": []}))
	(run_dir / "digest.html").write_text("<p>digest</p>")
	return run_dir / "digest.html"


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
	context = AppContext(tmp_path / "scrollforme.toml", runs=RunManager(build=_fake_build))
	return TestClient(create_app(context), base_url=LOCAL)


def _config() -> dict:
	return default_raw_config() | {"sources": [{"module": "reddit.com", "description": "news"}]}


def test_config_is_default_until_saved(client):
	assert client.get("/api/config").json()["exists"] is False
	assert client.put("/api/config", json={"config": _config()}).status_code == 200
	assert client.get("/api/config").json()["config"]["sources"][0]["module"] == "reddit.com"


def test_invalid_config_is_rejected(client):
	response = client.put("/api/config", json={"config": default_raw_config()})
	assert response.status_code == 422


def test_run_produces_a_listed_digest(client):
	client.put("/api/config", json={"config": _config()})
	assert client.post("/api/runs", json={}).status_code == 202
	client.app.state.context.runs.wait(5)
	assert client.get("/api/runs/current").json()["status"] == "finished"
	runs = client.get("/api/runs").json()
	assert [run["id"] for run in runs] == ["2026-10-29_200000"]
	assert client.get(f"/api/runs/{runs[0]['id']}/digest").text == "<p>digest</p>"


@pytest.mark.parametrize("run_id", ["..", "..%2Fscrollforme.toml", "missing"])
def test_unknown_or_escaping_run_ids_are_404(client, run_id):
	assert client.get(f"/api/runs/{run_id}").status_code == 404


def test_cross_site_post_is_refused(client):
	response = client.put(
		"/api/config", json={"config": _config()}, headers={"Origin": "https://evil.example"}
	)
	assert response.status_code == 403


def test_non_json_post_is_refused(client):
	response = client.post("/api/runs", content="x", headers={"Content-Type": "text/plain"})
	assert response.status_code == 403


def test_foreign_host_is_refused(client):
	assert client.get("/api/config", headers={"Host": "attacker.example"}).status_code == 403


def test_setup_lists_modules_and_checks(client, tmp_path):
	(tmp_path / "modules" / "reddit.com").mkdir(parents=True)
	(tmp_path / "modules" / "reddit.com" / "__init__.py").write_text("")
	body = client.get("/api/setup").json()
	assert body["modules"] == ["reddit.com"]
	assert "Modules folder" in {check["name"] for check in body["checks"]}


def test_partial_config_is_returned_with_defaults(client, tmp_path):
	(tmp_path / "scrollforme.toml").write_text('[[sources]]\nmodule = "a.com"\ndescription = "x"\n')
	config = client.get("/api/config").json()["config"]
	assert config["agent"]["model"] == "claude-opus-5-5"
	assert config["sources"] == [{"module": "a.com", "description": "x"}]
