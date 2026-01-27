import requests
import xgboost as xgb
import pandas as pd
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np

# Загрузим модель
model = xgb.Booster()
model.load_model('xgboost_model.json')

# Создаем FastAPI приложение
app = FastAPI()

# Переменные для хранения предсказаний
predicted_load = None

# Нормализатор 
scaler = joblib.load('scaler.pkl')

# Функция для получения метрик с backend
async def get_metrics():
    global predicted_load
    while True:
        try:
            # Запрос к вашему backend для получения актуальных метрик
            response = requests.get('http://nginx/current_metrics')  # Укажите URL вашего backend
            metrics = response.json()

            # Преобразуем метрики в объект для использования в модели
            metrics_data = {
                'requests_per_sec': metrics['requests_per_sec'],
                'cpu_percent': metrics['cpu_percent'],
            }

            # Преобразуем данные в DataFrame
            df = pd.DataFrame([metrics_data])

            # Нормализуем данные
            df_normalized = scaler.transform(df)

            # Преобразуем в DMatrix для XGBoost
            dmatrix = xgb.DMatrix(df_normalized)

            # Получаем предсказания
            prediction = model.predict(dmatrix)

            predicted_load = scaler.inverse_transform(prediction)
            predicted_load = predicted_load.tolist()

        except Exception as e:
            print(f"Ошибка получения метрик или предсказания: {e}")

        # Пауза в 5 секунд перед следующим запросом
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
