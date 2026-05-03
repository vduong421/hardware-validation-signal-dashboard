#!/usr/bin/env python3
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

SHARED = Path(__file__).resolve().parents[1] / "_shared_project_workbench"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

from local_llm import chat_json


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def summarize(rows):
    total = len(rows)
    passed = sum(1 for row in rows if row["status"].upper() == "PASS")
    failed = total - passed
    requirements = {row["requirement"] for row in rows}
    covered_requirements = {row["requirement"] for row in rows if row["status"].upper() in {"PASS", "FAIL"}}

    by_test = defaultdict(list)
    for row in rows:
        by_test[row["test_id"]].append(row["status"].upper())

    flaky = [
        test_id for test_id, statuses in by_test.items()
        if "PASS" in statuses and "FAIL" in statuses
    ]

    failures_by_subsystem = Counter(
        row["subsystem"] for row in rows if row["status"].upper() == "FAIL"
    )
    failures_by_error = Counter(
        row["error_type"] or "unknown" for row in rows if row["status"].upper() == "FAIL"
    )
    failures_by_owner = Counter(
        row.get("owner", "unknown") or "unknown" for row in rows if row["status"].upper() == "FAIL"
    )
    results_by_run = defaultdict(lambda: {"PASS": 0, "FAIL": 0})
    for row in rows:
        run_id = row.get("run_id", "unknown") or "unknown"
        status = row["status"].upper()
        if status in {"PASS", "FAIL"}:
            results_by_run[run_id][status] += 1

    failed_rows = [row for row in rows if row["status"].upper() == "FAIL"]
    risky_tests = sorted(
        failed_rows,
        key=lambda row: (
            failures_by_subsystem[row["subsystem"]],
            failures_by_error[row["error_type"] or "unknown"],
        ),
        reverse=True,
    )[:8]

    release_status = "hold" if failed or flaky else "ready"

    return {
        "total_results": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total, 3) if total else 0,
        "requirement_coverage": round(len(covered_requirements) / len(requirements), 3) if requirements else 0,
        "flaky_tests": flaky,
        "failures_by_subsystem": dict(failures_by_subsystem.most_common()),
        "failures_by_error": dict(failures_by_error.most_common()),
        "failures_by_owner": dict(failures_by_owner.most_common()),
        "results_by_run": dict(sorted(results_by_run.items())),
        "top_risky_tests": risky_tests,
        "release_status": release_status,
        "operator_priority": [
            "Debug highest-frequency subsystem failures first",
            "Quarantine flaky tests before release signoff",
            "Review failing requirements with test owners"
        ],
    }


def write_markdown(summary, path):
    lines = [
        "# Validation Summary",
        "",
        f"- Total results: {summary['total_results']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        f"- Pass rate: {summary['pass_rate']:.1%}",
        f"- Requirement coverage: {summary['requirement_coverage']:.1%}",
        f"- Flaky tests: {', '.join(summary['flaky_tests']) if summary['flaky_tests'] else 'None'}",
        "",
        "## Failures By Subsystem",
    ]
    for subsystem, count in summary["failures_by_subsystem"].items():
        lines.append(f"- {subsystem}: {count}")
    lines.append("")
    lines.append("## Failures By Error")
    for error, count in summary["failures_by_error"].items():
        lines.append(f"- {error}: {count}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_ai_dashboard_brief(summary, model):
    prompt = f"""You are a hardware validation AI copilot.

You are given deterministic regression summary data.

Return ONLY valid JSON with:
- answer
- evidence
- next_action
- recommendation
- decision
- result
- subsystem_risks (array of 3 short bullets)
- debug_recommendations (array of 3 short bullets)
- release_readiness

Rules:
- stay grounded in the summary
- mention pass rate, requirement coverage, flaky tests, and failure clusters when relevant
- no hallucinated metrics
- keep it concise and engineering-focused

Summary:
{json.dumps(summary, indent=2)}
"""
    try:
        ai = chat_json(prompt, model=model)
        if not isinstance(ai, dict):
            ai = {}
    except Exception as e:
        ai = {
            "answer": f"Local AI failed: {e}",
            "evidence": "Fallback used deterministic validation summary.",
            "next_action": "Review deterministic failures and flaky tests.",
            "recommendation": "Debug high-frequency subsystem failures first.",
            "decision": "Hold release until failures and flaky tests are reviewed.",
            "result": "Fallback validation analysis generated.",
            "subsystem_risks": [],
            "debug_recommendations": [],
            "release_readiness": "hold"
        }

    return {
        "answer": ai.get("answer", "Validation summary generated."),
        "evidence": ai.get("evidence", f"Pass rate={summary.get('pass_rate')} coverage={summary.get('requirement_coverage')}"),
        "next_action": ai.get("next_action", "Investigate failing and flaky tests."),
        "recommendation": ai.get("recommendation", "Prioritize repeated subsystem failures."),
        "decision": ai.get("decision", "Hold release if failures remain."),
        "result": ai.get("result", "Hardware validation signal analysis complete."),
        "subsystem_risks": ai.get("subsystem_risks", []),
        "debug_recommendations": ai.get("debug_recommendations", []),
        "release_readiness": ai.get("release_readiness", summary.get("release_status", "hold"))
    }


def main():
    args = sys.argv[1:]
    input_path = Path(args[0] if args and not args[0].startswith("--") else "sample_validation_results.csv")
    use_ai = "--use-ai" in args
    model = "google/gemma-4-e4b"
    if "--model" in args:
        idx = args.index("--model")
        if idx + 1 < len(args):
            model = args[idx + 1]
    rows = read_rows(input_path)
    summary = summarize(rows)
    Path("validation-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(summary, Path("validation-summary.md"))
    if use_ai:
        ai = generate_ai_dashboard_brief(summary, model)
        Path("validation-ai-brief.json").write_text(json.dumps(ai, indent=2), encoding="utf-8")
        ai_md = [
            "# AI Hardware Validation Brief",
            "",
            f"## Result\n{ai.get('result', '')}",
            "",
            f"## Answer\n{ai.get('answer', '')}",
            "",
            f"## Evidence\n{ai.get('evidence', '')}",
            "",
            f"## Next Action\n{ai.get('next_action', '')}",
            "",
            f"## Recommendation\n{ai.get('recommendation', '')}",
            "",
            f"## Decision\n{ai.get('decision', '')}",
            "",
            "## Subsystem Risks",
            *[f"- {item}" for item in ai.get("subsystem_risks", [])],
            "",
            "## Debug Recommendations",
            *[f"- {item}" for item in ai.get("debug_recommendations", [])],
            "",
            f"## Release Readiness\n- {ai.get('release_readiness', '')}",
        ]
        Path("validation-ai-brief.md").write_text("\n".join(ai_md) + "\n", encoding="utf-8")
        summary["ai_copilot"] = ai

    Path("validation-ui-data.json").write_text(
        json.dumps({"summary": summary, "rows": rows}, indent=2),
        encoding="utf-8"
    )

    print(f"[VALIDATION DONE] total={summary['total_results']} passed={summary['passed']} failed={summary['failed']} pass_rate={summary['pass_rate']}")


if __name__ == "__main__":
    main()

