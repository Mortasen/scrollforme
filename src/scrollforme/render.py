"""Render site results into one self-contained HTML page.

Results are free-form dicts, so the template walks them recursively: mappings
become labelled fields, lists become lists, and an entry with a title and an
http(s) URL is shown as a headline link. Autoescaping is always on: every string
came from a website and is treated as untrusted text, never markup.
"""

from datetime import datetime

from jinja2 import Environment, PackageLoader, select_autoescape

from scrollforme.models import SourceResult

TITLE_KEYS = ("title", "name", "account", "headline")
URL_KEYS = ("url", "link", "permalink", "href")

_environment = Environment(
	loader=PackageLoader("scrollforme", "templates"),
	autoescape=select_autoescape(default=True, default_for_string=True),
)


def render_digest(results: list[SourceResult], generated_at: datetime) -> str:
	"""Return the digest page for `results`."""
	template = _environment.get_template("digest.html.j2")
	return template.render(results=results, generated_at=generated_at.strftime("%Y-%m-%d %H:%M"))


def is_link(value: object) -> bool:
	"""Whether `value` is a URL safe to put in an href."""
	return isinstance(value, str) and value.startswith(("https://", "http://"))


def split_headline(entry: dict) -> tuple[str, str, dict]:
	"""Pull a title and URL out of `entry`; return them with the remaining fields."""
	title_key = next((key for key in TITLE_KEYS if isinstance(entry.get(key), str)), None)
	url_key = next((key for key in URL_KEYS if is_link(entry.get(key))), None)
	if title_key is None or url_key is None:
		return "", "", entry
	rest = {key: value for key, value in entry.items() if key not in (title_key, url_key)}
	return entry[title_key], entry[url_key], rest


_environment.tests["link"] = is_link
_environment.filters["split_headline"] = split_headline
