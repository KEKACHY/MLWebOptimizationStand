import math
import os
import time
import logging

import docker
import requests
from prometheus_client import start_http_server, Gauge, Counter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
ML_URL = os.getenv("ML_URL", "http://ml-service:9000/current_prediction")
SERVICE_NAME = os.getenv("BACKEND_SERVICE_NAME", "predictive_web-backend")

MIN_REPLICAS = int(os.getenv("MIN_REPLICAS", "1"))
MAX_REPLICAS = int(os.getenv("MAX_REPLICAS", "5"))

RPS_PER_REPLICA = float(os.getenv("RPS_PER_REPLICA", "18"))

POLL_SEC = int(os.getenv("POLL_SEC", "10"))
UP_COOLDOWN_SEC = int(os.getenv("UP_COOLDOWN_SEC", "20"))
DOWN_COOLDOWN_SEC = int(os.getenv("DOWN_COOLDOWN_SEC", "60"))
DOWN_STABLE_WINDOWS = int(os.getenv("DOWN_STABLE_WINDOWS", "3"))

CURRENT_RPS = Gauge("scaler_current_rps", "Current RPS from Prometheus")
PREDICTED_RPS = Gauge("scaler_predicted_rps", "Predicted RPS from ML service")
DESIRED_REPLICAS = Gauge(
    "scaler_backend_desired_replicas",
    "Desired backend replicas",
    ["service"]
)
RUNNING_REPLICAS = Gauge(
    "scaler_backend_running_replicas",
    "Running backend replicas",
    ["service"]
)
SCALER_ACTIONS = Counter(
    "scaler_actions_total",
    "Autoscaler actions",
    ["action"]
)

docker_client = docker.from_env()


def promql(query: str) -> float:
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
        timeout=5,
    )
    response.raise_for_status()

    data = response.json()
    result = data.get("data", {}).get("result", [])

    if not result:
        return 0.0

    return float(result[0]["value"][1])


def get_current_rps() -> float:
    query = 'sum(rate(request_count_total{job="predictive-backend"}[1m]))'
    return promql(query)


def get_prediction(current_rps: float) -> float:
    try:
        response = requests.get(ML_URL, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "predicted_load" in data:
            return float(data["predicted_load"])

        if "predicted_requests_per_sec" in data:
            return float(data["predicted_requests_per_sec"])

        if "prediction" in data:
            prediction = data["prediction"]
            if isinstance(prediction, list):
                return float(prediction[0])
            return float(prediction)

        logging.warning("Unknown ML response format: %s", data)
        return current_rps

    except Exception as exc:
        logging.warning("ML-service error, fallback to current_rps: %s", exc)
        return current_rps


def get_service_state(service_name: str):
    service = docker_client.services.get(service_name)
    service.reload()

    desired = int(service.attrs["Spec"]["Mode"]["Replicated"]["Replicas"])
    tasks = service.tasks(filters={"desired-state": "running"})
    running = sum(1 for task in tasks if task["Status"]["State"] == "running")

    return service, desired, running


def clamp_replicas(value: int) -> int:
    return max(MIN_REPLICAS, min(MAX_REPLICAS, value))


def replicas_from_rps(rps: float) -> int:
    return clamp_replicas(max(1, math.ceil(rps / RPS_PER_REPLICA)))


def main():
    start_http_server(9101)

    last_scale_ts = 0.0
    low_windows = 0

    logging.info("Predictive autoscaler started")
    logging.info("ML_URL=%s", ML_URL)
    logging.info("PROMETHEUS_URL=%s", PROMETHEUS_URL)
    logging.info("SERVICE_NAME=%s", SERVICE_NAME)

    while True:
        try:
            current_rps = get_current_rps()
            predicted_rps = get_prediction(current_rps)

            service, desired, running = get_service_state(SERVICE_NAME)

            CURRENT_RPS.set(current_rps)
            PREDICTED_RPS.set(predicted_rps)
            DESIRED_REPLICAS.labels(SERVICE_NAME).set(desired)
            RUNNING_REPLICAS.labels(SERVICE_NAME).set(running)

            up_target = replicas_from_rps(predicted_rps)
            down_target = replicas_from_rps(current_rps)

            now = time.time()

            logging.info(
                "current_rps=%.2f predicted_rps=%.2f desired=%s running=%s up_target=%s down_target=%s",
                current_rps,
                predicted_rps,
                desired,
                running,
                up_target,
                down_target,
            )

            # Вверх масштабируемся по прогнозу
            if up_target > desired and (now - last_scale_ts) >= UP_COOLDOWN_SEC:
                logging.info(
                    "SCALE UP: %s -> %s, predicted_rps=%.2f",
                    desired,
                    up_target,
                    predicted_rps,
                )
                service.scale(up_target)
                SCALER_ACTIONS.labels("up").inc()
                last_scale_ts = now
                low_windows = 0

            # Вниз масштабируемся не по прогнозу, а по фактическому снижению нагрузки
            elif down_target < desired:
                low_windows += 1

                if (
                    low_windows >= DOWN_STABLE_WINDOWS
                    and (now - last_scale_ts) >= DOWN_COOLDOWN_SEC
                ):
                    logging.info(
                        "SCALE DOWN: %s -> %s, current_rps=%.2f",
                        desired,
                        down_target,
                        current_rps,
                    )
                    service.scale(down_target)
                    SCALER_ACTIONS.labels("down").inc()
                    last_scale_ts = now
                    low_windows = 0
                else:
                    logging.info(
                        "Scale down waiting: low_windows=%s/%s",
                        low_windows,
                        DOWN_STABLE_WINDOWS,
                    )
                    SCALER_ACTIONS.labels("noop").inc()

            else:
                low_windows = 0
                SCALER_ACTIONS.labels("noop").inc()

        except Exception as exc:
            logging.exception("Autoscaler loop failed: %s", exc)

        time.sleep(POLL_SEC)


if __name__ == "__main__":
    main()