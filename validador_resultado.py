"""
Valida uma carteira de apostas contra um resultado real.
Uso: python validador_resultado.py <milhar_sorteado>
Ex.: python validador_resultado.py 8797
"""
import sys
from gerador_aposta import (
    plano_A_maxima_cobertura,
    plano_B_busca_milhar,
    plano_C_milhar_centena_grupo,
)

PREMIOS = {
    "grupo":   18.0,
    "dezena":  60.0,
    "centena": 600.0,
    "milhar":  4000.0,
}


def validar(plano, milhar):
    milhar = milhar.zfill(4)
    centena = milhar[-3:]
    dezena = milhar[-2:]

    print(f"Milhar sorteado: {milhar}")
    print(f"Centena: {centena}  |  Dezena: {dezena}")
    print()

    ganho_total = 0.0
    for aposta in plano:
        tipo = aposta["tipo"]
        alvo = aposta["numero"]
        valor = aposta["valor"]

        acertou = (
            (tipo == "milhar" and milhar == alvo) or
            (tipo == "centena" and centena == alvo) or
            (tipo == "dezena" and dezena == alvo)
        )

        if acertou:
            ganho = valor * PREMIOS[tipo]
            ganho_total += ganho
            print(f"  [OK] {tipo:>8} {alvo}  ->  R$ {ganho:,.2f}")
        else:
            print(f"  [--] {tipo:>8} {alvo}")

    print()
    print(f"GANHO TOTAL: R$ {ganho_total:,.2f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python validador_resultado.py <milhar>")
        sys.exit(1)

    milhar = sys.argv[1]
    print("=" * 60)
    print("PLANO A — MAXIMA COBERTURA")
    print("=" * 60)
    validar(plano_A_maxima_cobertura(), milhar)
    print()
    print("=" * 60)
    print("PLANO B — BUSCA MILHAR")
    print("=" * 60)
    validar(plano_B_busca_milhar(), milhar)
    print()
    print("=" * 60)
    print("PLANO C — MIX")
    print("=" * 60)
    validar(plano_C_milhar_centena_grupo(), milhar)
