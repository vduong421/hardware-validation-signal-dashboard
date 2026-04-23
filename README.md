# Hardware Validation Signal Dashboard

Python project for turning hardware and software validation logs into recruiter-readable engineering signals: pass rate, flaky tests, requirement coverage, failure clusters, and release-readiness notes.

## Why This Project Exists

This project supports entry-level validation, test engineering, hardware application engineering, ASIC/FPGA verification, and systems software roles. It shows the same pattern many Bay Area postings ask for: parse engineering data, detect failures, summarize risk, and create a clear report for cross-functional teams.

## What It Demonstrates

- Python log parsing and structured CSV/JSON processing
- Pass/fail rate, flaky-test detection, and requirement coverage tracking
- Failure clustering by subsystem, error type, and test owner
- HTML/Markdown reporting for engineering review
- Hardware/software validation vocabulary: PCIe, CXL, FPGA, ASIC, firmware, system test, regression, coverage, triage

## Run

```bash
python analyzer.py sample_validation_results.csv
```

The script prints a console summary and writes:

- `validation-summary.json`
- `validation-summary.md`

## Resume Angle

Built a Python validation dashboard that parses hardware/software regression results, measures pass rate and coverage, detects flaky tests, clusters failures by subsystem, and generates JSON/Markdown summaries for engineering triage.
