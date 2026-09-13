# CAT / Aptitude Visual Question Solver

An agent skill that solves competitive-exam aptitude questions from a screenshot.
Built for **Antigravity CLI (`agy`)** and **Claude Code**.

Paste an image of a DI chart, an LR set, a geometry figure or a quant question and
the agent transcribes it, validates the transcription, computes the answer in
Python, and matches it against the options — instead of eyeballing bars and doing
percentages in its head.

## What it covers

- **Data Interpretation** — bar, grouped, stacked, 100%-stacked, line, dual-axis
  combo, pie, doughnut, area, cumulative/ogive, histogram, scatter, bubble, radar,
  waterfall, Pareto, index-to-100 series, growth-rate series, box plots, caselets,
  and tables with missing cells.
- **Logical Reasoning / DILR** — linear and circular seating, grids, assignment
  puzzles, selections, scheduling, partial orders, tournaments, routes and
  networks, cryptarithms, truth-teller/liar sets, Venn and set min–max.
- **Quantitative Aptitude** — arithmetic, algebra, number theory, geometry with
  figures, coordinate geometry, mensuration, P&C and probability.
- **Data Sufficiency** (GMAT/XAT) and **VARC** (RC, para-jumbles, para-summary,
  odd-one-out, critical reasoning).
- **Modes** — `solve` (default), `verify` ("check my answer" — it diagnoses which
  mistake produced your value), `teach` (the 60-second exam method), and `set`
  (4–6 questions on one data set answered in a single pass).

## Why it is accurate

| Failure mode | What the skill does instead |
| --- | --- |
| Eyeballing a bar between gridlines | Overlays a labelled pixel grid, then converts pixels to values by two-point calibration |
| A misread that silently propagates | Runs pie/stack/total/index/ogive/legend reconciliation **before** computing |
| Mental percentage arithmetic | Every number goes through `scripts/di.py` |
| Snapping to the nearest option | `match_option()` refuses a near-miss and lists the mistakes that would produce each distractor |
| Hedging on an uncertain read | `sensitivity()` re-runs the answer at every corner of the reading interval and reports ROBUST or SENSITIVE |
| Dropping one LR constraint | `scripts/lr.py` enumerates and prints the constraint count back |
| Hand-waving a set min/max | `scripts/sets.py` searches the Venn regions and prints an attainable witness |

## Install

### Antigravity CLI (`agy`)

```bash
git clone https://github.com/asyncninja0012/cat-aptitude-skill.git
cd cat-aptitude-skill
./install.sh              # Windows: powershell -ExecutionPolicy Bypass -File .\install.ps1
```

That registers this checkout in `~/.gemini/config/skills.json`, so a later
`git pull` updates the skill with no reinstall — `agy` re-reads the directory
each session. Start a new `agy` session and paste a question; the skill activates
on its own from its description.

Confirm the install, and which version is live:

```bash
agy --print='Which skills are available to you? Names only.'
# -> cat-visual-aptitude

agy --print='Without reading any files, what skill version does the
cat-visual-aptitude description state?'
# -> 1.0.0
```

The version marker lives in the skill's `description`, which is always in the
agent's context, so neither check needs file-read permission.

Other install modes:

| Command | Effect |
| --- | --- |
| `./install.sh copy` | Copy into `~/.gemini/config/skills/` (no auto-update) |
| `./install.sh workspace` | Register in `.agents/skills.json` for this repo only — commit it to share with a team |
| `agy plugin install /path/to/cat-aptitude-skill` | Install the whole repo as an agy **plugin** (it carries a `plugin.json`); manage with `agy plugin list / disable / uninstall` |

### Claude Code

```
/plugin marketplace add asyncninja0012/cat-aptitude-skill
/plugin install cat-aptitude@cat-aptitude-skill
```

Or without the marketplace: `./install.sh claude`, which copies the skill into
`~/.claude/skills/`.

### Dependency

Only the image scripts need one:

```bash
pip install pillow
```

`di.py`, `lr.py` and `sets.py` are pure standard library.

## Layout

```
plugin.json                       agy plugin manifest
.claude-plugin/                   Claude Code plugin + marketplace manifests
install.sh / install.ps1
skills/cat-visual-aptitude/
├── SKILL.md                      the pipeline the agent follows
├── references/                   loaded only when needed
│   ├── question-types.md         routing table for every chart and set type
│   ├── visual-reading.md         axis calibration, pixel measurement, odd inputs
│   ├── traps.md                  trap catalogue + distractor forensics
│   ├── lr-shapes.md              LR set shape -> enumeration recipe
│   └── formulas.md               quant formula and shortcut sheet
└── scripts/
    ├── crop.py                   crop / rotate / upscale / sharpen a region
    ├── overlay.py                labelled pixel grid for precise coordinate reads
    ├── calibrate.py              pixel -> value by two-point calibration
    ├── di.py                     validators, percentage maths, option matching, sensitivity
    ├── lr.py                     9 enumeration templates + must/could-be-true evaluator
    └── sets.py                   Venn region solver with attainable min/max
```

## Verify it works

```bash
python skills/cat-visual-aptitude/scripts/di.py   --selftest
python skills/cat-visual-aptitude/scripts/lr.py   --selftest
python skills/cat-visual-aptitude/scripts/sets.py --selftest
```

## Use

Paste a screenshot into `agy` or Claude Code and ask:

- "solve this"
- "I marked (C), is that right?"
- "how would I do this in 60 seconds?"
- (a whole DI set) "answer all four"

## Licence

MIT.
