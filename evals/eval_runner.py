import json
import os
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent)
)

from evaluator import (  # noqa: E402
    OPENCODE_BINARY,
    evaluate_response,
    run_opencode_command,
)


# =============================================================
# PATHS
# =============================================================

project_path = Path(__file__).resolve().parent.parent

dataset_path = (
    Path(__file__).parent
    / "dataset"
    / "golden_dataset.json"
)


# =============================================================
# QUALITY GATE THRESHOLDS
# =============================================================

MIN_PASS_RATE = 100.0

MIN_EXPECTED_PROPERTIES_PASS_RATE = 95.0

MAX_FORBIDDEN_BEHAVIOR_VIOLATION_RATE = 0.0

MAX_ERRORS = 0


# =============================================================
# ТАЙМАУТ ЗАПУСКА QA-АГЕНТА
# =============================================================

# Таймаут (сек) на один прогон qa-orchestrator. 0 / пусто → без таймаута.
QA_AGENT_TIMEOUT_SECONDS = (
    float(os.environ.get("EVAL_QA_AGENT_TIMEOUT_SECONDS", "5400"))
    or None
)


# =============================================================
# ЗАГРУЗКА GOLDEN DATASET
# =============================================================

with open(dataset_path, "r", encoding="utf-8") as file:
    eval_cases = json.load(file)


# =============================================================
# ПАРАМЕТРЫ, ПЕРЕДАВАЕМЫЕ QA-АГЕНТУ
# =============================================================

QA_PROMPT_PARAM_KEYS = (
    "jira_project",
    "testomat_project",
    "testomat_suite",
)


def validate_page_params(page_eval_cases):
    """
    Все кейсы одной страницы должны иметь одинаковые
    параметры запуска: один ответ агента оценивается
    всеми кейсами страницы, поэтому параметры не могут
    различаться между кейсами.
    """
    for key in QA_PROMPT_PARAM_KEYS:
        values = {
            case["input"].get(key)
            for case in page_eval_cases
        }
        if len(values) > 1:
            raise RuntimeError(
                f"Несогласованные параметры {key} "
                f"среди Eval Cases страницы: {values}"
            )


def build_qa_agent_prompt(page_id, page_eval_cases):
    """
    Собирает prompt для qa-orchestrator по шаблону
    /run-qa-flow: page, jira, [testomat_project],
    [testomat_suite].
    """
    first_input = page_eval_cases[0]["input"]

    jira_project = first_input.get("jira_project")

    if not jira_project:
        raise RuntimeError(
            f"Eval Case {page_eval_cases[0]['id']} "
            f"не содержит обязательный параметр "
            f"jira_project."
        )

    parts = [
        f"Запусти QA-поток: "
        f"page={page_id}, "
        f"jira={jira_project}."
    ]

    testomat_project = first_input.get("testomat_project")
    testomat_suite = first_input.get("testomat_suite")

    if testomat_project:
        parts.append(
            f"Testomat project — {testomat_project}."
        )
    else:
        parts.append("Testomat project — из env.")

    if testomat_suite:
        parts.append(
            f"Testomat suite — {testomat_suite}."
        )

    return " ".join(parts)


# =============================================================
# ENRICH EVAL CASE — expected_gate_results → expected_properties
# =============================================================

def enrich_eval_case(eval_case):
    """
    Превращает expected_gate_results в дополнительные
    expected_properties, чтобы судья их проверил.
    Возвращает копию кейса с расширенным массивом
    и картой {gate_name: property_text} для
    последующей агрегации.
    """
    enriched = dict(eval_case)

    enriched["expected_properties"] = list(
        eval_case["expected_properties"]
    )

    enriched["_base_property_count"] = len(
        eval_case["expected_properties"]
    )

    gate_results = eval_case.get("expected_gate_results") or {}

    gate_property_map = {}

    for gate_name, expected_value in gate_results.items():

        property_text = (
            f"Агент должен сообщить статус этапа "
            f"{gate_name} = {expected_value}"
        )

        gate_property_map[gate_name] = property_text

        enriched["expected_properties"].append(
            property_text
        )

    enriched["_gate_property_map"] = gate_property_map

    return enriched


