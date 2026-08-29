# Dados

Leitura do dataset oficial CICIoT2023 subsample (`data/raw/ciciot2023-neto-subsample/`, parquet `train` / `validation` / `test`). Schema e rótulos: [docs/dataset.md](../../../docs/dataset.md). Decisões da EDA: [docs/eda.md](../../../docs/eda.md).

## Classes

- `CiciotDataset` (`dataset.py`) — download HuggingFace, recorte estratificado e `load` dos splits. Único ponto que fala com disco/rede.
- `EdaInspector` e inspectores em `eda/` — schema, target, distribuição, qualidade, colinearidade, ICMP, tempo, vazamento. Não gravam arquivo.
- `EdaPipeline` / `EdaArtifactWriter` — orquestram e escrevem `artifacts/eda/`.

## Como rodar

```bash
python scripts/prepare_dataset.py
python scripts/run_eda.py
```
