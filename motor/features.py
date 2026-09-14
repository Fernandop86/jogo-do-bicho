import pandas as pd

from motor.padroes import (
    repeticoes_entre_concursos,
    repeticoes_no_mesmo_concurso,
)


def construir_features(df, coluna="milhar", premios_por_concurso=5):
    """
    Constrói, por valor, features adicionais:
    - repeticoes_consecutivas
    - repeticoes_mesmo_concurso
    - premio_medio
    """

    df = df.copy().reset_index(drop=True)
    df["concurso"] = df.index // premios_por_concurso
    df["premio"] = (df.index % premios_por_concurso) + 1

    # Garante que a coluna alvo é string para consistência
    df[coluna] = df[coluna].astype(str)

    universo = sorted(df[coluna].unique())

    # --- repetições entre concursos ---
    rep_cons = repeticoes_entre_concursos(
        df, coluna=coluna, premios_por_concurso=premios_por_concurso
    )
    cont_rep_cons = {v: 0 for v in universo}
    if not rep_cons.empty:
        for v, c in rep_cons[coluna].astype(str).value_counts().items():
            cont_rep_cons[v] = int(c)

    # --- repetições no mesmo concurso ---
    rep_mesmo = repeticoes_no_mesmo_concurso(
        df, coluna=coluna, premios_por_concurso=premios_por_concurso
    )
    cont_rep_mesmo = {v: 0 for v in universo}
    if not rep_mesmo.empty:
        agrupado = rep_mesmo.groupby(coluna)["vezes"].sum()
        for v, c in agrupado.items():
            cont_rep_mesmo[str(v)] = int(c)

    # --- prêmio médio ---
    df["premio"] = df["premio"].astype(float)
    premio_medio_series = df.groupby(coluna)["premio"].mean()
    premio_medio = {str(k): float(v) for k, v in premio_medio_series.items()}

    linhas = []
    for v in universo:
        linhas.append({
            coluna: v,
            "repeticoes_consecutivas": cont_rep_cons.get(v, 0),
            "repeticoes_mesmo_concurso": cont_rep_mesmo.get(v, 0),
            "premio_medio": premio_medio.get(v, 0.0),
        })

    return pd.DataFrame(linhas)
