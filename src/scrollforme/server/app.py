"""Assemble the FastAPI app: the local-only guard, the API, and the built frontend.

The frontend is a SvelteKit single-page app built into `web/build`; any path that
is not a file there gets its `index.html`, so client-side routes load directly.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from scrollforme.server.routes import router
from scrollforme.server.context import AppContext
from scrollforme.server.guard import reject_foreign_requests


def create_app(context: AppContext, web_dir: Path | None = None) -> FastAPI:
	"""The app for `context`, serving the frontend from `web_dir` when given."""
	app = FastAPI(title="scrollforme", docs_url=None, redoc_url=None, openapi_url=None)
	app.state.context = context
	app.middleware("http")(reject_foreign_requests)
	app.include_router(router)
	if web_dir is not None:
		_serve_frontend(app, web_dir.resolve())
	return app


def _serve_frontend(app: FastAPI, web_dir: Path) -> None:
	@app.get("/{path:path}", include_in_schema=False)
	def frontend(path: str) -> FileResponse:
		if path.startswith("api/"):
			raise HTTPException(404)
		file = (web_dir / path).resolve()
		inside = file.is_relative_to(web_dir) and file.is_file()
		return FileResponse(file if inside else web_dir / "index.html")
