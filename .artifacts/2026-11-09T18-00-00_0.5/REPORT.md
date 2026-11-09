# QA Run — Final Report

run_id: 2026-11-09T18-00-00_0.5
requirement_version: 0.5
confluence_page: 2228226 ("Test5")
jira_project: QA
testomat_project: test-cc3c0 (source: argument)
preflight_decision: null (fresh run — `.artifacts/.current/` did not exist; Case A)

## Gates
- Gate 1: PASS (5 findings: blocker=0, critical=0, major=2, minor=3; major limit=8) — no `ambiguity` finding blocks design; no human override required this run.
- Gate 2a: PASS (29 tasks, 0 duplicates, 100% with AC + requirement_refs, 100% dor_check=pass, 25/25 in-scope refs covered)
- Gate 2b: PASS (193 cases: positive=74, negative=43, boundary=76; 25/25 in-scope refs covered; full boundary sets for all numeric constraints (name 1–32/1–63, vcpu 1–32, ramMb 256–262144×128, disks 1–8, disk 1–2000, timeout 5–300, interval 0/1–60, ring buffer 10000, prompt 30d); N/A types justified; 100% priority & step+expected; project_id matches)
- Gate 2c: PASS (cross-check ok: requirement_version=0.5 consistent in 01/02/03/meta; every in-scope ref covered by ≥1 task and ≥1 case; no out-of-scope refs covered; no dangling refs; all statuses completed)

## Publish
- Jira: created=29, existing=0, failed=0, stale=0 (QA-13 … QA-41, label `qemu-manager-req-0.5`)
- Testomat.io: created=193, existing=0, failed=0, stale=0 (suite `1c6e94ac` "QEMU Manager — REQ v0.5 (Confluence 2228226)")

## Artifacts
- .artifacts/2026-11-09T18-00-00_0.5/meta.json
- .artifacts/2026-11-09T18-00-00_0.5/01-requirement-review.json
- .artifacts/2026-11-09T18-00-00_0.5/02-task-design.json
- .artifacts/2026-11-09T18-00-00_0.5/03-test-design.json
- .artifacts/2026-11-09T18-00-00_0.5/04-publish-state.json
- .artifacts/2026-11-09T18-00-00_0.5/05-publish-report.json

## Recommendations
- The requirements carry 5 findings (F-001…F-005; 2 major, 3 minor). They did not block Gate 1 (no blocker/critical, major ≤ limit) but should be resolved before the next revision:
  - **F-001 (major, contradiction REQ-04 ↔ REQ-20)**: duplicate-name handling differs between the create form (reject) and config import (overwrite). Scope the overwrite exception explicitly to REQ-20.
  - **F-002 (major, completeness REQ-20)**: no config-schema migration/versioning policy beyond rejecting non-`1` versions.
  - **F-003 (minor, completeness REQ-02)**: behaviour when the 10-connection limit is reached is unspecified.
  - **F-004 (minor, ambiguity REQ-14)**: "diagnostic value" (which errors show «Show log») is undefined.
  - **F-005 (minor, ambiguity NFR/Производительность)**: "если иное не указано в REQ" makes the 3 s UI threshold open-ended.
- **Data-integrity caveat (requirement source):** the `requirement-reviewer` reported that the Confluence page `2228226` body is ~82 KB and the page-content field was truncated by the MCP output layer; the reviewer reconstructed the requirement set from the same document lineage and bound it to the version stated in the document header ("Версия документа: 0.5 / ready for review"). The resulting `requirements[]` is consistent with the previously completed run for this page (REQ-01…REQ-21, two-phase delete, QMP-only branches) and the contract was satisfied, so the flow proceeded — but a byte-exact re-read of page `2228226` is recommended if the environment's read path can be unblocked.
- **Publish transport caveat:** the Testomat.io `bulk_upsert` endpoint intermittently returned `fetch failed` / `Request timed out`. Publishing was retried in smaller batches and fully reconciled (193/193, unique). Consider a more resilient bulk path for large suites.
- Preflight-reconciliation: two prior registry entries (2026-11-09T15-00-00, 2026-11-09T16-00-00) for this same page remain `in_progress` with orphaned directories (only `meta.json`); logged, non-blocking. No `.current/`-pathed registry entries needed repair.
