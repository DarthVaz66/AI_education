# Skill: task-design

**Паттерн:** **Generator** (шаблон Jira-задачи + правила стиля) с элементами **Pipeline** (не переходить к формированию payload, пока требования не прошли Gate 1).

## Назначение
Преобразовать требования, прошедшие Gate 1, в **payload для создания задач Jira**. На этом этапе сущности в Jira не создаются.

## Inputs
- артефакт `requirement-review-report` со `status = completed` и `gate_recommendation = pass`;
- параметры Jira (проект, тип задачи);
- Definition of Ready / шаблон задачи.

## Шаги
1. **Decompose** — разбить требования на задачи по принципу «одна задача — один проверяемый результат».
2. **Structure** — заполнить шаблон: summary, description, acceptance criteria, links to requirements, dependencies.
3. **Trace** — установить связь каждой задачи с требованием / требованием-родителем.
4. **Validate** — проверить, что задача соответствует Definition of Ready и не дублирует существующие задачи.
5. **Save artifact** — сохранить артефакт `task-design-payload` в Artifact Store до выхода из Skill. **Задачи в Jira не создаются.**

## Output Contract
Skill обязан вернуть артефакт **`task-design-payload`** со следующими обязательными полями:
- `artifact_id`;
- `requirement_version` (должна совпадать с `requirement-review-report.requirement_version`);
- `timestamp`;
- `jira_params` (проект, тип задачи);
- `tasks[]` — каждая с полями `temp_id`, `summary`, `description`, `acceptance_criteria[]`, `requirement_refs[]`, `dependencies[]`, `dor_check` (`pass` / `fail`);
- `duplicate_check` — `pass` / `fail`, со списком найденных дублей;
- `status` — `completed` / `blocked`;
- `gate_recommendation` — `pass` / `fail`;
- `blocking_reason` (обязательно при `status = blocked`).

**Условия успешного завершения:** артефакт сохранён в Artifact Store; у каждой задачи заполнены acceptance criteria, `requirement_refs` и `dor_check = pass`; `duplicate_check = pass`; `status = completed`; `gate_recommendation = pass`.

## Правила
- не формировать payload, если Gate 1 не пройден;
- каждая задача должна иметь acceptance criteria;
- запрещено «дробить» требование на задачи без явной необходимости;
- при неоднозначности — возврат в `requirement-review`, а не «доработка на лету»;
- **не создавать сущности в Jira** — только артефакт-payload.

## Quality Gate
См. **Gate 2a — Jira Tasks Quality Gate** (трассируемость, acceptance criteria, Definition of Ready, отсутствие дублей и висячих задач).

## Failure Behaviour
При отсутствии параметров Jira — вернуть `status = blocked` и `blocking_reason`; при конфликте с существующими задачами — зафиксировать в `duplicate_check` и вернуть `gate_recommendation = fail`; при непрохождении Gate 2a — вернуть артефакт на доработку в `task-design` или эскалировать. Публикация в Jira выполняется оркестратором только на этапе Publish после прохождения всех гейтов.