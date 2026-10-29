"""reddit.com: the user's subreddits and home feed, without the endless scroll.

The visit must look to Reddit like the user browsing it themselves: the normal www.reddit.com
pages in a new tab of their own everyday browser, opened one at a time and scrolled a screen at a
time with PageDown. So there are no shortcuts a person would not take (.json listings, the API,
RSS, old.reddit.com), and a challenge or block page ends the visit instead of being worked around.
"""

from scrollforme.agent import browse_site

from .subreddits import listing_url, subreddits_named_in

__all__ = ["browse"]

_HOME_FEED_URL = "https://www.reddit.com/"

# Post pages the agent may open per visit, on top of one listing page per subreddit.
_MAX_POST_PAGES = 5

_BROWSING_GUIDANCE = f"""\
Browse the way the user would by hand, so the visit looks like theirs. Use only the ordinary
www.reddit.com pages a person opens: subreddit listings, the home feed and post pages. Never
request .json, /api/, RSS or old.reddit.com URLs, and never follow links off Reddit. Stay in the
one tab you opened and go from page to page with navigate_page in it. On a listing, press PageDown
a few times, once per screen, letting new posts load in between; never jump to the end. Open a
post page only when the description asks about comments or a title alone does not say what the
post is, and open at most {_MAX_POST_PAGES} of them.

Read pages with take_snapshot, or with get_page_text where it is available, which is cheaper.
Each snapshot costs context, so take one after a few PageDowns rather than after every press. A
post shows up as a link whose URL contains /comments/, with the title as its text and the
subreddit (r/<name>) next to it. Skip anything marked Promoted or Sponsored.

Leave cookie banners, "open in app" prompts and other overlays alone; the posts are in the page
underneath. If one hides them, press Escape once, as a person would. If you see "Prove your
humanity", a CAPTCHA, a "blocked" notice or a logged-out page, stop at once. Do not retry or look
for a way around it. Return {{"notice": "..."}} saying what you saw and that the user should open
Reddit in their own browser and sort it out there.

For each post give its title, subreddit, url (the permalink as a full https://www.reddit.com URL)
and a one-line summary. Leave out scores, vote counts and comment counts."""


def browse(description: str) -> dict:
	"""Visit Reddit for the purpose in `description` and return what was found."""
	subreddits = subreddits_named_in(description)
	start_url = listing_url(subreddits[0]) if subreddits else _HOME_FEED_URL
	guidance = f"{_route_guidance(subreddits)}\n\n{_BROWSING_GUIDANCE}"
	return browse_site("reddit.com", start_url, description, guidance)


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
