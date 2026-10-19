# AGENTS.md — Oscillator Adventures («Приключения осциллятора»)

Guide for anyone — human or coding agent (Claude Code, Codex, Cursor, Copilot, Aider…) — picking up this repo.
Read this file before changing anything. `CLAUDE.md` just points here.

## What this is

A browser side-scroller drawn on an oscilloscope screen. The player is a **sine wave** running along the trace.
It plays a melody; **jumping** lifts the melody an octave (+24 on a double jump), **folding** (a wavefolder squeeze)
lets it crawl under hanging functions and drops it an octave. Obstacles are maths functions, effect gates
(rectifier, ring modulator) and boss fights. Story: analog signals (Triangle, Sine, Meander, old Complex oscillator)
are taken by digital forms led by **Wavetable**; the Sine — "just a test signal" — goes to get them back.

- **Everything is one static file: `index.html`** — HTML, CSS and one `<script>` (an IIFE). Canvas 2D + Web Audio.
  No build step, no bundler, no runtime dependencies, no server code.
- **Player-facing text is Russian.** Code, comments and commit messages are English. Comments explain *why*.
- Mobile-first: phones get full-screen touch play (hold left half = fold, tap right half = jump).

## Quick start

```bash
git clone <this repo> && cd osc-game
python3 -m http.server 8000          # any static server works
open http://localhost:8000/#test     # #test shows the level/boss jump menu
```

Keys: **Space / ↑** jump (again in the air = double), **↓ / S** fold, **P** pause, **M** mute, **G** god mode
(invulnerable, for testing), **F** full screen. On `localhost` and Vercel preview hosts the test menu is always on
and every level is unlocked.

## Checks — run before every PR

```bash
node tools/check.mjs                 # syntax-check the main script
pip install playwright && python3 -m playwright install chromium   # once
python3 tools/smoke.py               # opens the intro, every level, every boss, free play; fails on any page error
python3 tools/smoke.py --shots /tmp/shots    # …and saves a screenshot of each
```

Sound can't be checked by a script. If you change audio, say so in the PR and ask a human to listen.

## Workflow

| Branch | Deploys to | Who pushes |
|---|---|---|
| `staging` | Vercel **preview** (its own URL) | contributors, via PRs |
| `main` | **production** | maintainer only, by fast-forwarding `staging` after testing the preview |

1. Branch from `staging`, open the PR **into `staging`**. Never push to `main`.
2. One concern per PR. In the description: what changed for the player, how you checked it (commands, screenshots),
   what you could not check (usually: how it sounds).
3. Keep `AGENTS.md` true: if you change a mechanic, a rule or a file layout, update the matching section here
   in the same PR.
4. Don't commit test screenshots or tool output (`.gitignore` covers the usual names).

## Hard rules

1. **One file, no build, no dependencies.** Fonts come from Google Fonts with system fallbacks. No npm packages at
   runtime (analytics are plain `<script>` tags served by Vercel).
2. **World units.** The world is 480 units wide, `GROUND = 238`, base height 300. `scale = cw / 480`; extra screen
   height becomes sky (`offY`). Text is drawn in screen pixels via `text()` / `textScreen()` so it stays readable.
3. **Colours are oscilloscope channels and carry meaning — don't repurpose them:**
   CH1 yellow `#f4e15a` = the Sine (player) · CH2 cyan = ground functions · CH3 magenta = hanging functions ·
   CH4 green = partials and "good" · red `#ff4d3d` = digital and danger (bosses, attacks, effect gates) ·
   orange = Complex / FM · lavender = Triangle · gold = mode capsules.
4. **Fair input.** Anything timing-based is judged at the moment of the press, against what the player *sees and
   hears* (see `heardBeat()` — it compensates audio output latency). Hints sit where the player looks, not only in a HUD.
5. **Boss fights:** no regular obstacles, no capsules. A boss with its own track mutes the Sine's part (`bossTrack`).
6. **Music reflects the fight:** Square's duty drives the synthwave pulse width, Bitcrusher's bit depth quantises the
   chiptune, Wavetable's stripped harmonics remove dubstep layers.
7. **Mobile is first-class.** The page *is* the game on every device (`playMode` is on from the first frame).
   Check new UI at 390×844 and 844×390. On phones (`MOB`) type is bigger and technical readouts are hidden.
