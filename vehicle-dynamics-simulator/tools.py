# Built-in
import os
import math
import xml.etree.ElementTree as ET
from math import asin, sqrt

# Third-party
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
from scipy import stats
from scipy import interpolate
from scipy.interpolate import interp1d, splprep, splev, splrep
from scipy.stats import gaussian_kde
from scipy.signal import butter, filtfilt
from pyproj import Transformer
from geopy.distance import geodesic
import matplotlib.cm as cm
import matplotlib.colors as colors
from statistics import median, stdev


# Código do tools atualizado, com possibilidade de não utilização da altura nas simulações, adição de diferentes técnicas de
# interpolação no modelo, adição do filtro butterworth, adição da possibilidade de aplicação do filtro butterworth no raio 
# para reduzir mudanças abruptas, adição de diferentes técnicas de conversão de lat e long para metros e adição de mais
# gráficos na função de geração de gráficos, cálculo de métricas de erro entre dois dataframes, cálculo de estatísticas
#  da simulação,plot dos erros e função que converte de kml para csv. Também foi alterado a curva de potencia para
#  o caso em que as curvas das marchas não se cruzam. Ele converte para array, também,
#  para evitar erros advindos do uso de listas




def convert_kml_to_csv(kml_path: str) -> pd.DataFrame:
    """
    Converte KML em CSV (apenas LineString), removendo o fechamento de linha.
    Retorna DataFrame com latitude, longitude, altitude.
    """
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    kml_path = os.path.abspath(kml_path)
    csv_path = os.path.splitext(kml_path)[0] + '.csv'

    tree = ET.parse(kml_path)
    root = tree.getroot()

    coords = []

    for linestring in root.findall('.//kml:LineString', ns):
        coords_elem = linestring.find('kml:coordinates', ns)
        if coords_elem is not None:
            points = [line.strip() for line in coords_elem.text.strip().split()]
            clean_points = []
            for pt in points:
                lon, lat, *alt = map(float, pt.split(','))
                alt = alt[0] if alt else 0.0
                clean_points.append({'latitude': lat, 'longitude': lon, 'altitude': alt})

            if len(clean_points) >= 2:
                first = (clean_points[0]['latitude'], clean_points[0]['longitude'])
                last = (clean_points[-1]['latitude'], clean_points[-1]['longitude'])
                if first == last:
                    clean_points.pop()

            coords.extend(clean_points)

    df = pd.DataFrame(coords)
    df.to_csv(csv_path, index=False)
    print(f"Arquivo CSV salvo em: {csv_path}")

    return df


def calcular_utm_epsg(lat, lon):
    """
    Calcula o código EPSG UTM automaticamente baseado na latitude e longitude.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.

    Returns:
        str: Código EPSG adequado para a zona UTM.
    """
    zona = int((lon + 180) / 6) + 1
    hemisferio = 326 if lat >= 0 else 327
    epsg_code = f"EPSG:{hemisferio}{zona:02d}"
    return epsg_code


def latlon_to_xy(lat, lon, method='haversine', utm_epsg=None):
    """
    Converte latitude e longitude para coordenadas em metros.

    Args:
        lat (array-like): Vetor de latitudes.
        lon (array-like): Vetor de longitudes.
        method (str): Método de conversão. Opções:
                      'haversine', 'geopy', 'utm'
        utm_epsg (str, optional): Código EPSG UTM. Se None e method='utm', calcula automaticamente.

    Returns:
        tuple: (x, y) em metros
    """
    lat = np.asarray(lat)
    lon = np.asarray(lon)

    if method == 'haversine':
        R = 6378137
        lat_rad = np.radians(lat)
        lon_rad = np.radians(lon)
        x = (lon_rad - lon_rad[0]) * R * np.cos(lat_rad[0])
        y = (lat_rad - lat_rad[0]) * R

    elif method == 'geopy':
        x = [0]
        y = [0]
        lat_ref, lon_ref = lat[0], lon[0]
        for i in range(1, len(lat)):
            dx = geodesic((lat_ref, lon_ref), (lat_ref, lon[i])).meters
            dy = geodesic((lat_ref, lon_ref), (lat[i], lon_ref)).meters

            if lon[i] < lon_ref:
                dx *= -1
            if lat[i] < lat_ref:
                dy *= -1

            x.append(x[-1] + dx)
            y.append(y[-1] + dy)

        x = np.array(x)
        y = np.array(y)

    elif method == 'utm':
        if utm_epsg is None:
            utm_epsg = calcular_utm_epsg(lat[0], lon[0])
        transformer = Transformer.from_crs("EPSG:4326", utm_epsg, always_xy=True)
        x, y = transformer.transform(lon, lat)
        x, y = np.array(x), np.array(y)

    else:
        raise ValueError("method deve ser 'haversine', 'geopy' ou 'utm'")

    return x, y


