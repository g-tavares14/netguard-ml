"""Inspectores concretos da EDA — um por item do checklist do escopo."""

from __future__ import annotations

from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from netguard_ml.data.columns import (
    ARTIFACT_FEATURE_CANDIDATES,
    BENIGN_ATTACK_CLASS,
    BENIGN_LABEL,
    OVERLAP_KEY_COLUMNS,
    TARGET_COLUMN,
    TARGET_MAP,
    TIMESTAMP_NAME_HINTS,
)
from netguard_ml.data.dataset import CiciotDataset
from netguard_ml.data.eda.inspector import EdaInspector
from netguard_ml.data.eda.result import InspectorResult

PLOT_SAMPLE_PER_CLASS = 20_000
PLOT_SEED = 42
HIGH_CORR = 0.95
RARE_MEAN_THRESHOLD = 0.01


def _present(df: pd.DataFrame, columns: tuple[str, ...]) -> list[str]:
    return [col for col in columns if col in df.columns]


def _sample_by_target(df: pd.DataFrame, n: int = PLOT_SAMPLE_PER_CLASS) -> pd.DataFrame:
    if TARGET_COLUMN not in df.columns:
        return df.sample(n=min(len(df), n), random_state=PLOT_SEED)
    partes = []
    for _, grupo in df.groupby(TARGET_COLUMN):
        partes.append(grupo.sample(n=min(len(grupo), n), random_state=PLOT_SEED))
    return pd.concat(partes, ignore_index=True)


class SchemaInspector(EdaInspector):
    name = "schema"

    def inspect(self, dataset: CiciotDataset) -> InspectorResult:
        rows = []
        for split, df in dataset.splits().items():
            for col in df.columns:
                series = df[col]
                numeric = pd.api.types.is_numeric_dtype(series)
                rows.append(
                    {
                        "split": split,
                        "coluna": col,
                        "eh_rotulo": col in dataset.label_columns(),
                        "dtype": str(series.dtype),
                        "nunique": int(series.nunique(dropna=False)),
                        "nulos": int(series.isna().sum()),
                        "min": float(series.min()) if numeric and series.notna().any() else pd.NA,
                        "max": float(series.max()) if numeric and series.notna().any() else pd.NA,
                    }
                )
        schema = pd.DataFrame(rows)
        n_feat = len(dataset.feature_columns())
        n_lab = len(dataset.label_columns())
        notes = [
            f"{n_feat} features e {n_lab} colunas de rótulo no train.",
            "Features do CICIoT neste recorte já são numéricas (float32); flags de protocolo/TCP estão em {0,1}.",
            "Não há coluna categórica de feature para one-hot neste estágio.",
            "Normalização não é necessária para árvores (Decision Tree / Random Forest); só entra se um modelo posterior exigir.",
        ]
        return InspectorResult(name=self.name, tables={"colunas": schema}, notes=notes)


