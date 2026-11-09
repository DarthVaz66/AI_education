---
description: Запустить QA-поток для Confluence-страницы
agent: qa-orchestrator
---

Запусти полный QA-поток для страницы Confluence **$1**.
Параметры Jira: проект **$2**. Параметры Testomat.io: проект **$3**.
Действуй по workflow: preflight (`.artifacts/.current`) → requirement-review → Gate 1 →
task-design / test-design → Gate 2a / 2b / 2c → Publish → Report → финализация
(`.artifacts/.current` → `.artifacts/{run_id}`).

Если на preflight обнаружен непустой `.artifacts/.current/` — следуй
`QA_RESUME_MODE` (`ask` / `resume` / `archive`).