# QEMU Manager — Requirements-to-Design Pipeline

Мультиагентная система на OpenCode, которая проводит требования из Confluence
через анализ, проектирование задач Jira и тестовой модели Testomat.io, с контролем
качества на каждом шаге и идемпотентной публикацией во внешние системы.

## Архитектура

```
Пользователь
   │
   ▼
QA Orchestrator (primary)
   ├──▶ Requirement Reviewer (subagent) ──▶ .artifacts/.current/01-requirement-review.json ──▶ Gate 1
   ├──▶ Task Designer       (subagent) ──▶ .artifacts/.current/02-task-design.json       ──▶ Gate 2a ──┐
   └──▶ Test Designer       (subagent) ──▶ .artifacts/.current/03-test-design.json       ──▶ Gate 2b ──┴──▶ Gate 2c
                                                                                                                │
                                                                                                                ▼
                                                                                                            Publish
                                                                                                     (Jira + Testomat.io)
                                                                                                                │
                                                                                                                ▼
                                                                                                    Final / Blocking
                                                                                                         Report
                                                                                                                │
                                                                                                                ▼
                                                                                       mv .artifacts/.current → .artifacts/{run_id}
```

**Агенты** (`.opencode/agents/`):
- `qa-orchestrator.md` — primary. Делегирует этапы, применяет Quality Gates,
  публикует артефакты, формирует отчёты, управляет `.artifacts/.current/`.
- `requirement-reviewer.md` — анализ требований Confluence.
- `task-designer.md` — построение payload задач Jira.
- `test-designer.md` — построение тестовой модели Testomat.io.

**Скиллы** (`.opencode/skills/`) — методология, а не дубли агентских инструкций:
- `requirement-review/` — техники поиска противоречий, неоднозначностей, пробелов.
- `task-design/` — стратегии декомпозиции, формат AC, Definition of Ready.
- `test-design/` — equivalence partitioning, boundary values, state transition,
  decision tables, priority rubric, формат шагов `step + expected`, правила N/A.

**Артефакты** — жизненный цикл через `.artifacts/.current/`:

Во время прогона все артефакты пишутся в `.artifacts/.current/`:
- `meta.json` — метаданные прогона (включая `testomat_project_id`,
  `testomat_project_id_source`, `preflight_decision`, `human_override`).
- `01-requirement-review.json` — находки requirement-reviewer.
- `02-task-design.json` — payload задач Jira.
- `03-test-design.json` — тестовая модель Testomat.io.
- `04-publish-state.json` — чекпойнт публикации (идемпотентность).
- `05-publish-report.json` — итоговая сводка публикации.
- `REPORT.md` — Final Report или Blocking Report.

По завершении прогона (успех или блокировка) `.artifacts/.current/`
переименовывается в `.artifacts/{run_id}/`. `run_id` — временная метка старта
прогона (`{ISO-timestamp}_{req_version}`); по ней прогон находится в
`.artifacts/index.json`.

Субагенты (`requirement-reviewer`, `task-designer`, `test-designer`) имеют
доступ **только** к `.artifacts/.current/`. Ни один субагент не может прочитать
артефакты прошлых прогонов.

## Требования

- Node.js 20+
- OpenCode CLI
- Аккаунты: Atlassian (Confluence + Jira), Testomat.io
- Git (для версионирования `.artifacts/`)

## Установка

1. Клонировать репозиторий и установить зависимости:
   ```bash
   git clone <repo> && cd qemu-manager-pipeline
   npm install
   ```

2. Скопировать `.env.example` в `.env` и заполнить:
   ```bash
   # Atlassian (Confluence + Jira)
   ATLASSIAN_SITE=https://your-domain.atlassian.net
   ATLASSIAN_EMAIL=you@example.com
   ATLASSIAN_API_TOKEN=...

   # Testomat.io
   TESTOMATIO_PROJECT_TOKEN=tstmt_xxxxxxxxxxxxxxxxxxxxx
   TESTOMATIO_PROJECT_ID=12345

   # Quality gates
   QA_GATE1_MAJOR_LIMIT=5

   # Preflight resume behavior (ask | resume | archive)
   QA_RESUME_MODE=ask
   ```

   `.env` добавлен в `.gitignore`. Токены не коммитятся.

