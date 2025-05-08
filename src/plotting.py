import matplotlib.pyplot as plt
import seaborn as sns

def plot_eda_summary(df, city_name):
    """
    Gera dois gráficos para análise exploratória da temperatura:
    - Boxplot da temperatura por mês
    - Histograma com curva de densidade (KDE) das temperaturas

    Útil para observar distribuição, outliers e padrões sazonais.

    Parâmetros:
    - df (pd.DataFrame): DataFrame contendo colunas 'Month' e 'Temperature'
    - city_name (str): Nome da cidade (usado no título dos gráficos)
    """
  
    plt.figure(figsize=(10, 4))
    sns.boxplot(x=df['Month'], y=df['Temperature'])
    plt.title(f"Boxplot Mensal da Temperatura - {city_name}")
    plt.xlabel("Mês")
    plt.ylabel("Temperatura (°C)")
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(8, 4))
    sns.histplot(df['Temperature'], kde=True, bins=30)
    plt.title(f"Distribuição da Temperatura - {city_name}")
    plt.xlabel("Temperatura (°C)")
    plt.tight_layout()
    plt.show()

def plot_temperature_by_year(df, city_name):
    """
    Plota a série temporal da temperatura média anual da cidade ao longo do tempo.

    Agrega os dados por ano e exibe um gráfico de linha com marcadores.

    Parâmetros:
    - df (pd.DataFrame): DataFrame contendo colunas 'Date' (datetime) e 'Temperature'
    - city_name (str): Nome da cidade (usado no título do gráfico)
    """
    df_yearly = df.copy()
    df_yearly["Year"] = df_yearly["Date"].dt.year
    df_yearly = df_yearly.groupby("Year")["Temperature"].mean().reset_index()

    plt.figure(figsize=(12, 4))
    plt.plot(df_yearly["Year"], df_yearly["Temperature"], marker='o', linestyle='-')
    plt.title(f"Temperatura Média Anual - {city_name}")
    plt.xlabel("Ano")
    plt.ylabel("Temperatura Média (°C)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
