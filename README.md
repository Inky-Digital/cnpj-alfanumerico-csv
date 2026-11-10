# CNPJ alfanumérico em CSV

Arquivos de teste e um validador local para conferir se uma importação ou exportação de ERP preserva letras, zeros à esquerda e dígitos verificadores. Roda com Python 3.9 ou superior, sem instalar dependências.

```sh
python3 validar_csv.py exemplos/cadastros-validos.csv
python3 validar_csv.py exemplos/cadastros-com-erros.csv
python3 validar_csv.py exportacao.csv --coluna CNPJ --delimitador ','
```

O padrão é a coluna `cnpj` e o separador `;`. Use UTF-8, com ou sem BOM. O programa lê o arquivo local, preserva o original e informa linhas e motivos sem imprimir o conteúdo das células. Aceita CNPJ numérico e alfanumérico, com ou sem a máscara completa. Na validação, ignora espaços nas pontas e usa maiúsculas.

| Código de saída | Resultado |
| --- | --- |
| `0` | Todos os registros passaram. |
| `1` | Há pelo menos um registro inválido. |
| `2` | O arquivo ou os parâmetros impedem a conferência. |

## Como testar a ida e a volta

1. Use `exemplos/cadastros-validos.csv` em homologação. Se o importador pedir outro cabeçalho, ajuste apenas os nomes e colunas exigidos, mantendo os CNPJs como texto. Cada linha é um cenário. As duas formas de `12ABC34501DE35` têm a mesma chave, então teste uma por vez se o ERP impedir cadastros duplicados.
2. Importe, salve, pesquise e exporte os registros. Faça a mesma conferência em cada sistema que recebe o arquivo.
3. Rode o validador na exportação e compare cada CNPJ com seu valor de origem pela chave do registro. Se a máscara mudar, compare os 14 caracteres após retirar a máscara. Verifique também se todos os registros esperados voltaram.
4. Use `exemplos/cadastros-com-erros.csv` para confirmar que o importador acusa CNPJ vazio, formato incorreto e dígito inválido.

Os CSVs incluem dados ilustrativos, entre eles o exemplo de cálculo do manual da Receita. O validador confere formato e dígitos. A existência e a situação do CNPJ exigem uma consulta cadastral. Um CNPJ diferente com dígitos válidos também pode passar, por isso a comparação com a origem faz parte do teste.

```sh
python3 -m unittest -v
```

Mantido pela [Inky Digital](https://inkydigital.com.br/). Veja o [guia para testar CNPJ alfanumérico em importações CSV](https://inkydigital.com.br/blog/cnpj-alfanumerico-csv) e o [manual de cálculo da Receita Federal](https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/documentos-tecnicos/cnpj/manual-dv-cnpj.pdf/view).