8. **Short words.** A hint is 2–3 words, a toast is one thought, a boss callout is one big word or number.
9. **No clicks in audio.** Envelopes on a sounding voice use `setTargetAtTime` from the current value. A
   `setValueAtTime` jump on a playing gain clicks (and the delay echoes it). Exception: the chiptune's stepped envelope.
10. **The frame loop must never die:** `requestAnimationFrame` is the first line of `frame()`. All `localStorage`
    access goes through the `store` wrapper (it can throw).
11. **Phosphor look, crisp text.** The canvas fades by `1 − e^(−70·dt)` per frame (short trails). Text that changes
    is drawn with `crispText()` / `bigText()` (wipes the phosphor under it); dialogue sits on `darkPlate()`.
    While the screen is pixelated (`pixOn`), `textScreen`/`crispText` write to a text layer `txCv` above the pixels and
    `render()` points `ctx` at it once the world is drawn — HUD, callouts and dialogue stay sharp.
12. **Every new thing explains itself the first time** (`ob.hint` / `tagHint`).

## Map of the script (in file order — line numbers drift, search by name)

- **World constants** — `WORLD_W`, `GROUND`, `HERO_*`, `GRAV`, `JUMP_V`, `DJUMP_V`, `SPEED_MAX`, `MINC`, `COL`.
- **Story data** — `CAST` (name, colour, wave, `digital`, `pitch` for key clicks), `OPENING`, `BOSSES` (`intro`/`outro` + fight params).
- **Levels** — `LEVELS` (key, mode, bpm, speed, length, obstacle pools, `intro`, `boss`), `NEED` (partials to open the boss),
  `STEPS` (scales), `MODES` (+3 free-play modes), `POWERS` (capsules MDR/TRI/CPX).
- **Waves** — `waveVal(th, type, t)`: shared shapes for hero, sprites, capsules, bosses; `wtFrame`.
- **Audio** — `initAudio`, scheduler `schedule` / `playStep`, voices and tracks (`orchestra`, `synthwave`, `drums`,
  `chiptune`, `dubstep`, `levelBand`), the Sine's part (`MOTIFS`, `SYN`, `melNote`, `chordTone`), effects, `sfx*`, `musicFilter`.
- **Obstacles** — `makeOb(kind, x)`; spawning — `spawn`, `tagHint`; reset — `reset`.
- **Bosses** — `spawnBoss`, `hitBoss`, `bossDone`, then one block per boss (`updatePwm`, `updateCrush`, `updateChords`,
  `seqRound`/`seqJudge`/`seqEvaluate`, `wtShoot`/`catchHarm`).
- **Player** — `collide`, `pressJump`, `doJump`, `takeHit`, `givePower`, `start`, `levelUp`, `die`, `gameOver`, `pause`/`resume`.
- **Onboarding** — `tutTick`, `bestTakeoff`, `drawTut`.
- **Story engine** — `story`, `storyNext`, `storySkip`, opening scene (`makeOpening`, `runAct`, `sceneTick`).
- **Overlay & HUD** — `showTitle`, `showOverlay('over'|'paused')`, `renderLevelChips`, `hud`.
- **Input & layout** — keys, pointer on `#bezel`, `layoutPlay`, `enterPlayMode` / `exitPlayMode`, `toggleFs`.
- **Update** — `update(dt)`, `updateBoss(dt)`.
- **Drawing** — `trace` (two-pass glow), `drawScenery`, `drawBoss`, `drawSprite`, `drawStoryText`, `drawPartialGate`,
  `bossCallout`, `drawProgressBar`, `render(dt)`, `postFx` (Bitcrusher pixelation).
- **Loop** — `frame` (auto quality drop `lowQ` on weak phones), test menu `testJump`.

## Systems

### Hero and physics
`y` = height of the wave's bottom above ground, `vy` positive up. Jump `JUMP_V`, double `DJUMP_V`, 0.13 s jump buffer.
Fold (`foldHeld`) squeezes the amplitude `A_NORM → A_FOLD` and speeds up falling. Platforms (`platforms`) are shared
by bosses: land from above, `standing`, walk off the edge, `landOn(pf)`.

### Obstacles
`makeOb` returns `{ w, h, label, prof(u) }`, `u ∈ [0,1]` across the width.
Ground ones: `prof(u)` is a fraction of `h`. Hanging ones (`ground:false`): `prof(u)` is the gap above ground (≥ `MINC`).
Animated ones read `beatPos` (synced to audio). Effect gates (`gate:'rect'|'ring'`) don't kill, they apply an effect
(`applyFx`, state in `fx`). Tall walls never come twice in a row and leave room to land. Rectifier gates are rationed
(`rectAt`). **To add one:** a `case` in `makeOb`, optionally a `hint`, then add the kind to a level's pool in `LEVELS`.

