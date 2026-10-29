"""State the API shares between requests: the config file and the run."""

from pathlib import Path
from dataclasses import dataclass, field

from scrollforme.server.runs import RunManager
from scrollforme.config import default_raw_config, read_raw_config, resolve_dir, with_defaults


@dataclass
class AppContext:
	"""One per server process."""

	config_path: Path
	runs: RunManager = field(default_factory=RunManager)

	@property
	def base_dir(self) -> Path:
		"""The folder relative config paths resolve against."""
		return self.config_path.parent

	def config_exists(self) -> bool:
		"""Whether setup has saved a config yet."""
		return self.config_path.is_file()

	def raw_config(self) -> dict:
		"""The saved config's TOML data with defaults filled in, or the defaults before setup."""
		if not self.config_exists():
			return default_raw_config()
		return with_defaults(read_raw_config(self.config_path))

	def output_dir(self) -> Path:
		"""Where runs are saved."""
		return resolve_dir(self.raw_config(), "output_dir", self.base_dir)
