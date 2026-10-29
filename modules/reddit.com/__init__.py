"""reddit.com: the user's subreddits and home feed, without the endless scroll."""

from scrollforme.agent import browse_site

__all__ = ["browse"]

_START_URL = "https://www.reddit.com/"

_GUIDANCE = """\
Go straight to the subreddits the description names (https://www.reddit.com/r/<name>/top/?t=day)
rather than the algorithmic home feed. Skip promoted posts. For each post give its title,
subreddit, link and a one-line summary; read comments only if the description asks for them."""


def browse(description: str) -> dict:
	"""Visit Reddit for the purpose in `description` and return what was found."""
	return browse_site("reddit.com", _START_URL, description, _GUIDANCE)
