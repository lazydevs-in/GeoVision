# GeoVision — Agent Context

**This file is binding for every AI agent (Cursor or any other) on every device in this project.**
Read it in full before touching anything. Project: satellite-based green cover monitoring and
forecasting for Kolkata (KMC, 141 wards), years 2018–2024.
Repo (reference only, agents never access it): https://github.com/lazydevs-in/GeoVision.git

## Read first, in this order

1. **This file.**
2. **`docs/agent-build-plan.md`** — source of truth for scope, locked decisions, data contracts, phases.
3. **`CHANGELOG.md`** — top of `## [Unreleased]`: what your partner just did, who owns which phase.
4. **`.cursor/skills/ponytail/SKILL.md`** — always-on coding style, level `full`.
5. **`.cursor/skills/geovision-phase/SKILL.md`** — when asked to build / continue / check a phase.

If a file above does not exist locally, say so. Never reconstruct its contents from memory.

## Team

| Person | CHANGELOG tag |
|---|---|
| Debayan | `Debayan` |
| Anuja | `Anuja` |

Two people work in parallel, on separate devices, each with their own agent. If you do not know
who you are working for, ask once at session start, then use that tag for the whole session.

---

## Git Rule — absolute, no exceptions

**Agents never run any git or GitHub operation.** Forbidden: `git` (commit, push, pull, fetch,
clone, merge, rebase, stash, checkout, switch, reset, branch, tag, init, add, status, diff, log),
`gh`, GitHub API/web access, reading `.git/`.

- Humans commit, push and pull manually. You only edit local files.
- Finish by listing the files you changed so the human can stage them.
- If you need your partner's work and it is not on disk, say "not present locally, please pull". Do not try to fetch it.
- If the human says "update local files to match the repo", edit only from content they paste or point to on disk.

---

## Working in parallel (two people, two agents)

1. **Claim before you build.** Read `CHANGELOG.md`. If the phase has an open claim by the other person (a `START` with no later `DONE`/`BLOCKED`/`DROP`), stop and tell the user. Otherwise add your own `START` line first.
2. **One phase, one owner at a time.** Do not edit files belonging to a phase the other person has claimed, unless the user says so.
3. **Shared files** (`configs/*.yaml`, `requirements.txt`, `README.md`, `docs/agent-build-plan.md`, `.gitignore`): smallest possible edit, never reorder or reformat, always log in CHANGELOG.
4. **Do not reformat or "clean up" files you were not asked to touch.** It creates merge conflicts for the human.
5. **Data contract changes need both people.** Stop and ask (see "Stop and ask first").

---

## CHANGELOG Rule

- `CHANGELOG.md` at repo root is the **only** changelog. No others.
- **Update it after every task, before you say you are done.** Under `## [Unreleased]` → today's `### YYYY-MM-DD`.
- **Append-only.** Never edit or delete another entry. Add your lines under today's header (create it at the top if missing). `.gitattributes` merges this file line-by-line so both of you can append safely.
- One line per change. Format:

```
- [Tag] TYPE (Phase N) what changed — key files — Human next: <exact command or "nothing">
```

| TYPE | Use for |
|---|---|
| `START` | claiming a phase / task |
| `ADDED` `CHANGED` `FIXED` `REMOVED` | code, config, docs |
| `DONE` | agent steps of a phase finished (state which acceptance tests are agent-verified vs Human) |
| `BLOCKED` | hit a Stop-if-blocked, with the reason |
| `DROP` | releasing a claim without finishing |
| `NOTE` | decision, limitation, something the partner must know |

- Log only what actually happened. Never log a Human step (GEE export, Colab run, QC) as done unless the user told you it is done.
- Metrics and results go in the log only if copied from real output you saw.

---

## Human-only steps — never fake them

GEE login and exports, Drive downloads, Colab/Kaggle GPU runs, QGIS visual QC, mentor sign-off,
Streamlit Cloud deploy. You write the script and a checklist, then **stop**.

- Never claim you ran an export, training run, or deploy.
- Never create fake rasters, fake metrics or fake sample data to make something "work".
- Tiny synthetic fixtures inside `tests/` are fine if clearly named as synthetic.
- Never run GEE exports, large downloads or model training yourself.

---

## No hallucination

1. **Verify before you cite.** Any file path, function, config key, band name, dataset ID or API argument you mention must be read or grepped first. Not found → say "not found".
2. **Only use identifiers the plan or repo already gives you** (plan §2.3 and §4: `COPERNICUS/S2_SR_HARMONIZED`, `ST_B10`, `ward_id`, class IDs 0–3, EPSG codes). Anything else: label it **"unverified"** and tell the human what to check.
3. **No invented numbers.** Thresholds, metrics, areas, correlations come from files or runs, never from memory or guesses.
4. **"Tests pass" only if you ran them and saw the output.** Otherwise write "not run".
5. **Ambiguous? Ask one short question.** Do not guess intent.
6. **Cite the plan** (`plan §5 Phase 3`) when a decision rests on it.
7. **Conflict between plan, code, companion docs and the user → stop and report.** Do not silently pick a side. Companion docs (`concrete-finish-plan.md`, `green-cover-fyp-plan.md`, `beginner-model-training-guide.md`) may not be in the repo; if so, say so.
8. **End every reply with:** `Done:` / `Not done:` / `Not verified:` / `Human next:`.

---

## Scope discipline

- **Locked:** Kolkata (KMC, 141 wards), years 2018–2024, post-monsoon Oct 1 → Feb 28, 4 classes (`0` vegetation, `1` built-up, `2` water, `3` barren), free stack only. See plan §2.
- **Phase order is mandatory.** Build only the phase you were asked for. Phases 9–11 do not start before the Phase 7 gate is recorded in `docs/metrics_log.md`. Nice items only in Phase 12.
- **Data contracts are exact:** file paths, names, dtypes, class IDs, `ward_id`, CRS (`EPSG:4326` exchange, `EPSG:32645` for area). Plan §4.
- **No new dependency** without asking.
- **Repo layout** follows plan §3. The repo root is the plan's `green-cover-fyp/` tree (the repo is named GeoVision; the layout inside is the same).
- **Precedence:** user instruction > plan locked decisions and contracts > this file > ponytail brevity. Ponytail decides how little code to write, never which deliverables to drop.

---

## Stop and ask first

Report and wait for the user before you:

- deviate from the plan or change a data contract
- change city, years, season, classes or CRS
- add or swap a dependency
- delete or overwrite anything under `data/`, `models/` or `reports/` (say what would be lost)
- change a shared config the other person also depends on

---

## Before you say "done"

- Run `pytest tests/` and `ruff check src/ tests/` **for the code you touched** (skip what is not set up yet and say so).
- Update `CHANGELOG.md`.
- Keep large files out of tracked paths: rasters, `*.tif`, `*.npy` tiles and `models/*.pt` are gitignored. Never move them into a tracked location.
- Reply briefly. Status in conversation only; no unsolicited status documents.
