"""CLI: executa a pipeline de EDA sobre os splits oficiais."""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from netguard_ml.data.dataset import CiciotDataset
from netguard_ml.data.eda.pipeline import EdaPipeline
from netguard_ml.data.eda.writer import EdaArtifactWriter


def main() -> None:
    dataset = CiciotDataset(root=ROOT)
    writer = EdaArtifactWriter(ROOT / "artifacts" / "eda")
    EdaPipeline(dataset, writer).run()


if __name__ == "__main__":
    main()
