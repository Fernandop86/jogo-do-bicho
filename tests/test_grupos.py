"""Testes para motor/grupos.py"""
import pytest

from motor.grupos import dezena_para_grupo, grupo_para_animal


class TestDezenaParaGrupo:
    """Valida a conversão dezena -> grupo (1-25)."""

    @pytest.mark.parametrize("dezena,esperado", [
        (1, 1), (2, 1), (3, 1), (4, 1),
        (5, 2), (6, 2), (7, 2), (8, 2),
        (97, 25), (98, 25), (99, 25), (0, 25),
    ])
    def test_dezena_para_grupo(self, dezena, esperado):
        assert dezena_para_grupo(dezena) == esperado

    def test_dezena_zero_vira_grupo_25(self):
        assert dezena_para_grupo(0) == 25

    def test_dezena_string(self):
        assert dezena_para_grupo("05") == 2

    def test_dezena_invalida(self):
        with pytest.raises((ValueError, TypeError)):
            dezena_para_grupo("abc")


class TestGrupoParaAnimal:
    """Valida a conversão grupo -> nome do animal."""

    @pytest.mark.parametrize("grupo,animal", [
        (1, "Avestruz"),
        (2, "Águia"),
        (17, "Macaco"),
        (25, "Vaca"),
    ])
    def test_grupo_para_animal(self, grupo, animal):
        assert grupo_para_animal(grupo) == animal

    def test_grupo_invalido(self):
        assert grupo_para_animal(99) == "Desconhecido"
        assert grupo_para_animal(0) == "Desconhecido"
