import pandas as pd

from motor.importacao import importar_csv_largo
from motor.dashboard import renderizar_dashboard


CAMINHO = r"D:\Raspagem de Dados jogo do bicho\dados\jogo_do_bicho_2024.csv"

print("Carregando histórico...")
df = importar_csv_largo(CAMINHO)
print(f"Carregados {len(df)} prêmios.")
print()


for coluna in ["grupo", "dezena", "centena"]:
    renderizar_dashboard(
        df,
        coluna=coluna,
        janelas=(10, 30, 50, 100),
        premios_por_concurso=5,
        coluna_recencia="recencia_100",
        top_n=10,
    )