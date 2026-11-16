# QA Run — Blocking Report

run_id: 2026-11-16_02-06-16
stopped_at: Gate 2b — Test Model Quality Gate
reason: gate_fail
preflight_decision: fresh_start
archived_previous: —

## Gates
- Gate 1: PASS (13 findings — blocker=0, critical=0, major=7, minor=6; major ≤ QA_GATE1_MAJOR_LIMIT=8; нет ambiguity «blocks design»; нет prompt_injection blocker/critical)
- Gate 2a: PASS (27 tasks — 20 implementation + 7 clarification; 100% AC/requirement_refs; пояснения по major-findings F-001…F-007; DoR=pass 100%; 0 дублей)
- Gate 2b: **FAIL** — нарушен критерий «0 кейсов с ожиданием «не падает» без конкретного наблюдаемого результата»
- Gate 2c: NOT RUN (выполняется только после PASS Gate 2b)

## What was produced
Финальные пути (после финализации rename `.current` → `{run_id}`):
- .artifacts/2026-11-16_02-06-16/01-requirement-review.json — status=completed, requirement_version=0.5, 34 требования (26 in_scope), findings: 7 major / 6 minor
- .artifacts/2026-11-16_02-06-16/02-task-design.json — status=completed, 27 задач (20 implementation / 7 clarification)
- .artifacts/2026-11-16_02-06-16/03-test-design.json — status=completed, 146 кейсов (positive=80, negative=56, boundary=10), coverage_summary по 26 in-scope refs
- .artifacts/2026-11-16_02-06-16/meta.json — status=blocked, gate_results={gate1:pass, gate2a:pass, gate2b:fail, gate2c:null}, blocking_findings_present=true
- 04-publish-state.json / 05-publish-report.json — НЕ создавались (Publish не запускался)

## What was blocked
- **Publish (Jira create + Testomat.io create) не выполнялся.** Publish guard не пройден:
  `gate_results.gate2b != "pass"` и `blocking_findings_present == true` → create-операции запрещены.
- Ни одной Jira-задачи и ни одного Testomat.io-кейса не создано.
- Gate 2c не применялся.

## Findings / Errors
Нарушенный критерий Gate 2b: *«0 кейсов с ожиданием «не падает» без конкретного наблюдаемого результата»*.

- **TC-120** — requirement_ref `REQ-18`, type `positive`, priority `normal`
  - title: «Состояние degraded не приводит к падению или зависанию VS Code»
  - step: «Поработать в VS Code при degraded»
  - expected: «VS Code не падает и не зависает (AC3)»
  - Проблема: ожидание сформулировано как чистое отрицание («не падает») без конкретного наблюдаемого результата. Требование REQ-18 при этом даёт наблюдаемые факты (`дерево пустое`, `команды возвращают friendly-ошибку по REQ-14`), которые в кейсе не отражены.
  - Для сравнения: в предыдущем прогоне эквивалентный кейс содержал observable («…; дерево пустое») и Gate 2b проходил.

Прочие критерии Gate 2b выполнены:
- каждое AC покрыто ≥1 positive (у каждого in-scope ref есть positive-кейсы);
- ветки ошибок покрыты negative либо N/A с конкретным reason (coverage_summary, 25 N/A-записей с reason);
- числовые/диапазонные ограничения покрыты boundary-набором (TC-021, TC-022, TC-061, TC-085, TC-105, TC-111, TC-112, TC-126, TC-132) либо N/A с reason;
- у 100% кейсов есть priority; шаги оформлены парами step+expected; 0 кейсов без requirement_ref;
- testomat_params.project_id = "test-cc3c0" совпадает с meta.json.testomat_project_id.

Дополнительно (не влияет на решение, для сведения):
- Пограничные по диагностичности формулировки: TC-118 expected «Успешно (AC1)», TC-121 expected «Event-based автообновление работает (AC4)» — рекомендуется конкретизировать наблюдаемый результат.

## Security
- prompt_injection: не обнаружен (ни в тексте Confluence, ни в артефактах).
- Секреты в артефактах не обнаружены; create-операции не выполнялись.

## Action required from human
1. Устранить дефект тест-модели: кейс TC-120 должен содержать конкретный наблюдаемый результат (например, «дерево пустое; команды возвращают friendly-ошибку по REQ-14; VS Code не падает/не зависает»).
2. Принять решение по эскалации:
   - Human override по Gate 2b в рамках этого прогона **неприменим** — установлено `blocking_findings_present=true`; override не может разрешить publish при blocking findings.
   - Resume незавершённого прогона не поддерживается. После исправления (методики/генерации test-designer) требуется **новый запуск** `/run-qa-flow` с чистым `.artifacts/.current/`; текущий `.current` будет (при следующем старте) автоматически архивирован в `.artifacts/failed_*`.
   - Либо явно зафиксировать исключение продуктового решения (с отдельным подтверждением владельца), если кейс считается допустимым.
