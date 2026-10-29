"""Start digest runs in the background and report their progress.

`build_digest` is synchronous and each module's browse() calls asyncio.run, so a
run happens in a worker thread. Only one run at a time: every run uses the one
browser profile, which Chrome locks.
"""

import threading
from pathlib import Path
from datetime import datetime
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace

from loguru import logger

from scrollforme.digest import build_digest
from scrollforme.config import Settings, Source

BuildDigest = Callable[..., Path]


class RunInProgress(Exception):
	"""A run was requested while another one is still going."""


@dataclass(frozen=True)
class RunState:
	"""What the current or most recent run is doing, as the dashboard shows it."""

	status: str = "idle"
	started_at: str = ""
	total: int = 0
	index: int = 0
	current_module: str = ""
	run_id: str = ""
	error: str = ""


class RunManager:
	"""Owns the single background run."""

	def __init__(self, build: BuildDigest = build_digest) -> None:
		self._build = build
		self._lock = threading.Lock()
		self._state = RunState()
		self._thread: threading.Thread | None = None

	def state(self) -> dict:
		"""The current run state as JSON data."""
		return asdict(self._state)

	def is_running(self) -> bool:
		"""Whether a run is going now."""
		return self._state.status == "running"

	def start(self, settings: Settings) -> None:
		"""Begin a run in a worker thread; raise RunInProgress if one is going."""
		with self._lock:
			if self.is_running():
				raise RunInProgress
			self._state = RunState("running", datetime.now().isoformat(), len(settings.sources))
			self._thread = threading.Thread(target=self._run, args=(settings,), daemon=True)
			self._thread.start()

	def wait(self, timeout: float | None = None) -> None:
		"""Block until the current run's thread ends; for tests and shutdown."""
		if self._thread:
			self._thread.join(timeout)

	def _run(self, settings: Settings) -> None:
		try:
			html_path = self._build(settings, self._on_source_start)
			self._state = replace(self._state, status="finished", run_id=html_path.parent.name)
		except Exception as error:
			logger.exception("Run failed")
			self._state = replace(self._state, status="failed", error=str(error))

	def _on_source_start(self, index: int, source: Source) -> None:
		self._state = replace(self._state, index=index, current_module=source.module)