# =============================================================
# ЗАПУСК QA-АГЕНТА (С --agent qa-orchestrator)
# =============================================================

def run_qa_agent(prompt):

    agent_command = [
        OPENCODE_BINARY,
        "run",
        "--agent",
        "qa-orchestrator",
        "--format",
        "json",
        "--dir",
        str(project_path),
        prompt
    ]

    agent_response, return_code, stderr = (
        run_opencode_command(
            agent_command,
            timeout_seconds=QA_AGENT_TIMEOUT_SECONDS,
            label="QA Agent"
        )
    )

    print()
    print("QA AGENT RETURN CODE:", return_code)

    if return_code != 0 and stderr:
        print(stderr)

    return agent_response, return_code, stderr


# =============================================================
# ГРУППИРОВКА EVAL CASES ПО СТРАНИЦЕ
# =============================================================

cases_by_page = {}

for eval_case in eval_cases:

    eval_input = eval_case["input"]

    source = eval_input.get("source")

    if source != "confluence":
        raise RuntimeError(
            f"Eval Case {eval_case['id']} использует "
            f"неподдерживаемый источник: {source}"
        )

    page_id = eval_input["page_id"]

    cases_by_page.setdefault(page_id, []).append(
        eval_case
    )


# =============================================================
# STATE
# =============================================================

eval_results = []

# gate_stats[gate_name] = list of
#   {"eval_case_id": ..., "passed": bool | None}
gate_stats = {}


# =============================================================
# ОСНОВНОЙ ЦИКЛ ПО СТРАНИЦАМ
# =============================================================

