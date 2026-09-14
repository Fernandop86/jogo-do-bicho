from motor.importacao import importar_csv_largo

df = importar_csv_largo(r"D:\Raspagem de Dados jogo do bicho\dados\jogo_do_bicho_2024.csv")

print("Colunas retornadas pelo importacao.py:")
print(list(df.columns))
print()
print("Primeiras 3 linhas:")
print(df.head(3).to_string(index=False))
