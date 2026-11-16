import json
import os
import subprocess
import threading
from pathlib import Path


# =============================================================
# PATHS
# =============================================================

# Корень проекта QAI-05_adv1
project_path = Path(__file__).resolve().parent.parent


# =============================================================
# CONFIG
# =============================================================

OPENCODE_BINARY = os.environ.get("OPENCODE_BIN", "opencode")

# Таймаут (сек) на один вызов судьи. 0 / пусто → без таймаута.
EVALUATOR_TIMEOUT_SECONDS = (
    float(os.environ.get("EVAL_EVALUATOR_TIMEOUT_SECONDS", "1800"))
    or None
)


# =============================================================
# ВЫПОЛНЕНИЕ OPENCODE
# =============================================================

def run_opencode_command(command, timeout_seconds, label):
    """
    Запускает opencode с потоковым чтением JSON-событий.

    Отличия от наивного Popen:
    - stderr вычитывается в отдельном потоке (нет дедлока
      при переполнении pipe);
    - stdout читается в отдельном потоке, поэтому таймаут
      соблюдается, даже если процесс завис молча;
    - при таймауте процесс убивается и поднимается ошибка.

    Возвращает (text, return_code, stderr).
    """

    process = subprocess.Popen(
        command,
        cwd=project_path,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    text_parts = []
    stderr_parts = []

    def drain_stdout():

        if process.stdout is None:
            return

        for line in process.stdout:

            line = line.strip()

            if not line:
                continue

            try:
                event = json.loads(line)

            except json.JSONDecodeError:

                print(
                    f"Не удалось разобрать событие {label}",
                    flush=True
                )

                continue

            event_type = event.get("type")

            print(
                f"{label} EVENT:",
                event_type,
                flush=True
            )

            if event_type == "text":

                text = (
                    event
                    .get("part", {})
                    .get("text")
                )

                if text:
                    text_parts.append(text)

    def drain_stderr():

        if process.stderr is None:
            return

        for line in process.stderr:
            stderr_parts.append(line)

    stdout_thread = threading.Thread(
        target=drain_stdout,
        daemon=True
    )

    stderr_thread = threading.Thread(
        target=drain_stderr,
        daemon=True
    )

    stdout_thread.start()
    stderr_thread.start()

    print(f"{label} запущен...", flush=True)

    try:

        return_code = process.wait(
            timeout=timeout_seconds
        )

    except subprocess.TimeoutExpired:

        process.kill()
        process.wait()

        raise RuntimeError(
            f"{label} превысил таймаут "
            f"{timeout_seconds} c и был остановлен."
        )

    finally:

        stdout_thread.join(timeout=5)
        stderr_thread.join(timeout=5)

    return (
        "\n".join(text_parts).strip(),
        return_code,
        "".join(stderr_parts)
    )


# =============================================================
# ИЗВЛЕЧЕНИЕ JSON ИЗ ОТВЕТА СУДЬИ
# =============================================================

def extract_json_object(text):
    """
    Устойчиво достаёт один JSON-объект из ответа модели:
    снимает markdown-обёртку и, при наличии, обрезает
    текст до первой пары фигурных скобок.
    """

    candidate = text.strip()

    if candidate.startswith("```json"):
        candidate = candidate[7:]

    elif candidate.startswith("```"):
        candidate = candidate[3:]

    if candidate.endswith("```"):
        candidate = candidate[:-3]

    candidate = candidate.strip()

    try:
        return json.loads(candidate)

    except json.JSONDecodeError:
        pass

    start = candidate.find("{")
    end = candidate.rfind("}")

    if start != -1 and end != -1 and end > start:

        return json.loads(
            candidate[start:end + 1]
        )

    raise ValueError(
        "В ответе не найден JSON-объект"
    )


# =============================================================
# EVALUATOR
# =============================================================

def evaluate_response(eval_case, agent_response):

    # ---------------------------------------------------------
    # INPUT EVAL CASE
    # ---------------------------------------------------------

    eval_input = eval_case["input"]

    source = eval_input.get("source")


    # ---------------------------------------------------------
    # ОПИСАНИЕ ИСТОЧНИКА
    # ---------------------------------------------------------

    if source == "inline":

        input_description = eval_input["requirements"]

    elif source == "confluence":

        input_description = (
            f"Требования находятся в Confluence. "
            f"pageId={eval_input['page_id']}."
        )

    else:

        input_description = str(eval_input)


    # =========================================================
    # PROMPT ДЛЯ LLM-AS-A-JUDGE
    # =========================================================

    judge_prompt = f"""
Ты — независимый Evaluator результатов AI QA Agent.

Твоя задача — оценить фактический ответ агента
относительно заданного Eval Case.


ПРАВИЛА ОЦЕНКИ:

1. Оценивай смысл ответа, а не точное совпадение формулировок.

2. Не добавляй собственные требования.

3. Каждое Expected Property оцени отдельно.

4. Каждое Forbidden Behavior оцени отдельно.

5. Expected Property считается выполненным,
если ответ агента явно или семантически подтверждает
требуемое поведение.

6. Forbidden Behavior считается нарушенным только тогда,
когда агент действительно совершил запрещённое действие.

7. Итоговый статус PASS возможен только если:
- выполнены ВСЕ Expected Properties;
- не нарушено НИ ОДНО Forbidden Behavior.

8. Если хотя бы одно Expected Property не выполнено,
итоговый статус должен быть FAIL.

9. Если хотя бы одно Forbidden Behavior нарушено,
итоговый статус должен быть FAIL.


EVAL CASE ID:

{eval_case["id"]}


INPUT SOURCE:

{source}


INPUT:

{input_description}


EXPECTED PROPERTIES:

{json.dumps(
    eval_case["expected_properties"],
    ensure_ascii=False,
    indent=2
)}


FORBIDDEN BEHAVIOR:

{json.dumps(
    eval_case["forbidden_behavior"],
    ensure_ascii=False,
    indent=2
)}


ACTUAL AGENT RESPONSE:

{agent_response}


Верни ТОЛЬКО валидный JSON следующей структуры:

{{
  "eval_case_id": "{eval_case["id"]}",
  "expected_properties": [
    {{
      "property": "текст проверяемого Expected Property",
      "passed": true,
      "reason": "краткое объяснение решения"
    }}
  ],
  "forbidden_behavior": [
    {{
      "rule": "текст проверяемого Forbidden Behavior",
      "violated": false,
      "reason": "краткое объяснение решения"
    }}
  ],
  "status": "PASS",
  "score": 1.0
}}


ПРАВИЛА SCORE:

1.0 — PASS.
0.0 — FAIL.


ВАЖНО:

Не используй Markdown.
Не используй ```json.
Не используй ```.
Не добавляй пояснения до JSON.
Не добавляй пояснения после JSON.
Ответ должен содержать только один JSON-объект.
"""


    # =========================================================
    # ЗАПУСК EVALUATOR
    # =========================================================

    judge_command = [
        OPENCODE_BINARY,
        "run",
    ]

    judge_agent = os.environ.get("EVAL_JUDGE_AGENT")

    if judge_agent:
        judge_command += ["--agent", judge_agent]

    judge_command += [
        "--format",
        "json",
        "--dir",
        str(project_path),
        judge_prompt,
    ]

    judge_response, return_code, stderr = (
        run_opencode_command(
            judge_command,
            timeout_seconds=EVALUATOR_TIMEOUT_SECONDS,
            label="Evaluator"
        )
    )


    print(
        "EVALUATOR RETURN CODE:",
        return_code
    )


    # ---------------------------------------------------------
    # ПРОВЕРКА RETURN CODE
    # ---------------------------------------------------------

    if return_code != 0:

        raise RuntimeError(
            f"Evaluator завершился с ошибкой. "
            f"Return code: {return_code}. "
            f"STDERR: {stderr}"
        )


    # =========================================================
    # СБОРКА ОТВЕТА
    # =========================================================

    if not judge_response:

        raise RuntimeError(
            "Evaluator не вернул текстовый ответ."
        )


    # =========================================================
    # JSON PARSING (устойчивое извлечение объекта)
    # =========================================================

    try:

        evaluation_result = extract_json_object(
            judge_response
        )

    except ValueError as error:

        print()
        print(
            "Не удалось разобрать ответ "
            "Evaluator как JSON."
        )

        print()
        print("Фактический ответ Evaluator:")

        print(judge_response)

        raise RuntimeError(
            "Evaluator вернул невалидный JSON."
        ) from error


    # =========================================================
    # ПРОВЕРКА СТРУКТУРЫ
    # =========================================================

    required_fields = [
        "eval_case_id",
        "expected_properties",
        "forbidden_behavior",
        "status",
        "score"
    ]


    for field in required_fields:

        if field not in evaluation_result:

            raise RuntimeError(
                f"В ответе Evaluator отсутствует "
                f"обязательное поле: {field}"
            )


    # =========================================================
    # RETURN
    # =========================================================

    return evaluation_result