import pandas as pd


def calcular_atraso(df, coluna):
    """
    Calcula quantos resultados se passaram desde
    a última ocorrência de cada valor.

    O resultado é calculado considerando a ordem
    em que os registros aparecem no DataFrame.
    """

    valores = df[coluna].astype(str).tolist()

    ultimo_indice = {}
    tamanho = len(valores)

    for indice, valor in enumerate(valores):
        ultimo_indice[valor] = indice

    resultado = []

    for valor, indice in ultimo_indice.items():
        atraso = tamanho - 1 - indice

        resultado.append({
            coluna: valor,
            "atraso": atraso
        })

    return (
        pd.DataFrame(resultado)
        .sort_values("atraso", ascending=False)
        .reset_index(drop=True)
    )
