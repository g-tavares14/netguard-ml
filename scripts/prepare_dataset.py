"""Baixa o CICIoT2023 do HuggingFace e gera um recorte local para EDA/treino rápido."""

import urllib.request
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "ciciot2023-neto-subsample"
SUBSET_DIR = ROOT / "data" / "subset"

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
    def download(self):
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        for local, remoto in ARQUIVOS.items():
            destino = RAW_DIR / local
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

    def recorte(self, max_por_label=MAX_POR_LABEL, seed=SEED):
        origem = RAW_DIR / "train.parquet"
        if not origem.exists():
            raise FileNotFoundError(f"rode download() antes: falta {origem}")

        df = pl.read_parquet(origem)
        partes = [
            grupo.sample(n=min(len(grupo), max_por_label), seed=seed, shuffle=True)
            for _, grupo in df.group_by("Label")
        ]

        recorte = pl.concat(partes).sample(fraction=1.0, seed=seed, shuffle=True)

        SUBSET_DIR.mkdir(parents=True, exist_ok=True)
        saida = SUBSET_DIR / "ciciot2023_subset.parquet"
        recorte.write_parquet(saida)
        print(f"recorte: {len(recorte)} linhas -> {saida}")
        print(recorte["Label"].value_counts().sort("count", descending=True))


if __name__ == "__main__":
    dados = CiciotDataset()
    dados.download()
    dados.recorte()
