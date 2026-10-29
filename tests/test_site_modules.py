import inspect
from pathlib import Path

import pytest

from scrollforme.site_modules import available_domains, load_browse

MODULES_DIR = Path(__file__).parent.parent / "modules"


def test_shipped_modules_are_found():
	assert {"reddit.com", "instagram.com"} <= set(available_domains(MODULES_DIR))


@pytest.mark.parametrize("domain", ["reddit.com", "instagram.com"])
def test_shipped_module_exports_only_browse(domain):
	browse = load_browse(MODULES_DIR, domain)
	assert list(inspect.signature(browse).parameters) == ["description"]
	assert inspect.getmodule(browse).__all__ == ["browse"]


def test_module_with_dotted_name_can_import_its_own_submodules(tmp_path):
	package = tmp_path / "example.org"
	package.mkdir()
	(package / "helpers.py").write_text("def answer():\n\treturn {'ok': True}\n")
	(package / "__init__.py").write_text(
		"from .helpers import answer\n\n\ndef browse(description):\n\treturn answer()\n"
	)
	assert load_browse(tmp_path, "example.org")("anything") == {"ok": True}


@pytest.mark.parametrize("domain", ["missing.com", "../modules", "."])
def test_unknown_or_unsafe_domain_is_rejected(domain):
	with pytest.raises(FileNotFoundError):
		load_browse(MODULES_DIR, domain)


def test_module_without_browse_is_rejected(tmp_path):
	(tmp_path / "empty.com").mkdir()
	(tmp_path / "empty.com" / "__init__.py").write_text("")
	with pytest.raises(TypeError):
		load_browse(tmp_path, "empty.com")
