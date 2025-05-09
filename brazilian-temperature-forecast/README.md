# 🌡️ Brazilian Temperature Forecast

Previsão mensal de temperatura em cidades brasileiras utilizando diferentes modelos de séries temporais: estatísticos, regressivos, neurais e probabilísticos. A análise completa se encontra na notebook [**pipeline**](./notebooks/pipeline.ipynb), na pasta notebooks. 

---

## 🎯 Objetivo

Criar um pipeline modular e robusto para:
- Explorar dados históricos de temperatura
- Criar atributos temporais significativos
- Treinar e comparar modelos diversos
- Avaliar desempenho com repetição e amostragem

---

## 📁 Estrutura do Projeto

```
brazilian-temperature-forecast/
├── data/                    # Arquivos CSV de temperatura (não versionado)
├── src/                    # Código-fonte principal
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── plotting.py
│   ├── models/
│   │   ├── regression_models.py
│   │   ├── arima_models.py
│   │   ├── prophet_model.py
│   │   ├── lstm_model.py
│   │   └── boosting_models.py
│   ├── evaluation/
│   │   ├── sampling.py
│   │   └── plot_distributions.py
├── main.py                 # Execução do pipeline
├── requirements.txt        # Lista de bibliotecas usadas
├── README.md               # Esta documentação
└── .gitignore              # Arquivos e pastas ignoradas pelo Git
```

---

## ⚙️ O que o Código Faz

1. Lê arquivos CSV de temperatura em formato wide
2. Trata outliers e formata datas
3. Gera atributos temporais (lags, sazonais, médias móveis)
4. Treina múltiplos modelos:
   - Regressão, ARIMA, Prophet, LSTM, Boosting
5. Avalia com diferentes `train_size` e `seed`
6. Plota distribuições de erro por modelo (MAE, RMSE, R²)

---

## 🤖 Modelos Disponíveis

- **Regressão**: Random Forest, Ridge, Extra Trees, HistGradientBoosting
- **Estatísticos**: ARIMA, SARIMA
- **Probabilístico**: Prophet
- **Deep Learning**: LSTM
- **Boosting**: XGBoost, LightGBM

---

## 📊 Avaliação e Visualização

- Avaliação repetida com amostragem
- Boxplots e distribuições tipo KDE
- Métricas: MAE, RMSE, R²

---

## 🧪 Requisitos

Instale com:
```bash
pip install -r requirements.txt
```

---

## ✍️ Autor
Este projeto foi desenvolvido para análise e previsão de séries temporais climáticas reais no Brasil, podendo ser facilmente adaptado a outras variáveis ou países.

---

## 🤝 Contribuições
Pull requests são bem-vindos para melhorias de estrutura, desempenho ou novos modelos!
