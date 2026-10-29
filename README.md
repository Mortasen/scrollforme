# scrollforme

**Get your evenings back from the feed.** Reddit, Instagram and similar sites are built to keep you scrolling: infinite feeds, recommendations and "one more post". For people already stretched thin by work, this is compression burnout's quiet tax. The few minutes you meant to spend checking what your friends posted or what's new in your field turn into an hour.

scrollforme does the scrolling for you. You say in plain words what you actually use each site for ("my friends' posts", "new open models in r/LocalLLaMA"). A local AI agent visits each site in a browser that's logged in as you. It takes only what serves that purpose and hands back **one static page that ends**: no infinite scroll, no recommendations, no notifications, no like counts.

**Who it's for:** anyone who checks a few feeds for a real reason and loses far more time to them than that reason needs.

**How it gives time back:** reading a short digest takes a couple of minutes, not an open-ended session. It adds no alerts or prompts. You open the page when you want it, read it, and you're done.

Everything runs on your machine, in **your everyday browser**: the agent attaches to the Chrome or Firefox you already use, with your own logins, so sites see your normal browser. It uses that browser's DevTools MCP server ([chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) or [firefox-devtools-mcp](https://github.com/mozilla/firefox-devtools-mcp)) and runs on the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk).

## Quick start (web app)

Requirements:
- [uv](https://docs.astral.sh/uv/)
- [pnpm](https://pnpm.io/)
- your everyday Google Chrome (with Node.js for `npx`) or Firefox (with `firefox-devtools-mcp` installed)
- for Chrome: open `chrome://inspect/#remote-debugging` once and allow remote debugging; Chrome asks you to approve the connection. For Firefox: start it with `firefox --marionette`.
- a Claude Code login or an `ANTHROPIC_API_KEY`

```bash
uv sync
pnpm --dir web install && pnpm --dir web build
uv run scrollforme serve        # open http://127.0.0.1:8765/
```

The setup page walks you through it:
1. Check this machine.
2. Choose your sites and describe what you use each for.
3. Set limits on turns and dollars per site.
4. Save. There's no login step: scrollforme uses the browser you're already logged in to.

The dashboard then shows your latest digest, a **Run now** button with live progress, and earlier digests.

## How it works

```
scrollforme.toml ─► for each [[sources]] ─► modules/<domain>.browse(description) ─► dict
                                                   │
                                                   ▼  scrollforme.agent.browse_site(...)
                                     Claude agent ─► browser DevTools MCP ─► your Chrome / Firefox

dicts ─► output/<timestamp>/digest.json ─► digest.html (Jinja2)
```

- **One module per website.** `modules/reddit.com/`, `modules/instagram.com/` and so on. Each is a Python package exporting one function, `browse(description: str) -> dict`. `description` is your plain-language account of what you use the site for. The returned dict is free-form: whatever the module extracted.
- **One visit per source**, one at a time. Each visit has its own turn and dollar limits, and the agent is told to stop once it has what the description asks for.
- **The agent only reads.** It has no built-in tools (no shell and no file access), and only read-only browser tools are allowed: list and open tabs, navigate, wait, read the page and press keys to scroll. Any other call is denied without a prompt. No other MCP server loads, including your Claude Code config and your claude.ai connectors. Feed text is written by strangers and may contain prompt injection, and the browser is logged in as you.
- **The agent returns data, never HTML.** A fixed, autoescaped template renders each dict generically, with a CSP that blocks all scripts. An entry with a `title` and an `http(s)` `url` becomes a headline link, and only `http(s)` strings ever become links.

## Writing a module

Create `modules/<domain>/__init__.py`, export only `browse`, and name the domain in a `[[sources]]` entry. The stubs delegate to the shared agent with a start URL and some site notes:

```python
from scrollforme.agent import browse_site

__all__ = ["browse"]


def browse(description: str) -> dict:
	return browse_site("example.com", "https://example.com/feed", description, "Skip ads.")
```

A module can do anything else it likes instead (an API, RSS, its own parsing) as long as it returns a dict. Folder names contain dots, so `scrollforme.site_modules` loads them from their files, not by `import`. Relative imports inside a module still work.

## Your everyday browser, unchanged

scrollforme doesn't launch its own browser or keep a profile of its own. It attaches to the browser you already use, opens a new tab for each visit, and leaves your other tabs alone. Sites see your normal browser with your normal logins, as if you'd scrolled them yourself.

## Command line

Requirements: as in the quick start.

```bash
uv sync
cp scrollforme.example.toml scrollforme.toml   # then edit sources and descriptions
uv run scrollforme run                         # writes output/<timestamp>/digest.html
uv run scrollforme render output/<run>/digest.json   # re-render after template changes
```

From Python (for a scheduler or another front end), call `scrollforme.digest.build_digest(load_settings())`. It returns the path of the HTML file. It runs the modules named in `[[sources]]`, not every folder in `modules/`, because each module needs your description. It also warns about module folders that no source uses.

**Authentication.** The Agent SDK uses `ANTHROPIC_API_KEY` if it is set. Otherwise it uses your Claude Code login.

**Cost.** The default model is `claude-opus-5-5` at `medium` effort, capped by `max_budget_usd` per site visit. You can change all three in `[agent]`.

## Development

```bash
uv run scrollforme serve          # API on :8765
pnpm --dir web dev                # frontend with hot reload; /api is proxied to :8765
uv run pytest
uv run ruff format . && uv run ruff check .
```

Tasks are tracked with [Backlog.md](https://github.com/MrLesk/Backlog.md) in `backlog/`.
