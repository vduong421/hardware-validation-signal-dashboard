# Hardware Validation Signal Dashboard

Hardware Validation Signal Dashboard is a local validation analytics tool that parses hardware/software regression results, measures pass rate and coverage, detects flaky tests, clusters failures, and adds AI-assisted triage guidance.

It is designed for validation workflows where deterministic test evidence must remain auditable, while AI helps engineers explain the failure pattern and decide where to investigate first.

## What It Does

- Parses validation and regression test logs.
- Computes pass rate, failure rate, coverage, and subsystem distribution.
- Detects flaky tests and repeated failure signatures.
- Produces JSON and Markdown summaries.
- Serves a browser dashboard for validation review.
- Adds local AI triage recommendations.

## AI Features

- Local AI analyst explains the most important validation risks.
- AI-generated triage notes identify likely subsystem ownership.
- Recommendations are grounded in pass/fail, coverage, flaky-test, and failure-cluster metrics.
- The browser UI places deterministic evidence next to AI interpretation.

## Architecture

```text
Validation logs
      |
      v
Parser -> metrics -> flaky-test detection -> subsystem clustering
      |
      v
Local AI analyst -> triage summary + next debug action
      |
      v
Dashboard + JSON/Markdown reports
```

## Run

```powershell
run.bat
```

## Local AI Setup

Run LM Studio or another local OpenAI-compatible server with a small model such as `google/gemma-4-e4b`.

If AI is unavailable, all deterministic validation metrics still generate.

## Main Files

- `analyzer.py` - log parsing, metrics, and AI copilot generation.
- `server.py` - local dashboard API.
- `validation-ui-data.json` - dashboard data.
- `agents/Agent.md` - validation AI role instructions.

## Output

The dashboard shows release health, pass/fail metrics, subsystem risk, flaky-test detection, and AI-generated triage guidance.
