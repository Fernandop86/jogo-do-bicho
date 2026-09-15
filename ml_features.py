"""
Extrai features para Machine Learning a partir dos dados do Jogo do Bicho.

Uso:
    python ml_features.py --alvo grupo
    python ml_features.py --alvo dezena
    python ml_features.py --alvo centena
    python ml_features.py --alvo milhar
"""
import argparse
from pathlib import Path

import pandas as pd

from motor.importacao import importar_csv_largo


ALVOS_VALIDOS = ["grupo", "dezena", "centena", "milhar"]


def encontrar_csvs():
    pastas = [
        Path(__file__).parent / "dados",
        Path("dados"),
        Path(r"D:\Jogo do bicho\dados"),
    ]
    for pasta in pastas:
        if pasta.exists():
            arquivos = sorted(pasta.glob("jogo_do_bicho_*.csv"))
            if arquivos:
                return [str(a) for a in arquivos]
    raise FileNotFoundError("Nenhum CSV encontrado")


def carregar_tudo():
    partes = [importar_csv_largo(c) for c in encontrar_csvs()]
    df = pd.concat(partes, ignore_index=True)
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"])
    df = df.sort_values(["data", "modalidade", "premio"]).reset_index(drop=True)
    return df


def extrair_features_por_sorteio(df, coluna="grupo"):
    """
    Para cada sorteio, extrai features do historico ANTERIOR.

    Features:
    - frequencia_acumulada
    - atraso
    - recencia_10 / 30 / 100
    - foi_ultimo
    """
    valores = df[coluna].astype(str).tolist()
    datas = df["data"].tolist()
    modalidades = df["modalidade"].tolist()
    premios = df["premio"].tolist()

    ultimo_indice = {}
    frequencia = {}
    registros = []

    for i, valor in enumerate(valores):
        freq = frequencia.get(valor, 0)
        atraso = i - ultimo_indice[valor] if valor in ultimo_indice else i

        rec_10 = sum(1 for v in valores[max(0, i-10):i] if v == valor)
        rec_30 = sum(1 for v in valores[max(0, i-30):i] if v == valor)
        rec_100 = sum(1 for v in valores[max(0, i-100):i] if v == valor)

        foi_ultimo = 1 if i > 0 and valores[i-1] == valor else 0

        registros.append({
            "data": datas[i],
            "modalidade": modalidades[i],
            "premio": premios[i],
            "target": valor,
            "frequencia_acumulada": freq,
            "atraso": atraso,
            "recencia_10": rec_10,
            "recencia_30": rec_30,
            "recencia_100": rec_100,
            "foi_ultimo": foi_ultimo,
        })

        frequencia[valor] = freq + 1
        ultimo_indice[valor] = i

    return pd.DataFrame(registros)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alvo", default="grupo", choices=ALVOS_VALIDOS)
    args = parser.parse_args()

    print("=" * 70)
    print(f"EXTRAINDO FEATURES - ALVO: {args.alvo.upper()}")
    print("=" * 70)

    print("\nCarregando dados...")
    df = carregar_tudo()
    print(f"  {len(df):,} premios")

    print(f"\nExtraindo features para {args.alvo}...")
    features = extrair_features_por_sorteio(df, args.alvo)
    n_classes = features["target"].nunique()
    print(f"  {len(features):,} linhas x {len(features.columns)} colunas")
    print(f"  Classes distintas: {n_classes}")

    saida = f"ml_features_{args.alvo}.csv"
    features.to_csv(saida, index=False)
    print(f"\nOK: {saida} salvo")


if __name__ == "__main__":
    main()