Special kinds (all terms stay in English on screen):

| kind | what it does |
|---|---|
| `echo` | echo delay: the obstacle plus two fading copies one beat apart (`copy`, `span`). Hitting it leaves a `shadow` — you from 0.45 s ago, closing in from behind; it bites for 2 partials, lasts 7 s |
| `gcomp` | gate compressor: a tall wall squashed on every beat, recovering between — jump when it's low |
| `reso` | resonant peak: a Lorentzian spike that breathes over two beats; while on screen the music low-pass closes and resonates with it (`musicFilter`) |
| `nfloor` | noise floor (`zone:true`): a hissing strip on the ground — hurts only if you're standing on it; hiss rises as you approach (`noiseBedG`) |
| `fbk` | feedback (`monster:true`, red): starts tiny, grows exponentially once on screen, whines louder and higher (`fbOsc`/`fbG`) — jump it early |
| `dcs` | DC offset (`band:true`): a digital segmented snake whose body rides an offset drifting up and down over a bar — pass under or over |
| gates `pinv`, `snh` | phase invert flips the world upside down for 6 s (`flipK`, mirrored transform and world text) and thins the music (`musicHP`); sample & hold freezes the drawn/colliding Sine on each 8th note for 5 s (`hy()`, `snhY`) and crushes the bits |

All four gates (`rect`, `ring`, `pinv`, `snh`) share the `GATES` rationing. Glide ramps (`platforms`, `kind:'glide'`) spawn in
wide gaps: step on from the ground, ride up with portamento (`osc.detune` up to +700 ct) and a speed boost, get launched
off the end. **Time stretch** (`tst`) is a capsule offered at ≥ 118 BPM: 6 s at 0.72× world time and 0.75× tempo
(`bpmNow` vs `bpmBase`). **Rhythm bonus:** a jump within 9% of a beat (`rhythmCheck`, judged on `heardBeat`) doubles
partials picked up for 1.6 s.

### Partials = lives, and the Sonic-style pace
Each level starts with `START_PARTIALS = 4`. A hit (`takeHit`) costs `HIT_COST = 4`; they scatter and can be caught
back; 1.6 s invulnerability; a hit with none left ends the run. After a hit the toast says: 0 left — «следующий удар — последний», 1–4 — «осталось N · осторожно», more — just «осталось N». The same partials open the boss gate (`NEED[level]`).
On a level with a boss, speed and obstacle density follow `levelPartials / NEED` — closer to the gate is faster, losing
partials eases off; the music tempo follows speed.

### Onboarding
The first ground function, hanging function and tall wall slow the run to a freeze (`slow`, `update(dt * slow)`) exactly
where the move works; a card says what to press; the press performs the move. `bestTakeoff` simulates the jump over
the obstacle profile to find that point. Done steps are stored in `osc-adv-tut`.

### Levels
Ten levels (`LEVELS`), each with its own mode, genre (`band`), background (`scene`) and obstacle pool. Big-boss levels
alternate with genre levels that end in a mini-boss; **Wavetable is always the last level and the final boss.**

| # | Mode | Genre (`band`) | Scene | Signature obstacles | Boss |
|---|---|---|---|---|---|
| 1 | A Aeolian | pop (synth-pop) | `trees` | plain functions, noise floor | Square |
| 2 | C Harmonic minor | techno | `tunnel` | gate compressor, feedback | *Compressor* |
| 3 | D Dorian | chip | `graph` | FFT, comb, redux, S&H, rectify | Bitcrusher |
| 4 | G Mixolydian | reggae (one drop, dub echo) | `phyllo` | echo delay, resonant peak | *Limiter* |
| 5 | E Phrygian | trance | `liss` | AM, S&H ceilings, ring mod, phase invert | Supersaw |
| 6 | G Dorian | breaks (electro-breaks) | `spiro` | DC offset snake, S&H | *Arpeggiator* |
| 7 | F Lydian | glitch | `fractal` | all the digital gates mixed | Sequencer |
| 8 | C Ionian | ambient (no drums, a breather) | `aurora` | sparse, resonant peaks, phase invert | *Vocoder* |
| 9 | D Aeolian | dub (dub techno: minor-7 stabs into echo and a convolution reverb `rvbIn`) | `room` | echo delay, feedback, compressor | *Reverberator* |
| 10 | F# Aeolian | modern (progressive house) | `wt` | everything (`ALL_G`/`ALL_C`) | Wavetable |

