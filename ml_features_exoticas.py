"""
Features exoticas para ML - testar se ha sinal temporal.

Features:
- dia_semana (0-6)
- mes (1-12)
- modalidade_codigo (0-N)
- par_impar (0=par, 1=impar)
"""
import argparse
from pathlib import Path

import pandas as pd

from motor.importacao import importar_csv_largo


ALVOS_VALIDOS = ["grupo", "dezena"]


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


def extrair_features_exoticas(df, coluna="grupo"):
    """
    Extrai features temporais + features historicas.
    """
    valores = df[coluna].astype(str).tolist()
    datas = df["data"].tolist()
    modalidades = df["modalidade"].tolist()

    # Codificar modalidade
    modalidades_unicas = sorted(df["modalidade"].unique().tolist())
    modalidade_map = {m: i for i, m in enumerate(modalidades_unicas)}

    ultimo_indice = {}
    frequencia = {}
    registros = []

    for i, valor in enumerate(valores):
        freq = frequencia.get(valor, 0)
        atraso = i - ultimo_indice[valor] if valor in ultimo_indice else i

        rec_10 = sum(1 for v in valores[max(0, i-10):i] if v == valor)
        rec_30 = sum(1 for v in valores[max(0, i-30):i] if v == valor)

        data = pd.Timestamp(datas[i])
        dia_semana = data.weekday()
        mes = data.month

        # Par ou impar
        try:
            valor_int = int(valor)
            par_impar = valor_int % 2
        except ValueError:
            par_impar = -1

        registros.append({
            "data": datas[i],
            "modalidade": modalidades[i],
            "premio": df["premio"].iloc[i],
            "target": valor,
            # Features historicas
            "frequencia_acumulada": freq,
            "atraso": atraso,
            "recencia_10": rec_10,
            "recencia_30": rec_30,
            # Features exoticas
            "dia_semana": dia_semana,
            "mes": mes,
            "modalidade_codigo": modalidade_map.get(modalidades[i], -1),
            "par_impar": par_impar,
        })

        frequencia[valor] = freq + 1
        ultimo_indice[valor] = i

    return pd.DataFrame(registros)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alvo", default="grupo", choices=ALVOS_VALIDOS)
    args = parser.parse_args()

    print("=" * 70)
    print(f"FEATURES EXOTICAS - ALVO: {args.alvo.upper()}")
    print("=" * 70)

    print("\nCarregando dados...")
    df = carregar_tudo()
    print(f"  {len(df):,} premios")

    print(f"\nExtraindo features exoticas para {args.alvo}...")
    features = extrair_features_exoticas(df, args.alvo)
    print(f"  {len(features):,} linhas x {len(features.columns)} colunas")
    print(f"  Colunas: {list(features.columns)}")

    saida = f"ml_features_exoticas_{args.alvo}.csv"
    features.to_csv(saida, index=False)
    print(f"\nOK: {saida} salvo")


if __name__ == "__main__":
    main()
