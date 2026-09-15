"""Testes para motor/estatistica_avancada.py"""
import pandas as pd
import pytest

from motor.estatistica_avancada import (
    chi_quadrado_uniforme,
    zscore_por_valor,
)


@pytest.fixture
def df_uniforme():
    """DataFrame com distribuicao perfeita (100 valores iguais)."""
    return pd.DataFrame({"grupo": ["01"] * 100})


@pytest.fixture
def df_viciado():
    """DataFrame com um valor muito mais frequente (viciado)."""
    return pd.DataFrame({
        "grupo": ["01"] * 500 + ["02"] * 100 + ["03"] * 100
    })


class TestChiQuadrado:
    def test_chi_uniforme_p_alto(self, df_uniforme):
        """Uma so categoria deve dar p=1 (nao ha variacao)."""
        r = chi_quadrado_uniforme(df_uniforme, coluna="grupo")
        assert r["n"] == 100
        assert r["n_valores"] == 1
        assert r["p_value"] == 1.0

    def test_chi_viciado_p_baixo(self, df_viciado):
        """Distribuicao muito desigual deve ter p baixo."""
        r = chi_quadrado_uniforme(df_viciado, coluna="grupo")
        assert r["n"] == 700
        assert r["n_valores"] == 3
        assert r["p_value"] < 0.01
        assert "ALTAMENTE" in r["interpretacao"] or "significativa" in r["interpretacao"]

    def test_chi_retorna_campos(self, df_uniforme):
        r = chi_quadrado_uniforme(df_uniforme, coluna="grupo")
        assert "chi2" in r
        assert "p_value" in r
        assert "gl" in r
        assert "n" in r
        assert "n_valores" in r
        assert "esperado_por_valor" in r
        assert "interpretacao" in r


class TestZscore:
    def test_zscore_positivo(self, df_viciado):
        """Grupo 01 aparece mais que o esperado -> z positivo."""
        z = zscore_por_valor(df_viciado, coluna="grupo")
        linha_01 = z[z["grupo"] == "01"].iloc[0]
        assert linha_01["z"] > 0
        assert linha_01["observado"] == 500

    def test_zscore_negativo(self, df_viciado):
        """Grupos 02 e 03 aparecem menos -> z negativo."""
        z = zscore_por_valor(df_viciado, coluna="grupo")
        linha_02 = z[z["grupo"] == "02"].iloc[0]
        assert linha_02["z"] < 0

    def test_zscore_ordenado(self, df_viciado):
        """O resultado deve vir ordenado por z (maior primeiro)."""
        z = zscore_por_valor(df_viciado, coluna="grupo")
        assert z.iloc[0]["z"] >= z.iloc[-1]["z"]
