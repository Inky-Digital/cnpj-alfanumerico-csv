"""Confere formato e dígitos verificadores de CNPJs em um CSV local."""

import argparse
import csv
import re
import sys
from pathlib import Path


CNPJ_SEM_MASCARA = re.compile(r"[0-9A-Za-z]{12}[0-9]{2}")
CNPJ_COM_MASCARA = re.compile(
    r"[0-9A-Za-z]{2}\.[0-9A-Za-z]{3}\.[0-9A-Za-z]{3}/[0-9A-Za-z]{4}-[0-9]{2}"
)
MASCARA = str.maketrans("", "", "./-")


def normalizar(cnpj):
    cnpj = cnpj.strip()
    if CNPJ_SEM_MASCARA.fullmatch(cnpj) or CNPJ_COM_MASCARA.fullmatch(cnpj):
        return cnpj.translate(MASCARA).upper()
    return None


def digito_verificador(base):
    soma = sum(
        (ord(caractere) - 48) * (2 + i % 8)
        for i, caractere in enumerate(reversed(base))
    )
    resto = soma % 11
    return str(0 if resto < 2 else 11 - resto)


def erro_cnpj(valor):
    if not valor.strip():
        return "CNPJ vazio"
    cnpj = normalizar(valor)
    if cnpj is None:
        return "formato inválido"
    if len(set(cnpj)) == 1:
        return "sequência de dígitos repetidos"
    base = cnpj[:12]
    primeiro = digito_verificador(base)
    segundo = digito_verificador(base + primeiro)
    if cnpj[12:] != primeiro + segundo:
        return "dígitos verificadores não conferem"
    return None


def conferir_csv(arquivo, coluna, delimitador):
    erros = total = 0
    with arquivo.open(encoding="utf-8-sig", newline="") as entrada:
        leitor = csv.reader(entrada, delimiter=delimitador, strict=True)
        cabecalho = next(leitor, [])
        if cabecalho.count(coluna) != 1:
            raise ValueError("a coluna solicitada deve aparecer uma vez no cabeçalho")
        indice = cabecalho.index(coluna)
        for linha in leitor:
            if not linha:
                continue
            total += 1
            if len(linha) != len(cabecalho):
                erro = "quantidade de campos difere do cabeçalho"
            else:
                erro = erro_cnpj(linha[indice])
            if erro:
                erros += 1
                print(f"Linha {leitor.line_num}: {erro}.", file=sys.stderr)
    if not total:
        raise ValueError("o CSV não contém registros")
    return total, erros


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="arquivo CSV em UTF-8")
    parser.add_argument("--coluna", default="cnpj", help="nome da coluna (padrão: cnpj)")
    parser.add_argument(
        "--delimitador", choices=[",", ";"], default=";",
        help="separador de campos (padrão: ponto e vírgula)",
    )
    args = parser.parse_args()
    try:
        total, erros = conferir_csv(args.csv, args.coluna, args.delimitador)
    except UnicodeError:
        print("Erro: o arquivo precisa estar em UTF-8.", file=sys.stderr)
        return 2
    except csv.Error:
        print("Erro: CSV malformado ou campo acima do limite do leitor.", file=sys.stderr)
        return 2
    except OSError:
        print("Erro: não foi possível ler o arquivo.", file=sys.stderr)
        return 2
    except ValueError as erro:
        print(f"Erro: {erro}.", file=sys.stderr)
        return 2
    print(f"{total} registro(s) conferido(s), {erros} com erro.")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
