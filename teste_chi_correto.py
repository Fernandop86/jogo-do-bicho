from motor.importacao import importar_csv_largo
import numpy as np
from scipy import stats

df = importar_csv_largo(r"D:\Raspagem de Dados jogo do bicho\dados\jogo_do_bicho_2024.csv")

contagem = df["grupo"].value_counts().sort_index()
obs = contagem.values
total = obs.sum()
n_grupos = len(contagem)
esp = np.full(n_grupos, total / n_grupos)

chi2, p = stats.chisquare(obs, esp)

print("=" * 60)
print("CHI-QUADRADO CORRETO — GRUPO")
print("=" * 60)
print(f"Total observado: {total}")
print(f"N grupos:        {n_grupos}")
print(f"Esperado/grupo:  {total / n_grupos:.2f}")
print(f"Chi²:            {chi2:.3f}")
print(f"Gl:              {n_grupos - 1}")
print(f"p-value:         {p:.6f}")
print(f"Crítico 5%:      {stats.chi2.ppf(0.95, n_grupos - 1):.3f}")
print(f"Crítico 1%:      {stats.chi2.ppf(0.99, n_grupos - 1):.3f}")
print()
if p < 0.01:
    print(">>> DIFERENÇA ALTAMENTE SIGNIFICATIVA (p < 0.01)")
elif p < 0.05:
    print(">>> Diferença significativa (p < 0.05)")
else:
    print(">>> Compatível com uniformidade (acaso)")
print()

# Z-scores corretos
print("=" * 60)
print("Z-SCORES CORRETOS (por grupo)")
print("=" * 60)
p_esperada = 1 / n_grupos
desvio = np.sqrt(total * p_esperada * (1 - p_esperada))

for grupo, obs_g in contagem.items():
    z = (obs_g - total / n_grupos) / desvio
    sinal = "+" if z > 0 else ""
    marca = " ⭐" if abs(z) > 1.96 else ""
    print(f"  grupo {grupo}: obs={obs_g}  z={sinal}{z:.3f}{marca}")
