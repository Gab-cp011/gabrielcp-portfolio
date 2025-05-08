# 🏍️ Simulador de Dinâmica Veicular em Python

## ✨ Sobre o Projeto

Este é meu projeto final de graduação em Engenharia Mecânica no CEFET/RJ, focado em simulação física de veículos terrestres. Ele nasceu do TCC de João Marcos Cavalcante da Silva na UFRJ (2023), que desenvolveu uma versão funcional para carros com base na dinâmica longitudinal e lateral.

A partir desse núcleo original, **estou dando continuidade ao projeto com o desenvolvimento de uma versão dedicada a motocicletas**.

Nosso objetivo principal permanece: **criar um simulador automotivo didático, acessível e inteiramente em Python**, utilizando apenas equações analíticas e fundamentos da engenharia mecânica.

---

## 🧩 Estrutura Modular

| Arquivo                  | Função                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------- |
| `loop.py`                | Coração da simulação. Realiza os cálculos ponto a ponto com base na física do movimento.    |
| `roots.py`               | Resolve a equação de Torricelli adaptada com restrições físicas (potência, aderência etc.). |
| `tools.py`               | Funções auxiliares: interpolação, cálculos de raios, curvas de potência, filtragens etc.    |
| `velocity_correction.py` | Corrige velocidades quando os limites de aderência são ultrapassados em algum trecho.       |
| `print_functions.py`     | Monitoramento e debug de simulações.                                                        |

---

## 🎯 Objetivo Atual: Motocicletas

A missão atual é **adaptar e validar o simulador para veículos de duas rodas**, respeitando suas características dinâmicas específicas, usando modelagens simples e baseadas na literatura acadêmica.

Também estão sendo implementadas melhorias de desempenho e organização do código.

---

## 🔍 Funcionalidades Já Implementadas

* Simulação da velocidade ao longo de uma trajetória 3D ou 2D com base em equações analíticas
* Consideração de forças reais: peso, arrasto, rolamento, tração e sustentação
* Respeito ao limite de aderência combinada (Elipse de Tração)
* Simulação com ou sem marchas, incluindo RPM e curvas de potência realistas
* Geração de DataFrame com: distância, velocidade, acelerações, força, tempo, marcha, etc.
* Implementação de funções para tratar dados de telemetria (que muitas vezes são input do algoritmo)
* Plots e cálculos de métricas para validação do modelo

---

🧪 Exemplo de Simulação

Este repositório inclui um exemplo de simulação validada, que compara os resultados do modelo com dados reais extraídos do jogo Project CARS 2. O arquivo Analise.html documenta essa análise e pode ser visualizado diretamente [clicando aqui](https://gab-cp011.github.io/gabrielcp-portfolio/Analise.html)). 

A comparação serve como uma validação empírica do modelo proposto e ilustra sua capacidade de representar a dinâmica de um veículo de forma plausível e realista.

## 🛠 Como Usar

### 1. Instale as dependências:

```bash
pip install numpy pandas matplotlib shapely scipy
```

### 2. Prepare os dados:

Você precisa fornecer listas `x`, `y`, `z` com as coordenadas da pista e parâmetros do veículo.

### 3. Rode a simulação:

```python
from loop_original import loop

resultado = loop(
    fx=1, fy=1, x=x, y=y, z=z, P=90, m=210, Cl=0.2, Cd=0.35, Af=0.9,
    Crr=0.015, ld=1, lt=1, h=0.3, Tracao='D', Vo=0, Frenagem=1,
    Vmax=180, mu=1.2, nu=1,
    marcha=True, Ps=[...], ns=[...],
    finaldrive=4.2, gearslist=[3.2, 2.1, 1.3, 1.0, 0.8], rw=0.3
)
```

### 4. Visualize os resultados:

```python
from tools_original import graph
graph(resultado)
```

---

## 📘 Referência Teórica

Baseado no TCC original de João Marcos Cavalcante (UFRJ, 2023), com tópicos sobre:

* Forças atuantes: arrasto, peso, tração, rolamento, sustentação
* Cinemática longitudinal e lateral
* Elipse de tração (Círculo de Kamm)
* Equação de Torricelli adaptada para restrições físicas

A nova fase do projeto amplia esse conteúdo para motocicletas.

---

## 🧪 Saídas da Simulação

O `DataFrame` de saída contém:

* `Distance (m)`
* `Speed (m/s)`
* `Ax (m/s²)` — aceleração longitudinal
* `Ay (m/s²)` — aceleração lateral
* `Force (N)` — força resultante longitudinal
* `Time (s)`
* `Gears`, `GRatios`, `RPM` — se marchas estiverem ativadas

---

## 👤 Créditos

* **João Marcos Cavalcante da Silva** — autor da versão original (carro)
* **Gabriel Cândido Passos** — autor da versão atual para motocicletas e manutenção do projeto
