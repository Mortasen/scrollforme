"""Find and load the per-website modules in the modules folder.

Each subfolder of `modules/` is named after a website domain (`reddit.com`) and
is a Python package exporting one function, `browse(description) -> dict`. The
dots make the folder name an invalid import path, so each package is loaded
from its files under a mangled name instead.
"""

import sys
import importlib.util
from pathlib import Path
from types import ModuleType
from collections.abc import Callable

BrowseFunction = Callable[[str], dict]


def available_domains(modules_dir: Path) -> list[str]:
	"""Domains that have a module package in `modules_dir`."""
	packages = (path for path in modules_dir.iterdir() if (path / "__init__.py").is_file())
	return sorted(path.name for path in packages)


def load_browse(modules_dir: Path, domain: str) -> BrowseFunction:
	"""Import the module for `domain` and return its browse function."""
	package = _import_package(modules_dir, domain)
	browse = getattr(package, "browse", None)
	if not callable(browse):
		raise TypeError(f"module {domain} does not export browse(description)")
	return browse


def _import_package(modules_dir: Path, domain: str) -> ModuleType:
	package_dir = modules_dir / domain
	if Path(domain).name != domain or not (package_dir / "__init__.py").is_file():
		raise FileNotFoundError(f"no module for {domain!r} in {modules_dir}")
	name = f"scrollforme_site_{domain.replace('.', '_').replace('-', '_')}"
	spec = importlib.util.spec_from_file_location(
		name, package_dir / "__init__.py", submodule_search_locations=[str(package_dir)]
	)
	package = importlib.util.module_from_spec(spec)
	sys.modules[name] = package
	spec.loader.exec_module(package)
	return package