for page_id, page_eval_cases in cases_by_page.items():

    print()
    print("=" * 80)
    print("ЗАПУСК QA AGENT")
    print("=" * 80)

    print()
    print("Источник требований: Confluence")
    print(f"pageId: {page_id}")

    print(
        f"Количество Eval Cases для этой страницы: "
        f"{len(page_eval_cases)}"
    )

    print()

    # ---------------------------------------------------------
    # ВАЛИДАЦИЯ ПАРАМЕТРОВ СТРАНИЦЫ
    # ---------------------------------------------------------

    try:
        validate_page_params(page_eval_cases)

    except RuntimeError as err:

        print(f"Ошибка валидации параметров: {err}")

        for eval_case in page_eval_cases:
            eval_results.append({
                "id": eval_case["id"],
                "name": eval_case["name"],
                "status": "ERROR",
                "score": 0.0,
                "expected_properties": [],
                "forbidden_behavior": []
            })

        continue

    # ---------------------------------------------------------
    # PROMPT ДЛЯ QA-АГЕНТА
    # ---------------------------------------------------------

    try:
        prompt = build_qa_agent_prompt(
            page_id,
            page_eval_cases
        )

    except RuntimeError as err:

        print(f"Ошибка построения prompt: {err}")

        for eval_case in page_eval_cases:
            eval_results.append({
                "id": eval_case["id"],
                "name": eval_case["name"],
                "status": "ERROR",
                "score": 0.0,
                "expected_properties": [],
                "forbidden_behavior": []
            })

        continue

    print("PROMPT ДЛЯ АГЕНТА:")
    print(prompt)
    print()

    # ---------------------------------------------------------
    # ЗАПУСК
    # ---------------------------------------------------------

    agent_response, return_code, stderr = run_qa_agent(
        prompt
    )

    if return_code != 0 or not agent_response:

        print("QA Agent не вернул пригодный ответ.")

        for eval_case in page_eval_cases:
            eval_results.append({
                "id": eval_case["id"],
                "name": eval_case["name"],
                "status": "ERROR",
                "score": 0.0,
                "expected_properties": [],
                "forbidden_behavior": []
            })

        continue

    # ---------------------------------------------------------
    # ВЫВОД ОТВЕТА
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("ОТВЕТ QA AGENT")
    print("=" * 80)
    print(agent_response)
    print("=" * 80)

    # ---------------------------------------------------------
    # EVALUATION
    # ---------------------------------------------------------

    for eval_case in page_eval_cases:

        print()
        print("-" * 80)
        print(f"Evaluation: {eval_case['id']}")
        print(f"Название: {eval_case['name']}")
        print("-" * 80)

        print()
        print("Запускаем Evaluator...")

        enriched_case = enrich_eval_case(eval_case)

        try:
            evaluation_result = evaluate_response(
                enriched_case,
                agent_response
            )

            print()
            print("=" * 80)
            print("РЕЗУЛЬТАТ EVALUATION")
            print("=" * 80)

            print(json.dumps(
                evaluation_result,
                ensure_ascii=False,
                indent=2
            ))

            print("=" * 80)

            status = evaluation_result["status"]
            score = evaluation_result["score"]

            eval_results.append({
                "id": eval_case["id"],
                "name": eval_case["name"],
                "status": status,
                "score": score,
                "expected_properties":
                    evaluation_result["expected_properties"],
                "forbidden_behavior":
                    evaluation_result["forbidden_behavior"]
            })

            # ---------------------------------------------
            # АГРЕГАЦИЯ ПО ЭТАПАМ (GATES)
            # ---------------------------------------------

            gate_property_map = enriched_case[
                "_gate_property_map"
            ]

            base_property_count = enriched_case[
                "_base_property_count"
            ]

            response_properties = evaluation_result.get(
                "expected_properties",
                []
            )

            # Гейтовые свойства были дописаны в конец
            # expected_properties, поэтому при совпадении
            # количества сопоставляем их по позиции
            # (устойчиво к перефразировке судьёй).
            # Иначе — fallback по тексту свойства.
            properties_aligned = (
                len(response_properties)
                == len(enriched_case["expected_properties"])
            )

            for offset, (
                gate_name,
                gate_property_text
            ) in enumerate(
                gate_property_map.items()
            ):

                gate_passed = None

                if properties_aligned:

                    index = base_property_count + offset

                    gate_passed = (
                        response_properties[index]
                        .get("passed") is True
                    )

                else:

                    for prop in response_properties:
                        if (
                            prop.get("property")
                            == gate_property_text
                        ):
                            gate_passed = (
                                prop.get("passed") is True
                            )
                            break

                gate_stats.setdefault(
                    gate_name, []
                ).append({
                    "eval_case_id": eval_case["id"],
                    "passed": gate_passed
                })

            print()
            print("EVAL CASE:", eval_case["id"])
            print("STATUS:", status)
            print("SCORE:", score)

        except Exception as error:

            print()
            print("Ошибка Evaluator:", error)

            eval_results.append({
                "id": eval_case["id"],
                "name": eval_case["name"],
                "status": "ERROR",
                "score": 0.0,
                "expected_properties": [],
                "forbidden_behavior": []
            })


# =============================================================
# EVALUATION SUMMARY
# =============================================================

print()
print()
print("=" * 80)
print("EVALUATION SUMMARY")
print("=" * 80)


# =============================================================
# BASIC METRICS
# =============================================================

total = len(eval_results)

passed = sum(
    1 for r in eval_results
    if r["status"] == "PASS"
)

failed = sum(
    1 for r in eval_results
    if r["status"] == "FAIL"
)

errors = sum(
    1 for r in eval_results
    if r["status"] == "ERROR"
)

if total > 0:
    pass_rate = (passed / total) * 100
else:
    pass_rate = 0.0

if total > 0:
    average_score = (
        sum(r["score"] for r in eval_results)
        / total
    )
else:
    average_score = 0.0


# =============================================================
# EXPECTED PROPERTIES PASS RATE
# =============================================================

total_expected_properties = 0
passed_expected_properties = 0

