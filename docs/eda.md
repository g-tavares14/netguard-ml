# EDA — Subsample CICIoT

Análise do CICIoT2023 subsample (`random_3way`). Números que viram regra vêm do **train** (1,143,802 linhas). O Recorte de EDA só itera.

Unidade: **Fluxo** (linha já agregada pelo CIC). Target: `label == 0` → **Normal**, `label == 1` → **Attack**. `Label` e `attack_class` só nesta EDA — não na saída do primeiro modelo. Schema oficial: [dataset.md](dataset.md).


## Recorte de EDA

Usado só para iterar. Regras abaixo saem do **train**.

- linhas: 66,782
- Normal/Attack: {"Attack": 64782, "Normal": 2000}


## Schema das features de Fluxo

Rótulos à parte (`Label`, `Label_orig`, `attack_class`, `label`): 4 colunas. Features: 46.

| coluna | tipo |
| --- | --- |
| `flow_duration` | `float32` |
| `Header_Length` | `float32` |
| `Protocol Type` | `float32` |
| `Duration` | `float32` |
| `Rate` | `float32` |
| `Srate` | `float32` |
| `Drate` | `float32` |
| `fin_flag_number` | `float32` |
| `syn_flag_number` | `float32` |
| `rst_flag_number` | `float32` |
| `psh_flag_number` | `float32` |
| `ack_flag_number` | `float32` |
| `ece_flag_number` | `float32` |
| `cwr_flag_number` | `float32` |
| `ack_count` | `float32` |
| `syn_count` | `float32` |
| `fin_count` | `float32` |
| `urg_count` | `float32` |
| `rst_count` | `float32` |
| `HTTP` | `float32` |
| `HTTPS` | `float32` |
| `DNS` | `float32` |
| `Telnet` | `float32` |
| `SMTP` | `float32` |
| `SSH` | `float32` |
| `IRC` | `float32` |
| `TCP` | `float32` |
| `UDP` | `float32` |
| `DHCP` | `float32` |
| `ARP` | `float32` |
| `ICMP` | `float32` |
| `IPv` | `float32` |
| `LLC` | `float32` |
| `Tot sum` | `float32` |
| `Min` | `float32` |
| `Max` | `float32` |
| `AVG` | `float32` |
| `Std` | `float32` |
| `Tot size` | `float32` |
| `IAT` | `float32` |
| `Number` | `float32` |
| `Magnitue` | `float32` |
| `Radius` | `float32` |
| `Covariance` | `float32` |
| `Variance` | `float32` |
| `Weight` | `float32` |

Rótulos nas features: nenhum (correto).

## Balanceamento

### Normal / Attack (`label`)

| valor | n |
| --- | ---: |
| Attack | 983,802 |
| Normal | 160,000 |

Attack é **maioria** neste subsample (o HuggingFace capou benignos em 200 mil no corpus e cortou ataques por subtipo). O exemplo de “99% Normal” do escopo não se aplica a esta fonte. Accuracy isolada continua inútil.

`label` bruto: {"1": 983802, "0": 160000}.

### `Label` (EDA somente)

| valor | n |
| --- | ---: |
| BenignTraffic | 160,000 |
| DDoS-SynonymousIP_Flood | 40,155 |
| DDoS-UDP_Fragmentation | 40,148 |
| Recon-HostDiscovery | 40,088 |
| DDoS-ICMP_Flood | 40,075 |
| Recon-PortScan | 40,066 |
| DoS-SYN_Flood | 40,063 |
| Recon-OSScan | 40,047 |
| DDoS-TCP_Flood | 40,033 |
| DoS-UDP_Flood | 40,018 |
| DNS_Spoofing | 40,010 |
| DDoS-ACK_Fragmentation | 40,002 |
| DDoS-SYN_Flood | 39,990 |
| Mirai-greeth_flood | 39,979 |
| DDoS-PSHACK_Flood | 39,958 |
| DDoS-UDP_Flood | 39,950 |
| DoS-TCP_Flood | 39,933 |
| MITM-ArpSpoofing | 39,928 |
| Mirai-udpplain | 39,926 |
| Mirai-greip_flood | 39,924 |
| DDoS-ICMP_Fragmentation | 39,912 |
| DoS-HTTP_Flood | 39,873 |
| DDoS-RSTFINFlood | 39,838 |
| VulnerabilityScan | 29,836 |
| DDoS-HTTP_Flood | 23,024 |
| DDoS-SlowLoris | 18,784 |
| DictionaryBruteForce | 10,521 |
| BrowserHijacking | 4,704 |
| CommandInjection | 4,323 |
| SqlInjection | 4,217 |
| XSS | 3,117 |
| Backdoor_Malware | 2,578 |
| Recon-PingSweep | 1,797 |
| Uploading_Attack | 985 |

