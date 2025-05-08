# src/models/regression_models.py
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

def evaluate_model(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    return mae, rmse, r2, y_pred

def get_regression_models():
    return [
        (RandomForestRegressor(n_estimators=100, random_state=42), "Random Forest"),
        (HistGradientBoostingRegressor(max_iter=200, random_state=42), "HistGradientBoosting"),
        (ExtraTreesRegressor(n_estimators=100, random_state=42), "Extra Trees"),
        (Ridge(alpha=1.0), "Ridge Regression")
    ]