def aplicar_butterworth(x, y, z=None, use_z=False, butter_cutoff=0.05, butter_order=4, fs=None):
    """
    Aplica o filtro Butterworth em x, y (e z se fornecido).

    Args:
        x, y, z (array-like): Coordenadas.
        use_z (bool): Considerar z na filtragem.
        butter_cutoff (float): Frequência de corte.
        butter_order (int): Ordem do filtro.
        fs (float): Frequência de amostragem.

    Returns:
        tuple: (x_filtrado, y_filtrado, z_filtrado)

        ## Frequência de Corte Recomendada para o Filtro Butterworth

    A escolha da frequência de corte (`cutoff`) depende diretamente do espaçamento entre os pontos interpolados (`deltaD`). 

    A tabela abaixo sugere valores típicos para projetos de análise e simulação de trajetórias baseadas em dados GPS/KML:

    | deltaD (Espaçamento dos pontos) | Frequência de Amostragem fs = 1/deltaD (Hz) | Frequência de Corte sugerida (cutoff) | Comentário |
    |---------------------------------|----------------------------------------------|----------------------------------------|------------|
    | 0.1 m                           | 10 Hz                                       | 0.5 a 1 Hz                             | Dados muito detalhados, remove apenas ruído fino |
    | 0.5 m                           | 2 Hz                                        | 0.2 a 0.5 Hz                           | Caminhos detalhados, com leve suavização |
    | 1.0 m                           | 1 Hz                                        | 0.1 a 0.3 Hz                           | Uso geral para dados KML / GPS urbanos |
    | 2.0 m                           | 0.5 Hz                                      | 0.05 a 0.2 Hz                          | Grandes trajetos urbanos ou mistos |
    | 5.0 m                           | 0.2 Hz                                      | 0.03 a 0.1 Hz                          | Estradas, rodovias, percursos longos |
    | 10.0 m                          | 0.1 Hz                                      | 0.02 a 0.05 Hz                         | Mapas de longa distância, macro trajetos |

    ---

    ### Regras gerais:

    - Frequência de Amostragem:
    ```python
    fs = 1 / deltaD

    """
    x, y = np.asarray(x), np.asarray(y)
    if use_z:
        z = np.asarray(z)

    if fs is None:
        fs = len(x) / (x[-1] - x[0])

    nyq = 0.5 * fs
    normal_cutoff = butter_cutoff / nyq
    b, a = butter(butter_order, normal_cutoff, btype='low', analog=False)

    x_f = filtfilt(b, a, x)
    y_f = filtfilt(b, a, y)
    z_f = filtfilt(b, a, z) if use_z else np.zeros_like(x_f)

    return x_f, y_f, z_f



