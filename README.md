# scrollforme

Feeds like Reddit and Instagram are built to keep you scrolling. scrollforme lets an AI agent do the scrolling instead. It reads the feeds you choose in a browser that is already logged in as you, takes a fixed number of posts from each, and writes one static HTML page that ends.

Everything runs on your machine. The agent drives Chrome through [stealth-browser-mcp](https://github.com/vibheksoni/stealth-browser-mcp) and runs on the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk).

## How it works

```
scrollforme.toml ─► for each source ─► Claude agent ─► stealth-browser MCP ─► Chrome (your profile)
                                            │
                                            ▼  JSON matching models.SOURCE_DIGEST_SCHEMA
                        validate + cap ─► output/<timestamp>/digest.json ─► digest.html (Jinja2)
```

- **One agent run per source**, one source at a time. Each run has its own turn and dollar limits and is told the most items it may collect.
- **The agent only reads.** It has no built-in tools (no shell and no file access), and only these browser tools are allowed: spawn, navigate, wait, scroll, query and read the page, and close. Any other call is denied without a prompt. No other MCP server loads, including your Claude Code config and your claude.ai connectors. Feed text is written by strangers and may contain prompt injection, and the browser is logged in as you.
- **The agent returns data, never HTML.** Its JSON is validated and cut down to the item limit. Then a fixed, autoescaped template renders it, with a CSP that blocks all scripts. Like counts and follower counts are left out on purpose.

## Why a separate browser profile

Chrome 136 and later no longer allow remote debugging on your default profile, and Chrome locks any profile that is already open. So scrollforme keeps its own persistent profile in `profile/`. You log in to each site there once and the logins persist.

## Setup

Requirements: [uv](https://docs.astral.sh/uv/), Google Chrome, and a stealth-browser-mcp checkout with its own venv (the default location is `~/.local/src/stealth-browser-mcp`).

```bash
uv sync
cp scrollforme.example.toml scrollforme.toml   # then edit sources, paths, limits
uv run scrollforme login                       # opens Chrome on the profile; log in, then close it
uv run scrollforme run                         # writes output/<timestamp>/digest.html
uv run scrollforme render output/<run>/digest.json   # re-render after template changes
```

**Authentication.** The Agent SDK uses `ANTHROPIC_API_KEY` if it is set. Otherwise it uses your Claude Code login.

**Cost.** The default model is `claude-opus-5-5` at `medium` effort, capped by `max_budget_usd` per source. You can change all three in `[agent]`.

## Development

```bash
uv run pytest
uv run ruff format . && uv run ruff check .
```

Tasks are tracked with [Backlog.md](https://github.com/MrLesk/Backlog.md) in `backlog/`.
