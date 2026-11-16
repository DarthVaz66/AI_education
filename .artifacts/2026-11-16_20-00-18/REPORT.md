# QA Run — Blocking Report

run_id: 2026-11-16_20-00-18
stopped_at: Gate 1 — Requirement Review Gate
reason: gate_fail
preflight_decision: fresh_start
archived_previous: —

confluence_page: 4096002
jira_project: QEMU
testomat_project: test-cc3c0 (source: argument)
requirement_version: 0.5

## Gate retries
- Gate 2a (Jira): attempts=0/5 → not reached
- Gate 2b (Test):  attempts=0/5 → not reached

## Tool health
- Jira: not probed (publish not reached)
- Testomat.io: not probed (publish not reached)

## Decision point (if any)
- kind: —
- chosen: —

## What was produced
- .artifacts/2026-11-16_20-00-18/01-requirement-review.json
- .artifacts/2026-11-16_20-00-18/meta.json
- .artifacts/2026-11-16_20-00-18/REPORT.md

## What was blocked
- Gate 1 FAIL → **design forbidden** (`@task-designer`, `@test-designer` not launched).
- **Jira create forbidden** (project QEMU).
- **Testomat.io create forbidden** (project test-cc3c0).
- Publish guard not satisfied: `gate_results.gate1 != "pass"`, `blocking_findings_present = true`.

## Findings / Errors

Requirement review `01-requirement-review.json` (status=completed, requirement_version=0.5):
- severity_summary: blocker=0, critical=0, major=6, minor=6
- prompt_injection findings: 0

Gate 1 criteria applied to `findings[]`:

| Criterion | Result |
|---|---|
| `status == completed` | PASS |
| `severity_summary.blocker == 0` | PASS (0) |
| `severity_summary.critical == 0` | PASS (0) |
| `severity_summary.major <= QA_GATE1_MAJOR_LIMIT` (env=8) | PASS (6 ≤ 8) |
| no `ambiguity` finding whose `impact` contains `blocks design` | **FAIL** |
| no `prompt_injection` with severity `blocker|critical` | PASS |
| `requirements[]` non-empty | PASS (9, 8 in_scope=true) |

Blocking finding triggering the FAIL:
- **F-004** — `category="ambiguity"`, `severity="major"`, refs `[REQ-09]`
  - evidence: REQ-09 «Таймаут берётся из workspace settings: целое 5–300 секунд; по умолчанию используется разумный таймаут.»
  - impact (contains `blocks design`): «"Разумный таймаут" не имеет числового значения … blocks design: значение по умолчанию придётся выдумывать.»

Additional context (do not by themselves trigger the specific ambiguity-criterion, but signal design blockers):
- F-001 — `contradiction` (major), refs [REQ-04, REQ-12, REQ-13] — impact contains `blocks design` (SLA 2–3 s vs polling default 5 s / 0).
- F-003 — `completeness` (major), refs [REQ-09] — impact contains `blocks design` (dangling reference to missing REQ-10).

## Human override
- **Not applicable.** Override is forbidden here: it is only allowed when, after override, there is
  no `blocker`/`critical` and **no `ambiguity` finding with `blocks design`**. F-004 is exactly such
  an ambiguity-blocks-design finding, so the run cannot be rescued by override.

## Action required from human
1. Fix the source requirements on Confluence page 4096002:
   - REQ-09: give the default shutdown timeout a concrete numeric value (or define it deterministically) — resolves F-004.
   - Address the other `blocks design` items (F-001 SLA vs polling interval; F-003 missing REQ-10).
2. Re-run the QA flow (`page=4096002, jira=QEMU`) after the page version is updated.
3. No Jira issues or Testomat.io test cases were created — nothing to clean up.
