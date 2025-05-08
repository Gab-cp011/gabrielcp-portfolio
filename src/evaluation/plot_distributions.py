import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def plot_distribution_kde(df, metric):
    """
    Plota a distribuição de uma métrica de erro por modelo, combinando histograma e curva de densidade (KDE).

    Ideal para comparar visualmente a dispersão e tendência central de métricas como MAE, RMSE ou R² entre diferentes modelos.

    Parâmetros:
    - df (pd.DataFrame): DataFrame contendo ao menos as colunas 'Model' e a métrica especificada
    - metric (str): Nome da métrica a ser visualizada ('MAE', 'RMSE' ou 'R2')
    """

    plt.figure(figsize=(10, 5))
    sns.histplot(data=df, x=metric, hue='Model', kde=True, element="step", stat="density", common_norm=False)
    plt.title(f'Distribuição de {metric} por Modelo')
    plt.xlabel(metric)
    plt.ylabel("Densidade")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_distribution_all(df):
    """
    Gera gráficos de distribuição para todas as métricas de avaliação (MAE, RMSE, R²) de uma só vez.

    Utiliza a função plot_distribution_kde para cada métrica.

    Parâmetros:
    - df (pd.DataFrame): DataFrame com resultados agregados por modelo contendo as métricas 'MAE', 'RMSE' e 'R2'
    """
    for metric in ['MAE', 'RMSE', 'R2']:
        plot_distribution_kde(df, metric)