for result in eval_results:
    for prop in result.get(
        "expected_properties", []
    ):
        total_expected_properties += 1
        if prop.get("passed") is True:
            passed_expected_properties += 1

if total_expected_properties > 0:
    expected_properties_pass_rate = (
        passed_expected_properties
        / total_expected_properties
    ) * 100
else:
    expected_properties_pass_rate = 0.0


# =============================================================
# FORBIDDEN BEHAVIOR VIOLATION RATE
# =============================================================

total_forbidden_behaviors = 0
violated_forbidden_behaviors = 0

for result in eval_results:
    for fb in result.get(
        "forbidden_behavior", []
    ):
        total_forbidden_behaviors += 1
        if fb.get("violated") is True:
            violated_forbidden_behaviors += 1

if total_forbidden_behaviors > 0:
    forbidden_behavior_violation_rate = (
        violated_forbidden_behaviors
        / total_forbidden_behaviors
    ) * 100
else:
    forbidden_behavior_violation_rate = 0.0


# =============================================================
# PER-STAGE (GATE) METRICS
# =============================================================

gate_summary = {}

for gate_name, entries in gate_stats.items():

    total_g = len(entries)

    evaluated_g = sum(
        1 for e in entries
        if e["passed"] is not None
    )

    passed_g = sum(
        1 for e in entries
        if e["passed"] is True
    )

    failed_g = sum(
        1 for e in entries
        if e["passed"] is False
    )

    unevaluated_g = total_g - evaluated_g

    rate = (
        passed_g / evaluated_g * 100
        if evaluated_g > 0
        else 0.0
    )

    gate_summary[gate_name] = {
        "total": total_g,
        "evaluated": evaluated_g,
        "passed": passed_g,
        "failed": failed_g,
        "unevaluated": unevaluated_g,
        "pass_rate": round(rate, 1)
    }


# =============================================================
# BASIC METRICS OUTPUT
# =============================================================

print()
print(f"Total:         {total}")
print(f"Passed:        {passed}")
print(f"Failed:        {failed}")
print(f"Errors:        {errors}")
print(f"Pass Rate:     {pass_rate:.1f}%")
print(f"Average Score: {average_score:.2f}")


# =============================================================
# QUALITY METRICS OUTPUT
# =============================================================

print()
print("QUALITY METRICS")
print("-" * 80)

print(
    f"Expected Properties:                 "
    f"{passed_expected_properties}/"
    f"{total_expected_properties}"
)

print(
    f"Expected Properties Pass Rate:       "
    f"{expected_properties_pass_rate:.1f}%"
)

print(
    f"Forbidden Behaviors Violated:        "
    f"{violated_forbidden_behaviors}/"
    f"{total_forbidden_behaviors}"
)

print(
    f"Forbidden Behavior Violation Rate:   "
    f"{forbidden_behavior_violation_rate:.1f}%"
)


# =============================================================
# PER-STAGE METRICS OUTPUT
# =============================================================

print()
print("PER-STAGE (GATE) METRICS")
print("-" * 80)

if gate_summary:

    for gate_name, stats in gate_summary.items():
        print(
            f"{gate_name:<15} "
            f"passed={stats['passed']}/"
            f"{stats['evaluated']} "
            f"rate={stats['pass_rate']:.1f}%"
        )

else:
    print("Нет expected_gate_results в golden dataset.")


# =============================================================
# РЕЗУЛЬТАТЫ ПО КАЖДОМУ EVAL CASE
# =============================================================

print()
print("-" * 80)

for result in eval_results:
    print(
        f"{result['id']:<20}"
        f"{result['status']:<10}"
        f"Score: {result['score']}"
    )

print("-" * 80)


# =============================================================
# QUALITY GATE
# =============================================================

pass_rate_gate = pass_rate >= MIN_PASS_RATE

expected_properties_gate = (
    expected_properties_pass_rate
    >= MIN_EXPECTED_PROPERTIES_PASS_RATE
)

