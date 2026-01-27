from fastapi import FastAPI
from fastapi.responses import JSONResponse
import threading
import numpy as np
from tensorflow.keras.models import load_model
import joblib

from collect_metrics import metrics_buffer, collect_metrics, BUFFER_SIZE

app = FastAPI(title="ML Service LSTM")

# -------------------------------
# Загружаем модель и scaler'ы
# -------------------------------
try:
    model = load_model("lstm_model.keras")
except Exception as e:
    print(f"Ошибка загрузки модели: {e}")
    model = None

try:
    scaler_X = joblib.load("scaler_X.pkl")
    scaler_y = joblib.load("scaler_y.pkl")
except Exception as e:
    print(f"Ошибка загрузки scaler'ов: {e}")
    scaler_X = None
    scaler_y = None

# -------------------------------
# Endpoint для предсказания
# -------------------------------
@app.get("/predict")
def predict():
    if model is None:
        return JSONResponse(status_code=500, content={"error": "Модель не загружена"})

    if scaler_X is None or scaler_y is None:
        return JSONResponse(status_code=500, content={"error": "Scaler'ы не загружены"})

    if len(metrics_buffer) < BUFFER_SIZE:
        return JSONResponse(
            status_code=400,
            content={"error": "Недостаточно данных для предсказания"}
        )

    try:
        # (BUFFER_SIZE, 4)
        X_raw = np.array(metrics_buffer)

        # масштабируем вход как при обучении
        X_scaled = scaler_X.transform(X_raw)
        X_scaled = X_scaled.reshape(1, BUFFER_SIZE, 4)

        # предсказание (нормализованное)
        y_scaled = model.predict(X_scaled)

        # обратно в реальные requests/sec
        y = scaler_y.inverse_transform(y_scaled)

        return {
            "prediction_requests_per_sec": float(y[0, 0])
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# -------------------------------
# Сбор метрик
# -------------------------------
threading.Thread(
    target=collect_metrics,
    daemon=True
).start()

@app.get("/metrics_buffer")
def get_metrics_buffer():
    return {"metrics_buffer": metrics_buffer.copy()}