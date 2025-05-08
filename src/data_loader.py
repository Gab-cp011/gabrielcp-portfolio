import pandas as pd
import numpy as np

MONTH_COLUMNS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def load_city_temperature(file_path):
    """
    Carrega e pré-processa um arquivo CSV com dados mensais de temperatura para uma cidade brasileira.

    O arquivo deve estar no formato "wide", onde cada linha representa um ano e as colunas de mês vão de 'JAN' a 'DEC'.

    Etapas de processamento:
    - Converte os dados para formato "long" (uma linha por mês).
    - Constrói uma coluna de datas (datetime) com o primeiro dia de cada mês.
    - Converte temperaturas para numérico, tratando valores ausentes ou inválidos.
    - Detecta outliers (valores acima de 70°C) e os substitui por:
        - a média dos valores anterior e posterior válidos (se disponíveis), ou
        - a média mensal histórica (caso contrário).
    - Retorna um DataFrame com colunas ['Date', 'Temperature', 'Month'], pronto para análise e modelagem.

    Parâmetros:
    - file_path (str): Caminho para o arquivo CSV de entrada.

    Retorna:
    - pd.DataFrame: DataFrame processado com temperatura mensal por data.
    """
    df = pd.read_csv(file_path)
    df_long = df.melt(id_vars=['YEAR'], value_vars=MONTH_COLUMNS, var_name='Month', value_name='Temperature')
    month_map = {m: i for i, m in enumerate(MONTH_COLUMNS, start=1)}
    df_long['Month'] = df_long['Month'].map(month_map)
    df_long['Date'] = pd.to_datetime(dict(year=df_long['YEAR'], month=df_long['Month'], day=1))
    df_long = df_long.sort_values('Date').reset_index(drop=True)
    df_long['Temperature'] = pd.to_numeric(df_long['Temperature'], errors='coerce')
    df_long['IsOutlier'] = df_long['Temperature'] > 70
    monthly_means = df_long[~df_long['IsOutlier']].groupby("Month")["Temperature"].mean().to_dict()

    temp_values = df_long["Temperature"].values
    month_values = df_long["Month"].values

    for i in df_long[df_long["IsOutlier"]].index:
        prev_val = temp_values[i - 1] if i > 0 and np.isfinite(temp_values[i - 1]) and temp_values[i - 1] <= 70 else None
        next_val = temp_values[i + 1] if i < len(temp_values) - 1 and np.isfinite(temp_values[i + 1]) and temp_values[i + 1] <= 70 else None
        if prev_val is not None and next_val is not None:
            temp_values[i] = (prev_val + next_val) / 2
        else:
            temp_values[i] = monthly_means.get(month_values[i], np.nan)

    df_long["Temperature"] = temp_values
    df_long.drop(columns=["IsOutlier"], inplace=True)
    return df_long[['Date', 'Temperature', 'Month']]
