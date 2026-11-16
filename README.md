# QEMU Manager — Requirements-to-Design Pipeline

Мультиагентная система на OpenCode, которая проводит требования из Confluence
через анализ, проектирование задач Jira и тестовой модели Testomat.io, с контролем
качества на каждом шаге и идемпотентной публикацией во внешние системы.

## Архитектура

```text
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

Незавершённый `.current` (остался на момент старта нового запуска) **не
резюмится** — он принудительно архивируется в `.artifacts/failed_<run_id>/`
(или `.artifacts/failed_before_<current_datetime>/`, если в `index.json` нет
записи для `.current`). Новый прогон всегда начинается с чистого `.current/`.

**Агенты** (`.opencode/agents/`):
- `qa-orchestrator.md` — primary. Делегирует этапы, применяет Quality Gates,
  публикует артефакты, формирует отчёты, управляет `.artifacts/.current/`.
- `requirement-reviewer.md` — анализ требований Confluence.
- `task-designer.md` — построение payload задач Jira.
- `test-designer.md` — построение тестовой модели Testomat.io.

**Скиллы** (`.opencode/skills/`) — методология, а не дубли агентских инструкций:
- `requirement-review/` — техники поиска противоречий, неоднозначностей, пробелов,
  prompt injection.
- `task-design/` — стратегии декомпозиции, формат AC, Definition of Ready,
  clarification-задачи по major findings.
- `test-design/` — equivalence partitioning, boundary values, state transition,
  decision tables, priority rubric, формат шагов `step + expected`, правила N/A.

**Артефакты** — жизненный цикл через `.artifacts/.current/`:

Во время прогона все артефакты пишутся в `.artifacts/.current/`:
- `meta.json` — метаданные прогона (включая `testomat_project_id`,
  `testomat_project_id_source`, `preflight_decision`, `archived_previous_run_id`,
  `archived_previous_path`, `human_override`, `gate_results`,
  `blocking_findings_present`).
- `01-requirement-review.json` — находки requirement-reviewer.
- `02-task-design.json` — payload задач Jira.
- `03-test-design.json` — тестовая модель Testomat.io.
- `04-publish-state.json` — чекпойнт публикации (идемпотентность внутри прогона).
- `05-publish-report.json` — итоговая сводка публикации.
- `REPORT.md` — Final Report или Blocking Report.

По завершении прогона (успех или блокировка) `.artifacts/.current/`
переименовывается в `.artifacts/{run_id}/`. `run_id` — временная метка старта
прогона в формате `{YYYY-MM-DD_HH-MM-SS}` (UTC, разделитель `_` между датой и
временем); по ней прогон находится в `.artifacts/index.json`.

Незавершённый прогон (`.current` остался на момент старта нового запуска) **не
резюмится** — он принудительно архивируется в `.artifacts/failed_<run_id>/`
(или `.artifacts/failed_before_<current_datetime>/`, если в `index.json` нет
записи для `.current`). Resume не поддерживается: недоверенный незавершённый
прогон всегда начинается заново.

Субагенты (`requirement-reviewer`, `task-designer`, `test-designer`) имеют
доступ **только** к `.artifacts/.current/`. Ни один субагент не может прочитать
артефакты прошлых прогонов (включая `failed_*`).

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

## Незавершённый прогон и архивация в `failed_*`

**Resume не поддерживается.** Если на момент старта `/run-qa-flow` в
`.artifacts/.current/` остались артефакты — это недоверенный незавершённый
прогон. Оркестратор **до начала новой работы**:

1. Читает `.artifacts/index.json` и ищет последнюю запись с
   `path=".artifacts/.current/"`.
2. Если запись найдена — переименовывает `.artifacts/.current/` в
   `.artifacts/failed_<old_run_id>/`, где `old_run_id` — `run_id` из этой записи.
3. Если записи нет (index.json пуст или не содержит `.current`) —
   переименовывает `.artifacts/.current/` в
   `.artifacts/failed_before_<YYYY-MM-DD_HH-MM-SS>/` (текущее UTC-время).
4. Обновляет `index.json`: старый прогон получает `status="failed"` и
   `path=".artifacts/failed_.../"`; добавляет запись нового прогона с
   `path=".artifacts/.current/"`.
5. Создаёт новый `.artifacts/.current/` и запускает прогон с чистого листа.

**Почему так:** незавершённый прогон мог быть остановлен на любом шаге, его
`04-publish-state.json` мог быть записан не до конца, а промежуточные артефакты
могли быть не согласованы. Идемпотентность publish обеспечивается
**preflight-поиском** в Jira/Testomat, а не resume'ом локального state-файла.

**Примеры имён архива:**
- `run_id` предыдущего прогона был `2026-11-08_10-30-00` →
  `.artifacts/failed_2026-11-08_10-30-00/`.
- `index.json` пуст → `.artifacts/failed_before_2026-11-09_18-00-00/`.

Архив `failed_*` доступен для ручного ревью. Автоматический reconcile со
старыми сущностями в Jira/Testomat не выполняется — если прошлый прогон успел
создать что-то до падения, при следующем запуске preflight-поиск найдёт это
как `existing`, но orphaned-сущности с изменившимся summary/AC требуют ручной
сверки человеком.

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

> `QA_RESUME_MODE` больше не используется. Поведение при непустом
> `.artifacts/.current/` детерминировано: принудительная архивация в `failed_*`
> и старт нового прогона с чистого `.current/`. Resume не поддерживается.

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
4. После каждого успешного создания — немедленная запись в
   `.artifacts/.current/04-publish-state.json`.
5. При падении — `status = failed` в state-файле; state-файл сохраняется в
   архивном `failed_*`. Следующий запуск стартует с чистого `04-publish-state.json`,
   но preflight-поиск (п.1–2) исключает дубли.

Повторный запуск `/run-qa-flow` с теми же аргументами безопасен. Локальный
`04-publish-state.json` между прогонами не переиспользуется.

## Quality Gates

| Gate | Что проверяет | Кто решает |
|---|---|---|
| 1 | Findings requirement-review | Оркестратор |
| 2a | Трассировка и AC задач Jira | Оркестратор |
| 2b | Покрытие positive/negative/boundary, N/A с reason, priority, шаги | Оркестратор |
| 2c | Согласованность артефактов, cross-check, совпадение project_id | Оркестратор |

Критерии Gate 1: `blocker = 0`, `critical = 0`, `major ≤ QA_GATE1_MAJOR_LIMIT`,
нет ambiguous с impact = `blocks design`, нет `prompt_injection` с severity
`blocker|critical`. Скиллы не принимают решение по Gate — только возвращают
findings. Human override фиксируется в `meta.json`.

При `Gate 1 FAIL`, blocker/critical findings или prompt injection
`blocker|critical` — **design и publish запрещены**. Clarification-задачи по
`major` findings создаются только при PASS Gate 1 и без превышения
`QA_GATE1_MAJOR_LIMIT`.

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

**Архив недоверенных прогонов:**
```bash
ls -d .artifacts/failed_* 2>/dev/null
cat .artifacts/failed_<run_id>/meta.json
cat .artifacts/failed_before_<datetime>/meta.json
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
  автоматически архивирует его в `.artifacts/failed_<run_id>/` (или
  `failed_before_<datetime>`, если в `index.json` нет записи) и начнёт новый
  прогон с чистого `.current/`. Вручную ничего переименовывать не нужно.
