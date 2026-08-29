# Análise exploratória — CICIoT2023 subsample

[← Voltar ao README](../README.md) | [Dataset oficial](dataset.md) | [Escopo inicial](escopo-inicial.md)

EDA do recorte HuggingFace [`lacg030175/CIC-IoT-2023-neto-subsample`](https://huggingface.co/datasets/lacg030175/CIC-IoT-2023-neto-subsample), config `random_3way`, revision em `data/raw/ciciot2023-neto-subsample/SOURCE.json`.

Como reproduzir (a partir da raiz, no `.venv`):

```bash
python scripts/prepare_dataset.py   # se os parquets ainda não existirem
python scripts/run_eda.py
```

Tabelas e figuras ficam em `artifacts/eda/` (gitignored). Este documento registra os números e as **decisões** para a próxima etapa.

Os splits oficiais não foram reembaralhados. O recorte `data/subset/ciciot2023_subset.parquet` não substitui o `train`.

## 1. Schema

50 colunas: **46 features** `float32` e **4 rótulos** (`Label`, `Label_orig`, `attack_class`, `label` como `int8`).

Não há feature categórica para one-hot neste recorte. Flags de protocolo e TCP já estão em `{0, 1}`. Árvores não precisam de scaler; normalização só entra se um modelo posterior exigir.

## 2. Target

Mapeamento oficial deste estágio:

| `label` | classe |
| --- | --- |
| 0 | `normal` |
| 1 | `attack` |

Nos três splits: `label==0` ⇔ `Label==BenignTraffic` ⇔ `attack_class==Benign`, e `Label` ≡ `Label_orig`. `Label_orig` é redundante.

Um tipo específico (`DDoS-ICMP_Flood`, ping sweep, etc.) **não** entra na saída do classificador agora. `Label` e `attack_class` ficam só para diagnóstico.

## 3. Tamanho e distribuição

| Split | Linhas | normal | attack | % attack |
| --- | ---: | ---: | ---: | ---: |
| train | 1.143.802 | 160.000 | 983.802 | 86,0% |
| validation | 142.976 | 20.000 | 122.976 | 86,0% |
| test | 142.975 | 20.000 | 122.975 | 86,0% |

O desbalanceamento é **invertido** em relação a um IDS típico: o subsample HuggingFace limitou ataques (~50 mil por subtipo) e manteve 200 mil fluxos benignos. Um classificador constante `attack` acerta ~86% — accuracy isolada continua inútil. Recall de `attack`, FNR e FPR seguem as métricas do [escopo](escopo-inicial.md).

34 subtipos CICIoT e 8 famílias nos três splits. Train:

| `attack_class` | n | % |
| --- | ---: | ---: |
| DDoS | 441.869 | 38,6% |
| Benign | 160.000 | 14,0% |
| DoS | 159.887 | 14,0% |
| Recon | 151.834 | 13,3% |
| Mirai | 119.829 | 10,5% |
| Spoofing | 79.938 | 7,0% |
| Web-based | 19.924 | 1,7% |
| BruteForce | 10.521 | 0,9% |

## 4. Qualidade

| Split | Nulos | Inf | Duplicatas |
| --- | ---: | ---: | ---: |
| train | 0 | 0 | 27.291 (2,39%) |
| validation | 0 | 0 | 725 |
| test | 0 | 0 | 744 |

- **Constante:** `Telnet` (sempre 0) — descartar.
- **Flags raras** (média ≤ 1% ou ≥ 99%): `SMTP`, `DHCP`, `IRC`, `ece_flag_number`, `cwr_flag_number`, `DNS`, `SSH`, `ARP`; `IPv`/`LLC` ≈ 0,999. Candidatas a drop se não discriminarem na baseline.

A próxima etapa deve **deduplicar o train** (validação e teste oficiais não se misturam nesse passo).

## 5. Colinearidade e transformação

Pares idênticos no train: `Rate` ≡ `Srate`, `IPv` ≡ `LLC`.

|corr| ≥ 0,95 no train (além dos idênticos): `Std`–`Radius` (~1,0), `Number`–`Weight`–`IAT` (~0,998), `AVG`–`Magnitue` (~0,97), `Max`–`Std`/`Radius` (~0,96).

Árvores toleram colinearidade. Boosting/linear, se vierem depois, devem tratar o bloco de tamanho (`Tot sum`, `Min`, `Max`, `AVG`, `Tot size`, `Magnitue`, `Radius`, `Std`).

## 6. ICMP

`ICMP` é **feature candidata**, não classe de saída.

- `DDoS-ICMP_Flood`: ICMP médio 0,999 (40.075 linhas no train).
- `DDoS-ICMP_Fragmentation`: 0,975 (39.912).
- `Recon-PingSweep`: ICMP médio **0** (1.797) — ping sweep **não** aparece nessa flag.
- Tráfego normal: ICMP médio 0,000019.

HTTPS é bem mais comum em `normal` (0,71) do que em `attack` (0,11); TCP também (0,86 vs 0,58). Isso é sinal de protocolo, não rótulo vazado.

## 7. Tempo

Nenhuma das 50 colunas é timestamp de captura. `IAT` é intervalo entre pacotes (mediana ~8,3×10⁷ no train), não relógio. A ordem das linhas **não** é tempo.

**Janelas temporais ficam fora** até existir ordenação temporal real.

## 8. Vazamento

- Sem id de host, sessão ou fluxo: não há group split. Protocolo: **splits publicados**, sem reembaralhar o conjunto.
- Sobreposição de chaves de fluxo (`flow_duration`, `Header_Length`, `Rate`, `IAT`, `Tot size`, `ICMP`, `TCP`, `Number`, `Weight`): train∩validation **5.796**, train∩test **5.822**, validation∩test **1.201**. Vazamento por linha duplicada/parecida, não por tempo.
- **`IAT`, `Number` e `Weight`** têm medianas quase constantes por família (flood DoS/DDoS: `Number=9,5` / `Weight=141,55`; benigno e parte de recon/web: `13,5` / `244,6`; outra parte de recon/web: `5,5` / `38,5`). Padrão típico de artefato de captura do CICIoT: o modelo pode aprender o cenário, não o ataque.

A baseline deve treinar **com e sem** `IAT` / `Number` / `Weight`. Não dropá-las em silêncio.

## 9. Features para a próxima etapa

Não usar como X: `Label`, `Label_orig`, `attack_class`, `label`.

| Decisão | Colunas | Motivo |
| --- | --- | --- |
| Descartar | `Telnet`, `Srate`, `LLC` | constante ou cópia idêntica |
| Experimento controlado | `IAT`, `Number`, `Weight` | suspeita de artefato / vazamento |
| Manter | demais 40 features, inclusive `ICMP` | candidatas da baseline |
| Opcional na baseline | flags raras (`SMTP`, `DHCP`, `IRC`, `ece_flag_number`, `cwr_flag_number`) | quase nulas |

Preprocessing que a etapa seguinte deve implementar (ainda não existe no repo):

1. Montar X só com features, y = `label`.
2. Dropar `Telnet`, `Srate`, `LLC`.
3. Deduplicar o train.
4. `class_weight` (ou equivalente) por causa dos 14% / 86%.
5. Sem scaler na Decision Tree.
6. Guardar o preprocessing versionado junto do modelo, quando houver exportação.

## 10. Limitações

- Este recorte não é o CICIoT completo (46,7 M linhas).
- Há mais ataque que tráfego normal — o contrário do operacional típico.
- ICMP flood ≠ ping sweep neste schema.
- Splits aleatórios estratificados: fluxos da mesma captura podem aparecer em treino e teste; não há como agrupar.
- RIPE Atlas continua fora do protocolo de avaliação.

## Classes

A EDA é um conjunto de classes em `src/netguard_ml/data/`:

- `CiciotDataset` — download, recorte e leitura dos splits
- `EdaInspector` + 8 inspectores (`Schema`, `Target`, `Distribution`, `Quality`, `Collinearity`, `Icmp`, `Temporal`, `Leakage`)
- `EdaPipeline` / `EdaArtifactWriter` — orquestração e artefatos
