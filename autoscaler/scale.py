import docker
import requests
import time

client = docker.from_env()
PROM_URL = "http://prometheus:9090/api/v1/query?query=request_count_total"

def get_requests():
    try:
        resp = requests.get(PROM_URL).json()
        return float(resp['data']['result'][0]['value'][1])
    except:
        return 0.0

while True:
    r = get_requests()
    try:
        container = client.containers.get("web-backend")
        if r > 100:
            client.containers.run("GlossaryKEKACHY_backend_image", detach=True, name="web-backend-scale1")
        elif r < 50:
            for c in client.containers.list(all=True):
                if "web-backend-scale" in c.name:
                    c.remove(force=True)
    except Exception as e:
        print(e)
    time.sleep(10)