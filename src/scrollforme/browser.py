"""Open the dedicated browser profile by hand so the user can log in once.

Chrome refuses remote debugging on its default profile, and a profile already
open in the user's own Chrome is locked, so scrollforme keeps its own profile.
"""

import subprocess

from loguru import logger

from scrollforme.config import BrowserSettings

# nodriver, which stealth-browser-mcp launches Chrome through, always passes
# --password-store=basic. Cookies are encrypted with a key chosen by this
# flag, so the login launch must match it or the agent finds itself logged out.
NODRIVER_COMPATIBLE_ARGS = ["--password-store=basic", "--no-first-run"]


def start_login_browser(browser: BrowserSettings, urls: list[str]) -> subprocess.Popen:
	"""Launch Chrome on the scrollforme profile without waiting; the caller tracks the process."""
	browser.profile_dir.mkdir(parents=True, exist_ok=True)
	return subprocess.Popen(build_login_command(browser, urls))


def open_profile_for_login(browser: BrowserSettings, urls: list[str]) -> None:
	"""Launch Chrome on the scrollforme profile and wait until the user closes it."""
	browser.profile_dir.mkdir(parents=True, exist_ok=True)
	logger.info("Log in to each site, then close the browser window to finish.")
	subprocess.run(build_login_command(browser, urls), check=False)


def build_login_command(browser: BrowserSettings, urls: list[str]) -> list[str]:
	"""The Chrome command line for a manual login session on the profile."""
	profile_arg = f"--user-data-dir={browser.profile_dir}"
	return [browser.chrome_binary, profile_arg, *NODRIVER_COMPATIBLE_ARGS, *urls]
