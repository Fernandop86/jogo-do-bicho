import pandas as pd


def recencia(df, coluna, janelas=None):
    """
    Calcula quantas vezes cada valor apareceu
    nas últimas N ocorrências, para cada janela.

    Parâmetros
    ----------
    df : DataFrame
    coluna : str
        Coluna a analisar (ex.: 'milhar', 'grupo', 'dezena').
    janelas : list[int]
        Tamanhos das janelas recentes. Padrão: [10, 20, 30, 50, 100].

    Retorna
    -------
    DataFrame com colunas: valor, janela, ocorrencias
    """

    if janelas is None:
        janelas = [10, 20, 30, 50, 100]

    valores = df[coluna].astype(str).tolist()
    total = len(valores)

    registros = []

    for janela in janelas:
        if janela > total:
            continue

        recentes = valores[-janela:]
        contagem = pd.Series(recentes).value_counts()

        for valor, ocorrencias in contagem.items():
            registros.append({
                coluna: valor,
                "janela": janela,
                "ocorrencias": int(ocorrencias)
            })

    return (
        pd.DataFrame(registros)
        .sort_values([coluna, "janela"])
        .reset_index(drop=True)
    )
