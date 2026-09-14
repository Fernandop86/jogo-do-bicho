from motor.importacao import importar_csv_largo
from motor.processamento import processar_numero

df = importar_csv_largo(r"D:\Raspagem de Dados jogo do bicho\dados\jogo_do_bicho_2024.csv")

# Pega uma amostra
amostra = df.sample(20, random_state=42)

print("=" * 70)
print("VALIDAÇÃO: grupo do CSV vs grupo calculado por nós")
print("=" * 70)
print(f"{'milhar':>8} {'grupo_csv':>10} {'grupo_nosso':>12} {'bicho_csv':>15} {'bicho_nosso':>15} {'OK?':>5}")
print("-" * 70)

divergencias = 0
for _, linha in amostra.iterrows():
    milhar = linha["milhar"]
    g_csv = linha["grupo_csv"]
    b_csv = linha["bicho_csv"]

    try:
        r = processar_numero(milhar)
        g_nosso = str(r["grupo"]).zfill(2)
        b_nosso = r["bicho"]
    except Exception as e:
        g_nosso = "ERRO"
        b_nosso = str(e)

    ok = "SIM" if (g_csv == g_nosso and b_csv == b_nosso) else "NAO"
    if ok == "NAO":
        divergencias += 1

    print(f"{milhar:>8} {g_csv:>10} {g_nosso:>12} {b_csv:>15} {b_nosso:>15} {ok:>5}")

print()
print(f"Divergências: {divergencias}/20")