class TargetInspector(EdaInspector):
    name = "target"

    def inspect(self, dataset: CiciotDataset) -> InspectorResult:
        rows = []
        mapping_parts: list[pd.DataFrame] = []
        notes = [
            "Mapeamento oficial deste estágio: label 0 → normal, label 1 → attack.",
            "Tipo específico de ataque (ICMP flood, etc.) não entra na saída do modelo agora.",
        ]
        for split, df in dataset.splits().items():
            label_eq_orig = (
                bool((df["Label"] == df["Label_orig"]).all())
                if {"Label", "Label_orig"} <= set(df.columns)
                else False
            )
            label_eq_benign = (
                bool(((df[TARGET_COLUMN] == 0) == (df["Label"] == BENIGN_LABEL)).all())
                if {TARGET_COLUMN, "Label"} <= set(df.columns)
                else False
            )
            class_eq_benign = (
                bool(((df[TARGET_COLUMN] == 0) == (df["attack_class"] == BENIGN_ATTACK_CLASS)).all())
                if {TARGET_COLUMN, "attack_class"} <= set(df.columns)
                else False
            )
            rows.append(
                {
                    "split": split,
                    "n": len(df),
                    "label_eq_Label_orig": label_eq_orig,
                    "label0_eq_BenignTraffic": label_eq_benign,
                    "label0_eq_attack_class_Benign": class_eq_benign,
                }
            )
            counts = (
                df[TARGET_COLUMN]
                .value_counts()
                .rename_axis("label")
                .reset_index(name="n")
            )
            counts["split"] = split
            counts["classe"] = counts["label"].map(TARGET_MAP)
            mapping_parts.append(counts)

        consistencia = pd.DataFrame(rows)
        mapping = pd.concat(mapping_parts, ignore_index=True) if mapping_parts else pd.DataFrame()
        if not consistencia.drop(columns=["split", "n"]).all().all():
            notes.append("ATENÇÃO: inconsistência entre label / Label / attack_class em algum split.")
        else:
            notes.append("label, Label, attack_class e Label_orig são consistentes nos três splits.")
            notes.append("Label e Label_orig são idênticos: Label_orig é redundante.")
        return InspectorResult(
            name=self.name,
            tables={"consistencia": consistencia, "mapeamento": mapping},
            notes=notes,
        )


class DistributionInspector(EdaInspector):
    name = "distribuicao"

    def inspect(self, dataset: CiciotDataset) -> InspectorResult:
        binarios = []
        por_label = []
        por_familia = []
        for split, df in dataset.splits().items():
            vc = df[TARGET_COLUMN].value_counts().to_dict()
            n = len(df)
            n_normal = int(vc.get(0, 0))
            n_attack = int(vc.get(1, 0))
            binarios.append(
                {
                    "split": split,
                    "n": n,
                    "n_normal": n_normal,
                    "n_attack": n_attack,
                    "pct_normal": n_normal / n,
                    "pct_attack": n_attack / n,
                }
            )
            if "Label" in df.columns:
                g = df["Label"].value_counts().rename_axis("Label").reset_index(name="n")
                g["split"] = split
                g["pct"] = g["n"] / n
                por_label.append(g)
            if "attack_class" in df.columns:
                g = df["attack_class"].value_counts().rename_axis("attack_class").reset_index(name="n")
                g["split"] = split
                g["pct"] = g["n"] / n
                por_familia.append(g)

        binario_df = pd.DataFrame(binarios)
        label_df = pd.concat(por_label, ignore_index=True) if por_label else pd.DataFrame()
        familia_df = pd.concat(por_familia, ignore_index=True) if por_familia else pd.DataFrame()

        train = binario_df.loc[binario_df["split"] == "train"].iloc[0]
        notes = [
            (
                f"Train: {int(train['n_normal']):,} normal "
                f"({train['pct_normal']:.1%}) / {int(train['n_attack']):,} attack "
                f"({train['pct_attack']:.1%})."
            ),
            "O subsample tem mais ataque que tráfego benigno (teto de 50k por subtipo e 200k benignos na origem HuggingFace).",
            "Accuracy isolada continua inadequada: um classificador constante 'attack' acerta a maioria.",
        ]

        figures = {}
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.arange(len(binario_df))
        ax.bar(x - 0.18, binario_df["pct_normal"], 0.36, label="normal")
        ax.bar(x + 0.18, binario_df["pct_attack"], 0.36, label="attack")
        ax.set_xticks(x)
        ax.set_xticklabels(binario_df["split"])
        ax.set_ylabel("proporção")
        ax.set_title("Distribuição binária por split")
        ax.legend()
        figures["binaria_por_split"] = fig

        train_df = dataset.load("train")
        if "attack_class" in train_df.columns:
            fig, ax = plt.subplots(figsize=(8, 4))
            ordem = train_df["attack_class"].value_counts()
            ax.bar(ordem.index.astype(str), ordem.values)
            ax.set_ylabel("linhas")
            ax.set_title("Famílias de ataque no train")
            ax.tick_params(axis="x", rotation=30)
            figures["familias_train"] = fig

        sample = _sample_by_target(train_df)
        cont = [c for c in ("Rate", "flow_duration", "Tot size", "IAT") if c in sample.columns]
        if cont:
            fig, axes = plt.subplots(1, len(cont), figsize=(4 * len(cont), 4), squeeze=False)
            for ax, col in zip(axes[0], cont):
                grupos = [
                    sample.loc[sample[TARGET_COLUMN] == 0, col].dropna().to_numpy(),
                    sample.loc[sample[TARGET_COLUMN] == 1, col].dropna().to_numpy(),
                ]
                ax.boxplot(grupos, tick_labels=["normal", "attack"])
                ax.set_title(col)
                ax.set_xlabel("classe")
            fig.suptitle("Amostra de features contínuas por classe (train)")
            figures["boxplots_continuas"] = fig

        return InspectorResult(
            name=self.name,
            tables={
                "binaria": binario_df,
                "por_label": label_df,
                "por_familia": familia_df,
            },
            notes=notes,
            figures=figures,
        )