3. Убедиться, что MCP-серверы объявлены в `opencode.json`:
   - `jira-confluence` (Confluence + Jira);
   - `testomat` (Testomat.io).

   Отдельный MCP для артефактов **не нужен**: артефакты пишутся в файловую
   систему внутри проекта.

### Где взять параметры Testomat.io

- **`TESTOMATIO_PROJECT_TOKEN`** — Settings → API & Tokens → Project token
  (начинается с `tstmt_`).
- **`TESTOMATIO_PROJECT_ID`** — числовой ID проекта из URL при просмотре проекта:
  `https://app.testomat.io/projects/<project_id>/...`.

## Запуск агента

Команда: `/run-qa-flow`

| Аргумент | Обязателен | Пример | Что это |
|---|---|---|---|
| `page` | да | `https://.../pages/123456` или `123456` | Confluence page ID или URL |
| `jira_project` | да | `QA` | Ключ проекта Jira |
| `testomat_project` | **нет** | `12345` | ID проекта Testomat.io. Если не указан — берётся из `TESTOMATIO_PROJECT_ID` |
| `testomat_suite` | нет | `67890` | ID сьюта Testomat.io (по умолчанию корень) |

### Минимальный запуск

`testomat_project` не указывается — резолвится из `.env`:

```bash
/run-qa-flow https://your-domain.atlassian.net/wiki/spaces/QA/pages/123456/QEMU+Manager QA
```

### Запуск с явным project_id (совпадает с env)

Допустимо, если значение совпадает с `TESTOMATIO_PROJECT_ID`. Используется для
трассировки в `meta.json`:

```bash
/run-qa-flow https://your-domain.atlassian.net/wiki/spaces/QA/pages/123456/QEMU+Manager QA 12345
```

### Запуск с suite_id

Четвёртый аргумент — `suite_id`:

```bash
/run-qa-flow https://your-domain.atlassian.net/wiki/spaces/QA/pages/123456/QEMU+Manager QA 12345 67890
```

Если `testomat_project` не хотите указывать, но `suite_id` нужен — используйте
пустую строку или `-` для пропуска необязательного аргумента (зависит от парсера
команды; при сомнениях — задайте `testomat_project` явно, равным env):

```bash
/run-qa-flow <page> QA - 67890
```

### ⚠️ Конфликт аргумента и env

Если `testomat_project` передан и **не совпадает** с `TESTOMATIO_PROJECT_ID` —
прогон блокируется с `reason = "project_id_source_conflict"`. Причина: MCP-сервер
заскоупирован на env-проект, и публикация всё равно ушла бы в env, а не в
аргумент. Молча писать не туда — хуже, чем явно остановиться.

Исправление: приведите аргумент и env к одному значению либо уберите аргумент.

### Альтернативный запуск через CLI

Если TUI не подхватывает `/run-qa-flow`, используйте прямой вызов агента:

```bash
opencode run --agent qa-orchestrator \
  "Запусти QA-поток: page=123456, jira=QA. Testomat project — из env"
```

### Только проверка без публикации

```bash
opencode run --agent qa-orchestrator \
  "Запусти QA-поток: page=123456, jira=QA. Publish не выполнять, остановиться после Gate 2c и сформировать Final Report"
```

`04-publish-state.json` и `05-publish-report.json` не создаются, `REPORT.md`
содержит сводку гейтов и рекомендации. Финализация `.current` → `.artifacts/{run_id}`
всё равно выполняется по завершении.

## Resume и архивация

Состояние прогона живёт в `.artifacts/.current/`. Поведение при повторном
запуске с непустым `.current` управляется переменной `QA_RESUME_MODE`:

