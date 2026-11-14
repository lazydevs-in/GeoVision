# Changelog

Single progress log for GeoVision. Written by agents on both devices. Rules live in `AGENTS.md`.

**Format:** `- [Tag] TYPE (Phase N) what changed — key files — Human next: <command or "nothing">`
**Types:** `START` `ADDED` `CHANGED` `FIXED` `REMOVED` `DONE` `BLOCKED` `DROP` `NOTE`
**Append-only.** Newest day on top. Never edit someone else's line.
**Open claim** = a `START` for a phase with no later `DONE`, `BLOCKED` or `DROP` for it.

## [Unreleased]

### 2026-11-14
- [Debayan] ADDED (Phase 0) Locked-stack `requirements.txt` (unpinned; pin in Phase 11) — `requirements.txt` — Human next: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` when ready to install
- [Debayan] ADDED (setup) Agent rules and skills — `AGENTS.md`, `.cursor/skills/ponytail/SKILL.md`, `.cursor/skills/geovision-phase/SKILL.md`, `CHANGELOG.md`, `.gitattributes` — Human next: copy `docs/agent-build-plan.md` into the repo, set the friend's name in `AGENTS.md`, commit
