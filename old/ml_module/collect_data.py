import csv
import time
import os
import psutil
import requests

METRICS_URL = "http://web-backend:8000/metrics"
CSV_PATH = "data/data.csv"

METRICS = ["requests_per_sec", "cpu_percent", "memory_bytes", "errors_per_sec"]

# предыдущие значения для расчёта интервала
prev_requests = None
prev_errors = None
prev_time = None

if not os.path.exists(CSV_PATH):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp"] + METRICS)

def get_prometheus_value(metric_name, text):
    for line in text.splitlines():
        if line.startswith(metric_name + " "):
            try:
                return float(line.split()[1])
            except:
                return 0
    return 0

while True:
    timestamp = time.time()
    try:
        resp = requests.get(METRICS_URL)
        resp.raise_for_status()
        text = resp.text
        total_requests = get_prometheus_value("request_count_total", text)
        total_errors = get_prometheus_value("http_errors_total", text)
    except:
        total_requests = 0
        total_errors = 0

    # интервал для расчёта rates
    if prev_requests is None:
        requests_per_sec = 0
        errors_per_sec = 0
    else:
        interval = timestamp - prev_time
        requests_per_sec = (total_requests - prev_requests) / interval
        errors_per_sec = (total_errors - prev_errors) / interval

    prev_requests = total_requests
    prev_errors = total_errors
    prev_time = timestamp

    # реальные CPU и память в момент замера
    cpu_percent = psutil.cpu_percent(interval=None)
    memory_bytes = psutil.virtual_memory().used

    row = [timestamp, requests_per_sec, cpu_percent, memory_bytes, errors_per_sec]

    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    time.sleep(5)