# Dataset oficial

[← Voltar ao README](../README.md) | [Escopo Inicial](escopo-inicial.md) | [Roadmap AWS](aws-roadmap.md)

O dataset oficial do NetGuard ML é o **CICIoT2023** (Neto et al., 2023), na distribuição HuggingFace [`lacg030175/CIC-IoT-2023-neto-subsample`](https://huggingface.co/datasets/lacg030175/CIC-IoT-2023-neto-subsample), config **`random_3way`**.

Não usamos os 169 CSVs do CIC nem a API do RIPE Atlas para treino ou teste do classificador.

## Por que esta fonte

| Critério do [escopo inicial](escopo-inicial.md) | Situação |
| --- | --- |
| Tráfego de rede rotulado | sim (`Label` com 34 classes, inclusive `BenignTraffic`) |
| Target binário `normal` / `attack` | coluna `label`: `0` = benign, `1` = attack |
| ICMP e ping flood | `DDoS-ICMP_Flood`, `DDoS-ICMP_Fragmentation`, `Recon-PingSweep` + feature `ICMP` |
| Tamanho viável no laptop | ~1,43 M linhas, ~72 MB parquet (não os 46,7 M / 13 GB do conjunto completo) |
| Divisão já definida | `train` / `validation` / `test` estratificados, seed=42 |

O HuggingFace é um **recorte estratificado** do corpus CIC (200 mil linhas benignas; até 50 mil por subtipo de ataque). A citação acadêmica continua sendo o artigo do CIC, não o espelho.

## Arquivos locais

Gitignorados em `data/raw/ciciot2023-neto-subsample/` (`SOURCE.json` tem o revision):

| Split | Arquivo | Linhas |
| --- | --- | ---: |
| treino | `train.parquet` | 1.143.802 |
| validação | `validation.parquet` | 142.976 |
| teste | `test.parquet` | 142.975 |

Use estes três arquivos. Não reembaralhar o conjunto inteiro para criar outro split.

Para baixar de novo e gerar um recorte de EDA (só a partir do `train`):

```bash
python scripts/prepare_dataset.py
```

O recorte vai para `data/subset/ciciot2023_subset.parquet` (até 2000 linhas por `Label`, seed 42). Validação e teste oficiais não são misturados nesse arquivo.

## Target e rótulos

- Saída do modelo neste estágio: binário. Mapear `label==0` → `normal`, `label==1` → `attack`.
- `Label` / `Label_orig` guardam o tipo CICIoT (`DDoS-ICMP_Flood`, …). Só entram na saída do sistema se um modelo for treinado e avaliado para isso.
- `attack_class` agrupa famílias (Benign, DDoS, DoS, Recon, Mirai, Spoofing, Web-based, BruteForce).

## Features

46 colunas de fluxo do CICIoT (duração, taxa, flags TCP, indicadores de protocolo incluindo `ICMP`, tamanhos, IAT, estatísticas) mais as quatro colunas de rótulo. Não há timestamp de captura: `IAT` é intervalo entre pacotes, não relógio. A ordem das linhas **não** é tempo. A EDA confirma isso e lista features utilizáveis em [Análise exploratória](eda.md).

## O que não entra no protocolo de avaliação

- o CICIoT completo de 46,7 M linhas (mesmo schema, outro tamanho);
- RIPE Atlas (RTT/perda sem rótulo e sem as 46 features);
- recortes Kaggle não versionados neste `SOURCE.json`.

## Citação

> E. C. P. Neto, S. Dadkhah, R. Ferreira, A. Zohourian, R. Lu, A. A. Ghorbani.
> CICIoT2023: A real-time dataset and benchmark for large-scale attacks in IoT environment.
> *Sensors*, 2023. https://doi.org/10.3390/s23135941

- Página do CIC: https://www.unb.ca/cic/datasets/iotdataset-2023.html
- Recorte usado: https://huggingface.co/datasets/lacg030175/CIC-IoT-2023-neto-subsample (revision em `SOURCE.json`)

