# scrollforme: agent notes

Read `README.md` first for what the tool does and how a run flows.

## Project facts

- Python 3.12 managed with `uv`. Code is indented with tabs (enforced by `ruff format`). Imports go in groups (standard library, third party, local), and each group is sorted by line length, not alphabetically, which is why ruff's `I` rule is off.
- `modules/<domain>/` holds one Python package per website, and each exports only `browse(description: str) -> dict`. The dotted folder names can't be imported normally; `site_modules.load_browse` loads them from their files. The shipped modules are stubs that call `agent.browse_site`.
- `src/scrollforme/`:
  - `config`: TOML → settings, plus `use_settings`/`get_settings`, because `browse()` takes no settings argument.
  - `site_modules`: the module loader.
  - `digest`: runs every configured source's module and writes digest.json + digest.html (`build_digest`, `rerender`).
  - `agent`: Agent SDK options, prompt and `browse_site`.
  - `models`: the per-source result record.
  - `browser`: manual login.
  - `render` + `templates/`: generic HTML rendering of free-form dicts.
  - `cli`: thin argparse wrapper over `digest`, plus `serve`.
  - `server/`: the local FastAPI app for the web UI. `guard.py` refuses non-localhost Hosts, cross-site Origins and non-JSON writes; keep it, because the config names programs the server runs.
- `web/`: the SvelteKit SPA (setup wizard and dashboard), on the user's web standard. Read `web/AGENTS.md` before changing it.
- The agent's output schema is a free-form object. Live runs showed the model sends nested lists as JSON-encoded strings, even with a recursive schema, so `agent.decode_nested_json` decodes them.
- Personal files are git-ignored and must stay out of commits: `scrollforme.toml`, `profile/` (holds real login cookies), `output/`.

## Safety invariants

Do not weaken these without the user's explicit agreement:

1. The browsing agent gets:
   - `tools=[]`, `permission_mode="dontAsk"` and `setting_sources=[]`;
   - only the tools in `agent.READ_ONLY_BROWSER_TOOLS`, with `WRITING_BROWSER_TOOLS` disallowed;
   - `strict_mcp_config=True` and `ENABLE_CLAUDEAI_MCP_SERVERS=false`.

   The last two settings matter: without them the account's claude.ai connectors (Google Drive and others) load into the agent. Adding a tool that can type, click, upload, run scripts or write files gives injected feed content a way to act as the logged-in user. `tests/test_agent.py` pins all of this, and the SDK init message's `tools` list is how to check it live.
2. The agent returns JSON. Only `render.py`, with autoescaping on, produces HTML, and only `http(s)` strings become links.
3. Every site visit has `max_turns` and `max_budget_usd`.

## Testing

`uv run pytest` runs offline. A live run needs a logged-in `profile/`, Chrome and an Anthropic credential, so it is a manual check, not a unit test.

## Tasks

Use the Backlog.md MCP tools (or the `backlog` CLI) for work items in `backlog/`.
