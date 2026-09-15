"""Testes para motor/score.py"""
import pandas as pd
import pytest

from motor.score import normalizar


class TestNormalizar:
    def test_normalizar_variacao(self):
        """Series com variacao -> normaliza 0 a 1."""
        s = pd.Series([1, 2, 3, 4, 5])
        n = normalizar(s)
        assert n.min() == 0.0
        assert n.max() == 1.0
        assert len(n) == 5

    def test_normalizar_constante(self):
        """Series com valores iguais -> retorna 0.5."""
        s = pd.Series([5, 5, 5, 5])
        n = normalizar(s)
        assert all(n == 0.5)

    def test_normalizar_preserva_ordem(self):
        """A ordem relativa deve ser preservada."""
        s = pd.Series([10, 20, 30])
        n = normalizar(s)
        assert n.iloc[0] < n.iloc[1] < n.iloc[2]

    def test_normalizar_extremos(self):
        """Extremos viram 0 e 1."""
        s = pd.Series([100, 50, 200])
        n = normalizar(s)
        assert n.iloc[0] == (100 - 50) / (200 - 50)
        assert n.min() == 0.0
        assert n.max() == 1.0
