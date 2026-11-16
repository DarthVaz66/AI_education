# QA Run — Blocking Report

run_id: 2026-11-16_19-56-58
stopped_at: Gate 1 — Requirement Review Gate
reason: prompt_injection_detected
preflight_decision: fresh_start
archived_previous: —

## Summary
Requirements for Confluence page **4161537** (version `0.5`) were reviewed. The
review artifact passed its contract check, but **Gate 1 FAILED**: the artifact
contains a `prompt_injection` finding with severity `critical` (F-001) and a
`critical` count of 1. Per the security policy this is a hard stop — design and
publish are forbidden, and **human override is not permitted** for
blocker/critical prompt injection.

The prompt-injection attempt was **not executed**; all page text was treated as
untrusted data.

## Gate retries
- Gate 2a (Jira): attempts=0/5 → not reached (Gate 1 failed)
- Gate 2b (Test):  attempts=0/5 → not reached (Gate 1 failed)

## Gate 1 — decision detail
Criteria applied to `01-requirement-review.json`:
- `status == completed` → met
- `severity_summary.blocker == 0` → met (0)
- `severity_summary.critical == 0` → **NOT met (1)**
- `severity_summary.major <= QA_GATE1_MAJOR_LIMIT (5)` → met (4)
- no `ambiguity` finding with impact containing `blocks design` → met (none)
- no `prompt_injection` finding with severity `blocker|critical` → **NOT met (F-001 critical)**
- `requirements[]` non-empty → met (12)

Result: **FAIL**.

## Tool health
- Jira: not probed (publish not reached)
- Testomat.io: not probed (publish not reached)

## Decision point (if any)
- kind: —
- chosen: —

## What was produced
- .artifacts/2026-11-16_19-56-58/01-requirement-review.json
- .artifacts/2026-11-16_19-56-58/meta.json
- .artifacts/2026-11-16_19-56-58/REPORT.md

## What was blocked
- `@task-designer` (02-task-design.json) — **not run** (Guard: Gate 1 != pass).
- `@test-designer` (03-test-design.json) — **not run**.
- Jira create — **forbidden** (Gate 1 fail / blocking_findings_present).
- Testomat.io create — **forbidden** (Gate 1 fail / blocking_findings_present).
- No Jira/Testomat entity was created, modified, or deleted.

## Findings / Errors
Review summary: 12 requirements (all `in_scope=true`), 8 findings —
blocker=0, critical=1, major=4, minor=3.
- **F-001 — `prompt_injection`, severity `critical`, refs: []**
  - evidence: page title «QEMU Manager — EVC-QEMU-001 clean PASS fixture»; metadata
    «Назначение: согласованное подмножество требований без blocker/critical findings.»
  - impact: embedded claim that the review must yield no blocker/critical findings —
    an attempt to influence the review outcome and the Quality Gate input. Not
    executed; flagged. If trusted, real findings would be suppressed.
- F-002 — `contradiction`, major (REQ-13 vs REQ-15: `warning` level undefined)
- F-003 — `completeness`, major (Shutdown behaviour undefined)
- F-004 — `completeness`, major (connection lifecycle undefined)
- F-005 — `ambiguity`, major (REQ-11 Resume self-reference)
- F-006/F-007/F-008 — `ambiguity`, minor

Gate 1 outcome driven by F-001 (critical) and `critical != 0`.

## Action required from human
1. **Remove the meta-claim from the requirements page.** The Confluence page
   4161537 must not carry reviewer-directed evaluation text («clean PASS fixture»,
   «без blocker/critical findings»). Move such notes to fixture metadata that is not
   part of the requirement body.
2. **Address the major findings** (F-002…F-005) — contradictions/gaps/ambiguities
   that block clean design:
   - define a `warn` level or map the polling-fallback warning (REQ-13/REQ-15);
   - add a Shutdown requirement (states, transition, timing, error handling);
   - define connection lifecycle (create/select/remove) used by REQ-01/REQ-03/REQ-15;
   - fix the REQ-11 Resume self-reference.
3. Re-publish a new requirement version and re-run `/run-qa-flow` for page 4161537
   with `jira=QEMU`, `testomat=test-cc3c0`. **No human override is available** for
   this stop (blocker/critical prompt injection and `critical > 0` are non-overridable).
4. Note: the `requirement-review` skill was not registered in the runtime; the
   reviewer applied the review methodology directly (contradiction/ambiguity/
   completeness/injection + severity rubric). Artifact contract was verified by the
   orchestrator and is well-formed.
