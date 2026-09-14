import sys
import pandas as pd

from motor.processamento import processar_numero
from motor.dashboard import renderizar_dashboard
from motor.ia_analista import Analista, responder


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


numeros = [
    "4187", "7914", "1203", "8562", "0325",
    "2501", "4187", "7914", "4187", "8562",
    "0325", "4187", "1203", "8562", "7914",
    "4187", "2501", "8562", "0325", "7914",
    "4187", "7914", "1203", "8562", "0325",
    "4187", "2501", "8562", "0325", "7914",
]


dados = [processar_numero(n) for n in numeros]
df = pd.DataFrame(dados)


if len(sys.argv) > 1 and sys.argv[1] == "ia":
    a = Analista(df, premios_por_concurso=5, coluna_recencia="recencia_10")

    print("=" * 60)
    print("IA ANALISTA — MODO INTERATIVO")
    print("Digite 'ajuda' para ver os comandos. 'sair' para encerrar.")
    print("=" * 60)
    print()

    while True:
        try:
            texto = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not texto:
            continue

        resposta = responder(a, texto)
        if resposta is None:
            print("Até a próxima.")
            break

        print()
        print(resposta)
        print()
else:
    coluna = sys.argv[1] if len(sys.argv) > 1 else "milhar"
    renderizar_dashboard(
        df,
        coluna=coluna,
        janelas=(5, 10),
        premios_por_concurso=5,
        coluna_recencia="recencia_10",
        top_n=10,
    )