**Approach effects.** Every boss level builds up to its boss gradually with `apS` (eased `levelPartials / NEED`, 1 when
the gate is open; `trackApproach`, `apBand(band)`), so the boss is heard and seen coming:

| Level → boss | What grows |
|---|---|
| 1 → Square | a square layer under the Sine (`uni` oscillators as squares); the drawn wave squares up (`heroSq`) |
| 2 → Compressor | the screen is squeezed from the sides, pumping on the kick (`drawSqueeze`, `sqz`, up to 46/120 units); lets go at the fight |
| 3 → Bitcrusher | bit depth 16 → 8 (`trackBits`, `lvlBits`): the voice crushes, the world pixelates (`crushPx`, `postFx`) |
| 4 → Limiter | a 0 dBFS ceiling comes down over the jumps (`limCeil()`, 330 → 150) |
| 5 → Supersaw | two detuned copies of the melody fade in, ±6 → ±46 ct (`uni`), the hero grows drifting ghosts |
| 6 → Arpeggiator | the melody's gaps fill with chord arpeggios, 8ths then 16ths (in `playStep`) |
| 7 → Sequencer | the glitch rhythm gains layers: 16th hats, extra kicks, rolls, ticks, then his step clock (`levelBand` glitch) |
| 8 → Vocoder | the Sine goes through two formant band-passes, a vowel per bar (`vocDry`/`vocWet`/`vocF`) |
| 9 → Reverberator | phosphor trails stretch (the fade slows from 70 to 14/s) and the Sine drowns in reverb (`rvbSine`) |
| 10 → Wavetable | the melody's FM index rises; the hero's wave morphs along the wavetable (`heroWt`) |

Free play runs on level 10; mode capsules switch mode, genre and scene together (`MODES[i].band/.scene`, `bandNow()`).
Difficulty formulas scale by `level / (LEVELS.length - 1)`, so adding a level doesn't break the curve.

### Bosses
`BOSSES[key]`: `who`, `hp`, `kind`, `y`, `tip`, `noAtk`, `ally`, `intro`, `outro`, `mini`.

| Level | Boss | `kind` | Mechanic | Music |
|---|---|---|---|---|
| 1 | Square (captured Meander) | `pwm` | Green pulse platforms; land → it collapses, duty `base` +6.5% (+2.5% in a chain); red inverted pulses are traps (−10%); he always pulls back to 50%; from 75% (`SQ_FINAL`) only an unbroken chain of `SQ_FINAL_CHAIN` counts; 97% wins | `synthwave`, pulse width = `duty` |
| 3 | Bitcrusher | `crush` | Catch "1" (+bit), "0" drops to checkpoint 4/8/12; 16 bits wins; screen pixelates | `chiptune` through quantiser = bits |
| 5 | Supersaw (Triangle) | `chords` | Chord platforms; land on the chord she plays; an atonal shield blocks and "leaks" the next chord | FM drums + off-beat bass |
| 7 | Sequencer | `seq` | "Simon says", centre screen: bar LISTEN (he plays a rhythm once), then every bar is REPEAT (tap it back — every tap counts, even mid-air) until it's right; the rhythm stays shown as a reference row above his steps, so you can sit a bar or two out and come in. Wrong → just try the next bar, nothing lost; right → a rest bar shows the next rhythm, then his call. Two rounds × 3 answers (`SEQ_RNDS`, `SEQ_NEED`), ±40% window on the heard beat | his steps + metronome |
| 10 | Wavetable | `harm` | Shoots, mostly alternating: dodge red (low → jump, mid → fold, high → stay), catch green = his next harmonic (h9 → h2); a red hit puts one back; Complex (ally) bends him with FM | `dubstep`, layers drop per harmonic |


