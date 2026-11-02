# Skill: test-design

**Паттерн:** **Generator** (матрица тест-кейсов) + **Inversion** (если требование неполное — сначала запросить уточнение, а не генерировать «дырявые» кейсы).

## Назначение
Сформировать **тестовую модель (payload) для Qase** с позитивными, негативными и граничными сценариями, где они применимы. На этом этапе сущности в Qase не создаются.

## Inputs
- артефакт `requirement-review-report` со `status = completed` и `gate_recommendation = pass`;
- параметры Qase;
- правила тест-дизайна (эквивалентные классы, граничные значения).

## Шаги
1. **Extract test conditions** — выделить проверяемые условия из требований и acceptance criteria.
2. **Positive design** — построить happy path и альтернативные успешные сценарии для каждого in-scope требования.
3. **Negative design** — построить сценарии для недопустимых входов, ошибок, исключений и нарушения предусловий; если для требования негативные сценарии неприменимы — пометить `N/A` с указанием причины.
4. **Boundary design** — применить анализ граничных значений (min, max, just-inside, just-outside, empty, missing) для требований с числовыми / диапазонными / лимитными условиями; если границы неприменимы — пометить `N/A` с указанием причины.
5. **Assemble matrix** — оформить матрицу: ID, title, precondition, steps, expected, type, requirement ref.
6. **Build coverage summary** — по каждому требованию зафиксировать применимые типы и N/A-типы с обоснованием.
7. **Save artifact** — сохранить артефакт `test-design-model` в Artifact Store до выхода из Skill. **Тест-кейсы в Qase не создаются.**

## Output Contract
Skill обязан вернуть артефакт **`test-design-model`** со следующими обязательными полями:
- `artifact_id`;
- `requirement_version` (должна совпадать с `requirement-review-report.requirement_version`);
- `timestamp`;
- `qase_params`;
- `cases[]` — каждый с полями `temp_id`, `title`, `precondition`, `steps[]`, `expected`, `type` (`positive` / `negative` / `boundary`), `requirement_ref`;
- `coverage_summary[]` — по каждому требованию: `requirement_ref`, `applicable_types[]`, `na_types[]` с полями `type` и `reason`;
- `status` — `completed` / `blocked`;
- `gate_recommendation` — `pass` / `fail`;
- `blocking_reason` (обязательно при `status = blocked`).

**Условия успешного завершения:** артефакт сохранён в Artifact Store; для каждого in-scope требования есть хотя бы один positive-кейс; применимые негативные и boundary-кейсы сформированы, неприменимые — помечены N/A с причиной; у всех кейсов заполнены обязательные поля; `status = completed`; `gate_recommendation = pass`.

## Правила
- каждый кейс должен трассироваться к требованию;
- boundary-кейсы обязательны для требований с числовыми / диапазонными / лимитными условиями; неприменимость — только с явным обоснованием в `coverage_summary`;
- negative-кейсы не должны дублировать positive-кейсы с «инвертированным ожиданием» без нового условия;
- при неоднозначности требования — зафиксировать пробел в `requirement-review`, а не «придумывать» ожидаемый результат;
- **не создавать сущности в Qase** — только артефакт-модель.

## Quality Gate
См. **Gate 2b — Test Model Quality Gate** (покрытие всех применимых типов, обоснование N/A, трассируемость, заполненность обязательных полей).

## Failure Behaviour
При невозможности получить параметры Qase — вернуть `status = blocked` и `blocking_reason`; при неполных требованиях — зафиксировать ограничения покрытия в `coverage_summary` и не выдавать модель за полную; при непрохождении Gate 2b — вернуть модель на доработку в `test-design` или эскалировать. Публикация в Qase выполняется оркестратором только на этапе Publish после прохождения всех гейтов.