| Значение | Поведение |
|---|---|
| `ask` (default) | Интерактивный prompt: `R` — resume, `A` — archive. В неинтерактивном режиме (CLI без TTY) ведёт себя как `archive`. |
| `resume` | Продолжить предыдущий прогон (reuse `run_id`, `meta.json`, состояние `04-publish-state.json`; завершённые стадии пропускаются). |
| `archive` | Переименовать `.artifacts/.current/` → `.artifacts/{old_run_id}/`, обновить `index.json` (`status=blocked`, `path=.artifacts/{old_run_id}/`), создать новый `.artifacts/.current/`. |

**Resume** безопасен: preflight-поиск в Jira и Testomat.io исключает дубли;
`04-publish-state.json` содержит `created`/`existing`/`failed` по каждому
элементу, и `failed` продолжается с того же места.

**Archive** используется, когда предыдущий прогон логически завершён
(пользователь не хочет resume), но `.current` остался из-за краша.

Повторный запуск с теми же аргументами безопасен: дубли в Jira и Testomat.io
исключены preflight-поиском.

## Как резолвится testomat_project_id

Приоритет источников:

| Приоритет | Источник | Условие |
|---|---|---|
| 1 | Аргумент `/run-qa-flow` | Передан и совпадает с env (или env не задан) |
| 2 | `TESTOMATIO_PROJECT_ID` из `.env` | Аргумент не передан |
| 3 | `testomat_project_info` (MCP) | Ни аргумент, ни env не заданы; берётся первый проект |

Результат фиксируется в `meta.json`:

```json
"testomat_project_id": 12345,
"testomat_project_id_source": "env"
```

Возможные значения `testomat_project_id_source`: `argument` / `env` /
`mcp_project_info`. Если ни один источник не дал значения — `Blocking Report`
с `reason = "testomat_project_id_unresolved"`.

## Переменные окружения

| Переменная | Назначение |
|---|---|
| `ATLASSIAN_SITE` | Базовый URL Atlassian |
| `ATLASSIAN_EMAIL` | Email для API |
| `ATLASSIAN_API_TOKEN` | API-токен Atlassian |
| `TESTOMATIO_PROJECT_TOKEN` | Project token Testomat.io (`tstmt_...`) |
| `TESTOMATIO_PROJECT_ID` | Числовой ID проекта Testomat.io (fallback для аргумента) |
| `TESTOMATIO_BASE_URL` | Базовый URL Testomat.io (по умолчанию `https://app.testomat.io`) |
| `QA_GATE1_MAJOR_LIMIT` | Порог major-находок для Gate 1 (по умолчанию `5`) |
| `QA_RESUME_MODE` | `ask` / `resume` / `archive` — поведение при обнаружении непустого `.artifacts/.current/` (по умолчанию `ask`; в неинтерактивном режиме → `archive`) |

## Конфигурация MCP

`opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "jira-confluence": {
      "type": "local",
      "command": ["npx", "-y", "mcp-jira-confluence"],
      "env": {
        "ATLASSIAN_SITE": "{env:ATLASSIAN_SITE}",
        "ATLASSIAN_EMAIL": "{env:ATLASSIAN_EMAIL}",
        "ATLASSIAN_API_TOKEN": "{env:ATLASSIAN_API_TOKEN}"
      },
      "enabled": true
    },
    "testomat": {
      "type": "local",
      "command": [
        "npx", "-y", "@testomatio/mcp@latest",
        "--token", "{env:TESTOMATIO_PROJECT_TOKEN}",
        "--project", "{env:TESTOMATIO_PROJECT_ID}"
      ],
      "environment": {
        "TESTOMATIO_BASE_URL": "https://app.testomat.io"
      },
      "enabled": true
    }
  }
}
```

## Как работает идемпотентность

1. Перед созданием задачи — поиск в Jira по label `qemu-manager-req-{version}` + summary.
2. Перед созданием кейса — `testomat_tests` с `command: "list"` и TQL-фильтром
   `test == '{title}' and suite == '{suite_id}'`.
3. Найденное — не дублируется, помечается `existing`.
4. После каждого успешного создания — немедленная запись в `.artifacts/.current/04-publish-state.json`.
5. При падении — `status = failed`, следующий запуск резюмит с этого элемента.

