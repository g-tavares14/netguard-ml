# Dados

Leitura e validação do dataset oficial: CICIoT2023 subsample (`data/raw/ciciot2023-neto-subsample/`, parquet `train` / `validation` / `test`). Schema e rótulos em [docs/dataset.md](../../../docs/dataset.md).

- `reader.py`: `DatasetSource` escolhe o leitor pela extensão (`.parquet`, `.csv`, `.tsv`, `.json`).
- `schema.py`: lista as colunas de feature e omite os rótulos.
- `main.py`: imprime o schema. Sem argumentos, lê os três splits em `data/raw/...`.

Como baixar os arquivos e rodar: [docs/como-executar.md](../../../docs/como-executar.md).
