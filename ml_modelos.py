"""
Treina e avalia modelos de ML para prever o proximo resultado.

Uso:
    python ml_modelos.py --alvo grupo
    python ml_modelos.py --alvo dezena
    python ml_modelos.py --alvo centena
    python ml_modelos.py --alvo milhar
"""
import argparse
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import TimeSeriesSplit

warnings.filterwarnings("ignore")

ALVOS_VALIDOS = ["grupo", "dezena", "centena", "milhar"]

FEATURE_COLS = [
    "frequencia_acumulada",
    "atraso",
    "recencia_10",
    "recencia_30",
    "recencia_100",
    "foi_ultimo",
]


def carregar_features(alvo):
    caminho = f"ml_features_{alvo}.csv"
    df = pd.read_csv(caminho)
    df["data"] = pd.to_datetime(df["data"])
    df = df.sort_values(["data", "modalidade", "premio"]).reset_index(drop=True)
    return df


def baseline_aleatorio(y_test, n_classes):
    np.random.seed(42)
    y_pred = np.random.randint(0, n_classes, size=len(y_test))
    return accuracy_score(y_test, y_pred)


def baseline_mais_frequente(y_test, y_train):
    moda = pd.Series(y_train).mode().iloc[0]
    y_pred = np.full(len(y_test), moda)
    return accuracy_score(y_test, y_pred)


def avaliar_modelo(nome, modelo, X, y, n_splits=5):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    acuracias = []
    log_losses = []

    for idx_train, idx_test in tscv.split(X):
        X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
        y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]

        modelo.fit(X_train, y_train)
        y_pred = modelo.predict(X_test)
        acuracias.append(accuracy_score(y_test, y_pred))

        if hasattr(modelo, "predict_proba"):
            try:
                y_proba = modelo.predict_proba(X_test)
                ll = log_loss(y_test, y_proba, labels=modelo.classes_)
                log_losses.append(ll)
            except Exception:
                pass

    return {
        "nome": nome,
        "acuracia_media": float(np.mean(acuracias)),
        "acuracia_std": float(np.std(acuracias)),
        "log_loss_medio": float(np.mean(log_losses)) if log_losses else None,
    }


def avaliar_baselines(X, y, n_classes, n_splits=5):
    tscv = TimeSeriesSplit(n_splits=n_splits)
    acc_aleatorio = []
    acc_mais_freq = []

    for idx_train, idx_test in tscv.split(X):
        y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]
        acc_aleatorio.append(baseline_aleatorio(y_test, n_classes))
        acc_mais_freq.append(baseline_mais_frequente(y_test, y_train))

    return {
        "aleatorio": {
            "acuracia_media": float(np.mean(acc_aleatorio)),
            "acuracia_std": float(np.std(acc_aleatorio)),
        },
        "mais_frequente": {
            "acuracia_media": float(np.mean(acc_mais_freq)),
            "acuracia_std": float(np.std(acc_mais_freq)),
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alvo", default="grupo", choices=ALVOS_VALIDOS)
    args = parser.parse_args()
    alvo = args.alvo

    print("=" * 70)
    print(f"EXPERIMENTO ML - ALVO: {alvo.upper()}")
    print("=" * 70)

    df = carregar_features(alvo)
    print(f"\n  {len(df):,} linhas carregadas")

    df["target_int"] = (
        df["target"].astype(str).astype("category").cat.codes
    )

    X = df[FEATURE_COLS]
    y = df["target_int"]
    n_classes = y.nunique()

    print(f"  Features: {FEATURE_COLS}")
    print(f"  Classes distintas: {n_classes}")
    print(f"  Esperado por azar: {100/n_classes:.4f}%")

    print("\n" + "=" * 70)
    print("BASELINES")
    print("=" * 70)

    baselines = avaliar_baselines(X, y, n_classes)
    acc_rand = baselines["aleatorio"]["acuracia_media"]
    acc_freq = baselines["mais_frequente"]["acuracia_media"]

    print(f"\n  Aleatorio:       {acc_rand*100:.4f}%  (+- {baselines['aleatorio']['acuracia_std']*100:.4f}%)")
    print(f"  Mais frequente:  {acc_freq*100:.4f}%  (+- {baselines['mais_frequente']['acuracia_std']*100:.4f}%)")

    print("\n" + "=" * 70)
    print("MODELOS")
    print("=" * 70)

    resultados = []

    print("\n[1/2] Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=20,
        max_depth=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    res_rf = avaliar_modelo("Random Forest", rf, X, y)
    resultados.append(res_rf)
    print(f"  Acuracia: {res_rf['acuracia_media']*100:.4f}%")

    print("\n[2/2] Regressao Logistica...")
    lr = LogisticRegression(max_iter=500, random_state=42, n_jobs=-1)
    res_lr = avaliar_modelo("Regressao Logistica", lr, X, y)
    resultados.append(res_lr)
    print(f"  Acuracia: {res_lr['acuracia_media']*100:.4f}%")

    print("\n" + "=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)

    print(f"\n{'Modelo':<25} {'Acuracia':>12} {'vs Aleatorio':>15}")
    print("-" * 70)
    print(f"{'Aleatorio':<25} {acc_rand*100:>11.4f}% {'(baseline)':>15}")
    print(f"{'Mais frequente':<25} {acc_freq*100:>11.4f}% {(acc_freq-acc_rand)*100:>+14.4f}%")

    for r in resultados:
        diff = r["acuracia_media"] - acc_rand
        sinal = "+" if diff > 0 else ""
        print(f"{r['nome']:<25} {r['acuracia_media']*100:>11.4f}% {sinal}{diff*100:>13.4f}%")

    print("\n" + "=" * 70)
    print("CONCLUSAO")
    print("=" * 70)

    melhor = max(resultados, key=lambda x: x["acuracia_media"])
    diff = melhor["acuracia_media"] - acc_rand

    print(f"\nMelhor modelo: {melhor['nome']} ({melhor['acuracia_media']*100:.4f}%)")
    print(f"Baseline aleatorio: {acc_rand*100:.4f}%")
    print(f"Diferenca: {diff*100:+.4f} pontos percentuais")

    if diff <= 0.01:
        print(f"\n>>> CONCLUSAO: A ML NAO bate o baseline aleatorio.")
        print(f">>> Alvo '{alvo}' e estatisticamente uniforme. Sem padrao exploravel.")
    else:
        print(f"\n>>> ATENCAO: A ML bateu o aleatorio por {diff*100:+.4f} p.p.")
        print(f">>> Verificar se ha vazamento ou se e ruido estatistico.")

    print("=" * 70)


if __name__ == "__main__":
    main()
