#evaluation/sampling.py
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import random

def evaluate_sample(model, X, y, train_size):
    """
    Avalia o desempenho de um modelo com uma divisão temporal simples dos dados.

    Utiliza a fração definida por 'train_size' para separar treino e teste, preservando a ordem temporal.

    Métricas retornadas:
    - MAE: Erro absoluto médio
    - RMSE: Raiz do erro quadrático médio
    - R²: Coeficiente de determinação

    Parâmetros:
    - model: Estimador com métodos .fit() e .predict()
    - X (ndarray): Features
    - y (ndarray): Target (temperatura)
    - train_size (float): Proporção inicial dos dados usada para treino (0 < train_size < 1)

    Retorna:
    - tuple: (mae, rmse, r2)
    """
    split_idx = int(len(X) * train_size)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    return mae, rmse, r2

def run_sampling(df, models, features, target='Temperature', n_runs=20):
    """
    Executa avaliação repetida de múltiplos modelos com diferentes tamanhos de treino e sementes aleatórias.

    Para cada combinação de:
    - tamanho de treino (de 0.55 a 0.9)
    - semente aleatória (n_runs)
    - modelo fornecido

    Calcula MAE, RMSE e R², retornando os resultados em formato tabular.

    Parâmetros:
    - df (pd.DataFrame): DataFrame original com dados de entrada
    - models (list): Lista de tuplas (modelo, nome)
    - features (list): Lista de colunas a usar como variáveis independentes
    - target (str): Coluna alvo (padrão = 'Temperature')
    - n_runs (int): Número de repetições para variação de seed

    Retorna:
    - pd.DataFrame: Resultados com colunas ['Model', 'Train_Size', 'Seed', 'MAE', 'RMSE', 'R2']
    """
    df_feat = df.copy()
    X = df_feat[features].values
    y = df_feat[target].values

    train_sizes = np.linspace(0.55, 0.9, num=6)
    seeds = [random.randint(0, 10000) for _ in range(n_runs)]

    results = []
    for train_size in train_sizes:
        for seed in seeds:
            np.random.seed(seed)
            for model, name in models:
                mae, rmse, r2 = evaluate_sample(model, X, y, train_size)
                results.append({
                    "Model": name,
                    "Train_Size": train_size,
                    "Seed": seed,
                    "MAE": mae,
                    "RMSE": rmse,
                    "R2": r2
                })

    return pd.DataFrame(results)
