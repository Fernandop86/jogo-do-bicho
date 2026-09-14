import pandas as pd


def repeticoes_entre_concursos(
    df,
    coluna="milhar",
    premios_por_concurso=5
):
    """
    Detecta milhares (ou grupos/dezenas) que aparecem
    em dois concursos CONSECUTIVOS.

    Retorna DataFrame com pares (valor, concurso_a, concurso_b).
    """

    df = df.copy().reset_index(drop=True)
    df["concurso"] = df.index // premios_por_concurso

    # valores por concurso
    por_concurso = (
        df.groupby("concurso")[coluna]
        .apply(lambda s: set(s.astype(str)))
        .sort_index()
    )

    registros = []

    concursos = por_concurso.index.tolist()

    for i in range(len(concursos) - 1):
        a = concursos[i]
        b = concursos[i + 1]

        repetidos = por_concurso[a] & por_concurso[b]

        for v in repetidos:
            registros.append({
                coluna: v,
                "concurso_a": a,
                "concurso_b": b,
            })

    return pd.DataFrame(registros)


def repeticoes_no_mesmo_concurso(
    df,
    coluna="milhar",
    premios_por_concurso=5
):
    """
    Detecta valores que aparecem mais de uma vez
    DENTRO do mesmo concurso (em prêmios diferentes).
    """

    df = df.copy().reset_index(drop=True)
    df["concurso"] = df.index // premios_por_concurso
    df["premio"] = (df.index % premios_por_concurso) + 1

    contagem = (
        df.groupby(["concurso", coluna])
        .size()
        .reset_index(name="vezes")
    )

    return contagem[contagem["vezes"] > 1].reset_index(drop=True)


def vizinhos_de_grupo(df, premios_por_concurso=5):
    """
    Para cada valor (grupo) em um concurso, verifica se o
    'grupo vizinho' (±1, com wraparound 1..25) aparece
    no MESMO concurso.
    """

    df = df.copy().reset_index(drop=True)
    df["concurso"] = df.index // premios_por_concurso

    registros = []

    for concurso, sub in df.groupby("concurso"):
        grupos = sub["grupo"].astype(int).tolist()
        grupos_set = set(grupos)

        for g in grupos:
            for delta in (-1, 1):
                vizinho = ((g - 1 + delta) % 25) + 1
                if vizinho in grupos_set:
                    registros.append({
                        "concurso": concurso,
                        "grupo": g,
                        "vizinho": vizinho,
                        "delta": delta,
                    })

    if not registros:
        return pd.DataFrame(columns=["concurso", "grupo", "vizinho", "delta"])

    return pd.DataFrame(registros)
