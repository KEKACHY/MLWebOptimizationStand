import pandas as pd
import numpy as np
import joblib

# Загрузим данные
file_path = 'data/data.csv'  # укажите путь к вашему файлу
data = pd.read_csv(file_path)

# 1. Преобразуем timestamp в читаемый формат (если это необходимо)
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s')

# 2. Просмотрим статистику для поиска выбросов
print(data.describe())

# 3. Если есть выбросы, можно их удалить. Например, исключим строки, где cpu_percent больше 40 (по вашему описанию)
data = data[data['cpu_percent'] < 40]

# 4. Нормализуем данные (если необходимо, для улучшения производительности модели)
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()

# Нормализуем только количество запросов и нагрузка cpu
data[['requests_per_sec', 'cpu_percent']] = scaler.fit_transform(
    data[['requests_per_sec', 'cpu_percent']]
)

# 5. Разделим данные на признаки и целевую переменную
X = data[['requests_per_sec', 'cpu_percent']]
y = data[['requests_per_sec', 'cpu_percent']]

# 6. Разделим на обучающую и тестовую выборки
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Теперь данные подготовлены для обучения модели
data.to_csv('processed_data.csv', index=False)
joblib.dump(scaler, 'scaler.pkl')