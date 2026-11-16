# QA Run — Blocking Report

run_id: 2026-11-16_21-00-40
stopped_at: Gate 1 — Requirement Review Gate
reason: gate_fail
preflight_decision: fresh_start
archived_previous: —

## Summary
Страница требований Confluence `4128770` («EVC-003 contradictions / security FAIL», QEMU Manager,
requirement_version `0.5`, version 2) прошла Requirement Review (`status=completed`, 6 требований,
5 in-scope). Артефакт валиден по контракту. По findings **Gate 1 = FAIL**: 2 critical-противоречия
(одно из них — security: credentials `user:pass@`). `blocking_findings_present = true`.
Design (шаг 3) и Publish (шаг 7) не запускались. В Jira (`QEMU`) и Testomat.io (`test-cc3c0`)
ничего не создавалось. Human override **не применим** (critical findings, затрагивающие
безопасность/данные).

Примечание по безопасности: prompt injection в текущем содержимом страницы (v2) **не обнаружен**.
Страница была отредактирована (autosaved `2026-11-16T20:25:34Z`) после предыдущего прогона
`2026-11-16_20-03-43`, в котором на версии v1 был зафиксирован `prompt_injection` (critical) в
секции Meta/Glossary. В v2 эта вставка отсутствует (проверено по дословному дампу сырого
storage-HTML: HTML-комментариев, zero-width-символов и инструктивных паттернов нет).

## Gate retries
- Gate 2a (Jira): attempts=0/5 → not started
- Gate 2b (Test):  attempts=0/5 → not started
- Gate 1 через субагента не перепроходится (только human override / Blocking Report)

## Tool health
- Jira (QEMU): not probed — publish не достигнут
- Testomat.io (test-cc3c0): not probed — publish не достигнут
- deferred legs: none

## Decision point (if any)
- kind: —
- chosen: —

## Gate 1 — результат применения критериев
| Критерий | Значение | Итог |
|---|---|---|
| status == completed | completed | OK |
| severity_summary.blocker == 0 | 0 | OK |
| severity_summary.critical == 0 | 2 | FAIL |
| severity_summary.major <= QA_GATE1_MAJOR_LIMIT (8) | 5 | OK |
| нет ambiguity с impact "blocks design" | нет | OK |
| нет prompt_injection severity blocker/critical | нет | OK |
| requirements[] непустой | 6 | OK |

severity_summary: { blocker: 0, critical: 2, major: 5, minor: 3 } (всего 10)

## Findings / Errors
- **F-001** contradiction / **critical** — NFR/Безопасность («URI не может содержать credentials `user:pass@`», «секреты не пишутся в настройки») ↔ REQ-02 («URI хранится как введён пользователем, включая формат `user:pass@`»; AC «workspace settings могут содержать URI в том виде, в котором его ввёл пользователь») ↔ REQ-14 (redaction embedded credentials). Security-NFR и функциональное требование несовместимы; риск утечки секретов.
- **F-002** contradiction / **critical** — Glossary («Operation outcome ... `partially_completed` ... Не является состоянием VM») ↔ REQ-07 («`partially_completed` — это состояние VM»). Противоречие модели данных.
- **F-003** contradiction / major — REQ-02 (при неудачном reconnect дерево очищается) ↔ REQ-03 (дерево не очищается, stale).
- **F-004** ambiguity / major — REQ-03 AC «сортировка и группировка соблюдаются»: ключ/направление сортировки и правила группировки не заданы, критерий непроверяем.
- **F-005** ambiguity / minor — REQ-14: правило redaction env-переменных `SECRET|TOKEN|PASSWORD|KEY` не определено.
- **F-006** ambiguity / minor — REQ-14: источник/формат `{code}` в fallback «Unexpected error: {code}» не указан.
- **F-007** completeness / major — REQ-03 ссылается на REQ-13, которого нет на странице.
- **F-008** completeness / major — отсутствуют REQ-01, REQ-04–06, REQ-08–13 при статусе «ready for review».
- **F-009** completeness / major — REQ-02 обещает удаление подключений, но нет AC на удаление.
- **F-010** completeness / minor — NFR/Безопасность без acceptance criteria.

## What was produced
- .artifacts/2026-11-16_21-00-40/01-requirement-review.json
- .artifacts/2026-11-16_21-00-40/meta.json
- .artifacts/2026-11-16_21-00-40/REPORT.md

## What was blocked
- 02-task-design.json (@task-designer) — не запускался (Gate 1 FAIL, blocking findings)
- 03-test-design.json (@test-designer) — не запускался (Gate 1 FAIL, blocking findings)
- Jira `QEMU`: create задач ЗАПРЕЩЁН
- Testomat.io `test-cc3c0`: create кейсов ЗАПРЕЩЁН

## Action required from human
Устранить критические противоречия на странице Confluence `4128770` и запустить прогон заново:
1. **F-001 (critical, security):** согласовать единое правило для credentials в URI — запрет/маскирование
   (валидация + redaction перед сохранением) ИЛИ явное разрешение хранения с политикой redaction;
   привести NFR/Безопасность, REQ-02 и REQ-14 в соответствие.
2. **F-002 (critical):** определить, чем является `partially_completed` — исходом операции или
   состоянием VM; согласовать Glossary и REQ-07.
3. **F-003:** унифицировать поведение дерева при неуспешном reconnect (очистка vs stale).
4. **F-004:** задать ключ/направление сортировки и правила группировки в REQ-03.
5. Дополнить AC: удаление подключения (F-009), NFR/Безопасность (F-010), уточнить redaction (F-005),
   формат `{code}` (F-006); добавить/убрать висячую ссылку REQ-13 (F-007); подтвердить состав
   отсутствующих REQ-ов (F-008).

Human override НЕ применим: присутствуют critical findings (F-001 security, F-002 данные),
`blocking_findings_present=true`.