Mini-bosses (`mini:true`, all in `updateMini` / `drawMini` / `arpLand`; the level's band keeps playing under them):

| Level | Mini-boss | Mechanic |
|---|---|---|
| 2 | Compressor `comp` | His threshold line drops on every downbeat (`compThr(compPhase())`), flashing a beat ahead — fold under it; between pumps catch green peaks (6) |
| 4 | Limiter `lim` | A 0 dBFS ceiling (`LIM_CEIL`) caps jumps; bricks float overhead — headbutt them while they're lit, on the skank (beats 2 and 4); off the beat you bounce. He also rolls ground obstacles |
| 6 | Arpeggiator `arp` | Staircases of note platforms UP / DOWN / UP·DOWN / RANDOM (`ARP_MODES`): land on every step in order without touching the ground; a slip replays it. The run slows to `ARP_SPEED` and each step is laid one jump's flight (`jumpAir(dh)` × speed) after the last, so a jump from anywhere on a step lands on the next |
| 9 | Reverberator `rvb` | Pads come by (`kind:'rvbpad'`); land on one and it throws your reflection at him, aimed ±24°. A miss bounces off the walls, ceiling and floor (`updateRvb`, `b.shots`), turns red and hurts you (2 partials) until it decays; his RT60 (`b.decay`, 1.3–3.2 s) drifts — long decay, more bounces. Run slows to `ARP_SPEED` |
| 8 | Vocoder `voc` | He asks for a vowel (`VOWELS`, formant synth `vowelSfx`); catch that one, a wrong one gives him a level back |

**To add a boss:** an entry in `BOSSES`, `boss:` on a level, init in `spawnBoss`, an `update*` branch in `updateBoss`,
a branch in `drawBoss`, a `bossCallout` in `render`, a `progressNow` case, lines in `CAST` (the test picker is built from `LEVELS`).

### HUD and feedback
One big short line per fight (`bossCallout(main, sub, colour, frac)`). Events are big and animated: `showPop(text,
colour, prio)` (partials "9/15", then "ЕЩЁ 3/2/1", "БОСС: …", "−4 ◎") and toasts via `bigText` (auto-fits the width).
A progress bar runs along the bottom (`drawProgressBar`): partials towards the gate on a level, progress to the win in
a fight; it blinks when the player holds < 4 partials; a loss rolls back with the lost stretch in red.
A dialogue always starts on a clean screen (`story()` clears pops, toasts, banners).
Timed effects stack at the top right, each with its own draining bar (`timers` in `render`: RECT, RING, INVERT,
S&H, ECHO shadow, on-beat ×2); a capsule power keeps its bar at the top centre. Defeated bosses: the captured analog
ones turn back (Square → Meander, Supersaw → Triangle), Wavetable becomes a sine, the digital ones keep their own
shape, just calmer.

### Story
`story(lines, done, scene)`; a line is `[who, text, action?]`. Letters type out with a key click per two letters
(`keyClick`, pitch from `CAST[who].pitch`); the speaker shakes NES-style. Text sits on `darkPlate()`. The opening uses
`scene.actors` and actions `calm` / `arrive` / `capture` / `leave`; its band (`orchestra`) sends note events so notes
pop over the characters in time with the sound.

### Audio
Main voice: `osc (+ fmOsc → detune)` → `pre` → wavefold `shaper` → `trim` → [`dryG` | rectifier `rectG`] → `env` →
`crushSh` (bits) → `ringG` (ring mod) → `lp` → **`music` bus** → `musicLP` → `master` → compressor; delay on `wet`.
All music goes through `musicLP`; SFX (`tones`, `noise`, `sfxFM`, `chordSfx`, key clicks) bypass it. `musicFilter`
animates it with long events (run start fade-in, gate/boss sweeps, muffled dialogue/pause/death, dip after a hit).

- **Scheduler:** 70 ms look-ahead; every 16th note calls `playStep(n, t)`, which picks what plays from game state.
- **The Sine's part:** short genre motifs built only from the current chord's tones (`MOTIFS[style]`, `chordTone`) —
  always in harmony, repeating A/B bars. Its voice per genre (`SYN[style]` → `melNote`): amp ADSR, gate
  (staccato/legato), an FM-index burst for harmonics, a closing low-pass envelope.
- **Level band** (`levelBand`, style from `bandNow()` = `LEVELS[level].band`): pads (`padNote`), bass/plucks with
  filter envelopes (`bandVoice`), drums (`kick`/`hat`/`clap`) on `padBus`, pumped by `duck()`. Genres: `pop`, `techno`
  (rumble + acid line), `chip`, `reggae` (one drop, skanks and rims into the dub echo `dubIn`), `trance`, `breaks`
  (broken beat, electro bass, zaps), `glitch`, `ambient` (no drums, swelling pads, bell glints into the echo), `modern`.
  Each genre also has `MOTIFS`, `SYN` and `STYLE_WET` entries. Dialogue drops the band to a pad breakdown.
- **Boss tracks:** `synthwave` (PWM via `makePWM`), `chiptune` (`chipBus → chipSh`), FM `drums`, `dubstep`.

### Scenery
`drawScenery`, style per level (`LEVELS[i].scene`): `trees` function trees (rose, bell, |x| fir, sinc willow), `tunnel` a
techno tunnel pulsing on the beat, `graph` graph networks over a quantised ridge, `phyllo` golden-angle sunflowers,
`liss` drifting Lissajous figures, `spiro` turning spirographs, `fractal` fractal trees under a Koch ridge, `aurora`
summed-sine curtains and stars, `room` a room in perspective with a ray bouncing off its walls, `wt` a 3D wavetable.
Hidden in boss fights.

### Storage (`localStorage` via `store`)
`osc-adv-best` (record), `osc-adv-unlocked10` (older keys migrate: nine levels — Wavetable 8 → 9; five levels — i → 2i, Wavetable → 9), `osc-adv-victory`, `osc-adv-muted`, `osc-adv-god`, `osc-adv-tut`.

### Analytics, headers, security
Vercel Web Analytics (`/_vercel/insights/script.js`) and Speed Insights (`/_vercel/speed-insights/script.js`) are
plain script tags; they only work on Vercel (404 locally — harmless). `vercel.json` sends a CSP (scripts: self +
inline; styles/fonts: self + Google Fonts; no objects, base, forms), `nosniff`, `Referrer-Policy`,
`Permissions-Policy`. There is no external input (no forms, no URL params besides `#test`, no network): anything
written to `innerHTML` is a constant, a number, or goes through `esc()`. **If you add an external source, add it
to the CSP**, or browsers will block it.

## Testing tricks

`tools/smoke.py` shows the pattern: it injects `window.T = { ev: (c) => eval(c) }` before `  showTitle();` so a test
can run code inside the game's closure: `T.ev("testJump('b3')")`, `T.ev('storySkip()')`, `T.ev('god = true')`.
Useful entry points: `testJump('op'|'l0'..'l9'|'b0'..'b9'|'free')`, `catchBit({val:1})`, `catchHarm({k:9})`,
`landOn(pf)`, `takeHit('x')`, `seqRound(boss, 1)`.

**Balance by bot:** a `setInterval` that only looks at what a player sees and calls `pressJump()`. Compare a precise
bot, a sloppy one (off by a third of a beat) and a random masher: good play should win, mashing should not.
Phones: Playwright context with `has_touch`, `is_mobile`, 390×844 and 844×390. Audio: launch Chromium with
`--autoplay-policy=no-user-gesture-required` and inspect node values (`env.gain.value`, `lp.frequency.value`).

## Tuning knobs

- Square: `SQ_STEP`, `SQ_CHAIN`, `SQ_RELAX`, `SQ_AIR`, `SQ_FINAL`, `SQ_FINAL_CHAIN`, `SQ_WIN`, trap chance, pulse width, spawn interval in `updatePwm`.
- Sequencer: `SEQ_RNDS` (patterns per round), `SEQ_NEED`, window `0.4` of a step in `seqJudge`.
- Levels: `LEVELS[i]` (`bpm`, `speed0`, `len`, `pTall`, `pCeil`, pools), `NEED`, the speed curve in `update` (`+140` at the gate).
- Lives: `START_PARTIALS`, `HIT_COST`.
- New obstacles: `GATES` spacing (3000) in `spawn`, glide ramp chance (`.09`), `fbk` growth (`8·e^(t/1.05)`, cap 150), `dcs` offset 34, shadow lifetime/cost, rhythm window `.09`, time-stretch factors `.72`/`.75`.

## Known gaps and ideas

- Not verifiable by script: the mix and the sound of every genre — always ask a human to listen.
- Legacy, unused: `updateFM`, `allyFM`, `fireFM`, `loseIndex`, `fmLit`, `setBattleFM`, `idxTokens`, platforms `kind:'fm'`,
  `harmTokens`, empty `flash()`, `BOSSES.*.atk` on bosses with `noAtk`. Safe to remove with care.
- The page copy in `<footer>` / `.deck` is hidden on every device now; it's kept as accessible text and for `#test`.
- Ideas: a mid-level checkpoint; a "stun" instead of a hit for the ring-mod sideband; a final scene after Wavetable.
