"""Acesso ao CICIoT2023 subsample (download, recorte e leitura dos splits)."""

from __future__ import annotations

from pathlib import Path
import urllib.request

import pandas as pd

from netguard_ml.data.columns import LABEL_COLUMNS, SPLITS

BASE_URL = (
    "https://huggingface.co/datasets/lacg030175/CIC-IoT-2023-neto-subsample"
    "/resolve/main/random_3way"
)
ARQUIVOS = {
    "train.parquet": "train-00000-of-00001.parquet",
    "validation.parquet": "validation-00000-of-00001.parquet",
    "test.parquet": "test-00000-of-00001.parquet",
}

SEED = 42
MAX_POR_LABEL = 2000


class CiciotDataset:
    """Único ponto de I/O do subsample: HuggingFace, parquet e recorte de EDA."""

    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root is not None else Path(__file__).resolve().parents[3]
        self.raw_dir = self.root / "data" / "raw" / "ciciot2023-neto-subsample"
        self.subset_dir = self.root / "data" / "subset"
        self._cache: dict[str, pd.DataFrame] = {}

    def path_for(self, split: str) -> Path:
        if split not in SPLITS:
            raise ValueError(f"split inválido: {split!r}; use {SPLITS}")
        return self.raw_dir / f"{split}.parquet"

    def load(self, split: str) -> pd.DataFrame:
        if split not in self._cache:
            path = self.path_for(split)
            if not path.exists():
                raise FileNotFoundError(
                    f"falta {path}. Rode: python scripts/prepare_dataset.py"
                )
            self._cache[split] = pd.read_parquet(path)
        return self._cache[split]

    def splits(self) -> dict[str, pd.DataFrame]:
        return {split: self.load(split) for split in SPLITS}

    def feature_columns(self) -> list[str]:
        return [col for col in self.load("train").columns if col not in LABEL_COLUMNS]

    def label_columns(self) -> list[str]:
        return [col for col in LABEL_COLUMNS if col in self.load("train").columns]

    def download(self) -> None:
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        for local, remoto in ARQUIVOS.items():
            destino = self.raw_dir / local
            if destino.exists():
                print(f"já existe: {destino}")
                continue
            url = f"{BASE_URL}/{remoto}"
            print(f"baixando {local} ...")
            pedido = urllib.request.Request(url, headers={"User-Agent": "netguard-ml"})
            with urllib.request.urlopen(pedido) as resp, open(destino, "wb") as saida:
                saida.write(resp.read())
            print(f"salvo em {destino}")
        print("download ok")

    def recorte(self, max_por_label: int = MAX_POR_LABEL, seed: int = SEED) -> Path:
        origem = self.path_for("train")
        if not origem.exists():
            raise FileNotFoundError(f"rode download() antes: falta {origem}")

        df = pd.read_parquet(origem)
        partes = []
        for _, grupo in df.groupby("Label"):
            n = min(len(grupo), max_por_label)
            partes.append(grupo.sample(n=n, random_state=seed))

        recorte = (
            pd.concat(partes, ignore_index=True)
            .sample(frac=1, random_state=seed)
            .reset_index(drop=True)
        )

        self.subset_dir.mkdir(parents=True, exist_ok=True)
        saida = self.subset_dir / "ciciot2023_subset.parquet"
        recorte.to_parquet(saida, index=False)
        print(f"recorte: {len(recorte)} linhas -> {saida}")
        print(recorte["Label"].value_counts().to_string())
        return saida
