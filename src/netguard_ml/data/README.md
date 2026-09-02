# Dados

Leitura e EDA do dataset oficial: CICIoT2023 subsample (`data/raw/ciciot2023-neto-subsample/`, parquet `train` / `validation` / `test`). Schema e rótulos em [docs/dataset.md](../../../docs/dataset.md). Achados em [docs/eda.md](../../../docs/eda.md).

```bash
python scripts/prepare_dataset.py
.venv/bin/python src/netguard_ml/data/main.py --on train --leakage
```

`--on recorte` itera no subset; regras do projeto usam `--on train`. `--write-docs` regenera `docs/eda.md`. Paths são relativos à raiz do repo.