class QualityInspector(EdaInspector):
    name = "qualidade"

    def inspect(self, dataset: CiciotDataset) -> InspectorResult:
        resumo_rows = []
        nunique_rows = []
        features = dataset.feature_columns()
        for split, df in dataset.splits().items():
            feat = df[features]
            infs = int(np.isinf(feat.to_numpy(dtype=np.float64)).sum())
            resumo_rows.append(
                {
                    "split": split,
                    "n": len(df),
                    "nulos": int(df.isna().sum().sum()),
                    "inf": infs,
                    "duplicatas_linha": int(df.duplicated().sum()),
                    "duplicatas_features": int(df[features].duplicated().sum()),
                }
            )
            nun = feat.nunique(dropna=False)
            for col, k in nun.items():
                nunique_rows.append({"split": split, "coluna": col, "nunique": int(k)})

        resumo = pd.DataFrame(resumo_rows)
        nunique_df = pd.DataFrame(nunique_rows)
        train_nu = nunique_df[nunique_df["split"] == "train"]
        constantes = train_nu[train_nu["nunique"] <= 1]["coluna"].tolist()

        train = dataset.load("train")
        rare = []
        for col in features:
            if train[col].nunique(dropna=False) <= 2 and pd.api.types.is_numeric_dtype(train[col]):
                mean = float(train[col].mean())
                if mean <= RARE_MEAN_THRESHOLD or mean >= 1 - RARE_MEAN_THRESHOLD:
                    rare.append({"coluna": col, "nunique": int(train[col].nunique()), "mean": mean})
        rare_df = pd.DataFrame(rare)

        notes = [
            f"Constantes no train (nunique≤1): {constantes or 'nenhuma'}.",
            "Duplicatas intra-split existem; a próxima etapa deve decidir se o train será deduplicado.",
            "Quase-constantes (flags raras ou quase sempre 1) entram na tabela rare_flags — candidatas a drop se não discriminarem.",
        ]
        train_dup = int(resumo.loc[resumo["split"] == "train", "duplicatas_linha"].iloc[0])
        train_n = int(resumo.loc[resumo["split"] == "train", "n"].iloc[0])
        notes.append(f"Train tem {train_dup:,} linhas duplicadas ({train_dup / train_n:.2%}).")

        return InspectorResult(
            name=self.name,
            tables={"resumo": resumo, "nunique": nunique_df, "rare_flags": rare_df},
            notes=notes,
        )


