"""
Testa se features exoticas adicionam sinal preditivo.

Compara:
- Modelo base (features historicas)
- Modelo com exoticas (historico + dia/mes/modalidade)
"""
import argparse
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import TimeSeriesSplit

warnings.filterwarnings("ignore")

FEATURES_BASE = [
    "frequencia_acumulada",
    "atraso",
    "recencia_10",
    "recencia_30",
]

FEATURES_EXOTICAS = FEATURES_BASE + [
    "dia_semana",
    "mes",
    "modalidade_codigo",
    
]


def avaliar(X, y, nome, n_splits=5):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    acuracias = []

    rf = RandomForestClassifier(
        n_estimators=30,
        max_depth=8,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
    )

    for idx_train, idx_test in tscv.split(X):
        X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
        y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]

        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)
        acuracias.append(accuracy_score(y_test, y_pred))

    return {
        "nome": nome,
        "acuracia_media": float(np.mean(acuracias)),
        "acuracia_std": float(np.std(acuracias)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alvo", default="grupo", choices=["grupo", "dezena"])
    args = parser.parse_args()

    print("=" * 70)
    print(f"FEATURES EXOTICAS - ALVO: {args.alvo.upper()}")
    print("=" * 70)

    df = pd.read_csv(f"ml_features_exoticas_{args.alvo}.csv")
    df["target_int"] = df["target"].astype(str).astype("category").cat.codes

    y = df["target_int"]
    n_classes = y.nunique()

    print(f"\n  {len(df):,} linhas")
    print(f"  Classes: {n_classes}")
    print(f"  Esperado por azar: {100/n_classes:.4f}%")

    # Modelo base
    print("\n[1/2] Modelo BASE (features historicas)...")
    res_base = avaliar(df[FEATURES_BASE], y, "Base")
    print(f"  Acuracia: {res_base['acuracia_media']*100:.4f}%")

    # Modelo com exoticas
    print("\n[2/2] Modelo com EXOTICAS (historico + dia/mes/modalidade)...")
    res_exot = avaliar(df[FEATURES_EXOTICAS], y, "Exoticas")
    print(f"  Acuracia: {res_exot['acuracia_media']*100:.4f}%")

    # Resultado
    print("\n" + "=" * 70)
    print("RESULTADO")
    print("=" * 70)

    diff = res_exot["acuracia_media"] - res_base["acuracia_media"]

    print(f"\n  Base:      {res_base['acuracia_media']*100:.4f}%")
    print(f"  Exoticas:  {res_exot['acuracia_media']*100:.4f}%")
    print(f"  Diferenca: {diff*100:+.4f} p.p.")

    if abs(diff) < 0.005:
        print(f"\n>>> CONCLUSAO: Features exoticas NAO adicionam sinal.")
        print(f">>> A diferenca de {abs(diff)*100:.4f} p.p. e ruido.")
    elif diff > 0:
        print(f"\n>>> Features exoticas MELHORARAM em {diff*100:.4f} p.p.")
        print(f">>> Verificar se e sinal real ou overfitting.")
    else:
        print(f"\n>>> Features exoticas PIORARAM em {abs(diff)*100:.4f} p.p.")
        print(f">>> Overfitting ou ruido.")

    print("=" * 70)


if __name__ == "__main__":
    main()
