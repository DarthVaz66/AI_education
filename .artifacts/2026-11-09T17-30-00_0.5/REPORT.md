# QA Run — Final Report

run_id: 2026-11-09T17-30-00_0.5
requirement_version: 0.5
confluence_page: 2228226
jira_project: QA
testomat_project: test-cc3c0 (source: argument)
preflight_decision: resume
continued_from_run_id: 2026-11-09T17-00-00_0.5

## Human override
- **Gate 1**: original=FAIL (major=7 > limit=5) → override=PASS
  - approved_by: Val
  - reason: "Test"
  - recorded in `meta.json.human_override`; valid for this run only.

## Gates
- Gate 1: PASS via human override (blocker=0, critical=0, major=7, minor=1) — no `ambiguity` finding blocks design; major limit (5) exceeded and overridden by human.
- Gate 2a: PASS (12 tasks, 0 duplicates, 100% with AC + requirement_refs, 100% dor_check=pass)
- Gate 2b: PASS (137 cases: positive=55, negative=58, boundary=24, N/A-with-reason for non-numeric constraints; 100% priority & step+expected; project_id matches)
- Gate 2c: PASS (cross-check ok: requirement_version=0.5 consistent; every requirement referenced in 01 covered by ≥1 task and ≥1 case; no dangling refs; all statuses completed)

## Publish
- Jira: created=12, existing=0, failed=0, stale=0 (QA-1 … QA-12, label `qemu-manager-req-0.5`)
- Testomat.io: created=137, existing=0, failed=0, stale=0 (suite `03f205ec` "QEMU Manager — REQ v0.5 (Confluence 2228226)")

## Artifacts
- .artifacts/2026-11-09T17-30-00_0.5/meta.json
- .artifacts/2026-11-09T17-30-00_0.5/01-requirement-review.json
- .artifacts/2026-11-09T17-30-00_0.5/02-task-design.json
- .artifacts/2026-11-09T17-30-00_0.5/03-test-design.json
- .artifacts/2026-11-09T17-30-00_0.5/04-publish-state.json
- .artifacts/2026-11-09T17-30-00_0.5/05-publish-report.json

## Recommendations
- The requirements (Confluence 2228226, v0.5) carry 7 **major** findings (F-001…F-007) that were shipped only because of the Gate 1 human override. Prioritise resolving them, in particular:
  - **F-001**: the 3 s state-change ACs (REQ-10/REQ-11) are inconsistent with the default 5 s polling (REQ-13); the test model assumes a forced refresh.
  - **F-003**: "storage pool availability" validation has no pool concept/field — server-side validation and negative tests are under-specified.
  - **F-004**: QMP-only behaviour is undefined for rename/clone/delete/suspend-resume.
- Consider adding issue links (Jira ↔ Testomat.io) and a test plan/run for the created suite on the next pass.
- Preflight-reconciliation: two prior registry entries (2026-11-09T15-00-00, 2026-11-09T16-00-00) for this same page were left `in_progress` with orphaned directories (crash window between `mv` and index update); their `path` was corrected to `.artifacts/{run_id}/`. Logged, non-blocking.
