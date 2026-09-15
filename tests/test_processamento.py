"""Testes para motor/processamento.py"""
import pytest

from motor.processamento import processar_numero


class TestProcessarNumero:
    """Valida o processamento de números de 4 dígitos."""

    def test_numero_simples(self):
        r = processar_numero("4187")
        assert r["milhar"] == "4187"
        assert r["centena"] == "187"
        assert r["dezena"] == "87"

    def test_zero_a_esquerda(self):
        r = processar_numero("0325")
        assert r["milhar"] == "0325"
        assert r["centena"] == "325"
        assert r["dezena"] == "25"

    def test_string_curta_faz_zfill(self):
        r = processar_numero("325")
        assert r["milhar"] == "0325"

    def test_numero_como_int(self):
        r = processar_numero(4187)
        assert r["milhar"] == "4187"

    def test_numero_invalido(self):
        with pytest.raises(ValueError):
            processar_numero("abcd")

    def test_numero_muito_longo(self):
        with pytest.raises(ValueError):
            processar_numero("12345")

    @pytest.mark.parametrize("numero,grupo_esperado", [
        ("0001", 1),
        ("0004", 1),
        ("0005", 2),
        ("9999", 25),
        ("0100", 25),
    ])
    def test_grupo_por_dezena(self, numero, grupo_esperado):
        r = processar_numero(numero)
        assert r["grupo"] == grupo_esperado
