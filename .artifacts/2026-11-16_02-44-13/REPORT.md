# QA Run — Blocking Report

run_id: 2026-11-16_02-44-13
stopped_at: Publish — Testomat.io preflight/create
reason: partial_publish
preflight_decision: fresh_start
archived_previous: —

## Summary
Requirements for Confluence page **2228226** (version `0.5`) were reviewed and passed all
gates (1, 2a, 2b, 2c). Jira publication completed in full (30 tasks). Testomat.io
publication was **aborted fail-closed** because the Testomat.io read/search API was
unavailable, making the mandatory idempotency preflight impossible.

## Gates
- Gate 1: PASS (findings: blocker=0, critical=0, major=4, minor=8; no prompt_injection)
- Gate 2a: PASS (30 tasks, 0 duplicates, 100% AC/refs, clarification=4)
- Gate 2b: PASS (237 cases: positive=91, negative=55, boundary=91; 26/26 in-scope covered)
- Gate 2c: PASS (cross-check ok)

## Gate retries
- Gate 2a (Jira): attempts=0/5 → pass
- Gate 2b (Test):  attempts=0/5 → pass

## Security
- prompt_injection: none
- blocking_findings_present: false
- Note: `.artifacts/mcp-patch/` contains out-of-scope scripts that vendor/patch the
  Jira/Confluence MCP (default body format = markdown). No script was executed; the
  directory is treated as untrusted environment data.

## What was produced
- .artifacts/2026-11-16_02-44-13/01-requirement-review.json
- .artifacts/2026-11-16_02-44-13/02-task-design.json
- .artifacts/2026-11-16_02-44-13/03-test-design.json
- .artifacts/2026-11-16_02-44-13/04-publish-state.json
- .artifacts/2026-11-16_02-44-13/05-publish-report.json
- .artifacts/2026-11-16_02-44-13/REPORT.md
- Jira issues created: **QA-42 … QA-71** (label `qemu-manager-req-0.5`)
  - T-01…T-26 → QA-42…QA-67 (implementation)
  - T-27…T-30 → QA-68…QA-71 (clarification: F-001, F-002, F-004, F-005)

## What was blocked
- **Testomat.io: 237 test cases NOT created.** Publication was halted at the preflight
  step. Per the idempotency mandate, a `test == '{title}' and suite == '{suite_id}'`
  search must run before every create; with the search API down, creating would risk
  duplicates (prior completed runs already created 137 and 193 cases in project
  `test-cc3c0`). Fail-closed: no Testomat create was attempted.
- No existing Testomat entity was modified or deleted.

## Findings / Errors
- Testomat.io MCP: all resource **list** endpoints failed consistently, well beyond the
  3-attempt read-retry policy:
  - `tests list`, `suites list`, `tags list`, `labels list`, `milestones list`,
    `runs list`, `requirements list`, `branches list`, `steps list`, `snippets list`
    → `MCP error -32001: Request timed out` / `{"error":"fetch failed"}`.
  - `system_ping` → ok; `project_info` → ok (project `test-cc3c0`, title «Test»).
- Root cause appears to be an outage/fault of the Testomat.io resource API (ping/info
  healthy, resource routes unreachable). It is not explained by `.artifacts/mcp-patch/`
  (that patch concerns the Jira/Confluence MCP only).

## Action required from human
1. Restore/verify the Testomat.io MCP resource endpoints (list/search).
2. Re-run `/run-qa-flow` for page 2228226 with the same arguments. It is safe to
   re-run: Jira duplicates are prevented by the preflight search
   (`project = "QA" AND labels = "qemu-manager-req-0.5" AND summary ~ "..."`) which will
   find the 30 already-created issues and mark them `existing`; Testomat cases will be
   created only after a working preflight search.
3. Optionally confirm whether the pre-existing Testomat entities from prior runs
   (requirement_version `0.5`, completed runs 2026-11-09T17-30-00_0.5 /
   2026-11-09T18-00-00_0.5) should be reconciled (`existing`/`stale`) before re-publish.
