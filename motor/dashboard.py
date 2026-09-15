
from motor.cruzamento import tabela_analise
from motor.estatistica_avancada import (
    chi_quadrado_uniforme,
    zscore_por_valor,
)
from motor.features import construir_features
from motor.score import calcular_score, calcular_score_v2

SEPARADOR = "=" * 72
SUBSEPARADOR = "-" * 72


def _marcar_perfil(linha):
    """
    Retorna uma etiqueta de perfil com base em
    frequencia_total, atraso e recencia_10.
    """
    atraso = linha.get("atraso", 0)
    rec = linha.get("recencia_10", 0)
    rep = linha.get("repeticoes_consecutivas", 0)

    etiquetas = []

    if rec >= 2:
        etiquetas.append("🔥 QUENTE")
    if atraso >= 3:
        etiquetas.append("❄️  FRIO")
    if rep >= 2:
        etiquetas.append("⚡ REPETITIVO")
    if not etiquetas:
        etiquetas.append("·  NEUTRO")

    return " ".join(etiquetas)


def renderizar_dashboard(
    df,
    coluna="milhar",
    janelas=(5, 10),
    premios_por_concurso=5,
    coluna_recencia="recencia_10",
    top_n=10,
):
    """
    Renderiza o dashboard completo para uma coluna.
    """

    print()
    print(SEPARADOR)
    print(f"DASHBOARD — ANÁLISE POR {coluna.upper()}")
    print(SEPARADOR)

    # ------------------------------------------------------------
    # 1. Tabela base
    # ------------------------------------------------------------
    tabela = tabela_analise(df, coluna, janelas=list(janelas))
    features = construir_features(
        df, coluna=coluna, premios_por_concurso=premios_por_concurso
    )

    # ------------------------------------------------------------
    # 2. Score v1
    # ------------------------------------------------------------
    print()
    print("📊 RANKING — SCORE V1 (freq + atraso + recência)")
    print(SUBSEPARADOR)
    rank_v1 = calcular_score(tabela, coluna_recencia=coluna_recencia)

    cols_v1 = [coluna, "frequencia_total", "atraso", coluna_recencia, "score"]
    print(rank_v1[cols_v1].head(top_n).to_string(index=False))

    # ------------------------------------------------------------
    # 3. Score v2
    # ------------------------------------------------------------
    print()
    print("📊 RANKING — SCORE V2 (+ repetições + prêmio médio)")
    print(SUBSEPARADOR)
    rank_v2 = calcular_score_v2(
        tabela, features, coluna=coluna, coluna_recencia=coluna_recencia
    )

    cols_v2 = [
        coluna, "frequencia_total", "atraso", coluna_recencia,
        "repeticoes_consecutivas", "premio_medio", "score",
    ]
    print(rank_v2[cols_v2].head(top_n).to_string(index=False))

    # ------------------------------------------------------------
    # 4. Perfis
    # ------------------------------------------------------------
    print()
    print("🎯 PERFIS DOS TOP 5 (V1)")
    print(SUBSEPARADOR)
    for _, linha in rank_v1.head(5).iterrows():
        # Enriquecer com features do v2
        f = features[features[coluna].astype(str) == str(linha[coluna])]
        rep = int(f["repeticoes_consecutivas"].iloc[0]) if not f.empty else 0
        linha_dict = linha.to_dict()
        linha_dict["repeticoes_consecutivas"] = rep
        perfil = _marcar_perfil(linha_dict)
        print(f"  {linha[coluna]!s:>6}   {perfil}")

    # ------------------------------------------------------------
    # 5. Chi-quadrado
    # ------------------------------------------------------------
    print()
    print("📐 TESTE CHI-QUADRADO (uniformidade)")
    print(SUBSEPARADOR)
    chi = chi_quadrado_uniforme(df, coluna=coluna)
    for k, v in chi.items():
        print(f"  {k:>15}: {v}")

    # ------------------------------------------------------------
    # 6. Z-scores
    # ------------------------------------------------------------
    print()
    print("📐 Z-SCORES (desvio da uniformidade)")
    print(SUBSEPARADOR)
    z = zscore_por_valor(df, coluna=coluna)
    print(z.head(top_n).to_string(index=False))

    print()
    print(SEPARADOR)
