import pandas as pd


def normalizar(serie):
    """
    Normaliza uma série para o intervalo [0, 1].
    Se todos os valores forem iguais, retorna 0.5.
    """
    minimo = serie.min()
    maximo = serie.max()
    if maximo == minimo:
        return pd.Series([0.5] * len(serie), index=serie.index)
    return (serie - minimo) / (maximo - minimo)


def calcular_score(
    tabela,
    pesos=None,
    coluna_recencia="recencia_10"
):
    """
    Calcula um score combinado por valor.

    Parâmetros
    ----------
    tabela : DataFrame
        Saída de tabela_analise().
    pesos : dict
        Ex.: {"frequencia": 0.3, "atraso": 0.3, "recencia": 0.4}
    coluna_recencia : str
        Qual coluna de recência usar como sinal.
    """

    if pesos is None:
        pesos = {
            "frequencia": 0.30,
            "atraso": 0.30,
            "recencia": 0.40,
        }

    df = tabela.copy()

    df["freq_norm"] = normalizar(df["frequencia_total"])
    df["atraso_norm"] = normalizar(df["atraso"])
    df["rec_norm"] = normalizar(df[coluna_recencia])

    df["score"] = (
        pesos["frequencia"] * df["freq_norm"]
        + pesos["atraso"] * df["atraso_norm"]
        + pesos["recencia"] * df["rec_norm"]
    )

    return (
        df.sort_values("score", ascending=False)
        .reset_index(drop=True)
    )

def calcular_score_v2(
    tabela,
    features,
    coluna="milhar",
    pesos=None,
    coluna_recencia="recencia_10",
):
    """
    Score v2: combina frequência, atraso, recência
    e features adicionais (repetições, prêmio médio).

    Parâmetros
    ----------
    tabela : DataFrame
        Saída de tabela_analise().
    features : DataFrame
        Saída de construir_features().
    pesos : dict
        Pesos para cada componente. Padrão:
        {"frequencia":0.25, "atraso":0.20, "recencia":0.25,
         "repeticoes":0.15, "premio":0.15}
    """

    if pesos is None:
        pesos = {
            "frequencia": 0.25,
            "atraso": 0.20,
            "recencia": 0.25,
            "repeticoes": 0.15,
            "premio": 0.15,
        }

    df = tabela.merge(features, on=coluna, how="left")

    df["freq_norm"] = normalizar(df["frequencia_total"])
    df["atraso_norm"] = normalizar(df["atraso"])
    df["rec_norm"] = normalizar(df[coluna_recencia])

    df["rep_norm"] = normalizar(
        df["repeticoes_consecutivas"] + df["repeticoes_mesmo_concurso"]
    )

    # premio_medio: 1 é bom, 5 é ruim -> inverter
    pm = df["premio_medio"].fillna(df["premio_medio"].mean())
    df["premio_norm"] = 1 - normalizar(pm)

    df["score"] = (
        pesos["frequencia"] * df["freq_norm"]
        + pesos["atraso"] * df["atraso_norm"]
        + pesos["recencia"] * df["rec_norm"]
        + pesos["repeticoes"] * df["rep_norm"]
        + pesos["premio"] * df["premio_norm"]
    )

    return (
        df.sort_values("score", ascending=False)
        .reset_index(drop=True)
    )
