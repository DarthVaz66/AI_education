# Skill: requirement-review

**Паттерн:** **Reviewer** — оценка требований по чек-листу, отделение «что проверять» от «как проверять».

## Назначение
Выявить противоречия, неоднозначности и пробелы полноты в требованиях до проектирования.

## Inputs
- требования из Confluence (snapshot);
- чек-лист review (contradictions / ambiguities / completeness);
- контекст продукта / границ релиза.

## Шаги
1. **Contradiction check** — сравнить требования между собой и с внешними ограничениями; зафиксировать конфликты.
2. **Ambiguity check** — найти формулировки, допускающие более одной интерпретации; указать альтернативные трактовки.
3. **Completeness check** — проверить наличие обязательных элементов: границы, исключения, зависимости, критерии приёмки, нефункциональные требования (если применимо).
4. **Scoring / Severity** — присвоить severity (blocker / critical / major / minor) и evidence.
5. **Save artifact** — сохранить артефакт `requirement-review-report` в Artifact Store до выхода из Skill.
6. **Emit report** — вернуть артефакт для проверки Gate 1.

## Output Contract
Skill обязан вернуть артефакт **`requirement-review-report`** со следующими обязательными полями:
- `artifact_id`;
- `requirement_version` (snapshot requirements);
- `timestamp`;
- `contradictions[]` — каждая с полями `id`, `description`, `severity`, `evidence`;
- `ambiguities[]` — каждая с полями `id`, `description`, `alternatives[]`, `severity`, `evidence`;
- `completeness_gaps[]` — каждый с полями `id`, `missing_element`, `severity`, `evidence`;
- `status` — `completed` / `blocked`;
- `gate_recommendation` — `pass` / `fail`;
- `blocking_reason` (обязательно при `status = blocked`).

**Условия успешного завершения:** артефакт сохранён в Artifact Store, все три категории проверены, у каждой проблемы заполнены severity и evidence, `status = completed`, `gate_recommendation = pass`.

## Правила
- не исправлять требования, только фиксировать проблемы;
- каждая проблема должна иметь evidence (цитата / ссылка);
- если противоречие затрагивает безопасность / данные / юридические аспекты — severity = blocker.

## Quality Gate
См. **Gate 1 — Requirement Review Gate**.

## Failure Behaviour
При невозможности прочитать Confluence — не формировать отчёт на предположениях, вернуть `status = blocked` и `blocking_reason`, эскалировать; при неполном чек-листе — зафиксировать в артефакте, какие категории не проверены, и вернуть `gate_recommendation = fail`.