Повторный запуск `/run-qa-flow` с теми же аргументами безопасен.

## Quality Gates

| Gate | Что проверяет | Кто решает |
|---|---|---|
| 1 | Findings requirement-review | Оркестратор |
| 2a | Трассировка и AC задач Jira | Оркестратор |
| 2b | Покрытие positive/negative/boundary, N/A с reason, priority, шаги | Оркестратор |
| 2c | Согласованность артефактов, cross-check, совпадение project_id | Оркестратор |

Критерии Gate 1: `blocker = 0`, `critical = 0`, `major ≤ QA_GATE1_MAJOR_LIMIT`,
нет ambiguous с impact = `blocks design`. Скиллы не принимают решение по Gate —
только возвращают findings. Human override фиксируется в `meta.json`.

## Просмотр артефактов

**Текущий прогон (пока идёт):**
```bash
cat .artifacts/.current/REPORT.md
cat .artifacts/.current/meta.json
cat .artifacts/.current/04-publish-state.json
```

**Завершённые прогоны:**
```bash
ls .artifacts/
cat .artifacts/<run_id>/REPORT.md
cat .artifacts/<run_id>/meta.json
```

**Реестр прогонов:**
```bash
cat .artifacts/index.json
```

## Troubleshooting

- **`/run-qa-flow` не появляется в автодополнении** — проверить
  `.opencode/commands/run-qa-flow.md` или секцию `"commands"` в `opencode.json`.
- **`project_id_source_conflict`** — аргумент и `TESTOMATIO_PROJECT_ID` расходятся.
  Приведите к одному значению либо уберите аргумент.
- **`testomat_project_id_unresolved`** — ни аргумент, ни env, ни MCP не дали
  project_id. Задайте `TESTOMATIO_PROJECT_ID` в `.env` либо передайте аргументом.
- **`.current` остался после краша** — при следующем запуске оркестратор
  спросит, resume или archive (см. `QA_RESUME_MODE`). Вручную ничего
  переименовывать не нужно.
- **Хочу посмотреть прошлый прогон** — он лежит в `.artifacts/{run_id}/`,
  найти `run_id` можно в `.artifacts/index.json`.
- **Хочу принудительно начать с чистого листа** — `QA_RESUME_MODE=archive`,
  затем запустить `/run-qa-flow`.
- **`corrupt_current_state`** — `.current/meta.json` повреждён и в `index.json`
  нет соответствующей записи. Удалите `.artifacts/.current/` вручную и
  перезапустите (потеря только незавершённого прогона).
- **`run_id_collision`** — при финализации/архивации уже существует
  `.artifacts/{run_id}/`. Обычно означает, что предыдущий прогон с тем же
  `run_id` не был очищен; переименуйте/удалите конфликтующий каталог вручную
  и перезапустите.
- **`bash_scope_violation`** — оркестратор попытался выполнить bash-команду
  вне Allowed Bash Commands. Это баг конфигурации; смотрите `REPORT.md`.
- **MCP не подключается** — проверить `.env` и `opencode.json`. Для Testomat.io
  убедиться, что `TESTOMATIO_PROJECT_TOKEN` начинается с `tstmt_`, а
  `TESTOMATIO_PROJECT_ID` — число.
- **Testomat.io отвечает 401** — проверить, что project token принадлежит
  проекту из `TESTOMATIO_PROJECT_ID`.
- **Testomat.io отвечает 404 на suite_id** — сьют не существует в проекте;
  запустить без `suite_id` (кейсы уйдут в корень).
- **Повторный запуск создаёт дубли** — проверить `.artifacts/.current/04-publish-state.json`
  (или `.artifacts/{run_id}/04-publish-state.json` для завершённого прогона),
  не удалять его до завершения прогона.
- **Артефакт не найден** — проверить `run_id` в `.artifacts/index.json`.
- **Gate 1 упал при `major ≤ 5`** — проверить `QA_GATE1_MAJOR_LIMIT` в `.env`.