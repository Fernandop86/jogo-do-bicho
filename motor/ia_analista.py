
from motor.cruzamento import tabela_analise
from motor.estatistica_avancada import (
    chi_quadrado_uniforme,
    zscore_por_valor,
)
from motor.features import construir_features
from motor.score import calcular_score, calcular_score_v2

# ------------------------------------------------------------
# Base de conhecimento: tudo que a IA precisa saber
# ------------------------------------------------------------

class Analista:
    def __init__(self, df, premios_por_concurso=5, coluna_recencia="recencia_10"):
        self.df = df
        self.premios_por_concurso = premios_por_concurso
        self.coluna_recencia = coluna_recencia
        self.cache = {}

    def _tabela(self, coluna, janelas=(5, 10)):
        chave = ("tabela", coluna, janelas)
        if chave not in self.cache:
            self.cache[chave] = tabela_analise(
                self.df, coluna, janelas=list(janelas)
            )
        return self.cache[chave]

    def _features(self, coluna):
        chave = ("feat", coluna)
        if chave not in self.cache:
            self.cache[chave] = construir_features(
                self.df, coluna=coluna,
                premios_por_concurso=self.premios_por_concurso
            )
        return self.cache[chave]

    def ranking(self, coluna="milhar", top_n=5):
        tabela = self._tabela(coluna)
        return calcular_score(
            tabela, coluna_recencia=self.coluna_recencia
        ).head(top_n)

    def ranking_v2(self, coluna="milhar", top_n=5):
        tabela = self._tabela(coluna)
        features = self._features(coluna)
        return calcular_score_v2(
            tabela, features, coluna=coluna,
            coluna_recencia=self.coluna_recencia
        ).head(top_n)

    def mais_atrasados(self, coluna="milhar", top_n=5):
        tabela = self._tabela(coluna)
        return tabela.sort_values("atraso", ascending=False).head(top_n)

    def mais_quentes(self, coluna="milhar", top_n=5):
        tabela = self._tabela(coluna)
        return tabela.sort_values(
            self.coluna_recencia, ascending=False
        ).head(top_n)

    def estatistica(self, coluna="milhar"):
        return {
            "chi": chi_quadrado_uniforme(self.df, coluna=coluna),
            "z": zscore_por_valor(self.df, coluna=coluna),
        }


# ------------------------------------------------------------
# Parser de intenção
# ------------------------------------------------------------

def detectar_coluna(texto):
    for c in ("milhar", "grupo", "dezena", "centena", "bicho"):
        if c in texto:
            return c
    return "milhar"


def detectar_intencao(texto):
    texto = texto.lower().strip()

    if texto in ("sair", "exit", "quit", "q"):
        return "sair"
    if "ajuda" in texto or "help" in texto or texto == "?":
        return "ajuda"
    if "resumo" in texto or "geral" in texto or "panorama" in texto:
        return "resumo"
    if "atras" in texto:
        return "atrasados"
    if "quent" in texto or "recent" in texto:
        return "quentes"
    if "uniform" in texto or "estat" in texto or "chi" in texto or "z-score" in texto:
        return "estatistica"
    if "ranking" in texto or "top" in texto or "melhor" in texto:
        return "ranking"
    return "desconhecida"


# ------------------------------------------------------------
# Geração de respostas
# ------------------------------------------------------------

def resposta_resumo(a, coluna="milhar"):
    tabela = a._tabela(coluna)
    chi = a.estatistica(coluna)["chi"]

    top = a.ranking(coluna, top_n=3)

    linhas = []
    linhas.append(
        f"Resumo do histórico ({len(a.df)} registros, "
        f"análise por {coluna}):"
    )
    linhas.append("")

    linhas.append(f"  • Total de valores distintos: {tabela.shape[0]}")
    linhas.append(f"  • Mais frequente: {top.iloc[0][coluna]} "
                  f"({int(top.iloc[0]['frequencia_total'])} ocorrências)")

    mais_atrasado = a.mais_atrasados(coluna, top_n=1).iloc[0]
    linhas.append(f"  • Mais atrasado: {mais_atrasado[coluna]} "
                  f"(atraso {int(mais_atrasado['atraso'])})")

    mais_quente = a.mais_quentes(coluna, top_n=1).iloc[0]
    linhas.append(f"  • Mais recente: {mais_quente[coluna]} "
                  f"(recência {int(mais_quente[a.coluna_recencia])} "
                  f"nos últimos 10)")

    linhas.append("")
    linhas.append(f"  • Chi² = {chi['chi2']:.2f}  |  p = {chi['p_value']:.4f}")
    linhas.append(f"  • Interpretação: {chi['interpretacao']}")

    linhas.append("")
    linhas.append("Top 3 pelo score v1:")
    for i, (_, r) in enumerate(top.iterrows(), 1):
        linhas.append(
            f"  {i}. {r[coluna]}  "
            f"(score {r['score']:.3f}, "
            f"freq {int(r['frequencia_total'])}, "
            f"atraso {int(r['atraso'])})"
        )

    return "\n".join(linhas)