forbidden_behavior_gate = (
    forbidden_behavior_violation_rate
    <= MAX_FORBIDDEN_BEHAVIOR_VIOLATION_RATE
)

errors_gate = errors <= MAX_ERRORS

quality_gate_passed = all([
    pass_rate_gate,
    expected_properties_gate,
    forbidden_behavior_gate,
    errors_gate
])

overall_status = (
    "PASS" if quality_gate_passed else "FAIL"
)


# =============================================================
# QUALITY GATE OUTPUT
# =============================================================

print()
print("=" * 80)
print("QUALITY GATE")
print("=" * 80)
print()

print(
    f"Pass Rate >= {MIN_PASS_RATE:.1f}%: "
    f"{'PASS' if pass_rate_gate else 'FAIL'} "
    f"(actual: {pass_rate:.1f}%)"
)

print(
    f"Expected Properties >= "
    f"{MIN_EXPECTED_PROPERTIES_PASS_RATE:.1f}%: "
    f"{'PASS' if expected_properties_gate else 'FAIL'} "
    f"(actual: {expected_properties_pass_rate:.1f}%)"
)

print(
    f"Forbidden Behavior <= "
    f"{MAX_FORBIDDEN_BEHAVIOR_VIOLATION_RATE:.1f}%: "
    f"{'PASS' if forbidden_behavior_gate else 'FAIL'} "
    f"(actual: {forbidden_behavior_violation_rate:.1f}%)"
)

print(
    f"Errors <= {MAX_ERRORS}: "
    f"{'PASS' if errors_gate else 'FAIL'} "
    f"(actual: {errors})"
)

print()
print("QUALITY GATE STATUS:", overall_status)
print("=" * 80)


# =============================================================
# СОХРАНЕНИЕ РЕЗУЛЬТАТОВ
# =============================================================

results_dir = (
    Path(__file__).parent / "results"
)

results_dir.mkdir(parents=True, exist_ok=True)

results_file = results_dir / "eval_results.json"


report = {

    "summary": {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "pass_rate": round(pass_rate, 1),
        "average_score": round(average_score, 2),
        "expected_properties_pass_rate": round(
            expected_properties_pass_rate, 1
        ),
        "forbidden_behavior_violation_rate": round(
            forbidden_behavior_violation_rate, 1
        ),
        "overall_status": overall_status
    },

    "metrics": {
        "expected_properties": {
            "total": total_expected_properties,
            "passed": passed_expected_properties,
            "pass_rate": round(
                expected_properties_pass_rate, 1
            )
        },
        "forbidden_behavior": {
            "total": total_forbidden_behaviors,
            "violated": violated_forbidden_behaviors,
            "violation_rate": round(
                forbidden_behavior_violation_rate, 1
            )
        },
        # NEW: статистика по этапам
        "by_gate": gate_summary
    },

    "quality_gate": {
        "status": overall_status,
        "criteria": {
            "pass_rate": {
                "threshold": MIN_PASS_RATE,
                "actual": round(pass_rate, 1),
                "passed": pass_rate_gate
            },
            "expected_properties_pass_rate": {
                "threshold":
                    MIN_EXPECTED_PROPERTIES_PASS_RATE,
                "actual": round(
                    expected_properties_pass_rate, 1
                ),
                "passed": expected_properties_gate
            },
            "forbidden_behavior_violation_rate": {
                "threshold":
                    MAX_FORBIDDEN_BEHAVIOR_VIOLATION_RATE,
                "actual": round(
                    forbidden_behavior_violation_rate, 1
                ),
                "passed": forbidden_behavior_gate
            },
            "errors": {
                "threshold": MAX_ERRORS,
                "actual": errors,
                "passed": errors_gate
            }
        }
    },

    "results": eval_results
}


with open(results_file, "w", encoding="utf-8") as file:
    json.dump(
        report,
        file,
        ensure_ascii=False,
        indent=2
    )

print()
print(f"Результаты сохранены: {results_file}")