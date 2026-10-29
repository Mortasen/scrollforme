"""Render source digests into one self-contained HTML page.

Autoescaping is always on: every string in a digest came from a feed and is
treated as untrusted text, never markup.
"""

from datetime import datetime

from jinja2 import Environment, PackageLoader, select_autoescape

from scrollforme.models import SourceDigest

_environment = Environment(
	loader=PackageLoader("scrollforme", "templates"),
	autoescape=select_autoescape(default=True, default_for_string=True),
)


def render_digest(digests: list[SourceDigest], generated_at: datetime) -> str:
	"""Return the digest page for `digests`."""
	template = _environment.get_template("digest.html.j2")
	return template.render(
		digests=digests,
		item_count=sum(len(digest.items) for digest in digests),
		generated_at=generated_at.strftime("%Y-%m-%d %H:%M"),
	)
