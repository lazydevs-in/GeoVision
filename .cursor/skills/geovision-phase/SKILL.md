---
name: geovision-phase
description: >
  Run one phase of the GeoVision build plan safely, for either teammate. Use when
  the user says "build phase N", "start phase N", "continue", "what's next",
  "status", "where are we", or asks what to do next on the green-cover project.
argument-hint: "[phase number 0-12 | status]"
---

# GeoVision phase workflow

Replaces the copy-paste handoff prompt in `docs/agent-build-plan.md` §10. The rules in
`AGENTS.md` (git ban, CHANGELOG, no hallucination, scope) apply to every step here.

## `status` (or "where are we")

1. Read `CHANGELOG.md`. List per phase: last `START` / `DONE` / `BLOCKED` / `DROP`, by whom, date.
2. Name the next unclaimed phase and what the Human must still run for the phases already `DONE`.
3. Write nothing. Answer in under 10 lines.

## `phase N` (or "continue" / "what's next")

No number given: take the highest `DONE` phase + 1 from the CHANGELOG, tell the user which one, and continue unless they object.

1. **Read** `AGENTS.md`, then plan §5 for Phase N only (Inputs, Agent steps, Commands/scripts, Acceptance tests, Stop-if-blocked), plus plan §4 data contracts.
2. **Check the gate.**
   - Previous phase `DONE` in the CHANGELOG, and its outputs exist on disk? If not, stop and tell the user exactly what the Human must do first.
   - Phases 9–11: also require the Phase 7 gate note in `docs/metrics_log.md`.
   - Phase 12 Nice items: only if every Must is green.
3. **Check the claim.** The other person has an open `START` on this phase? Stop and tell the user.
4. **Claim it.** Append `START (Phase N)` to today's CHANGELOG section.
5. **List the files you will create or change** (one line each), then proceed. Do not wait unless something is ambiguous.
6. **Build the Agent steps only.** Follow the contracts exactly. Leave Human steps as a checklist. Follow ponytail: smallest complete change, one small test for non-trivial logic.
7. **Validate** what you touched: `pytest` on its tests, `ruff check` on its files. Do not run GEE, downloads or training.
8. **Log** `ADDED`/`CHANGED`/`FIXED` lines, then `DONE (Phase N)`. In the `DONE` line say which acceptance tests are agent-verified and which wait on the Human. Use `BLOCKED` instead if a Stop-if-blocked fired.
9. **Report**, in this shape:

```
Phase N — <title>
Files: <created/changed, one per line>
Acceptance: <each test: ✅ agent-verified | ☐ Human | not run>
Human next: <exact commands/steps, in order>
Blocked: <Stop-if-blocked hit, or "none">
Not verified: <anything unchecked>
```

## Don't

- Don't start the next phase in the same run.
- Don't mark Human acceptance tests as passed.
- Don't touch files outside Phase N's scope, other than a minimal logged edit to a shared file.
