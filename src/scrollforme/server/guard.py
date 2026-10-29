"""Keep the local API usable only by pages served from this machine.

The API writes a config whose `mcp.command` and `chrome_binary` it later runs,
so any web page that could reach it could run programs. The server binds to
127.0.0.1, and this middleware also refuses a request when:
- its Host is not a localhost name, which stops DNS rebinding;
- it changes state and its Origin is another site's;
- it changes state and its body is not JSON, which a plain HTML form cannot send.
"""

from urllib.parse import urlsplit
from collections.abc import Awaitable, Callable, Mapping

from fastapi import Request, Response
from fastapi.responses import JSONResponse

LOCAL_HOSTNAMES = {"localhost", "127.0.0.1", "::1"}
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


async def reject_foreign_requests(
	request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
	"""HTTP middleware: answer 403 to any request `foreign_request_problem` objects to."""
	problem = foreign_request_problem(request.headers, request.method)
	if problem:
		return JSONResponse({"detail": problem}, status_code=403)
	return await call_next(request)


def foreign_request_problem(headers: Mapping[str, str], method: str) -> str | None:
	"""Why a request must be refused, or None when it may proceed."""
	if _hostname(headers.get("host", "")) not in LOCAL_HOSTNAMES:
		return "requests must use a localhost address"
	if method in SAFE_METHODS:
		return None
	origin = headers.get("origin")
	if origin and urlsplit(origin).hostname not in LOCAL_HOSTNAMES:
		return "cross-site requests are refused"
	if not headers.get("content-type", "").startswith("application/json"):
		return "requests that change state must send JSON"
	return None


def _hostname(host: str) -> str | None:
	return urlsplit(f"//{host}").hostname
