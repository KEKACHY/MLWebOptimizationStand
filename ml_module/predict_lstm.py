import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

WINDOW = 10
FEATURES = [
    "requests_per_sec",
    "cpu_percent",
    "memory_bytes",
    "errors_per_sec"
]

df = pd.read_csv("data/data.csv")
df = df.sort_values("timestamp")

model = load_model("lstm_model.keras")
scaler = joblib.load("scaler.pkl")

last = df[FEATURES].tail(WINDOW).values
last_scaled = scaler.transform(last)

X = last_scaled.reshape(1, WINDOW, len(FEATURES))

pred_scaled = model.predict(X)[0][0]

dummy = np.zeros((1, len(FEATURES)))
dummy[0, 0] = pred_scaled
pred = scaler.inverse_transform(dummy)[0, 0]

print("Predicted requests_per_sec:", pred)