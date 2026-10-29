#!/usr/bin/env node
/**
 * `pnpm screenshot <path-or-url> [...]`: look at the rendered app before calling UI work done.
 *
 * For a path such as `/settings` it starts the Vite dev server on a free port, captures each page
 * full-length at a phone width and a desktop width with the installed Chrome through
 * playwright-core, prints the image paths and any console or page errors, and stops the server.
 * A full URL is captured as given. Images go to .web-standard/screenshots/, which Git ignores.
 */
import { spawn, type ChildProcess } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import type { Browser, BrowserType, Page } from 'playwright-core';


const ROOT = path.resolve(import.meta.dirname, '..', '..');
const OUT_DIR = path.join(ROOT, '.web-standard', 'screenshots');
const WIDTHS = { phone: 390, desktop: 1280 };
type DevServer = { child: ChildProcess; url: string };
const SERVER_READY = /Local:\s+(http:\/\/\S+?)\/?\s/;


await main(process.argv.slice(2));


async function main(targets: string[]): Promise<void> {
	if (!targets.length) return fail('usage: pnpm screenshot <path-or-url> [...]');
	const chromium = await loadChromium();
	const server = targets.some(isPath) ? await startDevServer() : null;
	try {
		const browser = await chromium.launch({ channel: 'chrome' });
		for (const target of targets) await capture(browser, server ? new URL(target, server.url).href : target);
		await browser.close();
	} finally {
		server?.child.kill();
	}
}


async function loadChromium(): Promise<BrowserType> {
	try {
		return (await import('playwright-core')).chromium;
	} catch {
		return fail('playwright-core is missing: run `pnpm install` (web-standard sync adds it).');
	}
}


async function capture(browser: Browser, url: string): Promise<void> {
	mkdirSync(OUT_DIR, { recursive: true });
	for (const [name, width] of Object.entries(WIDTHS)) {
		const page = await browser.newPage({ viewport: { width, height: 900 } });
		const errors = collectErrors(page);
		await page.goto(url, { waitUntil: 'networkidle' });
		const file = path.join(OUT_DIR, `${slug(url)}-${name}.png`);
		await page.screenshot({ path: file, fullPage: true });
		console.log(`${name} (${width}px): ${path.relative(ROOT, file)}`);
		for (const error of errors) console.log(`  error: ${error}`);
		await page.close();
	}
}


function collectErrors(page: Page): string[] {
	const errors: string[] = [];
	page.on('console', (message) => message.type() === 'error' && errors.push(message.text()));
	page.on('pageerror', (error) => errors.push(error.message));
	return errors;
}


/** Start `vite dev` on a free port and resolve once it prints its local URL. */
function startDevServer(): Promise<DevServer> {
	const vite = path.join(ROOT, 'node_modules', '.bin', 'vite');
	const child = spawn(vite, ['dev', '--port', '0', '--strictPort', 'false'], { cwd: ROOT, env: { ...process.env, NO_COLOR: '1' } });
	return new Promise((resolve, reject) => {
		let output = '';
		child.stdout.on('data', (chunk: Buffer) => {
			output += chunk.toString();
			const match = SERVER_READY.exec(output);
			if (match) resolve({ child, url: match[1]! });
		});
		child.on('exit', () => reject(new Error(`vite dev exited:\n${output}`)));
	});
}


function isPath(target: string): boolean {
	return target.startsWith('/');
}


function slug(url: string): string {
	const { pathname } = new URL(url);
	return pathname.replace(/^\/|\/$/g, '').replace(/[^\w-]+/g, '_') || 'index';
}


function fail(message: string): never {
	console.error(message);
	process.exit(1);
}
