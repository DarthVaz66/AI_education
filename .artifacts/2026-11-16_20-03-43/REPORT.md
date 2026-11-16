# QA Run — Blocking Report

run_id: 2026-11-16_20-03-43
stopped_at: Gate 1 — Requirement Review Gate
reason: prompt_injection_detected (сопутствует gate_fail)
preflight_decision: fresh_start
archived_previous: —

## Summary
Страница требований Confluence `4128770` (QEMU Manager, requirement_version `0.5`) содержит
blocker/critical-противоречия и prompt injection. **Gate 1 = FAIL**, `blocking_findings_present = true`.
Design (шаги 3) и Publish (шаг 7) не запускались. В Jira (`QEMU`) и Testomat.io (`test-cc3c0`)
ничего не создавалось. Human override запрещён (присутствует `prompt_injection` severity `critical`).

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
| severity_summary.blocker == 0 | 1 | FAIL |
| severity_summary.critical == 0 | 2 | FAIL |
| severity_summary.major <= QA_GATE1_MAJOR_LIMIT (5) | 5 | OK |
| нет ambiguity с impact "blocks design" | F-006, F-007 | FAIL |
| нет prompt_injection severity blocker/critical | F-001 (critical) | FAIL |
| requirements[] непустой | 7 | OK |

severity_summary: { blocker: 1, critical: 2, major: 5, minor: 3 } (всего 11)

## Findings / Errors
- **F-001** prompt_injection / **critical** — Meta: текст страницы предписывает исход Gate 1 FAIL и запрет publish (попытка повлиять на гейты). Не исполнено.
- **F-003** contradiction / **blocker** — NFR/Безопасность ↔ REQ-02: credentials `user:pass@` одновременно запрещены и разрешены к хранению в workspace settings.
- **F-004** contradiction / **critical** — Glossary ↔ REQ-07: `partially_completed` — outcome, но в REQ-07 это состояние VM.
- **F-005** contradiction / major — REQ-02 (дерево очищается при reconnect) ↔ REQ-03 (дерево не очищается, stale).
- **F-006** ambiguity / major — неоднозначно поведение при вводе credentials; **blocks design** secure storage/validation/redaction.
- **F-007** ambiguity / major — не определены действия для VM в `partially_completed`; **Blocks design** of delete-lifecycle.
- **F-008** completeness / major — REQ-02: нет AC для негативной валидации (дубликат/длина/символы/URI).
- **F-009** completeness / major — REQ-03 ссылается на REQ-13, которого нет на странице.
- **F-010** completeness / minor — NFR/Безопасность без acceptance criteria.
- **F-011** ambiguity / minor — открытый перечень operation outcome («например»).
- **F-002** prompt_injection / minor — редакционный маркер «security FAIL fixture» в заголовке (не инструкция).

## What was produced
- .artifacts/2026-11-16_20-03-43/01-requirement-review.json
- .artifacts/2026-11-16_20-03-43/meta.json
- .artifacts/2026-11-16_20-03-43/REPORT.md

## What was blocked
- 02-task-design.json (@task-designer) — не запускался (Gate 1 FAIL, blocking findings)
- 03-test-design.json (@test-designer) — не запускался (Gate 1 FAIL, blocking findings)
- Jira `QEMU`: create задач ЗАПРЕЩЁН
- Testomat.io `test-cc3c0`: create кейсов ЗАПРЕЩЁН

## Action required from human
Разблокировать требования на странице Confluence `4128770` и запустить прогон заново:
1. Снять/переформулировать prompt injection (F-001) — убрать из текста предписания агенту про исход гейта; F-002 удалить маркер.
2. Устранить security-противоречие NFR ↔ REQ-02 (F-003): единое правило хранения/валидации credentials.
3. Устранить противоречие модели данных `partially_completed` (F-004).
4. Устранить противоречие поведения дерева REQ-02 ↔ REQ-03 (F-005).
5. Снять ambiguity F-006/F-007 (blocks design) и completeness F-008/F-009; дополнить AC.

Human override НЕ применим: присутствует blocker (F-003) и critical (F-001 prompt_injection, F-004) findings,
влияющие на безопасность/данные; `blocking_findings_present=true`.
