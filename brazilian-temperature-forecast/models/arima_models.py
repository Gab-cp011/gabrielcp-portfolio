# src/models/arima_models.py
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

def train_arima(df, order=(1, 1, 1)):
    y = df['Temperature']
    split_idx = int(len(y) * 0.8)
    train, test = y[:split_idx], y[split_idx:]
    model = ARIMA(train, order=order).fit()
    y_pred = model.forecast(steps=len(test))
    return _evaluate_forecast(test, y_pred, "ARIMA")

def train_sarima(df, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)):
    y = df['Temperature']
    split_idx = int(len(y) * 0.8)
    train, test = y[:split_idx], y[split_idx:]
    model = SARIMAX(train, order=order, seasonal_order=seasonal_order).fit(disp=False)
    y_pred = model.forecast(steps=len(test))
    return _evaluate_forecast(test, y_pred, "SARIMA")

def _evaluate_forecast(y_true, y_pred, name):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    print(f"\n📍 Modelo: {name}")
    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²:   {r2:.3f}")
    return y_true.reset_index(drop=True), y_pred