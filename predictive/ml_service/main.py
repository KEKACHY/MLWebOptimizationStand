import requests
import xgboost as xgb
import pandas as pd
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np

model = xgb.Booster()
model.load_model('xgboost_model.json')

app = FastAPI()

predicted_load = None

scaler = joblib.load('scaler.pkl')

# Функция для получения метрик с backend
async def get_metrics():
    global predicted_load
    while True:
        try:
            response = requests.get('http://nginx/current_metrics') 
            metrics = response.json()

            metrics_data = {
                'requests_per_sec': metrics['requests_per_sec'],
                'cpu_percent': metrics['cpu_percent'],
            }

            df = pd.DataFrame([metrics_data])

            df_normalized = scaler.transform(df)

            dmatrix = xgb.DMatrix(df_normalized)

            prediction = model.predict(dmatrix)

            predicted_value = scaler.inverse_transform(prediction)
            predicted_load = float(predicted_value.ravel()[0])

        except Exception as e:
            print(f"Ошибка получения метрик или предсказания: {e}")

        await asyncio.sleep(5)

# Эндпоинт для получения текущих предсказаний
@app.get("/current_prediction")
def current_prediction():
    if predicted_load is not None:
        return {"predicted_load": predicted_load}
    else:
        return {"error": "Предсказание еще не доступно"}

# Запуск задачи получения метрик и предсказаний каждые 5 секунд
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(get_metrics())
