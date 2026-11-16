# QA Run — Final Report

run_id: 2026-11-16_21-43-47
requirement_version: 0.5
confluence_page: 4161537
jira_project: QEMU
testomat_project: test-cc3c0 (source: argument)
preflight_decision: fresh_start
archived_previous: —

## Gates
- Gate 1: PASS (10 findings: blocker=0, critical=0, major=8, minor=2; QA_GATE1_MAJOR_LIMIT=8; no ambiguity "blocks design"; no prompt_injection blocker/critical; requirements[]=14 entries)
- Gate 2a: PASS (20 tasks: implementation=12, clarification=8; 0 duplicates; 100% AC; 100% dor_check=pass; clarification findings all major)
- Gate 2b: PASS (113 cases: positive=61, negative=31, boundary=21; full boundary sets on REQ-09/REQ-13/REQ-14/REQ-19; reasoned N/A elsewhere)
- Gate 2c: PASS (cross-check ok: version 0.5 consistent in 01/02/03/meta; project_id consistent; 13/13 in-scope refs covered; Glossary out-of-scope covered by none)

## Findings
(Polный список из 01-requirement-review.json)
- F-001 | completeness | major | refs: Non-Goals | evidence: страница не содержит раздела Non-Goals (после Glossary идут только REQ-01 … REQ-22) | impact: границы scope не зафиксированы, design/tests не отделяют in-scope от исключённого.
- F-002 | completeness | major | refs: REQ-02, REQ-04..07, REQ-12, REQ-15..16, REQ-18, REQ-20 | evidence: присутствуют только REQ-01,03,08–11,13–14,17,19,21–22; остальные номера отсутствуют | impact: невозможна проверка полноты/трассируемости; возможна потеря требований.
- F-003 | completeness | major | refs: Glossary | evidence: введены `partially_completed` и `degradedReason=runtime_missing` без покрывающих REQ | impact: эти значения нереализуемы/непокрыты тестами.
- F-004 | ambiguity | major | refs: NFR/Производительность | evidence: «…на других конфигурациях значения ориентировочные» | impact: квантор без границ → на не-эталонных конфигурациях нет детерминированного AC.
- F-005 | ambiguity | major | refs: REQ-03, REQ-13 | evidence: «временная недоступность данных → (stale)» — порог/длительность и переход stale→ошибка не заданы | impact: недетерминированный AC; неясно взаимодействие с interval=0.
- F-006 | ambiguity | minor | refs: REQ-11, REQ-21 | evidence: «Resume … для paused выполняет REQ-11» (самореферентно) | impact: допускает ошибочное прочтение; AC спасает, но текст вводит в заблуждение.
- F-007 | completeness | major | refs: REQ-01, Glossary | evidence: «ошибка активации → … „Retry“» — не определены ни триггер, ни эффект Retry | impact: кнопка Retry и переход в degraded не тестируемы.
- F-008 | ambiguity | major | refs: REQ-14 | evidence: redaction env-переменных «подстрочно по имени», список подстрок-триггеров не задан | impact: AC «лог не содержит секретов» неверифицируем.
- F-009 | completeness | major | refs: Glossary, REQ-14, REQ-01 | evidence: Glossary: в degraded «все команды возвращают friendly-ошибку по REQ-14», а REQ-14 покрывает только libvirt/QMP | impact: ссылка не обеспечена определением; поведение degraded/runtime_missing не специфицировано.
- F-010 | ambiguity | minor | refs: REQ-22, REQ-13 | evidence: «events или polling …», AC «в течение интервала обновления», но при domainEventSupport=true polling отключён | impact: база измерения AC неоднозначна (event vs polling латентность).

## Gate retries
- Gate 2a (Jira): attempts=0/5 → pass
- Gate 2b (Test):  attempts=0/5 → pass

## Security
- prompt_injection: none
- blocking_findings_present: false

## Publish
- Jira: created=20, existing=0, failed=0, stale=0
- Testomat.io: created=113, existing=0, failed=0, stale=0

## Tool health
- Jira: ok (attempts=1/12)
- Testomat.io: ok (attempts=1/12); container suite created (93e1e30b, file-type)
- deferred legs: none

## Artifacts
- .artifacts/2026-11-16_21-43-47/01-requirement-review.json
- .artifacts/2026-11-16_21-43-47/02-task-design.json
- .artifacts/2026-11-16_21-43-47/03-test-design.json
- .artifacts/2026-11-16_21-43-47/04-publish-state.json
- .artifacts/2026-11-16_21-43-47/05-publish-report.json
- .artifacts/2026-11-16_21-43-47/meta.json

## Recommendations
- Устранить findings F-001..F-009 через clarification-задачи (QEMU-32…QEMU-39) и перевыпуск требований; F-006, F-010 — minor.
- Testomat.io: удалить неиспользуемую folder-сьюту «QEMU Manager» (f6a8b14b), созданную ошибочно до определения file-type контейнера.
- Проект Testomat.io не содержал сьютов; при штатном пайплайне стоит заранее задавать `testomat_suite_id` (file-type), чтобы избегать создания обходной сьюты.
