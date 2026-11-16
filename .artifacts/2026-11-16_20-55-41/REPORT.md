# QA Run — Blocking Report

run_id: 2026-11-16_20-55-41
stopped_at: Gate 1 — Requirement Review Gate
reason: gate_fail
preflight_decision: fresh_start
archived_previous: —

confluence_page: 4096002 ("EVC-002 ambiguities + boundary")
jira_project: QEMU
testomat_project: test-cc3c0 (source: argument)
requirement_version: 0.5

## Gate retries
- Gate 2a (Jira): attempts=0/5 → not reached
- Gate 2b (Test):  attempts=0/5 → not reached

## Tool health
- Jira: not probed (publish not reached)
- Testomat.io: not probed (publish not reached)

## Decision point (if any)
- kind: —
- chosen: —

## What was produced
- .artifacts/2026-11-16_20-55-41/01-requirement-review.json
- .artifacts/2026-11-16_20-55-41/meta.json
- .artifacts/2026-11-16_20-55-41/REPORT.md

## What was blocked
- Gate 1 FAIL → **design forbidden** (`@task-designer`, `@test-designer` not launched).
- **Jira create forbidden** (project QEMU).
- **Testomat.io create forbidden** (project test-cc3c0).
- Publish guard not satisfied: `gate_results.gate1 != "pass"`, `blocking_findings_present = true`.

## Findings / Errors

Requirement review `01-requirement-review.json` (status=completed, requirement_version=0.5):
- severity_summary: blocker=0, critical=0, major=12, minor=2
- prompt_injection findings: 0
- requirements: 7 (all in_scope=true): REQ-04, REQ-09, REQ-12, REQ-13, REQ-14, REQ-16, REQ-18
- categories: ambiguity=10, contradiction=1, completeness=3
- contract check: PASS (required fields present; `ref` unique; `severity_summary` consistent with
  `findings[]`; no `gate_recommendation`).

Gate 1 criteria applied to `findings[]`:

| Criterion | Result |
|---|---|
| `status == completed` | PASS |
| `severity_summary.blocker == 0` | PASS (0) |
| `severity_summary.critical == 0` | PASS (0) |
| `severity_summary.major <= QA_GATE1_MAJOR_LIMIT` (env=8) | **FAIL (12 > 8)** |
| no `ambiguity` finding whose `impact` contains `blocks design` | PASS |
| no `prompt_injection` with severity `blocker|critical` | PASS (0) |
| `requirements[]` non-empty | PASS (7) |

Triggering criterion: **12 major findings exceed `QA_GATE1_MAJOR_LIMIT=8`.**

Major findings (12):
- F-001 ambiguity (REQ-04) — "появиться в дереве быстро" без числового порога
- F-002 contradiction (REQ-04, REQ-13) — «быстро» ↔ polling-интервал 0..60 c по REQ-13
- F-003 ambiguity (REQ-09) — «разумный таймаут» по умолчанию не задан числом
- F-004 ambiguity (REQ-09) — «Cancel» после отправленного ACPI-запроса
- F-005 ambiguity (REQ-12) — «при необходимости» не задаёт триггер определения IP
- F-007 ambiguity (REQ-13) — критерий поддержки libvirt events не определён
- F-008 ambiguity (REQ-16, REQ-04) — правила длины/символов для paths не заданы
- F-009 ambiguity (REQ-16, REQ-04) — источник клиентской проверки уникальности имени
- F-010 ambiguity (REQ-18) — неопределённый термин `degraded`
- F-011 ambiguity (REQ-14) — таблица маппинга ошибок в friendly-сообщения отсутствует
- F-012 completeness (REQ-09) — нет границ 5–300 и раннего завершения VM
- F-013 completeness (REQ-12) — нет поведения при ошибке получения списка bridge
Minor findings (2): F-006 ambiguity (REQ-12), F-014 completeness (REQ-13).

## Human override
Not self-applied. A human override for Gate 1 is **permitted in principle** here (non-security:
no blocker/critical findings, no `ambiguity` with `blocks design`) but must be explicitly approved
by a human and recorded in `meta.json` before any design/publish. The orchestrator does not approve
its own override and does not soften the criterion.

## Action required from human
1. Choose one:
   - **(a) Fix the source requirements** on Confluence page 4096002 so the reviewer's
     `major <= QA_GATE1_MAJOR_LIMIT` (address the ambiguities: "быстро" REQ-04, default
     "разумный таймаут" REQ-09, "при необходимости" REQ-12, term `degraded` REQ-18; plus
     completeness gaps REQ-09/REQ-12), then re-run the QA flow
     (`page=4096002, jira=QEMU`); **or**
   - **(b) Approve a human override** for Gate 1 (non-security) and re-run / republish.
   Note: `@task-designer`/`@test-designer` are **not** run and **no** Jira/Testomat entities are
   created while Gate 1 is failed (fail-closed).
2. No Jira issues or Testomat.io test cases were created — nothing to clean up.
