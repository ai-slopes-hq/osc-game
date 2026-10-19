# Приключения осциллятора · Oscillator Adventures

Синус бежит по экрану осциллографа, поёт мелодию и спасает аналоговые сигналы — Треугольника, Меандра и Комплекса — от цифровых форм во главе с Wavetable. Прыжок поднимает мелодию на октаву, фолд опускает; препятствия — математические функции и эффекты. Девять уровней, у каждого свой жанр — от синтипопа, техно и регги до эмбиента; боссы — Квадрат, Компрессор, Биткрашер, Лимитер, Суперпила, Арпеджиатор, Секвенсор, Вокодер и сам Wavetable.

*A sine wave runs across an oscilloscope, sings, jumps over maths functions and fights digital waveforms. One static `index.html`, Canvas 2D + Web Audio, no build.*

## Играть / Play

Телефон: держи левую половину экрана — фолд, тап справа — прыжок. Клавиатура: Пробел / ↑ — прыжок (ещё раз в воздухе — двойной), ↓ — фолд, P — пауза, M — звук, F — полный экран.

Локально / locally:

```bash
python3 -m http.server 8000   # then open http://localhost:8000/#test
```

## Разработка / Contributing

Всё, что нужно человеку или агенту (Claude Code, Codex и др.), чтобы продолжить разработку, — в [AGENTS.md](AGENTS.md): как устроен код, правила, проверки, куда слать PR.

Everything a contributor or coding agent needs is in [AGENTS.md](AGENTS.md). In short: branch from `staging`, run `node tools/check.mjs` and `python3 tools/smoke.py`, open the PR into `staging`.
