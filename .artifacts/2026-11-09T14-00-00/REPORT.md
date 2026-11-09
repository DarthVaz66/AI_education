# QA Run — Blocking Report

run_id: 2026-11-09T14-00-00
stopped_at: Gate 1 — Requirement Review Gate
reason: gate_fail

## Context
- confluence_page: 2129922 (title «Требования тест 4», space `~712020235d49aa26bb4f3e8f425cb4c132578a`, Confluence version 1)
- jira_project: QA
- testomat_project: test-cc3c0 (source: argument)
- **testomat_project_id resolution:** arg = `test-cc3c0`, env = unset (no `.env` present), MCP = `test-cc3c0` → resolved `test-cc3c0`, source = **argument** (no arg/env conflict)
- requirement_version: **0.4** (`requirement_status: ready_for_review`)
- resumed from in-progress run `2026-11-09T14-00-00` (same page / jira / testomat project)

## What was produced
- `.artifacts/2026-11-09T14-00-00/meta.json`
- `.artifacts/2026-11-09T14-00-00/01-requirement-review.json` (contract valid, no `gate_recommendation`)
- `.artifacts/index.json`
- (this report)

## What was blocked
- **Step 3 Design** (`02-task-design.json`, `03-test-design.json`) — NOT started
- **Gate 2a / 2b / 2c** — NOT evaluated
- **Step 7 Publish** (Jira `QA`, Testomat `test-cc3c0`) — NOT started
- No Jira issues and no Testomat cases were created. Confluence was not modified.

## Gate 1 decision (applied by orchestrator)
Criterion:
`severity_summary.blocker == 0 AND severity_summary.critical == 0 AND severity_summary.major <= QA_GATE1_MAJOR_LIMIT (default 5)` and no `ambiguity` finding whose `impact` contains `blocks design`.

Observed: **blocker = 0, critical = 1, major = 3, minor = 6** → **FAIL** (critical > 0).
`QA_GATE1_MAJOR_LIMIT` = default `5` (no `.env`, env var unset).

The criterion is not softened. This is not an artifact defect and not a case for orchestrator re-interpretation — it is a genuine critical requirement conflict; resolving it requires either a requirements fix or an explicit human override.

## Findings / Errors
Findings from `01-requirement-review.json` (10 total).

| id | category | severity | requirement_refs | impact (short) |
|----|----------|----------|------------------|----------------|
| F-001 | contradiction | **critical** | NFR/Безопасность, REQ-02, REQ-14 | NFR запрещает писать «URI с credentials» в настройки, но REQ-02 хранит URI подключений (возможен `qemu+ssh://user:pass@host`) в workspace settings → утечка учётных данных; design не может выбрать стратегию (запрет / reject / strip). |
| F-002 | contradiction | major | REQ-02, REQ-03 | Одно условие (активное подключение стало недоступно) даёт два несовместимых поведения: REQ-02 «очищает дерево» vs REQ-03 «последнее известное состояние с `(stale)`». |
| F-003 | contradiction | major | REQ-17 | Win/Linux-дефолт `Ctrl+Shift+W` совпадает с built-in VS Code «Close Window», при этом расширение не переопределяет built-in → AC «дефолтный биндинг работает на всех ОС» невыполним для Shutdown. |
| F-004 | ambiguity | minor | REQ-07, REQ-03 | `partially_completed` не входит в список состояний REQ-03; неясно — состояние VM или операции. |
| F-005 | ambiguity | minor | REQ-02 | Не определено, вызывает ли edit только имени (без смены URI) разрыв/переподключение и очистку дерева. |
| F-006 | ambiguity | minor | REQ-12 | REQ-12 «если IP определим» — неограниченное условие без механизма/таймаута/AC для ветки `unknown`. |
| F-007 | ambiguity | minor | REQ-14 | Redaction env-переменных `SECRET|TOKEN|PASSWORD|KEY` — не указано, чьё окружение сканируется (extension host / host OS / remote libvirt). |
| F-008 | completeness | major | REQ-14, REQ-18 | Таблица маппинга названа «libvirt / QMP», но содержит только VIR_ERR_*/system-коды; для QMP-only режима маппинга QMP-ошибок нет. |
| F-009 | completeness | minor | REQ-16, REQ-04 | REQ-16 добавляет серверную проверку «доступность storage pool», которой нет в REQ-04 и у которой нет AC. |
| F-010 | completeness | minor | Non-Goals, REQ-18, REQ-22 | Non-Goals перечисляет ограничения QMP-only только через REQ-04/12/13, опуская REQ-18/REQ-22. |

### Verification note
- CQL `id = 2129922` → page «Требования тест 4» (read access confirmed; write access confirmed by tool).
- Body non-emptiness independently corroborated by CQL text matches on the page: `text ~ "REQ-17"`, `text ~ "QMP"`, `text ~ "partially_completed"` all returned page 2129922 (these tokens do not occur in the title, so they match the body).
- Note: an earlier run `2026-11-09T13-00-00` recorded the same page as having an empty body. Current evidence shows the page now carries requirements (v0.4). The review for this run is grounded in the current content.

## Action required from human
Gate 1 FAIL blocks the run. One of the following is required:
1. **Fix the requirements** in Confluence `2129922` — first of all the critical `F-001` (credentials in URI vs the security NFR; define reject/strip behaviour and an AC asserting no plaintext credentials in settings), then the majors `F-002`, `F-003`, `F-008`; re-run `/run-qa-flow` with the same page.
2. **Explicit human override of Gate 1** — if the requirements are consciously accepted as-is. Provide:
   - `approved_by` (who approves),
   - `reason` (justification),
   - confirmation that the critical `F-001` (credential leak) is knowingly accepted.
   The override will be recorded in `.artifacts/2026-11-09T14-00-00/meta.json` → `human_override` and applies to this run only.

Without a requirements fix or an explicit override, continuation (Design → Gate 2a/2b/2c → Publish) is impossible: the Gate 1 criterion is not softened.
