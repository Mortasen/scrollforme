# scrollforme: agent notes

Read `README.md` first for what the tool does and how a run flows.

## Project facts

- Python 3.12 managed with `uv`. Code is indented with tabs (enforced by `ruff format`). Imports go in groups (standard library, third party, local), and each group is sorted by line length, not alphabetically, which is why ruff's `I` rule is off.
- `src/scrollforme/`: `config` (TOML → settings), `models` (agent output schema + validation), `agent` (Agent SDK options and prompt), `browser` (manual login), `render` + `templates/` (HTML), `cli`.
- Personal files are git-ignored and must stay out of commits: `scrollforme.toml`, `profile/` (holds real login cookies), `output/`.

## Safety invariants

Do not weaken these without the user's explicit agreement:

1. The browsing agent gets `tools=[]`, `permission_mode="dontAsk"`, `setting_sources=[]`, and only the tools in `agent.READ_ONLY_BROWSER_TOOLS`. Adding a tool that can type, click, upload, run scripts or write files gives injected feed content a way to act as the logged-in user.
2. The agent returns JSON. Only `render.py`, with autoescaping on, produces HTML.
3. Every source has `max_items`, and every run has `max_turns` and `max_budget_usd`.

## Testing

`uv run pytest` runs offline. A live run needs a logged-in `profile/`, Chrome and an Anthropic credential, so it is a manual check, not a unit test.

## Tasks

Use the Backlog.md MCP tools (or the `backlog` CLI) for work items in `backlog/`.
