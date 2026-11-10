import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validar_csv import erro_cnpj


RAIZ = Path(__file__).resolve().parent


def executar(arquivo, *opcoes):
    return subprocess.run(
        [sys.executable, str(RAIZ / "validar_csv.py"), str(arquivo), *opcoes],
        capture_output=True, text=True,
    )


class ValidacaoCSVTest(unittest.TestCase):
    def test_exemplos_validos_e_invalidos(self):
        validos = executar(RAIZ / "exemplos/cadastros-validos.csv")
        self.assertEqual(validos.returncode, 0, validos.stderr)
        self.assertIn("3 registro(s) conferido(s), 0 com erro", validos.stdout)

        invalidos = executar(RAIZ / "exemplos/cadastros-com-erros.csv")
        self.assertEqual(invalidos.returncode, 1)
        self.assertIn("5 registro(s) conferido(s), 5 com erro", invalidos.stdout)
        self.assertIn("Linha 3: dígitos verificadores não conferem", invalidos.stderr)
        self.assertNotIn("12ABC34501DE36", invalidos.stderr)

    def test_bom_virgula_coluna_customizada_e_campo_com_quebra(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "exportacao.csv"
            arquivo.write_text(
                'ID,CNPJ,Nota\r\n1,"00123456000149","linha, com vírgula\r\ne quebra"\r\n',
                encoding="utf-8-sig",
            )
            antes = arquivo.read_bytes()
            resultado = executar(arquivo, "--coluna", "CNPJ", "--delimitador", ",")
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertEqual(arquivo.read_bytes(), antes)

    def test_csv_inutilizavel_nao_passa(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "exportacao.csv"
            for conteudo in ("cnpj;cnpj\n", "cnpj\n", 'cnpj\n"12ABC34501DE35\n'):
                with self.subTest(conteudo=conteudo):
                    arquivo.write_text(conteudo, encoding="utf-8")
                    self.assertEqual(executar(arquivo).returncode, 2)

    def test_caracteres_e_mascara_sao_validados_antes_de_normalizar(self):
        self.assertIsNone(erro_cnpj(" 12.abc.345/01de-35 "))
        self.assertEqual(erro_cnpj("12ABC34501DÉ35"), "formato inválido")
        self.assertEqual(erro_cnpj("12ABC345/01DE35"), "formato inválido")
        self.assertEqual(erro_cnpj("00000000000000"), "sequência de dígitos repetidos")


if __name__ == "__main__":
    unittest.main()
