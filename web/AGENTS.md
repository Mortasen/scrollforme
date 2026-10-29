<!-- web-standard:begin (managed by web-standard; change it in /f/Tools/web-standard and run sync) -->

## Web standard

This web app follows the user's web standard: TypeScript, Svelte 5 with SvelteKit, Tailwind CSS 4,
shadcn-svelte on Bits UI and `@lucide/svelte`.

- Load the `frontend` skill before any frontend work, and follow it.
- UI work is done only when `pnpm check` and `pnpm lint` pass and you have looked at
  `pnpm screenshot <path>` output at phone and desktop widths.
- `eslint.config.js`, `.web-standard/`, `.codex/hooks.json`, the `frontend` skill links and this
  section are owned by the standard. Never edit them here, even when asked: say the change belongs
  in /f/Tools/web-standard. Project-specific lint rules go in `eslint.project.js`; standard rules
  cannot be switched off there or with disable comments.

<!-- web-standard:end -->
