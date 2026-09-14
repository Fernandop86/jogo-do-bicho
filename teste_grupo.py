from motor.importacao import importar_csv_largo

df = importar_csv_largo(r"D:\Raspagem de Dados jogo do bicho\dados\jogo_do_bicho_2024.csv")

print("Total de linhas:", len(df))
print()
print("Grupo - contagem:")
print(df["grupo"].value_counts().sort_index().to_string())
print()
print("Soma das contagens:", df["grupo"].value_counts().sum())
print()
print("Grupos únicos:", df["grupo"].nunique())
print()
print("Amostra de valores de grupo:")
print(df["grupo"].head(10).tolist())
