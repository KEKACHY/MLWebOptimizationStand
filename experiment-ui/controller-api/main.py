import csv
import shutil
import signal
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


app = FastAPI(title="Experiment Controller API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
LOCUST_FILE = BASE_DIR / "load" / "locustfile.py"

RESULTS_DIR.mkdir(exist_ok=True)

current_process: Optional[subprocess.Popen] = None
current_scenario: Optional[str] = None
current_run_dir: Optional[Path] = None


SCENARIOS = {
    "baseline": {
        "title": "Baseline",
        "available": True,
        "description": "Базовый сценарий без автомасштабирования. Backend работает в одной фиксированной реплике.",
        "target": "http://host.docker.internal:80",
        "replicas": 1,
    },
    "reactive": {
        "title": "Reactive",
        "available": False,
        "description": "Реактивное автомасштабирование пока не настроено.",
        "target": None,
        "replicas": None,
    },
    "predictive": {
        "title": "Predictive",
        "available": False,
        "description": "Предиктивное автомасштабирование пока не настроено.",
        "target": None,
        "replicas": None,
    },
}


def is_process_running() -> bool:
    return current_process is not None and current_process.poll() is None


def stop_current_process():
    global current_process, current_scenario

    if current_process is None:
        return

    if current_process.poll() is None:
        current_process.send_signal(signal.SIGTERM)

        try:
            current_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            current_process.kill()
            current_process.wait(timeout=5)

    current_process = None
    current_scenario = None


def get_csv_prefix() -> Optional[Path]:
    if current_run_dir is None:
        return None

    return current_run_dir / "result"


def read_stats(prefix: Path):
    stats_file = Path(str(prefix) + "_stats.csv")

    if not stats_file.exists():
        return None

    with stats_file.open("r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        return None

    aggregated = None

    for row in rows:
        if row.get("Name") == "Aggregated":
            aggregated = row
            break

    if aggregated is None:
        aggregated = rows[-1]

    def number(*keys, default=0):
        for key in keys:
            value = aggregated.get(key)
            if value not in [None, ""]:
                try:
                    return float(value)
                except ValueError:
                    return default
        return default

    return {
        "requests": int(number("Request Count")),
        "failures": int(number("Failure Count")),
        "rps": round(number("Requests/s"), 2),
        "failures_per_sec": round(number("Failures/s"), 2),
        "avg_response_time": round(number("Average Response Time"), 2),
        "median_response_time": round(number("Median Response Time"), 2),
        "p95": round(number("95%"), 2),
        "p99": round(number("99%"), 2),
    }


def read_history(prefix: Path):
    history_file = Path(str(prefix) + "_stats_history.csv")

    if not history_file.exists():
        return []

    result = []

    with history_file.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row.get("Name") not in ["Aggregated", ""]:
                continue

            def value(key, default=0):
                raw = row.get(key)
                if raw in [None, ""]:
                    return default
                try:
                    return float(raw)
                except ValueError:
                    return default

            result.append({
                "timestamp": row.get("Timestamp", ""),
                "users": value("User Count"),
                "rps": round(value("Requests/s"), 2),
                "failures_per_sec": round(value("Failures/s"), 2),
                "avg_response_time": round(value("Average Response Time"), 2),
                "p95": round(value("95%"), 2),
                "p99": round(value("99%"), 2),
            })

    return result[-120:]


@app.get("/api/scenarios")
def get_scenarios():
    return {
        "scenarios": SCENARIOS,
        "active_scenario": current_scenario,
        "is_running": is_process_running(),
    }


@app.post("/api/load/start/{scenario_name}")
def start_load(scenario_name: str):
    global current_process, current_scenario, current_run_dir

    if scenario_name not in SCENARIOS:
        raise HTTPException(status_code=404, detail="Unknown scenario")

    scenario = SCENARIOS[scenario_name]

    if not scenario["available"]:
        raise HTTPException(status_code=400, detail="Scenario is not available yet")

    if is_process_running():
        stop_current_process()

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_run_dir = RESULTS_DIR / scenario_name / run_id
    current_run_dir.mkdir(parents=True, exist_ok=True)

    csv_prefix = current_run_dir / "result"
    logfile = current_run_dir / "locust.log"

    command = [
        "locust",
        "-f", str(LOCUST_FILE),
        "--headless",
        "--host", scenario["target"],
        "--csv", str(csv_prefix),
        "--csv-full-history",
        "--logfile", str(logfile),
    ]

    current_process = subprocess.Popen(
        command,
        cwd=str(BASE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    current_scenario = scenario_name

    return {
        "status": "started",
        "scenario": scenario_name,
        "target": scenario["target"],
        "run_dir": str(current_run_dir),
    }


@app.post("/api/load/stop")
def stop_load():
    if not is_process_running():
        return {"status": "already_stopped"}

    stopped_scenario = current_scenario
    stop_current_process()

    return {
        "status": "stopped",
        "scenario": stopped_scenario,
    }


@app.get("/api/load/status")
def get_status():
    return {
        "is_running": is_process_running(),
        "active_scenario": current_scenario,
        "run_dir": str(current_run_dir) if current_run_dir else None,
    }


@app.get("/api/metrics")
def get_metrics():
    prefix = get_csv_prefix()

    if prefix is None:
        return {
            "stats": None,
            "history": [],
        }

    return {
        "stats": read_stats(prefix),
        "history": read_history(prefix),
    }


@app.get("/api/results/download")
def download_results():
    if current_run_dir is None or not current_run_dir.exists():
        raise HTTPException(status_code=404, detail="No results yet")

    archive_path = shutil.make_archive(
        base_name=str(current_run_dir),
        format="zip",
        root_dir=str(current_run_dir),
    )

    return FileResponse(
        archive_path,
        media_type="application/zip",
        filename=f"{current_run_dir.name}_results.zip",
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}