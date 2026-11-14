# Changelog

Single progress log for GeoVision. Written by agents on both devices. Rules live in `AGENTS.md`.

**Format:** `- [Tag] TYPE (Phase N) what changed — key files — Human next: <command or "nothing">`
**Types:** `START` `ADDED` `CHANGED` `FIXED` `REMOVED` `DONE` `BLOCKED` `DROP` `NOTE`
**Append-only.** Newest day on top. Never edit someone else's line.
**Open claim** = a `START` for a phase with no later `DONE`, `BLOCKED` or `DROP` for it.

## [Unreleased]

### 2026-11-14
- [Anuja] DONE (Phase 0) Repo skeleton + ward normalize — agent-verified: 141 wards+ward_id, aoi.geojson, config city/crs, pytest+ruff; Human: GEE OK already, optional QGIS 141 check — key files below — Human next: review then commit/push `feature/phase-0-skeleton` when ready
- [Anuja] ADDED (Phase 0) Folder tree, configs, normalize script, study area, SOURCE, test — `.gitignore`, `configs/city_aoi.yaml`, `configs/class_map.yaml`, `src/gee/normalize_wards.py`, `docs/study_area.md`, `data/raw/boundaries/SOURCE.md`, `tests/test_normalize_wards.py`, `README.md` — Human next: `python -m src.gee.normalize_wards` if re-download wards
- [Anuja] NOTE (Phase 0) Local branch `feature/phase-0-skeleton` (no commit by agent) — gee_project=`geovision-514712` — Human next: nothing
- [Anuja] START (Phase 0) Accounts, city lock, repo skeleton — Human next: nothing while agent builds
- [Debayan] ADDED (Phase 0) Locked-stack `requirements.txt` (unpinned; pin in Phase 11) — `requirements.txt` — Human next: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` when ready to install
- [Debayan] ADDED (setup) Agent rules and skills — `AGENTS.md`, `.cursor/skills/ponytail/SKILL.md`, `.cursor/skills/geovision-phase/SKILL.md`, `CHANGELOG.md`, `.gitattributes` — Human next: copy `docs/agent-build-plan.md` into the repo, set the friend's name in `AGENTS.md`, commit
