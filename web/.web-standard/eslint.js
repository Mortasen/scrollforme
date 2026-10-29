/**
 * The web standard's ESLint configuration, delivered into `.web-standard/eslint.js`.
 *
 * Order is the enforcement: stack presets first, then the project's own entries from the optional
 * `eslint.project.js` with any `ignores` stripped, then the enforced rules last so no project
 * entry can switch them off. `noInlineConfig` voids `eslint-disable` comments in scripts, and
 * `svelte/comment-directive: off` voids them in Svelte template HTML comments, which
 * `noInlineConfig` does not reach. Edit this in web-standard, never in a project.
 */
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import js from '@eslint/js';
import globals from 'globals';
import ts from 'typescript-eslint';
import svelte from 'eslint-plugin-svelte';
import prettier from 'eslint-config-prettier';
import tailwind from 'eslint-plugin-better-tailwindcss';
import { includeIgnoreFile } from 'eslint/config';


const ROOT = path.resolve(import.meta.dirname, '..');
const SETTINGS = JSON.parse(readFileSync(path.join(import.meta.dirname, 'config.json'), 'utf8'));
const MARKUP = ['**/*.svelte'];
const SCRIPTS = ['**/*.ts', '**/*.svelte.ts', '**/*.js', '**/*.svelte.js'];


export default [
	...gitignoreEntries(),
	{ ignores: ['.svelte-kit/', 'build/', 'dist/', '.web-standard/', ...SETTINGS.generatedPaths] },
	js.configs.recommended,
	...ts.configs.recommended,
	...svelte.configs.recommended,
	prettier,
	...svelte.configs.prettier,
	{ languageOptions: { globals: { ...globals.browser, ...globals.node } }, rules: { 'no-undef': 'off' } },
	svelteParser(),
	...(await projectEntries()),
	...enforcedRules(),
	{ linterOptions: { noInlineConfig: true } },
];


function gitignoreEntries() {
	const gitignore = path.join(ROOT, '.gitignore');
	return existsSync(gitignore) ? [includeIgnoreFile(gitignore)] : [];
}


function svelteParser() {
	return {
		files: [...MARKUP, '**/*.svelte.ts', '**/*.svelte.js'],
		languageOptions: { parserOptions: { projectService: true, extraFileExtensions: ['.svelte'], parser: ts.parser } },
	};
}


/** Load the project's own entries, without `ignores`, or none when it has no eslint.project.js. */
async function projectEntries() {
	const file = path.join(ROOT, 'eslint.project.js');
	if (!existsSync(file)) return [];
	const entries = (await import(pathToFileURL(file).href)).default ?? [];
	return [entries].flat().map(({ ignores: _ignored, ...entry }) => entry);
}


function enforcedRules() {
	const tailwindSettings = { entryPoint: SETTINGS.tailwindEntryPoint, rootFontSize: 16 };
	return [
		{
			files: [...MARKUP, ...SCRIPTS],
			plugins: { 'better-tailwindcss': tailwind },
			settings: { 'better-tailwindcss': tailwindSettings },
			rules: {
				'better-tailwindcss/enforce-canonical-classes': 'error',
				'better-tailwindcss/no-conflicting-classes': 'error',
				'better-tailwindcss/no-duplicate-classes': 'error',
				'better-tailwindcss/no-deprecated-classes': 'error',
			},
		},
		{
			files: MARKUP,
			rules: {
				'svelte/no-inline-styles': 'error',
				'svelte/comment-directive': 'off',
				'no-restricted-syntax': ['error', {
					selector: 'SvelteStyleElement',
					message: 'No <style> blocks: style with Tailwind classes and theme tokens.',
				}],
			},
		},
	];
}
