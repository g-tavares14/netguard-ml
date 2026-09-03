# Dados

Leitura e EDA do dataset oficial: CICIoT2023 subsample (`data/raw/ciciot2023-neto-subsample/`, parquet `train` / `validation` / `test`). Schema e rótulos em [docs/dataset.md](../../../docs/dataset.md). Achados em [docs/eda.md](../../../docs/eda.md).

- `reader.py`: `DatasetSource` escolhe o leitor pela extensão (`.parquet`, `.csv`, `.tsv`, `.json`).
- `schema.py`: lista as colunas de feature e omite os rótulos.
- `main.py`: imprime o schema. Sem argumentos, lê os três splits em `data/raw/...`.
- `eda.py`: relatório de EDA (schema, target, ICMP, vazamento). `--on train` é a fonte da verdade; `--write-docs` regenera `docs/eda.md`.

```bash
uv run python scripts/prepare_dataset.py
uv run python -m netguard_ml.data.main
uv run python -m netguard_ml.data.eda --on train --leakage
```
