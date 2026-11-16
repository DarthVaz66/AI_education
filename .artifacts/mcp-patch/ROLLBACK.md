# ROLLBACK — патч MCP `jira-confluence` (format=markdown)

## Что сделано
1. Создана **вендоренная копия** MCP (npm-кэш не тронут):
   `.opencode/mcp/mcp-jira-confluence/` (dist + package.json + node_modules + turndown/turndown-plugin-gfm).
2. Пропатчены файлы:
   - `dist/html-to-md.js` — новый конвертер HTML→MD (turndown + gfm), компактный;
   - `dist/confluence.js` — `getConfluencePage(..., format="storage")`; при `markdown` конвертит body;
   - `dist/tools.js` — у `get_confluence_page` добавлен `format`; **дефолт = `markdown`**; в markdown-режиме тело отдаётся plain-text (без JSON-обёртки).
3. `opencode.json`: MCP `jira-confluence` переключён на локальный `node .opencode/mcp/mcp-jira-confluence/dist/index.js`.
4. `.gitignore`: добавлены `.opencode/mcp/` и `.mcp-rollback/`.
5. npm-кэш `~/.npm/_npx/...` **НЕ изменялся**.

## Бэкап: `.mcp-rollback/2026-11-16_01-40-05/`
- `opencode.json.bak` — оригинальный конфиг (до патча);
- `opencode.json.patched` — текущий;
- `tools.js.before-flip` — `dist/tools.js` до смены дефолта (дефолт был `storage`);
- `original-mcp-jira-confluence/` — оригинальные `dist`, `package.json`, `README.md`, `LICENSE` (v3.1.3);
- `ROLLBACK.md` — этот файл.

## Откат — вариант A (полный, быстрый)
```bash
cd "$QA_WORK_DIR"   # QA_WORK_DIR из .opencode/.env (корень репозитория, со слэшем на конце)
cp .mcp-rollback/2026-11-16_01-40-05/opencode.json.bak opencode.json
rm -rf .opencode/mcp/mcp-jira-confluence
# (опц.) вернуть .gitignore: удалить строки ".opencode/mcp/" и ".mcp-rollback/"
# перезапустить opencode
```

## Откат — вариант B (только конфиг, форк остаётся)
Вернуть в `opencode.json`:
```json
"command": ["npx", "-y", "mcp-jira-confluence"],
```

## Откат дефолта формата (оставить форк, но вернуть storage по умолчанию)
```bash
cp .mcp-rollback/2026-11-16_01-40-05/tools.js.before-flip \
   .opencode/mcp/mcp-jira-confluence/dist/tools.js
```

## Поведение патча
- `get_confluence_page` без `format` → **Markdown** (тело 2228226: 51 198 Б вместо storage 80 386 Б);
- `get_confluence_page` с `format:"storage"` → прежний storage-HTML;
- для page 2228226 markdown = 51 198 Б ≤ лимита `tool_output.max_bytes=51200` → усечения нет (запас 2 байта, хрупко).

## Требуется
**Перезапуск opencode** — MCP-серверы поднимаются при старте.