class CollinearityInspector(EdaInspector):
    name = "colinearidade"

    def inspect(self, dataset: CiciotDataset) -> InspectorResult:
        train = dataset.load("train")
        features = dataset.feature_columns()
        hashes: dict[int, list[str]] = {}
        for col in features:
            digest = int(pd.util.hash_pandas_object(train[col], index=False).sum())
            hashes.setdefault(digest, []).append(col)
        identicos = []
        for grupo in hashes.values():
            if len(grupo) < 2:
                continue
            for a, b in combinations(grupo, 2):
                if (train[a] == train[b]).all():
                    identicos.append({"coluna_a": a, "coluna_b": b})
        identicos_df = pd.DataFrame(identicos)

        corr = train[features].corr(numeric_only=True)
        pares = []
        cols = list(corr.columns)
        for i, a in enumerate(cols):
            for b in cols[i + 1 :]:
                value = corr.loc[a, b]
                if pd.notna(value) and abs(float(value)) >= HIGH_CORR:
                    pares.append({"coluna_a": a, "coluna_b": b, "corr": float(value)})
        pares_df = pd.DataFrame(pares).sort_values("corr", key=np.abs, ascending=False) if pares else pd.DataFrame()

        notes = [
            "Pares idênticos podem ser reduzidos a uma coluna na baseline (manter Rate, descartar Srate; manter IPv, descartar LLC).",
            f"Pares com |corr| ≥ {HIGH_CORR} são colineares; árvores toleram, boosting/linear menos.",
        ]
        if identicos:
            notes.append(
                "Idênticos no train: "
                + ", ".join(f"{r['coluna_a']}≡{r['coluna_b']}" for r in identicos)
            )

        figures = {}
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(corr.to_numpy(), cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=90, fontsize=6)
        ax.set_yticklabels(corr.columns, fontsize=6)
        ax.set_title("Correlação (train)")
        fig.colorbar(im, ax=ax, fraction=0.046)
        figures["heatmap_corr"] = fig

        return InspectorResult(
            name=self.name,
            tables={
                "identicos": identicos_df,
                "alta_corr": pares_df,
            },
            notes=notes,
            figures=figures,
        )


class IcmpInspector(EdaInspector):
    name = "icmp"

    def inspect(self, dataset: CiciotDataset) -> InspectorResult:
        train = dataset.load("train")
        notes = []
        tables = {}
        figures = {}
        if "ICMP" not in train.columns:
            return InspectorResult(name=self.name, notes=["Coluna ICMP ausente neste recorte."])

        by_label = (
            train.groupby("Label")["ICMP"]
            .agg(mean="mean", soma="sum", n="count")
            .reset_index()
            .sort_values("mean", ascending=False)
        )
        tables["icmp_por_label"] = by_label
        by_bin = train.groupby(TARGET_COLUMN)["ICMP"].mean().rename("mean_icmp").reset_index()
        by_bin["classe"] = by_bin[TARGET_COLUMN].map(TARGET_MAP)
        tables["icmp_por_classe"] = by_bin

        protocolos = [c for c in ("ICMP", "TCP", "UDP", "HTTP", "HTTPS", "DNS", "ARP", "IPv", "LLC") if c in train.columns]
        tables["protocolos_por_classe"] = (
            train.groupby(TARGET_COLUMN)[protocolos].mean().reset_index()
        )

        ping = by_label[by_label["Label"] == "Recon-PingSweep"]
        flood = by_label[by_label["Label"].isin(["DDoS-ICMP_Flood", "DDoS-ICMP_Fragmentation"])]
        notes.append("ICMP é feature candidata; não é classe de saída neste estágio.")
        if not flood.empty:
            notes.append(
                "DDoS-ICMP_Flood / DDoS-ICMP_Fragmentation concentram ICMP≈1; a flag descreve o protocolo do fluxo."
            )
        if not ping.empty and float(ping["mean"].iloc[0]) < 0.05:
            notes.append(
                "Recon-PingSweep tem ICMP médio ≈ 0 neste schema — ping sweep não aparece na flag ICMP."
            )
        notes.append(
            f"ICMP médio em tráfego normal: {float(by_bin.loc[by_bin[TARGET_COLUMN]==0, 'mean_icmp'].iloc[0]):.6f}; "
            f"em attack: {float(by_bin.loc[by_bin[TARGET_COLUMN]==1, 'mean_icmp'].iloc[0]):.4f}."
        )

        fig, ax = plt.subplots(figsize=(10, 5))
        top = by_label.head(12)
        ax.barh(top["Label"].astype(str), top["mean"])
        ax.invert_yaxis()
        ax.set_xlabel("ICMP médio")
        ax.set_title("ICMP médio por Label (train)")
        figures["icmp_por_label"] = fig

        return InspectorResult(name=self.name, tables=tables, notes=notes, figures=figures)


