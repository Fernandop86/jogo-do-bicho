"""
Gerador de carteira de apostas com R$ 5.
Divide o capital em multiplas apostas complementares.
"""
from motor.importacao import importar_csv_largo

CAMINHO = r"D:\Raspagem de Dados jogo do bicho\dados\jogo_do_bicho_2024.csv"

df = importar_csv_largo(CAMINHO)


def plano_A_maxima_cobertura():
    """Foco em retorno frequente (grupo + dezena + centena)."""
    return [
        {"tipo": "grupo",   "valor": 1.00, "numero": "01"},
        {"tipo": "grupo",   "valor": 1.00, "numero": "08"},
        {"tipo": "dezena",  "valor": 1.00, "numero": "91"},
        {"tipo": "dezena",  "valor": 1.00, "numero": "63"},
        {"tipo": "centena", "valor": 1.00, "numero": "691"},
    ]


def plano_B_busca_milhar():
    """5 milhares, foco em alto retorno (1 em 2.000)."""
    return [
        {"tipo": "milhar", "valor": 1.00, "numero": "8797"},
        {"tipo": "milhar", "valor": 1.00, "numero": "2900"},
        {"tipo": "milhar", "valor": 1.00, "numero": "3932"},
        {"tipo": "milhar", "valor": 1.00, "numero": "1704"},
        {"tipo": "milhar", "valor": 1.00, "numero": "1814"},
    ]


def plano_C_milhar_centena_grupo():
    """O unico que passa de R$ 5.000 se acertar tudo."""
    return [
        {"tipo": "milhar",  "valor": 2.00, "numero": "8797"},
        {"tipo": "centena", "valor": 1.00, "numero": "691"},
        {"tipo": "grupo",   "valor": 1.00, "numero": "01"},
        {"tipo": "dezena",  "valor": 1.00, "numero": "91"},
    ]


def imprimir_plano(nome, plano):
    print()
    print("=" * 60)
    print(f"PLANO {nome}")
    print("=" * 60)
    total = 0
    for aposta in plano:
        total += aposta["valor"]
        print(f"  R$ {aposta['valor']:.2f}  {aposta['tipo']:>8}  {aposta['numero']}")
    print(f"  {'-' * 40}")
    print(f"  TOTAL: R$ {total:.2f}")


if __name__ == "__main__":
    imprimir_plano("A — MAXIMA COBERTURA", plano_A_maxima_cobertura())
    imprimir_plano("B — BUSCA MILHAR", plano_B_busca_milhar())
    imprimir_plano("C — MIX (milhar+centena+grupo+dezena)", plano_C_milhar_centena_grupo())
