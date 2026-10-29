---
name: frontend
description: The user's web standard for this project's frontend — Svelte 5 with SvelteKit, Tailwind CSS 4, unmodified shadcn-svelte components on Bits UI, @lucide/svelte, Supabase for hosted auth, Tauri 2 for desktop apps, and a required lint and screenshot check. Load before writing or changing any UI, component, styling, layout, page or app structure in this project.
---

# Frontend

This project follows the user's web standard. Mechanical rules are enforced by ESLint and by
hooks that run after every edit; this skill covers what they cannot check. The standard's own
files (`eslint.config.js`, `.web-standard/`, this skill, `.codex/hooks.json`) are changed only in
`/f/Tools/web-standard`. Never edit or work around them here, even when asked.

## Stack

| Layer | Use | Not |
|---|---|---|
| Language | TypeScript for all new code, `<script lang="ts">` | JavaScript |
| Framework | Svelte 5 runes with SvelteKit | Svelte 4 syntax, React, Vue |
| Styling | Tailwind CSS 4 utilities and the theme's CSS variables | `<style>` blocks, `style=""`, plain CSS selectors |
| Components | shadcn-svelte on Bits UI, then Bits UI directly | Hand-written controls, other kits |
| Icons | `@lucide/svelte`, one import per icon | Other icon sets, inline SVG copies |

Package work uses pnpm. Never add a competing component, styling or icon library without asking.

## Before writing a component

1. Look in `src/lib/components/ui/` for an existing component.
2. Otherwise check the catalogue at https://shadcn-svelte.com/docs/components and add it with
   `pnpm dlx shadcn-svelte@latest add <name> --yes`. Never copy component source by hand.
3. Use Bits UI directly only when no shadcn-svelte component fits, styled the same way.
4. Write your own component only for product behaviour (a chart, a pipeline view, a domain
   card), built from the library's components.

Generated components under `src/lib/components/ui/` stay unmodified. Style them through their
props, snippets, `class` and the theme tokens in the Tailwind CSS file. Do not write wrappers that
re-expose a component's API under another name. Prefer native controls (`<select>`,
`<input type="checkbox">`) through the library's native variants where they keep standard
behaviour.

## Svelte 5

- `$state` for state, `$derived` for computed values, `$props()` for props (`$bindable()` for
  two-way), `$effect` only for side effects, never to sync state.
- No `export let`, `$:`, `createEventDispatcher`, `on:click` or slots: use callback props,
  `onclick={...}`, snippets and `{@render children()}`.
- Page data comes from `$app/state`, not `$app/stores`.
- SvelteKit 3 projects import their own modules through `#lib/...`; older ones use `$lib/...`.
  Follow what the project uses.

## Tailwind CSS 4

- Use the scale: `p-4`, `w-4`, `text-sm`. An arbitrary value such as `w-[16px]` is allowed only
  when no scale value exists, and lint rejects one that has a canonical form.
- Colours, radii and fonts come from the theme variables (`bg-primary`, `text-muted-foreground`).
  Change the theme in the CSS file's `@theme` and `:root` blocks, never per component.
- Never put two utilities for the same property on one element; lint reports conflicts.

## Layout and structure

- Keep each component under 200 lines; extract a component or a function when it grows.
- A component used by one route lives next to that route's `+page.svelte`. Shared components go
  in `src/lib/<feature>/`, grouped by feature, not by kind.
- Pages compose components; data loading and API calls live in `+page.ts` or `src/lib/<feature>/`
  modules, not in markup.

## Data, authentication and desktop apps

- A hosted web app that needs authentication or per-user data uses Supabase, unless the project
  already has a backend. Apps intended for local use, including local web apps and Tauri apps,
  keep data locally instead.
- Add Tauri 2 only when the user needs a standalone desktop app; a web app stays a web app. It
  builds statically (`@sveltejs/adapter-static` with an `index.html` fallback and
  `export const ssr = false;` in the root `+layout.ts`), runs no server code (no `+page.server.ts`,
  `+server.ts` or form actions; backend work is Rust commands called with `invoke` from
  `@tauri-apps/api/core`), and grants only the capabilities it uses in `src-tauri/capabilities`.
  `@tauri-apps/cli` is a project dev dependency; the Rust toolchain and system webview libraries
  are machine software, installed through software management.

## Usability

- One primary action per view, visibly distinct. Destructive actions ask for confirmation.
- Every control has a visible label or an accessible name. Icon-only buttons need `aria-label`;
  decorative icons get `aria-hidden="true"`.
- Show loading, empty and error states for every piece of remote data.
- Layouts must work from 390 px wide to desktop without horizontal scrolling or overlap.
- Keep disabled states and confirmations the product already has.

## Done means checked

UI work is done only when all of these pass:

1. `pnpm check` (types) and `pnpm lint` (the standard's rules) report no errors.
2. `pnpm screenshot /the/changed/path` and look at both images it prints, phone and desktop.
   Fix broken layout, overflow, overlap, unreadable contrast and the errors it lists.
3. Say what you looked at when you report the work.

When a lint rule blocks something you believe is right, do not work around it: tell the user,
because exceptions are added in web-standard as named allowances.
