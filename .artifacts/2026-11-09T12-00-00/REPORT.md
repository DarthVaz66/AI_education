# QA Run — Blocking Report

run_id: 2026-11-09T12-00-00
stopped_at: Preflight — source requirements unavailable
reason: missing_input

## Context
- confluence_page: 21299221 — **not found (404)**
- jira_project: QA
- testomat_project: test-cc3c0 (source: argument)
- requirement_version: none (review not started)
- resolved testomat_project_id: test-cc3c0 (source: argument; no arg/env conflict, `.env` absent)

## What was produced
- `.artifacts/2026-11-09T12-00-00/meta.json`
- `.artifacts/index.json`
- (this report)

No requirement-review artifact was produced — the source page could not be read.

## What was blocked
- **Step 1 Requirement Review** — NOT started (source page unavailable)
- **Step 2 Gate 1** — NOT evaluated
- **Step 3 Design** (`02-task-design.json`, `03-test-design.json`) — NOT started
- **Gate 2a / 2b / 2c** — NOT evaluated
- **Step 7 Publish** (Jira `QA`, Testomat `test-cc3c0`) — NOT started
- No Jira issues and no Testomat cases were created.

## Findings / Errors
Confluence page `21299221` is not retrievable by this account. Independent verification:
- CQL `id = 21299221` → 0 results
- `get_confluence_page_versions(21299221)` → HTTP 404
- `check_confluence_permissions(21299221)` → HTTP 404 («Page 21299221 not found»)

Authentication itself is valid (user: Valentin / pvasecond@gmail.com); read access is confirmed for the accessible spaces (`MFS`, `Valentin`). The failure is specific to this page ID: it does not exist at `pvasecond.atlassian.net` or is not shared with this account.

For comparison, sibling IDs in the same space resolved fine (e.g. `360449` → «Требования тест 2», `1966081` → «Test3»), so the tooling/permissions path is working.

## Action required from human
The run cannot start because the mandatory source page is missing. Please provide one of:
1. **Correct Confluence page ID/URL** for the intended requirements page, then re-run `/run-qa-flow`.
2. **Access grant** — if `21299221` exists but lives in another space/tenant, share it with the account `pvasecond@gmail.com` (or fix the base URL), then re-run.
3. Confirmation that the page was deleted/moved — in that case pick the new location.

I did not start requirement review, design, or any publishing, and did not create anything in Jira or Testomat.io.
