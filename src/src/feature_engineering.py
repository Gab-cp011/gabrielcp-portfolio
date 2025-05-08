def create_time_features(df):
    """
    Gera variáveis derivadas de tempo e estatísticas temporais para modelagem de séries temporais.

    Esta função parte de um DataFrame contendo colunas 'Date' (datetime) e 'Temperature' e adiciona:
    - Ano e mês como variáveis explícitas
    - Representações sazonais do mês com funções seno e cosseno
    - Defasagens (lags) de 1 e 12 meses
    - Média e desvio padrão móvel com janela de 3 meses

    Após o processamento, remove as primeiras linhas com valores ausentes (devido aos lags e janelas) e retorna um novo DataFrame pronto para uso em modelos preditivos.

    Parâmetros:
    - df (pd.DataFrame): DataFrame contendo pelo menos 'Date' e 'Temperature'

    Retorna:
    - pd.DataFrame: DataFrame com atributos temporais adicionais e sem valores nulos
    """
  
    df = df.copy()
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['sin_month'] = np.sin(2 * np.pi * df['Month'] / 12)
    df['cos_month'] = np.cos(2 * np.pi * df['Month'] / 12)
    df['lag_1'] = df['Temperature'].shift(1)
    df['lag_12'] = df['Temperature'].shift(12)
    df['rolling_mean_3'] = df['Temperature'].rolling(window=3).mean()
    df['rolling_std_3'] = df['Temperature'].rolling(window=3).std()
    df = df.dropna().reset_index(drop=True)
  
    return df
