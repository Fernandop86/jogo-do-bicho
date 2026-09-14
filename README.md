# 🎰 Jogo do Bicho 2024 — Dashboard

Dashboard interativo para análise estatística do Jogo do Bicho.

## 📊 O que faz

- Carrega 10.325 prêmios do histórico 2024
- Analisa frequência de grupos, dezenas, centenas e milhares
- Gera sugestões diárias baseadas em dados históricos
- Executa backtest de apostas com R$ 5/dia
- Gráficos interativos e tabelas detalhadas

## 🚀 Como usar

### Local

1. Clone o repositório
2. `pip install -r requirements.txt`
3. `streamlit run dashboard_streamlit.py`

### Online

Acesse: (link será adicionado após publicação)

## 📁 Estrutura

- `dashboard_streamlit.py` — Dashboard principal
- `motor/` — Módulos de análise
- `dados/` — CSVs do histórico
- `.streamlit/config.toml` — Tema visual

## ⚠️ Aviso importante

Este projeto é para **análise estatística e curiosidade**.
**Não há padrão preditivo** — o jogo é estatisticamente uniforme
(chi² = 19.74, p = 0.71). Apostar tem retorno esperado **negativo**.

## 📜 Licença

Uso livre para fins educacionais.