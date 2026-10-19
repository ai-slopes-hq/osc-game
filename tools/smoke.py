#!/usr/bin/env python3
"""Smoke test: load the game headless, jump to the opening, every level, every boss and free play,
let each run a few seconds, and fail on any page error.

Setup once:  pip install playwright && python3 -m playwright install chromium
Run:         python3 tools/smoke.py            (add --shots DIR to save a screenshot of each)
"""
import pathlib, sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = (ROOT / 'index.html').read_text(encoding='utf-8')
# Expose the game's closure for tests: T.ev('expression') evaluates inside the IIFE.
HOOK = "window.T = { ev: (c) => eval(c) };\n  showTitle();\n"
assert "  showTitle();\n" in HTML, 'hook anchor `  showTitle();` not found'
HTML = HTML.replace("  showTitle();\n", HOOK, 1)

TARGETS = ['op', 'l0', 'b0', 'l1', 'b1', 'l2', 'b2', 'l3', 'b3', 'l4', 'b4', 'l5', 'b5', 'l6', 'b6', 'l7', 'b7', 'l8', 'b8', 'l9', 'b9', 'free']
shots = pathlib.Path(sys.argv[sys.argv.index('--shots') + 1]) if '--shots' in sys.argv else None

def ev(page, code):
    return page.evaluate('T.ev(%r)' % code)

failed = False
with sync_playwright() as p:
    browser = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    for target in TARGETS:
        page = browser.new_page(viewport={'width': 1100, 'height': 700})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content(HTML)
        page.wait_for_timeout(150)
        ev(page, "god = true; ['ground','ceil','tall'].forEach(k => tutDone.add(k))")
        ev(page, f"testJump('{target}')")
        page.wait_for_timeout(1500 if target == 'op' else 200)
        if target != 'op':
            for _ in range(40):  # skip dialogue
                if ev(page, '!!storyQ'):
                    ev(page, 'storySkip()')
                page.wait_for_timeout(60)
        page.wait_for_timeout(3000)
        state, boss = ev(page, 'state'), ev(page, 'boss && boss.key')
        ok = not errors and state in ('play', 'story')
        failed |= not ok
        print(f"{'ok ' if ok else 'ERR'} {target:5} state={state} boss={boss} {errors[:2] if errors else ''}")
        if shots:
            shots.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(shots / f'{target}.png'))
        page.close()
    browser.close()
sys.exit(1 if failed else 0)
