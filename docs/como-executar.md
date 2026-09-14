# Como executar o NetGuard ML

[← Voltar ao README](../README.md) | [Dataset Oficial](dataset.md) | [EDA](eda.md) | [Escopo Inicial](escopo-inicial.md)

Este tutorial cobre o que o repositório **já executa hoje**: ambiente Python com [uv](https://docs.astral.sh/uv/), download do CICIoT2023 subsample, inspeção do schema das features, EDA e testes.

Ainda **não** há treino de modelo, API, dashboard nem recursos AWS. Esses passos virão nas próximas entregas.

Todos os comandos partem da **raiz do repositório**.

## O que você precisa

| Item | Versão / observação |
| --- | --- |
| Python | 3.12 ou superior (o projeto fixa `3.12` em `.python-version`) |
| [uv](https://docs.astral.sh/uv/) | gerencia o ambiente e as dependências — não use `pip` / `venv` manual |
| Internet | só no primeiro download do dataset (~72 MB de parquet) |
| Disco | ~80 MB em `data/` (gitignorado; não entra no Git) |

## 1. Clone o repositório

```bash
git clone https://github.com/g-tavares14/netguard-ml.git
cd netguard-ml
```

## 2. Instale o uv e sincronize as dependências

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"

# Windows (PowerShell)
# irm https://astral.sh/uv/install.ps1 | iex
```

Confirme a instalação e crie o ambiente a partir de `pyproject.toml` + `uv.lock`:

```bash
uv --version
uv sync
```

`uv sync` instala o pacote `netguard-ml` em modo editável, o Polars, o pandas (EDA) e as ferramentas de desenvolvimento (pytest, Ruff, basedpyright). Não é necessário ativar `.venv` na mão: use `uv run` nos comandos seguintes.

## 3. Baixe e recorte o dataset

```bash
uv run python scripts/prepare_dataset.py
```

O script:

1. baixa os splits oficiais `train` / `validation` / `test` do HuggingFace (`random_3way`);
2. se o arquivo local já existir, **não baixa de novo**;
3. gera um recorte estratificado só a partir do `train` (até 2000 linhas por `Label`, seed 42).

Arquivos gerados:

```text
data/raw/ciciot2023-neto-subsample/train.parquet
data/raw/ciciot2023-neto-subsample/validation.parquet
data/raw/ciciot2023-neto-subsample/test.parquet
data/subset/ciciot2023_subset.parquet
```

Saída típica (primeira execução):

```text
baixando train.parquet ...
salvo em .../train.parquet
...
download ok
recorte: 66782 linhas -> .../ciciot2023_subset.parquet
```

Detalhes dos splits, rótulos e citação: [dataset.md](dataset.md).

## 4. Inspecione o schema das features

Sem argumentos, o `main` lê os três parquet em `data/raw/ciciot2023-neto-subsample/`:

```bash
uv run python -m netguard_ml.data.main
```

Para um arquivo específico (por exemplo o recorte de EDA):

```bash
uv run python -m netguard_ml.data.main data/subset/ciciot2023_subset.parquet
```

A saída é um dicionário Python: chave = nome do arquivo (stem), valor = colunas de **feature** com índice, nome e tipo. Colunas de rótulo (`Label`, `Label_orig`, `attack_class`, `label`) são omitidas.

Exemplo (recorte, primeiras colunas):

```text
{'ciciot2023_subset': {0: {'nome': 'flow_duration', 'tipo': 'Float32'}, 1: {'nome': 'Header_Length', 'tipo': 'Float32'}, ...}}
```

Formatos aceitos pelo leitor: `.parquet`, `.csv`, `.tsv`, `.json`.

## 5. Rode a EDA

O relatório usa o **train** como fonte da verdade. `--leakage` compara fingerprints das 46 features entre os splits. `--write-docs` regenera [docs/eda.md](eda.md).

```bash
uv run python -m netguard_ml.data.eda --on train --leakage
```

Para iterar no recorte (não substitui o train):

```bash
uv run python -m netguard_ml.data.eda --on recorte
```

Achados (Attack é maioria, ICMP é indicador 0/1, sem janela temporal): [eda.md](eda.md).

## 6. Rode os testes

```bash
uv run pytest tests/ -q
```

Os testes usam fixtures pequenas; **não** dependem dos parquet oficiais. Resultado esperado hoje:

```text
...............                                                          [100%]
15 passed
```

Um teste isolado:

```bash
uv run pytest tests/test_dataset_source.py::test_dataset_source_loads_parquet -q --tb=short
```

## Comandos opcionais de qualidade

O projeto usa Ruff (lint + format) e basedpyright (tipos). Não substitua por black, isort, flake8 ou mypy.

```bash
uv run ruff check --fix .
uv run ruff format .
uv run basedpyright
```

## O que ainda não dá para executar

Não existem, neste estágio:

- treino ou avaliação de modelo (`src/netguard_ml/models/` e `evaluation/` são placeholders);
- preprocessing / engenharia de features (próxima entrega; recomendações em [eda.md](eda.md));
- API, dashboard ou Terraform / AWS.

Se um comando desses aparecer em material antigo, ignore: o contrato atual é o deste tutorial e o [README](../README.md).

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
| --- | --- | --- |
| `FileNotFoundError` em `data/raw/...` | dataset ainda não baixado | rodar o passo 3 |
| `formato não suportado` | extensão fora de `.parquet` / `.csv` / `.tsv` / `.json` | passar um desses formatos |
| `uv: command not found` | uv não está no `PATH` | reinstalar e `source "$HOME/.local/bin/env"` (ou reabrir o terminal) |
| Python 3.11 ou anterior | versão abaixo do mínimo | instalar 3.12+; o `uv` respeita `.python-version` |
| Download lento ou interrompido | rede / HuggingFace | rodar o script de novo — arquivos já salvos são reaproveitados |
| Pasta `data/` não aparece no Git | esperado | `data/` está no `.gitignore`; cada máquina baixa o próprio recorte |

## Próximo passo no projeto

Com a EDA documentada, a próxima entrega é o preprocessing reproduzível (fit só no train, sem rótulos nas features). Ver [eda.md](eda.md) e o [escopo inicial](escopo-inicial.md).