def interpolar_trajetoria(x, y, z, deltaD, use_z=False, method='quadratic', butter_params=None, s=20, auto_fs=True):
    """
    Interpola pontos ao longo de uma trajetória.

    Args:
        x, y, z (array-like): Coordenadas da trajetória.
        deltaD (float): Distância desejada entre os novos pontos (m).
        use_z (bool): Considerar ou não a coordenada z na interpolação.
        method (str): 'quadratic', 'cubic' ou 'splineS'.
        butter_params (dict, optional): Parâmetros do filtro Butterworth:
            {'cutoff': frequência de corte, 'order': ordem do filtro, 'fs': freq. de amostragem (opcional)}
        s (float): Parâmetro de suavização da splineS (default = 20)
        auto_fs (bool): Se True, calcula automaticamente fs como 1/deltaD. Se False, espera butter_params['fs']

    Returns:
        tuple: x_interp, y_interp, z_interp (arrays interpolados)
    """

    x, y, z = np.asarray(x), np.asarray(y), np.asarray(z)

    # Cria pontos 2D ou 3D conforme configuração
    points = np.column_stack((x, y, z)) if use_z else np.column_stack((x, y))

    # Distância incremental e total
    segment_dist = np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1))
    total_dist = np.sum(segment_dist)

    # Distância acumulada normalizada
    distance = np.insert(np.cumsum(segment_dist), 0, 0)
    distance /= distance[-1]

    num_points = int(total_dist / deltaD) + 1
    alpha = np.linspace(0, 1, num_points)

    # Interpolação
    if method in ['quadratic', 'cubic']:
        interpolator = interp1d(distance, points, kind=method, axis=0)
        interp_points = interpolator(alpha)

    elif method == 'splineS':
        tck, _ = splprep([x, y, z] if use_z else [x, y], s=s)
        res = splev(np.linspace(0, 1, num_points), tck)
        x_s, y_s = res[0], res[1]
        z_s = res[2] if use_z else np.zeros_like(x_s)
        interp_points = np.column_stack((x_s, y_s, z_s))

    else:
        raise ValueError("method must be 'quadratic', 'cubic' or 'splineS'")

    if not use_z:
        z_col = np.zeros((interp_points.shape[0], 1))
        interp_points = np.hstack((interp_points[:, :2], z_col))

    x_interp, y_interp, z_interp = interp_points.T

    # Aplica filtro Butterworth após interpolar
    if butter_params:
        if auto_fs:
            fs = 1 / deltaD
        else:
            if 'fs' not in butter_params:
                raise ValueError("Frequência de amostragem 'fs' deve ser fornecida em butter_params se auto_fs=False")
            fs = butter_params['fs']

        x_interp, y_interp, z_interp = aplicar_butterworth(x_interp, y_interp, z_interp, use_z,
                                                            fs=fs,
                                                            butter_cutoff=butter_params['cutoff'],
                                                            butter_order=butter_params['order'])

    return x_interp, y_interp, z_interp




#Criacao das linhas que conectam cada ponto apos a interp():
def distanceXYZ(x, y, z=None, use_z=True):
    """Calcula as distâncias entre pontos consecutivos com ou sem eixo Z."""
    D = []
    for i in range(len(x) - 1):
        dx = x[i + 1] - x[i]
        dy = y[i + 1] - y[i]
        if use_z:
            if z is None:
                raise ValueError("z must be provided when use_z=True")
            dz = z[i + 1] - z[i]
        else:
            dz = 0
        D.append((dx**2 + dy**2 + dz**2) ** 0.5)
    return D

#Criacao dos raios para cada ponto, exceto primeiro e ultimo :
def radiusXYZ(x, y, z=None, use_z=True, return_curvature=False):
    """Calcula o raio do círculo formado por trios de pontos consecutivos.
       Se solicitado, retorna também a curvatura (1/R) """
    R = []
    kappa=[]
    for i in range(len(x) - 2):
        dx1 = x[i + 1] - x[i]
        dy1 = y[i + 1] - y[i]
        dx2 = x[i + 2] - x[i + 1]
        dy2 = y[i + 2] - y[i + 1]
        dx3 = x[i + 2] - x[i]
        dy3 = y[i + 2] - y[i]

        if use_z:
            if z is None:
                raise ValueError("z must be provided when use_z=True")
            dz1 = z[i + 1] - z[i]
            dz2 = z[i + 2] - z[i + 1]
            dz3 = z[i + 2] - z[i]
        else:
            dz1 = dz2 = dz3 = 0

        a = sqrt(dx1**2 + dy1**2 + dz1**2)
        b = sqrt(dx2**2 + dy2**2 + dz2**2)
        c = sqrt(dx3**2 + dy3**2 + dz3**2)

        p = (a + b + c) / 2
        A2 = p * (p - a) * (p - b) * (p - c)

        if A2 <= 0:
            r = 1e10
            k=0.0
        else:
            A = sqrt(A2)
            r = a * b * c / (4 * A)
            k = 1/r if r< 1e9 else 0.0
        R.append(r)
        if return_curvature:
            kappa.append(k)

    if return_curvature:
        return R, kappa
    else: 
        return R
    