def resposta_ranking(a, coluna="milhar", top_n=5):
    r = a.ranking(coluna, top_n=top_n)
    linhas = [f"Ranking por {coluna} (score v1, top {top_n}):", ""]
    for i, (_, row) in enumerate(r.iterrows(), 1):
        linhas.append(
            f"  {i}. {row[coluna]:>6}  "
            f"score={row['score']:.3f}  "
            f"freq={int(row['frequencia_total'])}  "
            f"atraso={int(row['atraso'])}"
        )
    return "\n".join(linhas)


def resposta_atrasados(a, coluna="milhar", top_n=5):
    r = a.mais_atrasados(coluna, top_n=top_n)
    linhas = [f"Mais atrasados em {coluna} (top {top_n}):", ""]
    for i, (_, row) in enumerate(r.iterrows(), 1):
        linhas.append(
            f"  {i}. {row[coluna]:>6}  "
            f"atraso={int(row['atraso'])}  "
            f"freq={int(row['frequencia_total'])}"
        )
    return "\n".join(linhas)


def resposta_quentes(a, coluna="milhar", top_n=5):
    r = a.mais_quentes(coluna, top_n=top_n)
    linhas = [f"Mais recentes em {coluna} (top {top_n}):", ""]
    for i, (_, row) in enumerate(r.iterrows(), 1):
        linhas.append(
            f"  {i}. {row[coluna]:>6}  "
            f"recência_10={int(row[a.coluna_recencia])}  "
            f"freq={int(row['frequencia_total'])}"
        )
    return "\n".join(linhas)


def resposta_estatistica(a, coluna="milhar"):
    est = a.estatistica(coluna)
    chi = est["chi"]
    z = est["z"]

    linhas = [f"Análise estatística por {coluna}:", ""]
    linhas.append(f"  Chi²  = {chi['chi2']:.3f}")
    linhas.append(f"  gl    = {chi['gl']}")
    linhas.append(f"  p     = {chi['p_value']:.4f}")
    linhas.append(f"  Leitura: {chi['interpretacao']}")
    linhas.append("")
    linhas.append("Z-scores (ordenados):")
    for _, row in z.iterrows():
        sinal = "+" if row["z"] > 0 else ""
        linhas.append(
            f"  {row[coluna]:>6}  obs={int(row['observado'])}  "
            f"esp={row['esperado']:.1f}  z={sinal}{row['z']:.3f}"
        )
    return "\n".join(linhas)


AJUDA = """
Comandos disponíveis:

  resumo                 - panorama geral
  ranking                - top pelo score (milhar por padrão)
  ranking grupo          - ranking de grupos
  ranking dezena         - ranking de dezenas
  ranking centena        - ranking de centenas
  atrasados              - quem está mais atrasado
  atrasados grupo        - atrasados por grupo
  quentes                - quem apareceu mais recentemente
  estatística            - chi² e z-scores
  estatística grupo      - estatística por grupo
  ajuda                  - mostra esta lista
  sair                   - encerra

Você pode combinar: "ranking grupo", "atrasados dezena", etc.
"""


def responder(a, texto):
    intencao = detectar_intencao(texto)
    coluna = detectar_coluna(texto)

    if intencao == "sair":
        return None
    if intencao == "ajuda":
        return AJUDA.strip()
    if intencao == "resumo":
        return resposta_resumo(a, coluna)
    if intencao == "ranking":
        return resposta_ranking(a, coluna)
    if intencao == "atrasados":
        return resposta_atrasados(a, coluna)
    if intencao == "quentes":
        return resposta_quentes(a, coluna)
    if intencao == "estatistica":
        return resposta_estatistica(a, coluna)

    return (
        f"Não entendi: '{texto}'. "
        f"Digite 'ajuda' para ver os comandos disponíveis."
    )