- **Хочу посмотреть прошлый незавершённый прогон** — он лежит в
  `.artifacts/failed_<run_id>/` или `.artifacts/failed_before_<datetime>/`,
  путь также в `.artifacts/index.json` (`status="failed"`).
- **`run_id_collision`** — при финализации/архивации уже существует
  `.artifacts/{run_id}/` или `.artifacts/failed_.../`. Обычно означает, что
  предыдущий прогон с тем же `run_id` не был очищен; переименуйте/удалите
  конфликтующий каталог вручную и перезапустите.
- **`bash_scope_violation`** — оркестратор попытался выполнить bash-команду
  вне Allowed Bash Commands. Это баг конфигурации; смотрите `REPORT.md`.
- **`blocking_findings_present`** — Gate 1 не пройден (blocker/critical findings
  или превышен `QA_GATE1_MAJOR_LIMIT`). Jira/Testomat create запрещён до
  исправления требований и нового PASS Gate 1.
- **`prompt_injection_detected`** — в требованиях или ответах MCP обнаружены
  инструкции, адресованные агенту. Прогон остановлен; требуется ручная
  нейтрализация источника и перезапуск.
- **`partial_publish`** — Jira или Testomat созданы частично. Смотрите
  `05-publish-report.json`; повторный запуск безопасен (preflight найдёт
  созданное и пометит `existing`).
- **MCP не подключается** — проверить `.env` и `opencode.json`. Для Testomat.io
  убедиться, что `TESTOMATIO_PROJECT_TOKEN` начинается с `tstmt_`, а
  `TESTOMATIO_PROJECT_ID` — число.
- **Testomat.io отвечает 401** — проверить, что project token принадлежит
  проекту из `TESTOMATIO_PROJECT_ID`.
- **Testomat.io отвечает 404 на suite_id** — сьют не существует в проекте;
  запустить без `suite_id` (кейсы уйдут в корень).
- **Повторный запуск создаёт дубли** — проверить preflight-поиск в Jira
  (`labels = "qemu-manager-req-{version}" AND summary ~ "{summary}"`) и в
  Testomat (`test == '{title}' and suite == '{suite_id}'`). State-файл
  `.artifacts/.current/04-publish-state.json` между прогонами не переиспользуется
  (каждый прогон стартует с чистого state), но preflight-поиск должен
  исключать дубли.
- **Артефакт не найден** — проверить `run_id` в `.artifacts/index.json`.
- **Gate 1 упал при `major ≤ 5`** — проверить `QA_GATE1_MAJOR_LIMIT` в `.env`.
- **Нужно вручную начать с чистого листа** — удалите `.artifacts/.current/`
  (он будет пересоздан при следующем запуске). Если хотите сохранить
  содержимое — переименуйте в `.artifacts/failed_<любое_имя>/` вручную.