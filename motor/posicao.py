

def adicionar_posicao(df, premios_por_concurso=5, concurso_inicial=1000):
    """
    Adiciona colunas 'concurso' e 'premio' a um DataFrame
    que já tenha a coluna 'milhar' (ou similar).

    Assume que cada bloco de N linhas consecutivas
    forma um concurso, com prêmios de 1 a N.

    Parâmetros
    ----------
    df : DataFrame
        Saída do processamento (colunas milhar, centena, dezena, grupo, bicho).
    premios_por_concurso : int
        Quantos prêmios por concurso (padrão 5).
    concurso_inicial : int
        Número do primeiro concurso (só para rótulo).

    Retorna
    -------
    DataFrame com colunas extras 'concurso' e 'premio'.
    """

    df = df.copy().reset_index(drop=True)

    total = len(df)
    concursos = []
    premios = []

    for i in range(total):
        idx_concurso = i // premios_por_concurso
        premio = (i % premios_por_concurso) + 1

        concursos.append(concurso_inicial + idx_concurso)
        premios.append(premio)

    df["concurso"] = concursos
    df["premio"] = premios

    return df
