// Syntax-check the game's main inline <script> (the longest one; the short ones are Vercel's analytics tags).
// Usage: node tools/check.mjs
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (!blocks.length) { console.error('no inline <script> found'); process.exit(1); }
const main = blocks.reduce((a, b) => (b.length > a.length ? b : a));
try {
  new vm.Script(main, { filename: 'index.html <script>' });
  console.log(`OK — main script parses (${main.split('\n').length} lines)`);
} catch (e) {
  console.error(e.stack || String(e));
  process.exit(1);
}
