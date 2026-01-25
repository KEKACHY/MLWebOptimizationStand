import requests
import csv
import time
import os

# URL Prometheus query API
PROM_URL = "http://prometheus:9090/api/v1/query"

# Путь к CSV
CSV_PATH = "data/data.csv"

# Метрики, которые хотим собирать
METRICS = {
    "requests": "request_count_total",
    "cpu": "process_cpu_seconds_total",
    "memory": "process_resident_memory_bytes",
    "errors": "http_errors_total"
}

# Создаём CSV с заголовками, если нет
if not os.path.exists(CSV_PATH):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp"] + list(METRICS.keys()))

# Функция для запроса метрики
def get_metric(query):
    try:
        resp = requests.get(PROM_URL, params={"query": query})
        resp.raise_for_status()
        data = resp.json()
        if data['data']['result']:
            val = float(data['data']['result'][0]['value'][1])
            return val
        else:
            return 0
    except:
        return 0

# Основной цикл
while True:
    timestamp = time.time()
    row = [timestamp]
    for name, query in METRICS.items():
        row.append(get_metric(query))
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)
    time.sleep(5)
