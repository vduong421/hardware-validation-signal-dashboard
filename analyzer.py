#!/usr/bin/env python3
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


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

    return {
        "total_results": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total, 3) if total else 0,
        "requirement_coverage": round(len(covered_requirements) / len(requirements), 3) if requirements else 0,
        "flaky_tests": flaky,
        "failures_by_subsystem": dict(failures_by_subsystem.most_common()),
        "failures_by_error": dict(failures_by_error.most_common()),
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


def main():
    input_path = Path(sys.argv[1] if len(sys.argv) > 1 else "sample_validation_results.csv")
    rows = read_rows(input_path)
    summary = summarize(rows)
    Path("validation-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(summary, Path("validation-summary.md"))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
