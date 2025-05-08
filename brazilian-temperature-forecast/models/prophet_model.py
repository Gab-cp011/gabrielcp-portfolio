# src/models/prophet_model.py
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import numpy as np

def train_prophet_model(df, city_name):
    df_prophet = df.rename(columns={"Date": "ds", "Temperature": "y"})
    split_idx = int(len(df_prophet) * 0.8)
    train, test = df_prophet.iloc[:split_idx], df_prophet.iloc[split_idx:]

    model = Prophet(yearly_seasonality=True, daily_seasonality=False, weekly_seasonality=False,
                    changepoint_prior_scale=0.01)
    model.add_seasonality(name='bimestral', period=60.5, fourier_order=3)
    model.fit(train)

    future = model.make_future_dataframe(periods=len(test), freq='MS')
    forecast = model.predict(future)

    y_true = test['y'].values
    y_pred = forecast.iloc[split_idx:]['yhat'].values

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    print(f"\n📍 Modelo: Prophet")
    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²:   {r2:.3f}")

    fig = model.plot(forecast)
    fig.set_size_inches(14, 6)
    ax = fig.gca()
    ax.set_title(f"Forecast com Prophet - {city_name}", fontsize=14)
    ax.set_xlabel("Data")
    ax.set_ylabel("Temperatura (°C)")
    ax.legend(["Histórico", "Previsão", "Incerteza"], loc="upper left")
    plt.tight_layout()
    plt.show()

    return forecast
