# src/models/boosting_models.py
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import matplotlib.pyplot as plt

def train_boosting_models(X_train, X_test, y_train, y_test, city_name):
    models = [
        (XGBRegressor(n_estimators=200, random_state=42), "XGBoost"),
        (LGBMRegressor(n_estimators=200, random_state=42, verbose=-1), "LightGBM")
    ]

    for model, name in models:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        print(f"\n📍 Modelo: {name}")
        print(f"MAE:  {mae:.2f}")
        print(f"RMSE: {rmse:.2f}")
        print(f"R²:   {r2:.3f}")

        plt.figure(figsize=(12, 4))
        plt.plot(y_test, label='Real')
        plt.plot(y_pred, label='Previsão')
        plt.title(f"{name} - Temperatura Prevista vs Real ({city_name})")
        plt.xlabel("Meses")
        plt.ylabel("Temperatura (°C)")
        plt.legend()
        plt.tight_layout()
        plt.show()


# # main.py (exemplo de uso)
# if __name__ == "__main__":
#     from src.data_loader import load_city_temperature
#     from src.feature_engineering import create_time_features
#     from src.plotting import plot_eda_summary, plot_temperature_by_year
#     from src.models.regression_models import get_regression_models, evaluate_model
#     from src.models.boosting_models import train_boosting_models

#     file_path = "data/station_goiania.csv"
#     city = "Goiânia"

#     df = load_city_temperature(file_path)
#     df_features = create_time_features(df)

#     plot_eda_summary(df, city)
#     plot_temperature_by_year(df, city)

#     features = ['Month', 'Year', 'sin_month', 'cos_month', 'lag_1', 'lag_12', 'rolling_mean_3', 'rolling_std_3']
#     X = df_features[features].values
#     y = df_features['Temperature'].values

#     split_idx = int(len(X) * 0.8)
#     X_train, X_test = X[:split_idx], X[split_idx:]
#     y_train, y_test = y[:split_idx], y[split_idx:]

#     for model, name in get_regression_models():
#         mae, rmse, r2, _ = evaluate_model(model, X_train, X_test, y_train, y_test)
#         print(f"{name} - MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.3f}")

#     train_boosting_models(X_train, X_test, y_train, y_test, city)