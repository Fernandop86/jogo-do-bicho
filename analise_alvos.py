from motor.importacao import importar_csv_largo

df = importar_csv_largo(r"D:\Raspagem de Dados jogo do bicho\dados\jogo_do_bicho_2024.csv")

# 1. Grupos mais frequentes
grupos = df["grupo"].value_counts()
print("=" * 60)
print("TOP 5 GRUPOS MAIS FREQUENTES (2024)")
print("=" * 60)
print(grupos.head(5).to_string())

# 2. Dezenas mais frequentes
dezenas = df["dezena"].value_counts()
print()
print("=" * 60)
print("TOP 5 DEZENAS MAIS FREQUENTES (2024)")
print("=" * 60)
print(dezenas.head(5).to_string())

# 3. Centenas mais frequentes
centenas = df["centena"].value_counts()
print()
print("=" * 60)
print("TOP 5 CENTENAS MAIS FREQUENTES (2024)")
print("=" * 60)
print(centenas.head(5).to_string())

# 4. Milhares mais frequentes
milhares = df["milhar"].value_counts()
print()
print("=" * 60)
print("TOP 5 MILHARES MAIS FREQUENTES (2024)")
print("=" * 60)
print(milhares.head(5).to_string())

# 5. Milhares mais atrasados
df_ordenado = df.reset_index(drop=True)
ultimo_idx = df_ordenado.groupby("milhar").apply(lambda x: x.index.max())
atrasos = (len(df_ordenado) - 1 - ultimo_idx).sort_values(ascending=False)
print()
print("=" * 60)
print("TOP 5 MILHARES MAIS ATRASADOS (2024)")
print("=" * 60)
print(atrasos.head(5).to_string())