### `attack_class` (EDA somente)

| valor | n |
| --- | ---: |
| DDoS | 441,869 |
| Benign | 160,000 |
| DoS | 159,887 |
| Recon | 151,834 |
| Mirai | 119,829 |
| Spoofing | 79,938 |
| Web-based | 19,924 |
| BruteForce | 10,521 |

Consistência: BenignTraffic ↔ `label==0`: True; `attack_class==Benign` ↔ `label==0`: True; `Label` == `Label_orig`: True.

## Qualidade

- nulos: nenhum
- duplicatas no train: 27,291
- colunas constantes: `Telnet`
- quase-constantes (moda ≥ 99,5%): `Drate` (99.9966%), `ece_flag_number` (99.9988%), `cwr_flag_number` (99.9990%), `DNS` (99.9064%), `SMTP` (99.9999%), `SSH` (99.8675%), `IRC` (99.9997%), `DHCP` (99.9999%), `ARP` (99.9350%), `IPv` (99.8870%), `LLC` (99.8870%)

## ICMP neste fonte

O README/escopo listavam tipo, código, echo request/reply e latência de ping. **Essas colunas não existem.** Há o Indicador ICMP (coluna `ICMP`, 0/1) e Labels (`DDoS-ICMP_Flood`, `DDoS-ICMP_Fragmentation`, `Recon-PingSweep`). Sem captura de pacotes.

- coluna `ICMP`: True (nunique=2)
- Fluxos com `ICMP > 0`: 79,111
- Fluxos com `Protocol Type == 1`: 38,906
- `Protocol Type` nunique: 3829 (float agregado pelo CIC, não é 1/6/17 limpo)
- `Recon-PingSweep`: 1,797 linhas, `ICMP > 0`: 0 — ping sweep **não** acende o indicador
- `Label` quando `ICMP > 0`: {"DDoS-ICMP_Flood": 40023, "DDoS-ICMP_Fragmentation": 38917, "DoS-UDP_Flood": 122, "Mirai-greip_flood": 11, "DDoS-UDP_Fragmentation": 9, "Mirai-greeth_flood": 8, "Mirai-udpplain": 6, "MITM-ArpSpoofing": 5, "DNS_Spoofing": 5, "BenignTraffic": 3, "DDoS-UDP_Flood": 2}
- colunas tipo/código/echo/ping encontradas: nenhuma
- wishlist ausente: tipo ICMP, código ICMP, echo request, echo reply, latência de ping

## Tempo

- colunas de relógio: nenhuma
- `IAT` (intervalo entre pacotes, **não** relógio): min=0.0, mediana=83253440.0, max=167639424.0
- ordem das linhas não é tempo. Classificador: este Fluxo é Normal ou Attack. Sem janela temporal neste fonte.


## Vazamento entre Splits

Sobreposição **exata** das 46 features de Fluxo (sem rótulos). Interseção > 0 = o mesmo vetor de features em dois Splits. Medido pela interseção de fingerprints (`hash_pandas_object` nas 46 features), não por merge de linhas.

- fingerprints únicos: {"train": 1116511, "validation": 142251, "test": 142231}
- interseção: {"train\u2229validation": 5210, "train\u2229test": 5254, "validation\u2229test": 1078}

Recomendação para o próximo PR: dropar duplicatas *dentro* de cada Split; nas sobreposições entre Splits, **não** mexer em validation/test — remover do train as linhas cuja feature-vector já aparece na avaliação, para o teste não ter sido visto no treino. Não reembaralhar o corpus.


## Recomendações para o PR de preprocessing

Não implementado aqui.

1. Entrada do modelo: as 46 features de Fluxo. Nunca `Label`, `Label_orig`, `attack_class` nem `label`.
2. Alvo: `label` mapeado para Normal/Attack.
3. Fit só no train; validation/test só avaliam.
4. Investigar no Pipeline: colunas constantes/quase-constantes (candidatas a drop), escala das features contínuas (IAT, Rate, tamanhos — magnitudes diferentes), `Protocol Type` float (milhares de valores, agregação CIC).
5. Não inventar tipo/código ICMP. Não agregar em janela neste fonte.
6. Manter os Splits publicados; não reembaralhar.
7. Attack é **maioria** neste subsample (~86% no train). Accuracy isolada continua inútil; o exemplo “99% Normal” do escopo **não** descreve esta fonte.

## Como reproduzir

```bash
uv run python scripts/prepare_dataset.py
uv run python -m netguard_ml.data.eda --on train --leakage
```
