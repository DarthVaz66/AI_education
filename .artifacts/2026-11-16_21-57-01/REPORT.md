# QA Run — Final Report

run_id: 2026-11-16_21-57-01
requirement_version: 0.5
confluence_page: 4096002
jira_project: QEMU
testomat_project: test-cc3c0 (source: argument)
preflight_decision: fresh_start
archived_previous: —

## Gates

| Gate | Итог | Детали |
|---|---|---|
| Gate 1 — Requirement Review | **PASS** | status=completed; blocker=0; critical=0; major=6 ≤ QA_GATE1_MAJOR_LIMIT(8); minor=1; нет ambiguity с impact `blocks design`; нет prompt_injection blocker/critical; requirements[]=7 (непуст) |
| Gate 2a — Jira Tasks | **PASS** | 13 задач (7 implementation + 6 clarification); 100% AC и requirement_refs; 100% dor_check=pass; 0 внутренних дублей; все clarifies_findings → major |
| Gate 2b — Test Model | **PASS** | 106 кейсов (positive=35, negative=21, boundary=50); AC покрыты positive; ветки ошибок — negative; полные boundary-наборы; 100% priority и step+expected; 2 N/A boundary с reason |
| Gate 2c — Cross-Artifact | **PASS** | requirement_version 0.5 совпадает в 01/02/03/meta; project_id совпадает; все 7 in-scope refs покрыты impl-задачами и кейсами; нет dangling refs |

## Findings (полный список)

- **F-001** | ambiguity | major | REQ-04 | «VM должна появиться в дереве быстро» — нет временной границы, тогда как REQ-12 задаёт «в течение 2 с». Impact: AC по времени появления VM неизмерим. Rec: задать конкретный SLA.
- **F-002** | ambiguity | major | REQ-09 | «По умолчанию используется разумный таймаут» — дефолт не задан. Impact: дефолтный timeout shutdown непроверяем. Rec: задать числовой дефолт (5–300).
- **F-003** | ambiguity | major | REQ-12 | «IP определяется при необходимости…» — триггер/путь резолва не определён. Impact: шаги теста недетерминированы. Rec: определить момент резолва IP и путь libvirt/QMP.
- **F-004** | completeness | major | REQ-12, REQ-18 | Для QMP-only текст tooltip у bridged disabled не специфицирован. Impact: точный текст tooltip неверифицируем. Rec: задать tooltip для QMP-only.
- **F-005** | completeness | major | Document | Разрывная нумерация REQ (есть только REQ-04, 09, 12, 13, 14, 16, 18). Impact: мешает трассировке/проверке полноты. Rec: подтвердить выдержку или восполнить нумерацию.
- **F-006** | completeness | major | Document | Отсутствуют разделы Non-Goals, NFR и Glossary. Impact: границы scope и нефункциональные ожидания не зафиксированы. Rec: добавить Non-Goals, NFR, глоссарий.
- **F-007** | completeness | minor | REQ-16, REQ-04 | REQ-16 опускает позиционное правило дефиса имени из REQ-04. Impact: тесты могут принять имена «-vm»/«vm-». Rec: явно упомянуть правило в REQ-16.

## Security
- prompt_injection: none (страница проверена в markdown- и storage-формате)
- blocking_findings_present: false
- Secrets не выводились; plaintext-секретов в артефактах/логах нет.

## Gate retries
- Gate 2a (Jira): attempts=0/5 → pass
- Gate 2b (Test):  attempts=0/5 → pass

## Publish
- Jira: created=10 (QEMU-40…QEMU-49), existing=3 (QEMU-23/26/27), failed=0, stale=0
- Testomat.io: created=106, existing=0, failed=0, stale=0

## Tool health
- Jira: ok (preflight label `qemu-manager-req-0.5` → 20 existing; search+create)
- Testomat.io: ok (system_ping ok; tests list/create); endpoint=/tests; suite=93e1e30b "QEMU Manager Tests"
- deferred legs: none

## Artifacts
- .artifacts/2026-11-16_21-57-01/01-requirement-review.json
- .artifacts/2026-11-16_21-57-01/02-task-design.json
- .artifacts/2026-11-16_21-57-01/03-test-design.json
- .artifacts/2026-11-16_21-57-01/04-publish-state.json
- .artifacts/2026-11-16_21-57-01/05-publish-report.json

## Recommendations
1. findings F-001…F-006 (major) сформировали clarification-задачи QEMU-44…QEMU-49 — уточнить требования до следующего перевыпуска, чтобы сократить разрыв нумерации и дефолты.
2. Publishing idempotent: повторный запуск найдёт уже созданные QEMU-40…49 и 106 кейсов (по label/summary и title) и пометит их `existing`.
3. Testomat create API требует suite_id (root не принимается) — кейсы размещены в suite 93e1e30b «QEMU Manager Tests» (первый прогон по странице 4096002 успешно опубликован впервые).