# Usar para calcular variação média de curvatura de um ponto para outro

def analisar_variacao_curvatura_direct(curvaturas):
    """
    Analisa estatisticamente a variação da curvatura (1/R) entre elementos consecutivos.

    Parâmetros:
    - curvaturas: lista de curvaturas (1/R)

    Retorna:
    - Dicionário com estatísticas descritivas da variação da curvatura.
    """
    # Variação entre curvaturas consecutivas
    variacoes_curvatura = [
        abs(curvaturas[i+1] - curvaturas[i]) for i in range(len(curvaturas) - 1)
    ]

    # Estatísticas
    if not variacoes_curvatura:
        return {
            'min': 0.0,
            'max': 0.0,
            'media': 0.0,
            'mediana': 0.0,
            'desvio_padrao': 0.0
        }

    return {
        'min': min(variacoes_curvatura),
        'max': max(variacoes_curvatura),
        'media': sum(variacoes_curvatura) / len(variacoes_curvatura),
        'mediana': median(variacoes_curvatura),
        'desvio_padrao': stdev(variacoes_curvatura)
    }


#Inclinacao da pista:
def grading(altitude,distanceseg):
    angle = []
    for i in range(1,len(distanceseg)):
        anglei = asin((altitude[i+1]-altitude[i])/(distanceseg[i]))
        angle.append(anglei)
    for i in range(0, len(angle) - 1): # limitando a inclinacao em 0.2 rad
        if abs(angle[i]) > 0.2:
            if angle[i] > 0:
                angle[i] = 0.2
            elif angle[i] < 0:
                angle[i] = -0.2
    return angle


#Identificacao da direcao da curva (-1 para esquerda, 1 para direita):
def curva(x,y):
    c = []
    l = list(zip(y, x))
    for i in range(0, len(l) - 2):
        A = [[l[i][0], l[i][1], 1], [l[i + 1][0], l[i + 1][1], 1], [l[i +2][0], l[i + 2][1], 1]] # alteração feita no sinal da curva, era 1 e -1 
        if np.linalg.det(A) > 0:
            c.append(-1)
        elif np.linalg.det(A) < 0:
            c.append(1)
        else:
            c.append(0)
    return c


#Criacao das curvas de potncia em funcao da marcha e da velocidade:
def powercurve(Ps, ns, relacaoFinal, relacoesMarcha, rw):

    Ps = np.asarray(Ps)
    ns = np.asarray(ns)
    relacoesMarcha = np.asarray(relacoesMarcha)

    # Cria função potência em função do RPM
    P = interp1d(ns, Ps, fill_value='extrapolate')

    # Inicializa listas de saída
    Vs = []
    Plist = []
    Vlist = []

    # Velocidade mínima da 1ª marcha
    Vs.append((ns[0] * math.pi * rw) / (30 * relacoesMarcha[0] * relacaoFinal))

    # Para cada troca de marcha
    for i in range(len(relacoesMarcha) - 1):
        # Velocidades inicial e final das marchas i e i+1
        Vs1 = (ns[0] * math.pi * rw) / (30 * relacoesMarcha[i] * relacaoFinal)
        Vf1 = (ns[-1] * math.pi * rw) / (30 * relacoesMarcha[i] * relacaoFinal)
        Vs2 = (ns[0] * math.pi * rw) / (30 * relacoesMarcha[i + 1] * relacaoFinal)
        Vf2 = (ns[-1] * math.pi * rw) / (30 * relacoesMarcha[i + 1] * relacaoFinal)

        # Curva Potência vs Velocidade em cada marcha
        v1 = np.linspace(Vs1, Vf1, 1000)
        p1 = P((v1 * 30 * relacaoFinal * relacoesMarcha[i]) / (math.pi * rw))

        v2 = np.linspace(Vs2, Vf2, 1000)
        p2 = P((v2 * 30 * relacaoFinal * relacoesMarcha[i + 1]) / (math.pi * rw))

        # Interseção das curvas para troca de marcha
        line1 = LineString(np.column_stack((v1, p1)))
        line2 = LineString(np.column_stack((v2, p2)))
        intersec = line1.intersection(line2)

        if intersec.is_empty:
            Vtroca = (Vf1 + Vs2) / 2  # Chute conservador
        else:
            Vtroca = intersec.x  # Velocidade onde a troca acontece

        Vs.append(Vtroca)

    # Última velocidade máxima da última marcha
    Vs.append((ns[-1] * math.pi * rw) / (30 * relacoesMarcha[-1] * relacaoFinal))

    # Construindo a curva final completa
    for i in range(len(Vs) - 1):
        v = np.linspace(Vs[i] + 1e-4, Vs[i + 1], 100)
        Vlist = np.concatenate((Vlist, v))
        Plist = np.concatenate((Plist, P((v * 30 * relacaoFinal * relacoesMarcha[i]) / (math.pi * rw))))

    return Plist, Vlist, Vs




