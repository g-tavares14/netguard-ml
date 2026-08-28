# Scripts de projeto

```bash
.venv/bin/python scripts/prepare_dataset.py
```

A classe `CiciotDataset` baixa o subsample HuggingFace para `data/raw/ciciot2023-neto-subsample/` e gera um recorte estratificado (até 2000 linhas por `Label`, seed 42) em `data/subset/ciciot2023_subset.parquet`, a partir do `train.parquet`.

Os splits `validation` e `test` não entram no recorte — continuam sendo o conjunto oficial de avaliação.
