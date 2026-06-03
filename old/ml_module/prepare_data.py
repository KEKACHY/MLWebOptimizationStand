import pandas as pd
import numpy as np
import joblib

file_path = 'data/data.csv' 
data = pd.read_csv(file_path)

# 1. Преобразование timestamp в читаемый формат
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s')

# 2. Просмотр статистики для поиска выбросов
print(data.describe())

# 3. Если есть выбросы, можно их удалить
data = data[data['cpu_percent'] < 40]

# 4. Нормализация данных
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()

# Нормализация только количества запросов и нагрузки cpu
data[['requests_per_sec', 'cpu_percent']] = scaler.fit_transform(
    data[['requests_per_sec', 'cpu_percent']]
)

# 5. Разделение данных на признаки и целевую переменную
X = data[['requests_per_sec', 'cpu_percent']]
y = data[['requests_per_sec', 'cpu_percent']]

# 6. Разделение на обучающую и тестовую выборки
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

data.to_csv('processed_data.csv', index=False)
joblib.dump(scaler, 'scaler.pkl')