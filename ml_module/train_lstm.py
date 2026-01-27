import joblib
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam

from prepare_lstm_data import load_and_prepare

# -------------------------------
# Параметры
# -------------------------------
DATA_PATH = "data/data.csv"
WINDOW = 24
HORIZON = 5

# -------------------------------
# Загружаем данные и подготавливаем
# -------------------------------
X, y, scaler_X, scaler_y = load_and_prepare(DATA_PATH, window=WINDOW, horizon=HORIZON)

# -------------------------------
# Train/test split
# -------------------------------
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# -------------------------------
# Создание модели LSTM
# -------------------------------
model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
    LSTM(32),
    Dense(1)
])

model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss="mse"
)

# -------------------------------
# EarlyStopping
# -------------------------------
es = EarlyStopping(
    patience=5,
    restore_best_weights=True
)

# -------------------------------
# Обучение модели
# -------------------------------
model.fit(
    X_train,
    y_train,
    epochs=50,
    batch_size=32,
    validation_data=(X_test, y_test),
    callbacks=[es],
    verbose=1,
    shuffle=False   # важно для временных рядов
)

# -------------------------------
# Сохраняем модель и скейлеры
# -------------------------------
model.save("lstm_model.keras")
joblib.dump(scaler_X, "scaler_X.pkl")
joblib.dump(scaler_y, "scaler_y.pkl")

print("Model and scalers saved")