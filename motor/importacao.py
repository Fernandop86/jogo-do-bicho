import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def importar_csv_largo(caminho):
    """
    Importa um CSV no formato largo do arquivo
    jogo_do_bicho_YYYY.csv (PTM, PT, PTV, ...).

    Retorna um DataFrame no formato longo:
    data, modalidade, horario, premio, milhar,
    centena, grupo, bicho, dezena
    """
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")

    df = pd.read_csv(caminho, dtype=str, encoding="utf-8")

    # Validar colunas essenciais
    colunas_requeridas = {"csvData", "Tipo"}
    if not colunas_requeridas.issubset(df.columns):
        faltando = colunas_requeridas - set(df.columns)
        raise ValueError(f"Colunas ausentes no CSV: {faltando}")

    # Preparar dados: preencher NaN com string vazia
    df = df.fillna("")

    registros_lista = []

    # Uma passada por prêmio (1 a 5)
    for premio_idx in range(1, 6):
        milhar = df[f"Premio_{premio_idx}"].str.strip()
        centena = df[f"Centena_{premio_idx}"].str.strip()
        grupo = df[f"Grupo_{premio_idx}"].str.strip()
        bicho = df[f"Bicho_{premio_idx}"].str.strip()

        # Filtrar linhas válidas (milhar não vazio)
        mascara_valido = milhar.astype(bool)

        if mascara_valido.any():
            subset = pd.DataFrame({
                "data": df.loc[mascara_valido, "csvData"],
                "modalidade": df.loc[mascara_valido, "Tipo"],
                "horario": df.loc[mascara_valido, "Horario"].fillna(""),
                "premio": premio_idx,
                "milhar": milhar[mascara_valido].str.zfill(4),
                "centena": centena[mascara_valido].apply(
                    lambda x: x.zfill(3) if x else ""
                ),
                "grupo": grupo[mascara_valido].apply(
                    lambda x: x.zfill(2) if x else ""
                ),
                "bicho": bicho[mascara_valido],
            })
            registros_lista.append(subset)

    if not registros_lista:
        logger.warning(f"Nenhum registro valido encontrado em {caminho}")
        return pd.DataFrame(columns=[
            "data", "modalidade", "horario", "premio", "milhar",
            "centena", "grupo", "bicho", "dezena",
        ])

    resultado = pd.concat(registros_lista, ignore_index=True)

    # Criar coluna dezena (últimos 2 dígitos do milhar)
    resultado["dezena"] = resultado["milhar"].str[-2:]

    logger.info(f"Importados {len(resultado)} registros de {caminho}")
    return resultado


def importar_pasta(pasta):
    """
    Importa TODOS os arquivos jogo_do_bicho_*.csv
    de uma pasta e concatena em um único DataFrame.
    """
    pasta = Path(pasta)
    arquivos = sorted(pasta.glob("jogo_do_bicho_*.csv"))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo encontrado em {pasta}")

    partes = []
    for arq in arquivos:
        logger.info(f"Importando: {arq.name}")
        partes.append(importar_csv_largo(arq))

    resultado = pd.concat(partes, ignore_index=True)
    return resultado