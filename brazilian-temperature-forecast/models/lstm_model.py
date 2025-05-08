# src/models/lstm_model.py
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def prepare_lstm_data(series, n_steps):
    X, y = [], []
    for i in range(n_steps, len(series)):
        X.append(series[i - n_steps:i])
        y.append(series[i])
    return np.array(X), np.array(y)

def train_lstm_model(df: pd.DataFrame, city_name: str, n_steps=12):
    df = df[['Date', 'Temperature']].copy()
    scaler = MinMaxScaler()
    df['ScaledTemp'] = scaler.fit_transform(df[['Temperature']])
    data = df['ScaledTemp'].values
    X, y = prepare_lstm_data(data, n_steps)

    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    model = Sequential([
        LSTM(64, activation='tanh', input_shape=(n_steps, 1)),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')

    model.fit(
        X_train, y_train,
        validation_split=0.1,
        epochs=100,
        batch_size=16,
        verbose=0,
        callbacks=[EarlyStopping(patience=10, restore_best_weights=True)]
    )

    y_pred = model.predict(X_test)
    y_pred_inv = scaler.inverse_transform(y_pred)
    y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1))

    mae = mean_absolute_error(y_test_inv, y_pred_inv)
    rmse = np.sqrt(mean_squared_error(y_test_inv, y_pred_inv))
    r2 = r2_score(y_test_inv, y_pred_inv)

    print("\n📍 Modelo: LSTM")
    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²:   {r2:.3f}")

    plt.figure(figsize=(12, 4))
    plt.plot(y_test_inv, label='Real')
    plt.plot(y_pred_inv, label='Previsão')
    plt.title(f"LSTM - Temperatura Prevista vs Real ({city_name})")
    plt.xlabel("Meses")
    plt.ylabel("Temperatura (°C)")
    plt.legend()
    plt.tight_layout()
    plt.show()

    return model
