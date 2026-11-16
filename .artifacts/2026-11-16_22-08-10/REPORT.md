# QA Run — Blocking Report

run_id: 2026-11-16_22-08-10
stopped_at: Gate 1 — Requirement Review Gate
reason: gate_fail
preflight_decision: fresh_start
archived_previous: —

## Summary
Gate 1 FAIL: `severity_summary.blocker = 1` (> 0) and `critical = 2` (> 0).
`blocking_findings_present = true`. Design, Jira create и Testomat create
**запрещены**. Human override невозможен до нового PASS Gate 1.

## Gates
| Gate | Result |
|---|---|
| Gate 1 — Requirement Review | **FAIL** (blocker=1, critical=2, major=4, minor=1) |
| Gate 2a — Jira Tasks | not_started |
| Gate 2b — Test Model | not_started |
| Gate 2c — Cross-Artifact | not_started |
| Publish | not_started |

Gate 1 criteria:
- status == completed → PASS
- severity_summary.blocker == 0 → **FAIL** (1)
- severity_summary.critical == 0 → **FAIL** (2)
- severity_summary.major <= QA_GATE1_MAJOR_LIMIT (8) → PASS (4)
- no ambiguity with "blocks design" → PASS
- no prompt_injection blocker/critical → PASS
- requirements[] non-empty → PASS (6)

## Gate retries
- Gate 2a (Jira): attempts=0/5 → not_started
- Gate 2b (Test):  attempts=0/5 → not_started

## Security
- prompt_injection: none (страница прочитана в markdown + raw storage; инъекционных блоков нет)
- blocking_findings_present: true

## Tool health
- Jira: not contacted (publish not reached)
- Testomat.io: not contacted (publish not reached)

## Decision point (if any)
- kind: —
- chosen: —

## What was produced
- .artifacts/2026-11-16_22-08-10/01-requirement-review.json (status=completed, 6 requirements, 8 findings)
- .artifacts/2026-11-16_22-08-10/meta.json
- .artifacts/2026-11-16_22-08-10/REPORT.md (this file)

Preflight note: `.artifacts/.current/` было непустым на момент старта (оставшийся
`meta.json` предыдущего прогона). Согласно инварианту он считается недоверенным;
данный прогон стартовал как fresh start (запись в index.json для `.current/`
отсутствовала, архивация `failed_*` не потребовалась — каталог создан заново
под текущий run_id).

## What was blocked
- `@task-designer` (02-task-design.json): не запускался — Gate 1 FAIL.
- `@test-designer` (03-test-design.json): не запускался — Gate 1 FAIL.
- Jira create (project QEMU): запрещено — Gate 1 FAIL / blocking_findings_present.
- Testomat.io create (project test-cc3c0): запрещено — Gate 1 FAIL / blocking_findings_present.

## Findings (полный список, 8)
| id | category | severity | requirement_refs | evidence / impact |
|---|---|---|---|---|
| F-001 | contradiction | **blocker** | NFR/Безопасность, REQ-02 | NFR запрещает credentials `user:pass@` в URI; REQ-02 предписывает хранить URI как введён пользователем, включая `user:pass@`. Секреты попадают в персистентные workspace settings вопреки NFR → ни design, ни security-тесты не построить однозначно. |
| F-002 | contradiction | **critical** | REQ-02, REQ-03 | REQ-02: при неудачном reconnect «дерево очищается»; REQ-03: при недоступности данных «дерево не очищается», stale. Противоположное поведение дерева → неоднозначный state machine и UI-тесты. |
| F-003 | contradiction | **critical** | Glossary, REQ-07 | Glossary: `partially_completed` «не является состоянием VM»; REQ-07: `partially_completed` — «состояние VM». Конфликт модели состояний → ломает state machine и отображение. |
| F-004 | completeness | major | REQ-01, REQ-04–06, REQ-08–13 | На странице только REQ-02,03,07,14; REQ-03 ссылается на отсутствующий REQ-13 (висячая ссылка). Document-level пробел → неполнота покрытия и трассируемости. |
| F-005 | ambiguity | major | REQ-03 | «сортировка и группировка соблюдаются» — не задан ключ/направление сортировки и правило группировки → AC непроверяем. |
| F-006 | ambiguity | major | REQ-14, NFR/Безопасность | Шаблон env-переменных `SECRET\|TOKEN\|PASSWORD\|KEY` — не указан режим сопоставления (регистр/подстрока/границы) → риск утечки секретов, недетерминированный redaction-тест. |
| F-007 | completeness | major | REQ-02 | REQ-02 задаёт ограничения имени (1–32, charset, уникальность) и операции add/edit/delete, но нет AC на валидацию/уникальность имени и на удаление → непокрытое поведение. |
| F-008 | ambiguity | minor | REQ-02 | «уникально в рабочей области» — «рабочая область» не определена в Glossary. |

severity_summary: { "blocker": 1, "critical": 2, "major": 4, "minor": 1 }

## Action required from human
1. Устранить противоречия F-001 (blocker, security), F-002 и F-003 (critical) в
   исходных требованиях на странице Confluence 4128770 — требуется продуктовое
   решение по политике хранения credentials в URI, поведению дерева при
   недоступности и статусу `partially_completed`.
2. Устранить пробелы полноты (F-004, F-007) и неоднозначности (F-005, F-006, F-008).
3. После обновления требований — повторный запуск `/run-qa-flow` с чистым
   `.artifacts/.current/` (resume не поддерживается).
4. Human override требует нового артефакта с PASS Gate 1 и невозможен при
   security-блокере F-001 и `blocking_findings_present=true`.
