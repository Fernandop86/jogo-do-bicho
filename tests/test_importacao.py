"""Testes para motor/importacao.py"""
from pathlib import Path

import pandas as pd
import pytest

from motor.importacao import importar_csv_largo


@pytest.fixture
def csv_exemplo(tmp_path):
    """Cria um CSV de exemplo no formato do Jogo do Bicho."""
    csv = tmp_path / "jogo_do_bicho_2024.csv"
    conteudo = """csvData,Tipo,Horario,Premio_1,Centena_1,Grupo_1,Bicho_1,Premio_2,Centena_2,Grupo_2,Bicho_2,Premio_3,Centena_3,Grupo_3,Bicho_3,Premio_4,Centena_4,Grupo_4,Bicho_4,Premio_5,Centena_5,Grupo_5,Bicho_5
2024-01-02,PTM,11:30,7369,369,18,Porco,3493,493,24,Veado,0634,634,09,Cobra,9656,656,14,Gato,9702,702,01,Avestruz
2024-01-02,PT,14:30,2468,468,17,Macaco,1670,670,18,Porco,3467,467,17,Macaco,3842,842,11,Cavalo,5009,009,03,Burro
2024-01-03,PTM,11:30,0783,783,21,Touro,3702,702,01,Avestruz,6389,389,23,Urso,6267,267,17,Macaco,4765,765,17,Macaco
"""
    csv.write_text(conteudo, encoding="utf-8")
    return csv


class TestImportacao:
    def test_importa_csv_valido(self, csv_exemplo):
        df = importar_csv_largo(str(csv_exemplo))
        assert len(df) == 15  # 3 linhas x 5 premios
        assert "milhar" in df.columns
        assert "grupo" in df.columns
        assert "bicho" in df.columns
        assert "dezena" in df.columns

    def test_preserva_zero_esquerda(self, csv_exemplo):
        df = importar_csv_largo(str(csv_exemplo))
        milhares = df["milhar"].tolist()
        assert "0783" in milhares
        assert "0634" in milhares

    def test_dezena_calculada(self, csv_exemplo):
        df = importar_csv_largo(str(csv_exemplo))
        linha = df[df["milhar"] == "7369"].iloc[0]
        assert linha["dezena"] == "69"

    def test_arquivo_inexistente(self):
        with pytest.raises(FileNotFoundError):
            importar_csv_largo("nao_existe.csv")
