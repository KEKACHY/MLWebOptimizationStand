import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler

WINDOW = 24
HORIZON = 5

FEATURES = [
    "requests_per_sec",
    "cpu_percent",
    "memory_bytes",
    "errors_per_sec"
]

def load_and_prepare(csv_path, window=WINDOW, horizon=HORIZON):
    df = pd.read_csv(csv_path)

    # 1. сортировка по времени (timestamp не фича)
    df = df.sort_values("timestamp").reset_index(drop=True)

    # 2. защита от отрицательных значений
    df["requests_per_sec"] = df["requests_per_sec"].clip(lower=0)
    df["errors_per_sec"] = df["errors_per_sec"].clip(lower=0)

    # 3. входные фичи
    X_raw = df[FEATURES].values

    # 4. таргет — requests_per_sec
    y_raw = df["requests_per_sec"].values.reshape(-1, 1)

    # 5. scaler'ы (раздельные)
    scaler_X = StandardScaler()
    scaler_y = MinMaxScaler()

    X_scaled = scaler_X.fit_transform(X_raw)
    y_scaled = scaler_y.fit_transform(y_raw)

    # 6. sliding window с горизонтом предсказания
    X, y = [], []
    for i in range(len(df) - window - horizon + 1):
        X.append(X_scaled[i : i + window])
        y.append(y_scaled[i + window + horizon - 1])  

    return (
        np.array(X),        
        np.array(y),        
        scaler_X,
        scaler_y
    )