# QA Run — Blocking Report

run_id: 2026-11-09T17-00-00_0.5
requirement_version: 0.5
confluence_page: 2228226
jira_project: QA
testomat_project: test-cc3c0 (source: argument)
preflight_decision: null
stopped_at: Gate 1 — Requirement Review Gate
reason: gate_fail

## Gates
- Gate 1: **FAIL** (8 findings: blocker=0, critical=0, major=7, minor=1; limit major<=5)
  - blocker == 0 → OK
  - critical == 0 → OK
  - major (7) <= QA_GATE1_MAJOR_LIMIT (5) → **VIOLATED** (7 > 5)
  - findings `ambiguity` with impact containing `blocks design` → none
- Gate 2a: NOT RUN (blocked at Gate 1)
- Gate 2b: NOT RUN (blocked at Gate 1)
- Gate 2c: NOT RUN (blocked at Gate 1)
- Publish: NOT RUN (blocked at Gate 1)

## What was produced
- .artifacts/2026-11-09T17-00-00_0.5/meta.json
- .artifacts/2026-11-09T17-00-00_0.5/01-requirement-review.json
- .artifacts/2026-11-09T17-00-00_0.5/REPORT.md

## What was blocked
- Design (`02-task-design.json`, `03-test-design.json`) — not started.
- Gate 2a / 2b / 2c — not evaluated.
- Publish to Jira (project QA) and Testomat.io (test-cc3c0) — not performed.
  No Jira issues and no Testomat.io test cases were created.

## Findings / Errors
Requirement review of Confluence page 2228226 (v0.5) produced 8 findings — 7 major + 1 minor
(exceeds the Gate 1 major limit of 5).

| id | category | severity | requirement_refs | summary |
|----|----------|----------|------------------|---------|
| F-001 | contradiction | major | REQ-04, REQ-10, REQ-11, REQ-13 | 3s state-change AC (REQ-10/11) unachievable under default 5s polling (REQ-13); forced refresh only stated in REQ-04 |
| F-002 | contradiction | major | REQ-03, REQ-12 | IP required in tree by REQ-12 but absent from REQ-03 displayed-field list |
| F-003 | ambiguity | major | REQ-04, REQ-16 | "storage pool availability" validation has no pool concept/field |
| F-004 | completeness | major | REQ-05, REQ-06, REQ-07, REQ-21, REQ-18, Non-Goals | QMP-only behavior undefined for Rename/Clone/Delete/Suspend-Resume |
| F-005 | completeness | major | REQ-03, REQ-09 | REQ-03 references REQ-09 for `stopped` transition, but REQ-09 defines no such AC |
| F-006 | ambiguity | major | REQ-13 | interval validation: "integer" not specified; fractional/negative/non-numeric and inline-error mechanism undefined |
| F-007 | ambiguity | major | REQ-02 | delete-connection warning defined only for `running` VMs; paused/suspended/crashed undefined |
| F-008 | completeness | minor | REQ-02, REQ-12, Glossary | terms `unknown` / `disconnected` missing from Glossary |

Artifact contract check: PASSED (all required fields present; each finding has
id/category/severity/requirement_refs/evidence/impact; no `gate_recommendation`;
severity_summary consistent with findings[]).

## Preflight reconciliation notes
- `.artifacts/.current/` was absent at preflight → Case A (new run created),
  `preflight_decision=null`.
- Two prior registry entries (`2026-11-09T15-00-00`, `2026-11-09T16-00-00`) were left
  `status=in_progress` for the same page 2228226 although no `.artifacts/.current/`
  existed and their `.artifacts/{run_id}/` directories were already present (crash window
  between `mv` and index update). Their `path` fields were corrected to
  `.artifacts/{run_id}/`; logged here as a reconciliation warning. No action blocked.

## Action required from human
Gate 1 failed: 7 major findings exceed the threshold of 5. Requirements for page 2228226
(v0.5) must be revised (ideally resolving F-001…F-007), OR a **human override** must be
explicitly approved for this run. To override, confirm:

> Override Gate 1 (original=FAIL, major=7 > limit=5) → PASS — approved_by=<you>, reason=<text>

On approval this single-run override will be recorded in `meta.json.human_override`, and
the flow will resume at Design → Gate 2a/2b/2c → Publish. Otherwise, the run remains
blocked.
