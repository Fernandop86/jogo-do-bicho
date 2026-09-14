"""
Simulador de apostas do Jogo do Bicho.
Testa cada plano contra 10.000 resultados aleatorios.
Mostra: quantas vezes ganhou, quanto ganhou, saldo final.
"""
import random
from motor.importacao import importar_csv_largo
from gerador_aposta import (
    plano_A_maxima_cobertura,
    plano_B_busca_milhar,
    plano_C_milhar_centena_grupo,
)

# Premios medios (aproximados, variam por operador)
PREMIOS = {
    "grupo":   18.0,
    "dezena":  60.0,
    "centena": 600.0,
    "milhar":  4000.0,
}


def simular_aposta(plano, numero_sorteado, premio_por_tipo=PREMIOS):
    """Verifica se a aposta ganhou algo."""
    milhar = numero_sorteado.zfill(4)
    centena = milhar[-3:]
    dezena = milhar[-2:]
    # Grupo nao usado na simulacao (simplificado)

    ganho_total = 0.0
    acertos = []

    for aposta in plano:
        tipo = aposta["tipo"]
        valor = aposta["valor"]
        alvo = aposta["numero"]

        acertou = False
        if tipo == "milhar" and milhar == alvo:
            acertou = True
        elif tipo == "centena" and centena == alvo:
            acertou = True
        elif tipo == "dezena" and dezena == alvo:
            acertou = True

        if acertou:
            ganho = valor * premio_por_tipo[tipo]
            ganho_total += ganho
            acertos.append((tipo, alvo, ganho))

    return ganho_total, acertos


def simular_plano(nome, plano, n_tentativas=10_000, seed=42):
    random.seed(seed)
    custo_total = sum(a["valor"] for a in plano)

    saldo = 0.0
    ganhos = 0
    historico_ganhos = []

    for _ in range(n_tentativas):
        sorteado = f"{random.randint(0, 9999):04d}"
        ganho, acertos = simular_aposta(plano, sorteado)
        saldo += ganho - custo_total
        if ganho > 0:
            ganhos += 1
            historico_ganhos.append(ganho)

    print()
    print("=" * 60)
    print(f"PLANO {nome} — {n_tentativas:,} simulacoes")
    print("=" * 60)
    print(f"  Custo por aposta:      R$ {custo_total:.2f}")
    print(f"  Custo total simulado:  R$ {custo_total * n_tentativas:,.2f}")
    print(f"  Vezes que ganhou algo: {ganhos} ({100*ganhos/n_tentativas:.3f}%)")
    if historico_ganhos:
        print(f"  Maior ganho unico:     R$ {max(historico_ganhos):,.2f}")
        print(f"  Ganho medio quando ganha: R$ {sum(historico_ganhos)/len(historico_ganhos):,.2f}")
    print(f"  SALDO FINAL:           R$ {saldo:,.2f}")
    print(f"  Retorno sobre aposta:  {100 * (saldo + custo_total*n_tentativas) / (custo_total*n_tentativas):.1f}%")

    # Conta quantos R$ 5.000+ ganhou
    acima_5000 = sum(1 for g in historico_ganhos if g >= 5000)
    print(f"  Vezes que passou R$ 5.000: {acima_5000}")


if __name__ == "__main__":
    print("Simulando 10.000 apostas por plano...")
    print("(Isso pode levar 10-20 segundos)")

    simular_plano("A — MAXIMA COBERTURA", plano_A_maxima_cobertura())
    simular_plano("B — BUSCA MILHAR", plano_B_busca_milhar())
    simular_plano("C — MIX", plano_C_milhar_centena_grupo())
