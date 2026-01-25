import requests
import time
import numpy as np

PROM_URL = "http://prometheus:9090/api/v1/query?query=request_count_total"

history = []

def get_requests():
    try:
        resp = requests.get(PROM_URL).json()
        return float(resp['data']['result'][0]['value'][1])
    except:
        return 0.0

while True:
    val = get_requests()
    history.append(val)
    if len(history) > 5:
        predicted = np.mean(history[-5:])
        print(f"Predicted load: {predicted}")
    time.sleep(5)