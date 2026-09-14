"""EDA do Subsample CICIoT: schema, target, ICMP, vazamento.

Paths relativos à raiz do repositório. Não usa caminhos absolutos de um SO.

Uso (na raiz do repo, com o dataset já baixado):

    uv run python -m netguard_ml.data.eda
    uv run python -m netguard_ml.data.eda --on recorte
    uv run python -m netguard_ml.data.eda --on train --leakage
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = REPO_ROOT / "data" / "raw" / "ciciot2023-neto-subsample"
SUBSET_PATH = REPO_ROOT / "data" / "subset" / "ciciot2023_subset.parquet"

ROTULOS = ("Label", "Label_orig", "attack_class", "label")
SPLITS = ("train", "validation", "test")
QUASE_CONSTANTE = 0.995
WISHLIST_ICMP = (
    "tipo ICMP",
    "código ICMP",
    "echo request",
    "echo reply",
    "latência de ping",
)


def colunas_feature(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in ROTULOS]


def carregar(origem: str) -> pd.DataFrame:
    if origem == "recorte":
        caminho = SUBSET_PATH
    elif origem in SPLITS:
        caminho = RAW_DIR / f"{origem}.parquet"
    else:
        raise ValueError(f"origem desconhecida: {origem}")
    if not caminho.exists():
        raise FileNotFoundError(
            f"arquivo não encontrado: {caminho}\n"
            "rode: uv run python scripts/prepare_dataset.py"
        )
    return pd.read_parquet(caminho)


def mapear_target(serie: pd.Series) -> pd.Series:
    return serie.map({0: "Normal", 1: "Attack"})


def schema_features(df: pd.DataFrame) -> list[dict[str, str]]:
    linhas = []
    for nome in colunas_feature(df):
        linhas.append({"nome": nome, "tipo": str(df[nome].dtype)})
    return linhas


def distribuicao(serie: pd.Series) -> dict[str, int]:
    return {str(k): int(v) for k, v in serie.value_counts().items()}


def nulos_e_constantes(df: pd.DataFrame) -> dict:
    feats = colunas_feature(df)
    n = len(df)
    nulos = {c: int(df[c].isna().sum()) for c in feats if df[c].isna().any()}
    constantes = []
    quase = []
    for c in feats:
        nunique = int(df[c].nunique(dropna=False))
        if nunique <= 1:
            constantes.append(c)
            continue
        freq = float(df[c].value_counts(dropna=False).iloc[0] / n)
        if freq >= QUASE_CONSTANTE:
            quase.append({"coluna": c, "fracao_moda": round(freq, 6)})
    return {
        "linhas": n,
        "nulos": nulos,
        "duplicatas_no_split": int(df.duplicated().sum()),
        "constantes": constantes,
        "quase_constantes": quase,
    }


def consistencia_rotulos(df: pd.DataFrame) -> dict:
    label_ok = bool(((df["Label"] == "BenignTraffic") == (df["label"] == 0)).all())
    class_ok = bool(((df["attack_class"] == "Benign") == (df["label"] == 0)).all())
    orig_igual = bool((df["Label"] == df["Label_orig"]).all())
    return {
        "BenignTraffic_iff_label_0": label_ok,
        "attack_class_Benign_iff_label_0": class_ok,
        "Label_igual_Label_orig": orig_igual,
    }


def icmp(df: pd.DataFrame) -> dict:
    nomes_wishlist = [
        c
        for c in df.columns
        if any(
            tok in c.lower()
            for tok in ("echo", "ping", "icmp_type", "icmp_code", "type", "code")
        )
        and c not in ("ICMP", "Protocol Type")
    ]
    tem_icmp = "ICMP" in df.columns
    icmp_pos = int((df["ICMP"] > 0).sum()) if tem_icmp else 0
    proto = df["Protocol Type"] if "Protocol Type" in df.columns else None
    proto1 = int((proto == 1).sum()) if proto is not None else 0
    labels_icmp = {}
    if tem_icmp:
        mask = df["ICMP"] > 0
        labels_icmp = distribuicao(df.loc[mask, "Label"]) if mask.any() else {}
    ping = (
        df[df["Label"] == "Recon-PingSweep"] if "Label" in df.columns else df.iloc[0:0]
    )
    return {
        "coluna_ICMP": tem_icmp,
        "icmp_nunique": int(df["ICMP"].nunique()) if tem_icmp else 0,
        "fluxos_ICMP_gt_0": icmp_pos,
        "fluxos_Protocol_Type_1": proto1,
        "protocol_type_nunique": int(proto.nunique()) if proto is not None else 0,
        "labels_quando_ICMP_gt_0": labels_icmp,
        "Recon-PingSweep_n": int(len(ping)),
        "Recon-PingSweep_ICMP_gt_0": int((ping["ICMP"] > 0).sum())
        if tem_icmp and len(ping)
        else 0,
        "colunas_tipo_codigo_echo_ping": nomes_wishlist,
        "wishlist_ausente": list(WISHLIST_ICMP),
    }


def timestamps(df: pd.DataFrame) -> dict:
    suspeitas = [
        c
        for c in df.columns
        if any(
            tok in c.lower() for tok in ("time", "timestamp", "date", "epoch", "clock")
        )
    ]
    iat = {}
    if "IAT" in df.columns:
        s = df["IAT"]
        iat = {
            "min": float(s.min()),
            "mediana": float(s.median()),
            "max": float(s.max()),
        }
    return {
        "colunas_de_relogio": suspeitas,
        "IAT": iat,
        "IAT_nao_e_relogio": True,
    }


def vazamento_features(df: pd.DataFrame) -> dict:
    feats = set(colunas_feature(df))
    rotulos_nas_features = [r for r in ROTULOS if r in feats]
    return {
        "rotulos_nas_features": rotulos_nas_features,
        "n_features": len(feats),
        "n_rotulos": sum(1 for r in ROTULOS if r in df.columns),
    }


def fingerprints(df: pd.DataFrame) -> pd.Series:
    return pd.util.hash_pandas_object(df[colunas_feature(df)], index=False)


def vazamento_entre_splits(splits: dict[str, pd.DataFrame]) -> dict:
    fps = {nome: set(fingerprints(df)) for nome, df in splits.items()}
    pares = {}
    nomes = list(fps)
    for i, a in enumerate(nomes):
        for b in nomes[i + 1 :]:
            pares[f"{a}∩{b}"] = len(fps[a] & fps[b])
    return {
        "fingerprints_por_split": {k: len(v) for k, v in fps.items()},
        "intersecao": pares,
    }


def resumo(origem: str, df: pd.DataFrame) -> dict:
    return {
        "origem": origem,
        "linhas": int(len(df)),
        "schema": schema_features(df),
        "target_Normal_Attack": distribuicao(mapear_target(df["label"])),
        "label_0_1": distribuicao(df["label"]),
        "Label": distribuicao(df["Label"]),
        "attack_class": distribuicao(df["attack_class"]),
        "qualidade": nulos_e_constantes(df),
        "consistencia_rotulos": consistencia_rotulos(df),
        "icmp": icmp(df),
        "tempo": timestamps(df),
        "vazamento_features": vazamento_features(df),
    }


def _fmt_contagem(d: dict[str, int]) -> str:
    linhas = [f"| {k} | {v:,} |" for k, v in d.items()]
    return "| valor | n |\n| --- | ---: |\n" + "\n".join(linhas)


def render_markdown(train: dict, recorte: dict | None, leakage: dict | None) -> str:
    schema_linhas = "\n".join(
        f"| `{c['nome']}` | `{c['tipo']}` |" for c in train["schema"]
    )
    constantes = train["qualidade"]["constantes"]
    quase = train["qualidade"]["quase_constantes"]
    const_txt = ", ".join(f"`{c}`" for c in constantes) if constantes else "(nenhuma)"
    quase_txt = (
        ", ".join(f"`{q['coluna']}` ({q['fracao_moda']:.4%})" for q in quase)
        if quase
        else "(nenhuma ≥ 99,5%)"
    )
    nulos = train["qualidade"]["nulos"]
    nulos_txt = json.dumps(nulos, ensure_ascii=False) if nulos else "nenhum"

    recorte_bloco = ""
    if recorte is not None:
        recorte_bloco = f"""
