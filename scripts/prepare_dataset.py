"""CLI: baixa o CICIoT2023 subsample e gera o recorte local para EDA rápida."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from netguard_ml.data.dataset import CiciotDataset


if __name__ == "__main__":
    dados = CiciotDataset(root=ROOT)
    dados.download()
    dados.recorte()