#Funcao para plotar o grafico apos o fim da simulacao

def graph(DF, x, y):
    """
    Gera gráficos completos de análise da simulação:
    - Velocidade
    - Aceleração
    - Trajeto colorido
    - Histograma de Velocidade
    - Scatter Ax vs Ay
    - Curvatura
    - Boxplot das Acelerações
    """

    fig = plt.figure(figsize=(16, 18), constrained_layout=True)
    gs = fig.add_gridspec(4, 2)

    major_ticks = np.arange(0, (DF.Distance.iloc[-1] / 1000), 0.5)

    # --- Gráfico Velocidade ---
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_xticks(major_ticks)
    ax1.xaxis.set_major_locator(plt.MaxNLocator(nbins=10))
    plt.setp(ax1.get_xticklabels(), rotation=0, ha='right')
    ax1.grid()
    ax1.plot(DF.Distance / 1000, 3.6 * DF.Speed, 'r', label='Speed')
    ax1.set_xlabel('Distância (km)')
    ax1.set_ylabel('Velocidade (km/h)')
    ax1.set_title('Velocidade')
    ax1.legend()

    # --- Gráfico Acelerações ---
    ax2 = fig.add_subplot(gs[1, :])
    ax2.set_xticks(major_ticks)
    ax2.xaxis.set_major_locator(plt.MaxNLocator(nbins=10))
    plt.setp(ax2.get_xticklabels(), rotation=0, ha='right')
    ax2.grid()
    ax2.plot(DF.Distance / 1000, DF.Ay, 'b:', label='Ay (m/s²)')
    ax2.plot(DF.Distance / 1000, DF.Ax, 'g--', label='Ax (m/s²)')
    ax2.set_xlabel('Distância (km)')
    ax2.set_ylabel('Aceleração (m/s²)')
    ax2.set_title('Acelerações')
    ax2.legend()

    # --- Mapa do Trajeto ---
    ax3 = fig.add_subplot(gs[2, 0])
    sc = ax3.scatter(x[:-1], y[:-1], c=DF.Speed, cmap='jet', s=10)
    cmap = cm.get_cmap("jet")
    norm = colors.Normalize(vmin=DF.Speed.min(), vmax=DF.Speed.max())
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax3, orientation='horizontal')
    cbar.set_label('Velocidade (km/h)')
    ax3.axis('off')
    ax3.set_title('Velocidade no Trajeto')

    # --- Histograma Velocidade ---
    ax4 = fig.add_subplot(gs[2, 1])
    ax4.hist(3.6 * DF.Speed, bins=30, color='skyblue', edgecolor='black')
    ax4.set_xlabel('Velocidade (km/h)')
    ax4.set_ylabel('Frequência')
    ax4.set_title('Histograma de Velocidade')

    # --- Scatter Ax vs Ay ---
    ax5 = fig.add_subplot(gs[3, 0])
    ax5.scatter(DF.Ax, DF.Ay, c=DF.Speed, cmap='jet', s=10)
    ax5.set_xlabel('Ax (m/s²)')
    ax5.set_ylabel('Ay (m/s²)')
    ax5.set_title('Ax vs Ay')

    plt.show()

