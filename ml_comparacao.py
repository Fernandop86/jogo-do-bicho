"""
Comparacao final dos experimentos de ML por alvo.

Uso:
    python ml_comparacao.py
"""
import json
from pathlib import Path


# Resultados registrados manualmente (baseados nas execucoes anteriores)
RESULTADOS = {
    "grupo": {
        "classes": 25,
        "esperado_azar": 4.0000,
        "aleatorio": 3.7400,
        "mais_frequente": 3.9700,
        "random_forest": 3.8900,
        "regressao_logistica": 4.0400,
        "melhor": "Regressao Logistica",
        "melhor_acc": 4.0400,
        "diff_pp": 0.3000,
    },
    "dezena": {
        "classes": 100,
        "esperado_azar": 1.0000,
        "aleatorio": 0.9631,
        "mais_frequente": 0.9836,
        "random_forest": 0.9563,
        "regressao_logistica": 1.0861,
        "melhor": "Regressao Logistica",
        "melhor_acc": 1.0861,
        "diff_pp": 0.1230,
    },
    "centena": {
        "classes": 1000,
        "esperado_azar": 0.1000,
        "aleatorio": 0.0820,
        "mais_frequente": 0.1025,
        "random_forest": 0.0888,
        "regressao_logistica": 0.0546,
        "melhor": "Random Forest",
        "melhor_acc": 0.0888,
        "diff_pp": 0.0068,
    },
    "milhar": {
        "classes": 10000,
        "esperado_azar": 0.0100,
        "aleatorio": None,  # nao calculado
        "mais_frequente": None,
        "random_forest": 0.0068,
        "regressao_logistica": None,  # cancelado
        "melhor": "Random Forest",
        "melhor_acc": 0.0068,
        "diff_pp": -0.0032,
    },
}


def imprimir_tabela():
    print("=" * 100)
    print("COMPARACAO FINAL - EXPERIMENTOS DE ML POR ALVO")
    print("=" * 100)
    print()
    print(f"{'Alvo':<12} {'Classes':>10} {'Azar':>10} {'Aleatorio':>12} "
          f"{'RF':>10} {'RL':>10} {'Melhor':>22} {'Diff':>10}")
    print("-" * 100)

    for alvo, r in RESULTADOS.items():
        aleat = f"{r['aleatorio']:.4f}%" if r['aleatorio'] is not None else "—"
        rf = f"{r['random_forest']:.4f}%" if r['random_forest'] is not None else "—"
        rl = f"{r['regressao_logistica']:.4f}%" if r['regressao_logistica'] is not None else "—"
        diff = f"{r['diff_pp']:+.4f}%"

        print(f"{alvo:<12} {r['classes']:>10,} {r['esperado_azar']:>9.4f}% "
              f"{aleat:>12} {rf:>10} {rl:>10} {r['melhor']:>22} {diff:>10}")

    print()


def imprimir_conclusao():
    print("=" * 100)
    print("CONCLUSAO")
    print("=" * 100)
    print()
    print("  Em TODOS os alvos testados, a Machine Learning NAO bateu")
    print("  o baseline aleatorio de forma estatisticamente significativa.")
    print()
    print("  Diferencas observadas (p.p.):")
    print()
    for alvo, r in RESULTADOS.items():
        if r['diff_pp'] > 0:
            sinal = "acima"
        else:
            sinal = "abaixo"
        print(f"    {alvo:<12} -> {abs(r['diff_pp']):.4f} p.p. {sinal} do aleatorio")
    print()
    print("  Interpretacao:")
    print("    - Diferencas < 0.5 p.p. sao ruido estatistico")
    print("    - Nenhum alvo mostrou sinal exploravel")
    print("    - O jogo e estatisticamente uniforme em todos os niveis")
    print()
    print("  Conclusao final:")
    print("    >>> Nao ha padrao preditivo nos dados analisados.")
    print("    >>> A ML confirma o que os testes chi2 ja mostravam.")
    print()


def salvar_json():
    saida = "ml_comparacao.json"
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(RESULTADOS, f, indent=2, ensure_ascii=False)
    print(f"OK: {saida} salvo")
    print()


def main():
    imprimir_tabela()
    imprimir_conclusao()
    salvar_json()


if __name__ == "__main__":
    main()
