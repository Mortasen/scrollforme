"""instagram.com: posts from people the user follows, without Reels or suggestions."""

from scrollforme.agent import browse_site

__all__ = ["browse"]

_START_URL = "https://www.instagram.com/?variant=following"

_GUIDANCE = """\
The start URL is the chronological feed of followed accounts. Skip suggested posts, ads and
Reels unless the description asks for them. For each post give the account, the post link, the
caption in short and a brief description of the image from its alt text."""


def browse(description: str) -> dict:
	"""Visit Instagram for the purpose in `description` and return what was found."""
	return browse_site("instagram.com", _START_URL, description, _GUIDANCE)
