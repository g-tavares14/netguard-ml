# Código Python do NetGuard ML

Pacote do pipeline. O dataset oficial é o CICIoT2023 subsample em `data/raw/ciciot2023-neto-subsample/` ([docs/dataset.md](../../docs/dataset.md)).

Hoje existem a leitura dos splits (`DatasetSource`), a inspeção do schema das features e a EDA em `netguard_ml.data`. Ainda não há preprocessing de modelo, treino nem contrato de inferência.

Achados da EDA: [docs/eda.md](../../docs/eda.md).
