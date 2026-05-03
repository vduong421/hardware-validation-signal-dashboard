import csv
import random
from pathlib import Path

subsystems = ["PCIe", "DDR", "CXL", "FPGA", "Thermal", "Firmware", "System", "NVMe"]
errors = ["timeout", "training_error", "timing_slack", "limit_exceeded", "crc_error", "link_down", "firmware_assert", ""]
owners = ["Validation", "Firmware", "Hardware", "Systems", "SignalIntegrity"]
requirements = [f"REQ-{i:03d}" for i in range(1, 31)]

random.seed(42)

rows = []
for i in range(1, 101):
    subsystem = random.choice(subsystems)
    status = "FAIL" if random.random() < 0.28 else "PASS"
    error = random.choice(errors[:-1]) if status == "FAIL" else ""
    test_base = f"{subsystem.lower()}_{random.randint(1, 25):03d}"

    rows.append({
        "test_id": test_base,
        "requirement": random.choice(requirements),
        "subsystem": subsystem,
        "status": status,
        "error_type": error,
        "owner": random.choice(owners),
        "duration_ms": random.randint(40, 5000),
        "run_id": f"RUN-{random.randint(1, 6):02d}"
    })

for flaky_name in ["pcie_link_001", "thermal_007", "ddr_training_004"]:
    rows.append({
        "test_id": flaky_name,
        "requirement": random.choice(requirements),
        "subsystem": flaky_name.split("_")[0].upper(),
        "status": "PASS",
        "error_type": "",
        "owner": "Validation",
        "duration_ms": random.randint(100, 3000),
        "run_id": "RUN-FLAKY-A"
    })
    rows.append({
        "test_id": flaky_name,
        "requirement": random.choice(requirements),
        "subsystem": flaky_name.split("_")[0].upper(),
        "status": "FAIL",
        "error_type": random.choice(["timeout", "training_error", "limit_exceeded"]),
        "owner": "Validation",
        "duration_ms": random.randint(100, 3000),
        "run_id": "RUN-FLAKY-B"
    })

path = Path("sample_validation_results.csv")
with path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=[
        "test_id",
        "requirement",
        "subsystem",
        "status",
        "error_type",
        "owner",
        "duration_ms",
        "run_id"
    ])
    writer.writeheader()
    writer.writerows(rows)

print(f"[OK] Generated {len(rows)} validation rows")