## Recorte de EDA

Usado só para iterar. Regras abaixo saem do **train**.

- linhas: {recorte["linhas"]:,}
- Normal/Attack: {json.dumps(recorte["target_Normal_Attack"], ensure_ascii=False)}
"""

    leak_bloco = ""
    if leakage is not None:
        leak_bloco = f"""
## Vazamento entre Splits

Sobreposição **exata** das 46 features de Fluxo (sem rótulos). Interseção > 0 = o mesmo vetor de features em dois Splits. Medido pela interseção de fingerprints (`hash_pandas_object` nas 46 features), não por merge de linhas.

- fingerprints únicos: {json.dumps(leakage["fingerprints_por_split"])}
- interseção: {json.dumps(leakage["intersecao"], ensure_ascii=False)}

Recomendação para o próximo PR: dropar duplicatas *dentro* de cada Split; nas sobreposições entre Splits, **não** mexer em validation/test — remover do train as linhas cuja feature-vector já aparece na avaliação, para o teste não ter sido visto no treino. Não reembaralhar o corpus.
"""

    cons = train["consistencia_rotulos"]
    icmp = train["icmp"]
    tempo = train["tempo"]
    vaz = train["vazamento_features"]

    return f"""# EDA — Subsample CICIoT

Análise do CICIoT2023 subsample (`random_3way`). Números que viram regra vêm do **train** ({train["linhas"]:,} linhas). O Recorte de EDA só itera.

Unidade: **Fluxo** (linha já agregada pelo CIC). Target: `label == 0` → **Normal**, `label == 1` → **Attack**. `Label` e `attack_class` só nesta EDA — não na saída do primeiro modelo. Schema oficial: [dataset.md](dataset.md).

{recorte_bloco}

## Schema das features de Fluxo

