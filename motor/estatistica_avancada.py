"""
Funções estatísticas avançadas para análise do Jogo do Bicho.

Inclui:
- chi_quadrado_uniforme: testa se distribuição difere de uniforme
- zscore_por_valor: calcula z-score de cada valor
"""
import numpy as np
import pandas as pd
from scipy import stats


def chi_quadrado_uniforme(df, coluna="milhar"):
    """
    Testa se a distribuição dos valores difere de uniforme.

    Corrigido:
    - usa len(df) como n total, nao a soma das contagens
    - trata caso de 1 so categoria (retorna p=1.0)
    """
    n_total = len(df)
    contagem = df[coluna].astype(str).value_counts()
    observado = contagem.values
    n_valores = len(contagem)

    # Caso especial: 1 so categoria -> nao da pra calcular chi2
    if n_valores < 2:
        return {
            "chi2": 0.0,
            "p_value": 1.0,
            "gl": 0,
            "n": int(n_total),
            "n_valores": n_valores,
            "esperado_por_valor": float(n_total),
            "interpretacao": "compativel com uniformidade (acaso)",
        }

    esperado = np.full(n_valores, n_total / n_valores)

    chi2, p = stats.chisquare(observado, esperado)

    if p < 0.01:
        interp = "diferenca ALTAMENTE significativa"
    elif p < 0.05:
        interp = "diferenca significativa"
    elif p < 0.10:
        interp = "diferenca marginal"
    else:
        interp = "compativel com uniformidade (acaso)"

    return {
        "chi2": float(chi2),
        "p_value": float(p),
        "gl": n_valores - 1,
        "n": int(n_total),
        "n_valores": n_valores,
        "esperado_por_valor": float(n_total / n_valores),
        "interpretacao": interp,
    }


def zscore_por_valor(df, coluna="milhar"):
    """
    Para cada valor, calcula:
    z = (observado - esperado) / desvio padrao esperado.

    Corrigido: usa len(df) como n total.
    """
    n_total = len(df)
    contagem = df[coluna].astype(str).value_counts()
    k = df[coluna].nunique()

    p = 1 / k
    esperado = n_total * p
    desvio = np.sqrt(n_total * p * (1 - p))

    registros = []
    for valor, obs in contagem.items():
        z = (obs - esperado) / desvio if desvio > 0 else 0.0
        registros.append({
            coluna: valor,
            "observado": int(obs),
            "esperado": round(esperado, 2),
            "z": round(z, 3),
        })

    return (
        pd.DataFrame(registros)
        .sort_values("z", ascending=False)
        .reset_index(drop=True)
    )
