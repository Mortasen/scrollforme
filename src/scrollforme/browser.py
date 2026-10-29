"""Open the dedicated browser profile by hand so the user can log in once.

Chrome refuses remote debugging on its default profile, and a profile already
open in the user's own Chrome is locked, so scrollforme keeps its own profile.
"""

import subprocess

from loguru import logger

from scrollforme.config import BrowserSettings


def open_profile_for_login(browser: BrowserSettings, urls: list[str]) -> None:
	"""Launch Chrome on the scrollforme profile and wait until the user closes it."""
	browser.profile_dir.mkdir(parents=True, exist_ok=True)
	command = [browser.chrome_binary, f"--user-data-dir={browser.profile_dir}", *urls]
	logger.info("Log in to each site, then close the browser window to finish.")
	subprocess.run(command, check=False)