Rótulos à parte (`Label`, `Label_orig`, `attack_class`, `label`): {vaz["n_rotulos"]} colunas. Features: {vaz["n_features"]}.

| coluna | tipo |
| --- | --- |
{schema_linhas}

Rótulos nas features: {vaz["rotulos_nas_features"] or "nenhum (correto)"}.

## Balanceamento

### Normal / Attack (`label`)

{_fmt_contagem(train["target_Normal_Attack"])}

Attack é **maioria** neste subsample (o HuggingFace capou benignos em 200 mil no corpus e cortou ataques por subtipo). O exemplo de “99% Normal” do escopo não se aplica a esta fonte. Accuracy isolada continua inútil.

`label` bruto: {json.dumps(train["label_0_1"])}.

### `Label` (EDA somente)

{_fmt_contagem(train["Label"])}

### `attack_class` (EDA somente)

{_fmt_contagem(train["attack_class"])}

Consistência: BenignTraffic ↔ `label==0`: {cons["BenignTraffic_iff_label_0"]}; `attack_class==Benign` ↔ `label==0`: {cons["attack_class_Benign_iff_label_0"]}; `Label` == `Label_orig`: {cons["Label_igual_Label_orig"]}.

## Qualidade

- nulos: {nulos_txt}
- duplicatas no train: {train["qualidade"]["duplicatas_no_split"]:,}
- colunas constantes: {const_txt}
- quase-constantes (moda ≥ 99,5%): {quase_txt}

## ICMP neste fonte

O README/escopo listavam tipo, código, echo request/reply e latência de ping. **Essas colunas não existem.** Há o Indicador ICMP (coluna `ICMP`, 0/1) e Labels (`DDoS-ICMP_Flood`, `DDoS-ICMP_Fragmentation`, `Recon-PingSweep`). Sem captura de pacotes.

- coluna `ICMP`: {icmp["coluna_ICMP"]} (nunique={icmp["icmp_nunique"]})
- Fluxos com `ICMP > 0`: {icmp["fluxos_ICMP_gt_0"]:,}
- Fluxos com `Protocol Type == 1`: {icmp["fluxos_Protocol_Type_1"]:,}
- `Protocol Type` nunique: {icmp["protocol_type_nunique"]} (float agregado pelo CIC, não é 1/6/17 limpo)
- `Recon-PingSweep`: {icmp["Recon-PingSweep_n"]:,} linhas, `ICMP > 0`: {icmp["Recon-PingSweep_ICMP_gt_0"]} — ping sweep **não** acende o indicador
- `Label` quando `ICMP > 0`: {json.dumps(icmp["labels_quando_ICMP_gt_0"], ensure_ascii=False)}
- colunas tipo/código/echo/ping encontradas: {icmp["colunas_tipo_codigo_echo_ping"] or "nenhuma"}
- wishlist ausente: {", ".join(icmp["wishlist_ausente"])}

## Tempo

- colunas de relógio: {tempo["colunas_de_relogio"] or "nenhuma"}
- `IAT` (intervalo entre pacotes, **não** relógio): min={tempo["IAT"].get("min")}, mediana={tempo["IAT"].get("mediana")}, max={tempo["IAT"].get("max")}
- ordem das linhas não é tempo. Classificador: este Fluxo é Normal ou Attack. Sem janela temporal neste fonte.

{leak_bloco}

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
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EDA do Subsample CICIoT")
    p.add_argument(
        "--on",
        choices=("recorte", "train"),
        default="train",
        help="fonte principal do relatório (default: train, a fonte da verdade)",
    )
    p.add_argument(
        "--leakage",
        action="store_true",
        help="compara fingerprints de train/validation/test",
    )
    p.add_argument(
        "--write-docs",
        action="store_true",
        help="grava docs/eda.md",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    recorte = None
    if SUBSET_PATH.exists():
        recorte = resumo("recorte", carregar("recorte"))
        print(f"recorte: {recorte['linhas']} linhas")

    df = carregar(args.on)
    principal = resumo(args.on, df)
    print(f"{args.on}: {principal['linhas']} linhas")
    print("schema features:", len(principal["schema"]))
    print("Normal/Attack:", principal["target_Normal_Attack"])
    print("constantes:", principal["qualidade"]["constantes"])
    print("ICMP>0:", principal["icmp"]["fluxos_ICMP_gt_0"])

    leakage = None
    if args.leakage:
        splits = {nome: carregar(nome) for nome in SPLITS}
        leakage = vazamento_entre_splits(splits)
        print("interseção fingerprints:", leakage["intersecao"])

    if args.on != "train":
        print("aviso: regras do projeto devem ser confirmadas com --on train")

    md = render_markdown(
        train=principal if args.on == "train" else resumo("train", carregar("train")),
        recorte=recorte,
        leakage=leakage,
    )
    if args.write_docs:
        dest = REPO_ROOT / "docs" / "eda.md"
        dest.write_text(md, encoding="utf-8")
        print(f"gravado: {dest}")
    else:
        print(md)


if __name__ == "__main__":
    main()
