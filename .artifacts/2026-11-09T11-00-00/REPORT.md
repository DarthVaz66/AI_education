# QA Run — Blocking Report

run_id: 2026-11-09T11-00-00
stopped_at: Gate 1 — Requirement Review Gate
reason: gate_fail

## Context
- confluence_page: 1966081 (title «Test3»)
- jira_project: QA
- testomat_project: test-cc3c0 (source: argument)
- requirement_version: 0.3
- resolved testomat_project_id: test-cc3c0 (source: argument; no arg/env conflict, `.env` absent)

## What was produced
- `.artifacts/2026-11-09T11-00-00/meta.json`
- `.artifacts/2026-11-09T11-00-00/01-requirement-review.json` (contract valid, no `gate_recommendation`)
- `.artifacts/index.json`

## What was blocked
- **Step 3 Design** (`02-task-design.json`, `03-test-design.json`) — NOT started
- **Gate 2a / 2b / 2c** — NOT evaluated
- **Step 7 Publish** (Jira `QA`, Testomat `test-cc3c0`) — NOT started
- No Jira issues and no Testomat cases were created.

## Gate 1 decision (applied by orchestrator)
Criterion: `severity_summary.blocker == 0 AND critical == 0 AND major <= QA_GATE1_MAJOR_LIMIT` and no `ambiguity` finding whose `impact` contains `blocks design`.

Observed: **blocker = 0, critical = 0, major = 10, minor = 9** → **FAIL** (major 10 > limit 5).

> Note: `QA_GATE1_MAJOR_LIMIT` is taken from env; `.env` is absent, so the default `5` applies. If the limit is intentionally configured higher, this gate result changes — confirm the intended limit.

## Findings / Errors
Findings from `01-requirement-review.json` (19 total; 10 major + 9 minor).

**Major (10):**

| id | category | refs | impact (short) |
|----|----------|------|----------------|
| F-001 | contradiction | REQ-04, REQ-20 | Дубликат имени VM: REQ-04 запрещает (inline error), REQ-20 предлагает Overwrite — несовместимые правила |
| F-002 | contradiction | REQ-16, REQ-04 | «Вся валидация на клиенте» (REQ-16) vs проверка путей через libvirt (REQ-04) — невыполнимо на клиенте |
| F-003 | contradiction | REQ-18, REQ-04, REQ-12, REQ-13 | QMP-only для REQ-12/13 описан, но для REQ-04 (пути) ветка деградации отсутствует → create без libvirt не определён |
| F-005 | ambiguity | REQ-01, REQ-02, REQ-20 | Назначение `.qemu-manager.json` не определено (триггер / хранилище / payload) |
| F-006 | ambiguity | REQ-20 | Семантика «Overwrite?» не определена (что перезаписывается, судьба дисков) |
| F-012 | completeness | REQ-03, REQ-13 | Переход в `crashed` без REQ и без детекции краха — обязательство REQ-03 не выполнено |
| F-013 | completeness | META | Мета заявляет «зависимости», но раздела зависимостей нет |
| F-014 | completeness | REQ-14 | Таблица маппинга ошибок отсутствует → маппинг непроверяем |
| F-015 | completeness | REQ-02 | Нет правил/AC для edit/delete подключений |
| F-018 | contradiction | NFR-Security, REQ-14 | «Секреты не логируются» vs «полный сырой request/response в лог» — нужен redaction |

**Minor (9):** F-004 (REQ-13 диапазон 1–60 vs спец-значение 0), F-007 (лимит 10 подключений), F-008 (`[conn:vm]` без VM), F-009 (конфликт биnding с built-in VS Code), F-010 (`degraded` двойного назначения), F-011 («Resume» для `paused` и `suspended`), F-016 (edge/error клонирования), F-017 (миграция схемы конфига), F-019 (критерий «диагностической ценности»).

## Action required from human
Gate 1 FAIL заблокировал прогон. Варианты:
1. **Устранить находки в требованиях (Confluence 1966081, версия 0.3)** — в первую очередь довести `major` до ≤ 5 (F-001, F-002, F-003, F-005, F-006, F-012, F-013, F-014, F-015, F-018), затем перезапустить `/run-qa-flow`.
2. **Подтвердить/скорректировать `QA_GATE1_MAJOR_LIMIT`** — если лимит по регламенту иной; после уточнения пересмотреть решение.
3. **Явный human override Gate 1** — если требования принимаются как есть. Укажите `approved_by` и `reason`; override будет записан в `.artifacts/2026-11-09T11-00-00/meta.json` → `human_override` (действует только для этого прогона).

Критерий Gate 1 не смягчается: без устранения находок, уточнения лимита или явного override продолжение (Design → Gate 2a/2b/2c → Publish) невозможно.