def calcular_estatisticas(df):
    stats = {
        'Estatística': [
            'Média Ay',
            'Média Ax',
            'Velocidade Média (km/h)',
            'Mínimo Ay',
            'Mínimo Ax',
            'Velocidade Mínima (km/h)',
            'Máximo Ay',
            'Máximo Ax',
            'Velocidade Máxima (km/h)',
            'Desvio Padrão Ax',
            'Desvio Padrão Ay',
            'Desvio Padrão da Velocidade'
        ],
        'Valor': [
            df['Ay'].mean(),
            df['Ax'].mean(),
            (df['Speed'] * 3.6).mean(),
            df['Ay'].min(),
            df['Ax'].min(),
            (df['Speed'] * 3.6).min(),
            df['Ay'].max(),
            df['Ax'].max(),
            (df['Speed'] * 3.6).max(),
            df['Ax'].std(),
            df['Ay'].std(),
            (df['Speed'] * 3.6).std()
        ]
    }
    return pd.DataFrame(stats)


def calcular_metricas(df1, df2):
    colunas = df1.columns.intersection(df2.columns)
    resultados = {
        'Métrica': [],
        'Coluna': [],
        'Valor': []
    }

    for coluna in colunas:
        y_true = df1[coluna].values
        y_pred = df2[coluna].values

        mae = np.mean(np.abs(y_true - y_pred))
        mse = np.mean((y_true - y_pred) ** 2)
        rmse = np.sqrt(mse)
        
        # Cálculo do R² manualmente
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else np.nan

        # Adicionando ao dicionário de resultados
        for metrica, valor in zip(['MAE', 'MSE', 'RMSE', 'R²'], [mae, mse, rmse, r2]):
            resultados['Métrica'].append(metrica)
            resultados['Coluna'].append(coluna)
            resultados['Valor'].append(valor)

    return pd.DataFrame(resultados)

def plot_erros(df1, df2):
    """
    Plota o erro absoluto ponto a ponto e o histograma do erro
    para as colunas: Speed, Ax e Ay entre dois DataFrames.

    Args:
        df1 (DataFrame): DataFrame original
        df2 (DataFrame): DataFrame comparado
    """
    colunas = ['Speed', 'Ax', 'Ay']

    for coluna in colunas:
        if coluna in df1.columns and coluna in df2.columns:

            erro_abs = np.abs(df1[coluna] - df2[coluna])

            fig, axs = plt.subplots(2, 1, figsize=(12, 8), constrained_layout=True)

            # Erro absoluto ponto a ponto
            axs[0].plot(df1['Distance'] / 1000, erro_abs, label=f'Erro Absoluto - {coluna}')
            axs[0].set_xlabel('Distância (km)')
            axs[0].set_ylabel('Erro Absoluto')
            axs[0].set_title(f'Erro Absoluto - {coluna}')
            axs[0].grid(True)
            axs[0].legend()

            # Histograma do erro absoluto
            axs[1].hist(erro_abs, bins=30, color='skyblue', edgecolor='black')
            axs[1].set_xlabel('Erro Absoluto')
            axs[1].set_ylabel('Frequência')
            axs[1].set_title(f'Histograma do Erro Absoluto - {coluna}')

            plt.show()


# Função para ser utilizada apenas internamente, na Michelin 
def arara_severity(df, column, column_weight='Speed', v_convert=True): 
    """
    Calcula a severidade para a aceleração longitudinal e lateral 

    Args:
    df (DataFrame): DataFrame com os dados de aceleração
    column: Coluna com a aceleração
    column_weight: Coluna com a velocidade, utilizada para ponderar a aceleração
    v_convert: Parâmetro utilizado para verificar se é necessário converter ou não a velocidade para km/h
    """
    if v_convert: 
        df[column_weight]*=3.6    

    # Calculando a média ponderada pela velocidade
    media_ponderada = np.average(df[column], weights=df[column_weight])

    desvios_quadraticos = (df[column] - media_ponderada) ** 2

    # Calculando a média ponderada dos desvios quadráticos pela velocidade
    media_ponderada_dos_desvios = np.average(desvios_quadraticos, weights=df[column_weight])

    # Retornando o desvio padrão (raiz quadrada da média ponderada dos desvios quadráticos)
    desvio_padrao_ponderado = np.sqrt(media_ponderada_dos_desvios)

    print('Severidade: ', desvio_padrao_ponderado )

    return desvio_padrao_ponderado

