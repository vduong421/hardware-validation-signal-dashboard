# Hardware Validation Signal Dashboard

Python project for turning hardware and software validation logs into operations-ready engineering signals: pass rate, flaky tests, requirement coverage, failure clusters, and release-readiness notes.

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

With local AI hardware-validation brief:

```bash
python analyzer.py sample_validation_results.csv --use-ai
```

The script prints a console summary and writes:

- `validation-summary.json`
- `validation-summary.md`
- `validation-ai-brief.json`
- `validation-ai-brief.md`

## Product Dashboard

The web dashboard includes:

- Local AI Analyst panel near the top
- Context-aware AI Chat with 4 sample technical question buttons
- visible Local AI running / finished status
- validation metrics cards
- requirement coverage progress bar
- failure breakdown charts by subsystem, error type, owner, and pass/fail
- run trend table grouped by validation run
- risky validation records table
- release-readiness decision output

AI responses are grounded in deterministic validation output and include:

- answer
- evidence
- next_action
- recommendation
- decision

## Resume Angle

Built a Python validation dashboard that parses hardware/software regression results, measures pass rate and coverage, detects flaky tests, clusters failures by subsystem, generates JSON/Markdown summaries, and exposes a local-AI triage dashboard for engineering release decisions.

## Project Workbench

Launch the production-style desktop workbench with:

```powershell
launch-workbench.bat
```

What it adds:

- Local-first AI copilot using `google/gemma-4-e4b` by default
- Operator-focused workbench for reviewing real project inputs and outputs
- System design, production-impact, and operational brief generation on demand
- Grounded responses based on this project's README, sample files, and deterministic outputs
