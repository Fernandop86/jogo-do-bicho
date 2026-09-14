import pandas as pd


def tabela_analise(df, coluna, janelas=None):
    """
    Constrói uma tabela única por valor da coluna,
    cruzando frequência total, atraso e recência
    em várias janelas.

    Parâmetros
    ----------
    df : DataFrame
        DataFrame já processado (com colunas milhar, centena, dezena, grupo, bicho).
    coluna : str
        Coluna a analisar (ex.: 'milhar', 'grupo').
    janelas : list[int]
        Tamanhos das janelas. Padrão: [10, 30, 50, 100].

    Retorna
    -------
    DataFrame com uma linha por valor e colunas:
    valor, frequencia_total, atraso, recencia_<janela>...
    """

    if janelas is None:
        janelas = [10, 30, 50, 100]

    valores = df[coluna].astype(str).tolist()
    total = len(valores)

    # Universo de valores = todos os que já apareceram
    universo = sorted(set(valores))

    # --- Frequência total ---
    freq = pd.Series(valores).value_counts()

    # --- Atraso (última ocorrência) ---
    ultimo_indice = {}
    for i, v in enumerate(valores):
        ultimo_indice[v] = i
    atraso = {v: total - 1 - i for v, i in ultimo_indice.items()}

    # --- Recência por janela ---
    rec = {}
    for janela in janelas:
        if janela > total:
            continue
        recentes = valores[-janela:]
        cont = pd.Series(recentes).value_counts()
        rec[janela] = cont

    # --- Montar tabela ---
    linhas = []
    for v in universo:
        linha = {
            coluna: v,
            "frequencia_total": int(freq.get(v, 0)),
            "atraso": int(atraso.get(v, 0)),
        }
        for janela in janelas:
            if janela in rec:
                linha[f"recencia_{janela}"] = int(rec[janela].get(v, 0))
        linhas.append(linha)

    return pd.DataFrame(linhas).reset_index(drop=True)

def tabela_analise_por_posicao(
    df,
    coluna="milhar",
    premios_por_concurso=5,
    janelas=None,
):
    """
    Versão da tabela_analise segmentada por prêmio.
    Retorna um DataFrame com uma linha por (valor, premio).
    """

    from motor.posicao import adicionar_posicao

    if janelas is None:
        janelas = [5, 10]

    df = adicionar_posicao(
        df,
        premios_por_concurso=premios_por_concurso,
    )

    resultados = []

    for premio in range(1, premios_por_concurso + 1):
        sub = df[df["premio"] == premio].copy()

        if sub.empty:
            continue

        # Reaproveita a função original, mas com um df já filtrado
        tabela = tabela_analise(sub, coluna, janelas=janelas)
        tabela["premio"] = premio

        resultados.append(tabela)

    if not resultados:
        return pd.DataFrame()

    return (
        pd.concat(resultados, ignore_index=True)
        .sort_values(["premio", coluna])
        .reset_index(drop=True)
    )
