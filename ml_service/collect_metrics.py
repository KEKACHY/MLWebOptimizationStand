import time
import requests
import psutil

METRICS_URL = "http://web-backend:8000/current_metrics"

BUFFER_SIZE = 15
metrics_buffer = []

# -------------------------------
# Добавление новой записи в очередь
# -------------------------------
def add_metrics(metrics):
    global metrics_buffer
    if len(metrics_buffer) >= BUFFER_SIZE:
        metrics_buffer.pop(0)  
    metrics_buffer.append(metrics)

# -------------------------------
# Цикл получения метрик с backend
# -------------------------------
def collect_metrics():
    while True:
        try:
            resp = requests.get(METRICS_URL)
            resp.raise_for_status()
            data = resp.json()
            row = [
                data["requests_per_sec"],
                data["cpu_percent"],
                data["memory_bytes"],
                data["errors_per_sec"]
            ]
            add_metrics(row)
        except Exception as e:
            print(f"Ошибка при сборе метрик: {e}")

        time.sleep(5)