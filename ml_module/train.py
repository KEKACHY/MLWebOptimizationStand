import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Загрузим обработанные данные
processed_data = pd.read_csv('processed_data.csv')

# Выбираем признаки и целевую переменную
X = processed_data[['requests_per_sec', 'cpu_percent']]
y = processed_data['requests_per_sec']

# Разделим данные на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Преобразуем данные в формат DMatrix для XGBoost
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

# Задаем параметры для XGBoost
params = {
    'objective': 'reg:squarederror',  # Задача регрессии
    'max_depth': 6,  # Глубина деревьев
    'eta': 0.1,  # Скорость обучения
    'subsample': 0.8,  # Используем случайные подмножества данных
    'colsample_bytree': 0.8  # Случайный выбор признаков
}

# Обучим модель XGBoost
num_round = 100  # Количество итераций (деревьев)
model_xgb = xgb.train(params, dtrain, num_round)

# Сделаем предсказания
y_pred_xgb = model_xgb.predict(dtest)

# Оценим модель с помощью средней абсолютной ошибки (MAE)
mae_xgb = mean_absolute_error(y_test, y_pred_xgb)
print(f'Mean Absolute Error (MAE) for XGBoost: {mae_xgb}')

# Визуализируем важность признаков
import matplotlib.pyplot as plt
xgb.plot_importance(model_xgb)
plt.show()

model_xgb.save_model('xgboost_model.json')