

def frequencia_grupos(df):
    return (
        df.groupby(["grupo", "bicho"])
        .size()
        .reset_index(name="ocorrencias")
        .sort_values("ocorrencias", ascending=False)
    )


def frequencia_dezenas(df):
    return (
        df.groupby("dezena")
        .size()
        .reset_index(name="ocorrencias")
        .sort_values("ocorrencias", ascending=False)
    )


def frequencia_centenas(df):
    return (
        df.groupby("centena")
        .size()
        .reset_index(name="ocorrencias")
        .sort_values("ocorrencias", ascending=False)
    )


def frequencia_milhares(df):
    return (
        df.groupby("milhar")
        .size()
        .reset_index(name="ocorrencias")
        .sort_values("ocorrencias", ascending=False)
    )
