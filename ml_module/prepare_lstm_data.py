import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

WINDOW = 10
FEATURES = [
    "requests_per_sec",
    "cpu_percent",
    "memory_bytes",
    "errors_per_sec"
]

def load_and_prepare(csv_path):
    df = pd.read_csv(csv_path)
    df = df.sort_values("timestamp").reset_index(drop=True)

    data = df[FEATURES].values

    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    X, y = [], []

    for i in range(WINDOW, len(data_scaled)):
        X.append(data_scaled[i-WINDOW:i])
        y.append(data_scaled[i, 0])  

    return np.array(X), np.array(y), scaler