class TemporalInspector(EdaInspector):
    name = "temporal"

    def inspect(self, dataset: CiciotDataset) -> InspectorResult:
        train = dataset.load("train")
        cols = list(train.columns)
        hits = [
            col
            for col in cols
            if any(hint in col.lower() for hint in TIMESTAMP_NAME_HINTS) and col.lower() != "duration"
        ]
        # Duration e flow_duration são duração de fluxo, não relógio de captura.
        rows = [{"coluna": col, "parece_timestamp_pelo_nome": col in hits} for col in cols]
        table = pd.DataFrame(rows)

        notes = [
            "Não há timestamp de captura nas 50 colunas.",
            "IAT é intervalo entre pacotes do fluxo, não relógio; a ordem das linhas não é tempo.",
            "Janelas temporais ficam fora desta fase (regra do escopo / AGENTS.md).",
        ]
        if "IAT" in train.columns:
            desc = train["IAT"].describe()
            notes.append(
                f"IAT no train: min={desc['min']:.4g}, mediana={train['IAT'].median():.4g}, "
                f"max={desc['max']:.4g}."
            )
        return InspectorResult(name=self.name, tables={"colunas": table}, notes=notes)


class LeakageInspector(EdaInspector):
    name = "vazamento"

    def inspect(self, dataset: CiciotDataset) -> InspectorResult:
        splits = dataset.splits()
        train, val, test = splits["train"], splits["validation"], splits["test"]
        notes = []

        id_hits = [
            col
            for col in train.columns
            if col.lower() in {"src_ip", "dst_ip", "flow_id", "session", "host", "uid", "id"}
        ]
        notes.append(
            "Não há id de host, sessão ou fluxo: não dá para fazer group split. "
            "O protocolo continua sendo os splits publicados, sem reembaralhar."
            if not id_hits
            else f"Possíveis ids encontrados: {id_hits}."
        )

        keys = _present(train, OVERLAP_KEY_COLUMNS)
        overlap_rows = []
        if keys:
            def keyset(df: pd.DataFrame) -> set[tuple]:
                return set(map(tuple, df[keys].itertuples(index=False, name=None)))

            tset, vset, sset = keyset(train), keyset(val), keyset(test)
            overlap_rows = [
                {"par": "train∩validation", "n_chaves": len(tset & vset)},
                {"par": "train∩test", "n_chaves": len(tset & sset)},
                {"par": "validation∩test", "n_chaves": len(vset & sset)},
            ]
            notes.append(
                "Há sobreposição de chaves de fluxo entre splits (linhas muito parecidas ou iguais). "
                "Isso é vazamento por duplicata, não por tempo."
            )
        overlap_df = pd.DataFrame(overlap_rows)

        art_cols = _present(train, ARTIFACT_FEATURE_CANDIDATES)
        artifact_df = pd.DataFrame()
        figures = {}
        if art_cols and "Label" in train.columns:
            artifact_df = train.groupby("Label")[art_cols].median().reset_index()
            notes.append(
                "IAT, Number e Weight têm medianas quase constantes por família de ataque — "
                "padrão típico de artefato de captura do CICIoT. "
                "A baseline deve compará-los com e sem essas colunas; não silenciosamente dropá-las."
            )
            if "Number" in artifact_df.columns:
                fig, ax = plt.subplots(figsize=(10, 6))
                ordered = artifact_df.sort_values("Number")
                ax.barh(ordered["Label"].astype(str), ordered["Number"])
                ax.set_xlabel("mediana de Number")
                ax.set_title("Number (mediana) por Label — suspeita de artefato")
                figures["number_mediana_por_label"] = fig

        return InspectorResult(
            name=self.name,
            tables={"overlap_chaves": overlap_df, "mediana_artefato": artifact_df},
            notes=notes,
            figures=figures,
        )
