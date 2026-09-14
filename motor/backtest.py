import pandas as pd

from motor.cruzamento import tabela_analise
from motor.score import calcular_score


def backtest(
    numeros,
    coluna="milhar",
    janela_minima=5,
    janelas_recencia=None,
    pesos=None,
    coluna_recencia="recencia_10",
    top_ns=(1, 3, 5),
):
    """
    Simula o uso do score ao longo do histórico.

    Para cada ponto de corte, calcula o score usando
    apenas os dados até ali e verifica a posição do
    próximo número sorteado no ranking.

    Retorna um dict com métricas.
    """

    if janelas_recencia is None:
        janelas_recencia = [5, 10]
    if pesos is None:
        pesos = {"frequencia": 0.30, "atraso": 0.30, "recencia": 0.40}

    from motor.processamento import processar_numero

    registros = []

    for corte in range(janela_minima, len(numeros)):
        passado = numeros[:corte]
        futuro = numeros[corte]

        dados_passado = [processar_numero(n) for n in passado]
        df_passado = pd.DataFrame(dados_passado)

        tabela = tabela_analise(df_passado, coluna, janelas=janelas_recencia)

        if coluna_recencia not in tabela.columns:
            # janela escolhida não existe — pula
            continue

        ranking = calcular_score(tabela, pesos=pesos, coluna_recencia=coluna_recencia)

        # Em que posição está o valor sorteado?
        valor_futuro = str(futuro).zfill(4) if coluna == "milhar" else str(futuro)
        # Para milhar, precisamos do milhar do número futuro
        if coluna == "milhar":
            valor_futuro = str(futuro).zfill(4)

        posicoes = ranking[coluna].astype(str).tolist()
        if valor_futuro not in posicoes:
            rank = None
        else:
            rank = posicoes.index(valor_futuro) + 1

        registros.append({
            "corte": corte,
            "sorteado": valor_futuro,
            "rank": rank,
            "total_candidatos": len(posicoes),
        })

    resultado = pd.DataFrame(registros)

    metricas = {
        "total_testes": len(resultado),
        "rank_medio": resultado["rank"].dropna().mean() if len(resultado) else None,
        "top1_hits": int((resultado["rank"] == 1).sum()),
        "top3_hits": int((resultado["rank"] <= 3).sum()),
        "top5_hits": int((resultado["rank"] <= 5).sum()),
    }

    return resultado, metricas

def backtest_comparativo(
    numeros,
    coluna="milhar",
    janela_minima=8,
    janelas_recencia=None,
    pesos_v1=None,
    pesos_v2=None,
    coluna_recencia="recencia_10",
    premios_por_concurso=5,
):
    """
    Roda o backtest para v1, v2 e baseline aleatório,
    devolvendo uma tabela comparativa.
    """

    import random
    import pandas as pd

    from motor.processamento import processar_numero
    from motor.cruzamento import tabela_analise
    from motor.features import construir_features
    from motor.score import calcular_score, calcular_score_v2

    if janelas_recencia is None:
        janelas_recencia = [5, 10]

    if pesos_v1 is None:
        pesos_v1 = {"frequencia": 0.30, "atraso": 0.30, "recencia": 0.40}

    if pesos_v2 is None:
        pesos_v2 = {
            "frequencia": 0.25,
            "atraso": 0.20,
            "recencia": 0.25,
            "repeticoes": 0.15,
            "premio": 0.15,
        }

    registros = []

    for corte in range(janela_minima, len(numeros)):
        passado = numeros[:corte]
        futuro = numeros[corte]

        dados_passado = [processar_numero(n) for n in passado]
        df_passado = pd.DataFrame(dados_passado)

        tabela = tabela_analise(df_passado, coluna, janelas=janelas_recencia)

        if coluna_recencia not in tabela.columns:
            continue

        features = construir_features(
            df_passado, coluna=coluna, premios_por_concurso=premios_por_concurso
        )

        r_v1 = calcular_score(tabela, pesos=pesos_v1, coluna_recencia=coluna_recencia)
        r_v2 = calcular_score_v2(
            tabela, features, coluna=coluna,
            pesos=pesos_v2, coluna_recencia=coluna_recencia
        )

        # baseline: embaralha
        r_rand = r_v1.sample(frac=1, random_state=corte).reset_index(drop=True)

        valor_futuro = str(futuro).zfill(4)

        def rank_de(ranking):
            posicoes = ranking[coluna].astype(str).tolist()
            if valor_futuro not in posicoes:
                return None
            return posicoes.index(valor_futuro) + 1

        registros.append({
            "corte": corte,
            "sorteado": valor_futuro,
            "rank_v1": rank_de(r_v1),
            "rank_v2": rank_de(r_v2),
            "rank_rand": rank_de(r_rand),
            "total_candidatos": len(r_v1),
        })

    df = pd.DataFrame(registros)

    def metricas(prefixo):
        ranks = df[f"rank_{prefixo}"].dropna()
        if len(ranks) == 0:
            return None
        return {
            "n": len(ranks),
            "rank_medio": ranks.mean(),
            "top1": int((ranks == 1).sum()),
            "top3": int((ranks <= 3).sum()),
            "top5": int((ranks <= 5).sum()),
        }

    return df, {
        "v1": metricas("v1"),
        "v2": metricas("v2"),
        "random": metricas("rand"),
    }
