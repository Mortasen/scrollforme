"""Find the subreddits a description names and the listing pages a person would open for them."""

import re

# "r/name", "/r/name" or "reddit.com/r/name"; Reddit names are 2-21 letters, digits or underscores.
_SUBREDDIT_MENTION = re.compile(r"(?<![\w])r/([A-Za-z0-9_]{2,21})(?![\w])")


def subreddits_named_in(description: str) -> list[str]:
	"""Return each subreddit the description mentions, once, in the order it first appears."""
	seen: dict[str, str] = {}
	for name in _SUBREDDIT_MENTION.findall(description):
		seen.setdefault(name.lower(), name)
	return list(seen.values())


def listing_url(subreddit: str) -> str:
	"""The subreddit's top posts of the day, as the site's own sort menu links to them."""
	return f"https://www.reddit.com/r/{subreddit}/top/?t=day"
