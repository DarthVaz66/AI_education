# QA Run — Blocking Report

run_id: 2026-11-09T10-00-00
stopped_at: Gate 1 — Requirement Review Gate
reason: gate_fail

## Context
- confluence_page: 360449
- jira_project: QA
- testomat_project: test-cc3c0 (source: argument)
- requirement_version: 0.2 (ready for review)
- resolved testomat_project_id: test-cc3c0 (source: argument; no arg/env conflict, `.env` absent)

## What was produced
- `.artifacts/2026-11-09T10-00-00/meta.json`
- `.artifacts/2026-11-09T10-00-00/01-requirement-review.json` (contract valid, no `gate_recommendation`)
- `.artifacts/index.json`

## What was blocked
- **Step 3 Design** (`02-task-design.json`, `03-test-design.json`) — NOT started
- **Gate 2a / 2b / 2c** — NOT evaluated
- **Step 7 Publish** (Jira `QA`, Testomat `test-cc3c0`) — NOT started
- No Jira issues and no Testomat cases were created.

## Gate 1 decision (applied by orchestrator)
Criterion: `severity_summary.blocker == 0 AND critical == 0 AND major <= QA_GATE1_MAJOR_LIMIT (default 5)` and no `ambiguity` finding whose `impact` contains `blocks design`.

Observed: **blocker = 1**, critical = 3, major = 9, minor = 2 → **FAIL** (blocker > 0; also critical > 0; also major > 5).

## Findings / Errors
Findings from `01-requirement-review.json` (all 15):

| id | category | severity | requirement_refs | impact (short) |
|----|----------|----------|------------------|----------------|
| F-001 | contradiction | **blocker** | REQ-12, Non-Goals | Scope противоречит функции: bridge/DHCP одновременно вне scope и обязательны → невозможно проектировать и определять дефекты |
| F-002 | contradiction | **critical** | REQ-07 | Полный rollback при удалении файлов дисков противоречит необратимости удаления qcow2 |
| F-003 | contradiction | **critical** | REQ-02, REQ-18, REQ-12, REQ-13 | QMP-only режим заявлен, но bridge-list/события требуют libvirt — часть AC недостижима |
| F-004 | contradiction | major | REQ-18, NFR | «libvirt ИЛИ QEMU+QMP» vs NFR «libvirt 8.0+, QEMU 6.0+» — разные матрицы окружений |
| F-005 | contradiction | major | REQ-16, REQ-04 | Клиентская валидация «по REQ-04» включает server-side (libvirt) проверки |
| F-006 | ambiguity | major | REQ-01, REQ-02 | `.qemu-manager.json` нигде не описан и не связан с workspace settings |
| F-007 | ambiguity | major | REQ-13 | `virConnectIsAlive` — не проверка поддержки событий; capability probe не определён |
| F-008 | completeness | **critical** | REQ-03, REQ-11, REQ-05..08 | Состояние `suspended` отображается, но не создаётся и не обрабатывается ни одной REQ |
| F-009 | completeness | major | REQ-02 | Лимит 10 подключений без AC/поведения при превышении |
| F-010 | ambiguity | major | REQ-12 | Не определён способ/условия определения IP для user-nat |
| F-011 | ambiguity | major | REQ-14 | Не определён критерий «ошибки с диагностической ценностью» для «Show log» |
| F-012 | completeness | major | REQ-15 | Не определено значение `[conn:vm]` для событий без VM/подключения |
| F-013 | completeness | major | REQ-20, REQ-04 | libvirt-зависимые проверки путей REQ-04 невыполнимы при offline-импорте |
| F-014 | ambiguity | minor | REQ-01, REQ-18 | Одно состояние `degraded` с разной семантикой выхода |
| F-015 | contradiction | minor | Мета | Заявление о «полноте по чек-листу» противоречит найденным пробелам |

## Action required from human
Gate 1 FAIL заблокировал прогон. Требуется одно из:
1. **Устранить находки в требованиях (Confluence 360449)** — в первую очередь blocker `F-001` и critical `F-002`, `F-003`, `F-008`; затем перезапустить `/run-qa-flow` с той же страницей.
2. **Явный human override Gate 1** — если требования сознательно принимаются как есть. Для этого подтвердите:
   - `approved_by` (кто утверждает),
   - `reason` (обоснование),
   - подтверждение, что blocker F-001 и criticals принимаются осознанно.
   Override будет зафиксирован в `.artifacts/2026-11-09T10-00-00/meta.json` → `human_override` и действует только для этого прогона.

Без устранения находок или явного override продолжение (Design → Gate 2a/2b/2c → Publish) невозможно: критерий Gate 1 не смягчается.
