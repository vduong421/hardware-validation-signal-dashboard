from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json

DATA_FILE = Path("validation-ui-data.json")
WEB_ROOT = Path("web")


def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {
        "summary": {
            "total_results": 0,
            "passed": 0,
            "failed": 0,
            "pass_rate": 0,
            "requirement_coverage": 0,
            "flaky_tests": [],
            "failures_by_subsystem": {},
            "failures_by_error": {},
            "failures_by_owner": {},
            "top_risky_tests": [],
            "release_status": "unknown",
            "operator_priority": [],
            "ai_copilot": {}
        },
        "rows": []
    }


def answer_question(question, data):
    q = question.lower()
    summary = data.get("summary", {})
    ai = summary.get("ai_copilot", {})

    flaky = summary.get("flaky_tests", [])
    subsys = summary.get("failures_by_subsystem", {})
    errors = summary.get("failures_by_error", {})
    top_sub = sorted(subsys.items(), key=lambda x: x[1], reverse=True)[:3]
    top_err = sorted(errors.items(), key=lambda x: x[1], reverse=True)[:3]

    if "flaky" in q:
        answer = f"{len(flaky)} flaky tests detected: {', '.join(flaky[:5])}."
        evidence = f"Flaky tests appear in multiple runs with PASS/FAIL transitions."
        next_action = f"Quarantine {len(flaky)} flaky tests and rerun validation."
        recommendation = "Focus on flaky tests affecting high-failure subsystems."
        decision = "Do not treat flaky results as stable."

    elif "subsystem" in q or "risk" in q:
        answer = f"Top failing subsystems: {top_sub}."
        evidence = f"Subsystem failure counts: {subsys}."
        next_action = f"Start debug with {top_sub[0][0]} subsystem."
        recommendation = "Assign engineers to highest-frequency subsystem failures."
        decision = "Block release if top subsystem failures persist."

    elif "error" in q or "root" in q:
        answer = f"Top error clusters: {top_err}."
        evidence = f"Error distribution: {errors}."
        next_action = f"Investigate {top_err[0][0]} errors first."
        recommendation = "Group failures by error type for faster triage."
        decision = "Prioritize repeated error patterns."

    elif "release" in q or "ready" in q:
        answer = f"Release is {summary.get('release_status')} with pass rate {round(summary.get('pass_rate',0)*100,1)}%."
        evidence = f"Failed={summary.get('failed')}, flaky={len(flaky)}, coverage={round(summary.get('requirement_coverage',0)*100,1)}%."
        next_action = "Fix failures and eliminate flaky tests."
        recommendation = "Do not proceed until stability improves."
        decision = "HOLD release."

    elif "behavior" in q or "flow" in q:
        answer = f"System processes {summary.get('total_results')} tests with {summary.get('failed')} failures and {len(flaky)} flaky signals."
        evidence = f"Failures concentrated in {top_sub} and errors {top_err}."
        next_action = "Trace failure propagation across subsystems."
        recommendation = "Improve validation stability and isolate flaky tests."
        decision = "System not stable yet."

    else:
        answer = f"Validation summary: {summary.get('passed')} pass / {summary.get('failed')} fail."
        evidence = f"Pass rate {round(summary.get('pass_rate',0)*100,1)}%, coverage {round(summary.get('requirement_coverage',0)*100,1)}%."
        next_action = "Review failures and flaky tests."
        recommendation = "Prioritize highest-risk subsystems."
        decision = "Proceed only if failures are resolved."

    return {
        "answer": answer,
        "evidence": evidence,
        "next_action": next_action,
        "recommendation": recommendation,
        "decision": decision,
        "risks": [k for k,_ in top_sub],
        "operator_actions": [
            "debug top subsystem",
            "analyze error clusters",
            "rerun flaky tests"
        ]
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
            return

        if self.path == "/data":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(load_data()).encode())
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == "/ask":
            length = int(self.headers.get("Content-Length", 0))
            question = self.rfile.read(length).decode()
            response = answer_question(question, load_data())

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            return

        self.send_response(404)
        self.end_headers()


if __name__ == "__main__":
    print("[OK] Hardware Validation Dashboard running at http://localhost:8006/")
    HTTPServer(("localhost", 8006), Handler).serve_forever()