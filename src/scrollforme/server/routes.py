"""The JSON API under /api.

Setup reads defaults, checks the machine, lists modules and saves the config;
the dashboard starts runs, follows their progress and opens saved digests.
"""

from typing import Annotated

from fastapi.responses import FileResponse
from fastapi import APIRouter, Body, HTTPException, Request

from scrollforme.site_modules import available_domains
from scrollforme.browser import start_login_browser
from scrollforme.server.context import AppContext
from scrollforme.server.runs import RunInProgress
from scrollforme.server.environment import check_environment
from scrollforme.server.history import UnknownRun, list_runs, read_run, run_file
from scrollforme.config import load_settings, parse_browser, resolve_dir, save_raw_config

router = APIRouter(prefix="/api")


def _context(request: Request) -> AppContext:
	return request.app.state.context


@router.get("/setup")
def get_setup(request: Request) -> dict:
	"""Machine checks and the modules a source can use."""
	context = _context(request)
	raw = context.raw_config()
	modules_dir = resolve_dir(raw, "modules_dir", context.base_dir)
	modules = available_domains(modules_dir) if modules_dir.is_dir() else []
	return {"checks": check_environment(raw, context.base_dir), "modules": modules}


@router.get("/config")
def get_config(request: Request) -> dict:
	"""The saved config, or the defaults with `exists: false` before setup."""
	context = _context(request)
	return {"exists": context.config_exists(), "config": context.raw_config()}


@router.put("/config")
def put_config(request: Request, config: Annotated[dict, Body(embed=True)]) -> dict:
	"""Validate and save the config; 422 with the reason when it is invalid."""
	context = _context(request)
	try:
		save_raw_config(config, context.config_path)
	except (ValueError, TypeError) as error:
		raise HTTPException(422, str(error)) from error
	return {"exists": True, "config": config}


@router.get("/login")
def get_login(request: Request) -> dict:
	"""Whether the login browser is open."""
	return {"open": _context(request).login_browser_open()}


@router.post("/login")
def post_login(request: Request) -> dict:
	"""Open Chrome on the profile at each configured site so the user can log in."""
	context = _context(request)
	if context.runs.is_running():
		raise HTTPException(409, "a run is using the browser profile")
	if not context.login_browser_open():
		raw = context.raw_config()
		urls = [f"https://www.{source['module']}/" for source in raw.get("sources", [])]
		browser = parse_browser(raw.get("browser", {}), context.base_dir)
		context.login_browser = start_login_browser(browser, list(dict.fromkeys(urls)))
	return {"open": True}


@router.get("/runs")
def get_runs(request: Request) -> list[dict]:
	"""Saved runs, newest first."""
	return list_runs(_context(request).output_dir())


@router.post("/runs", status_code=202)
def post_run(request: Request) -> dict:
	"""Start a run in the background; 409 if one is going or the login browser is open."""
	context = _context(request)
	if context.login_browser_open():
		raise HTTPException(409, "close the login browser first: it holds the profile")
	try:
		context.runs.start(load_settings(context.config_path))
	except RunInProgress as error:
		raise HTTPException(409, "a run is already going") from error
	except (OSError, ValueError, TypeError) as error:
		raise HTTPException(422, f"the config cannot be used: {error}") from error
	return context.runs.state()


@router.get("/runs/current")
def get_current_run(request: Request) -> dict:
	"""Progress of the current or most recent run."""
	return _context(request).runs.state()


@router.get("/runs/{run_id}")
def get_run(request: Request, run_id: str) -> dict:
	"""One run's full results."""
	try:
		return read_run(_context(request).output_dir(), run_id)
	except UnknownRun as error:
		raise HTTPException(404, "no such run") from error


@router.get("/runs/{run_id}/digest")
def get_run_digest(request: Request, run_id: str) -> FileResponse:
	"""One run's digest page."""
	try:
		return FileResponse(run_file(_context(request).output_dir(), run_id, "digest.html"))
	except UnknownRun as error:
		raise HTTPException(404, "no such run") from error
