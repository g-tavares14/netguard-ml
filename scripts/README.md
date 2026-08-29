# Scripts de projeto

```bash
.venv/bin/python scripts/prepare_dataset.py
.venv/bin/python scripts/run_eda.py
```

`prepare_dataset.py` é o CLI de `CiciotDataset`: baixa o subsample HuggingFace para `data/raw/ciciot2023-neto-subsample/` e gera um recorte estratificado (até 2000 linhas por `Label`, seed 42) em `data/subset/ciciot2023_subset.parquet`, a partir do `train.parquet`.

`run_eda.py` é o CLI de `EdaPipeline`: lê os três splits oficiais e grava tabelas/figuras em `artifacts/eda/`. O recorte de subset não entra nessa análise.

Validação e teste oficiais não são misturados no recorte nem na EDA como conjunto de treino.
