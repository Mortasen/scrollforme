"""reddit.com: the user's subreddits and home feed, without the endless scroll.

The visit must look to Reddit like the user browsing it themselves: the normal www.reddit.com
pages in their own logged-in, visible browser, opened one at a time and scrolled a screen at a
time. So there are no shortcuts a person would not take (.json listings, the API, RSS,
old.reddit.com), and a challenge or block page ends the visit instead of being worked around.
"""

from loguru import logger

from scrollforme.agent import browse_site
from scrollforme.config import get_settings

from .subreddits import listing_url, subreddits_named_in

__all__ = ["browse"]

_HOME_FEED_URL = "https://www.reddit.com/"

# Post pages the agent may open per visit, on top of one listing page per subreddit.
_MAX_POST_PAGES = 5

_BROWSING_GUIDANCE = f"""\
Browse the way the user would by hand, so the visit looks like theirs. Use only the ordinary
www.reddit.com pages a person opens: subreddit listings, the home feed and post pages. Never
request .json, /api/, RSS or old.reddit.com URLs, and never follow links off Reddit. Open one page
at a time. On a listing, scroll down about one screen at a time (scroll_page with amount 900 and
smooth on), a few screens at most, never straight to the bottom. Open a post page only when the
description asks about comments or a title alone does not say what the post is, and open at most
{_MAX_POST_PAGES} of them.

Read pages with query_elements, not get_page_content: a Reddit page's full HTML is too large for
one reply. Posts should be shreddit-post elements whose attributes carry post-title, permalink,
subreddit-prefixed-name and created-timestamp. Every result costs context, so scroll first and
then query "shreddit-post" once per listing with a limit of 15; a repeated query returns the same
first posts. If there are none, query article elements or links whose href contains /comments/
instead. Skip shreddit-ad-post elements and anything marked promoted.

Leave cookie banners, "open in app" and other overlays alone: you cannot click, and the posts are
in the page underneath. If you see "Prove your humanity", a CAPTCHA, a "blocked" notice or a
logged-out page, stop at once. Do not retry or look for a way around it. Close the browser and
return {{"notice": "..."}} saying what you saw and that the user should open Reddit with
`scrollforme login` and sort it out there.

For each post give its title, subreddit, url (the permalink as a full https://www.reddit.com URL)
and a one-line summary. Leave out scores, vote counts and comment counts."""


def browse(description: str) -> dict:
	"""Visit Reddit for the purpose in `description` and return what was found."""
	_warn_if_headless()
	subreddits = subreddits_named_in(description)
	start_url = listing_url(subreddits[0]) if subreddits else _HOME_FEED_URL
	guidance = f"{_route_guidance(subreddits)}\n\n{_BROWSING_GUIDANCE}"
	return browse_site("reddit.com", start_url, description, guidance)


def _warn_if_headless() -> None:
	if get_settings().browser.headless:
		logger.warning("reddit.com: headless Chrome is easy to tell apart from the user's own")


def _route_guidance(subreddits: list[str]) -> str:
	"""Say which listing pages to visit, in place of the algorithmic home feed when possible."""
	if not subreddits:
		return (
			"No r/<name> link was found in the description. If it names subreddits another "
			"way, visit their /top/?t=day listings; otherwise read the user's home feed at the "
			"start URL."
		)
	listings = "\n".join(f"- {listing_url(name)}" for name in subreddits)
	return (
		"Visit these listing pages, in this order, rather than the algorithmic home feed. "
		f"They are the subreddits the description names:\n{listings}"
	)
