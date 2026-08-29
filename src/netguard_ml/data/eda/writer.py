from pathlib import Path

import matplotlib.pyplot as plt

from netguard_ml.data.eda.result import InspectorResult


class EdaArtifactWriter:
    """Grava tabelas, notas e figuras de um InspectorResult em artifacts/eda/."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, result: InspectorResult) -> None:
        for table_name, frame in result.tables.items():
            path = self.output_dir / f"{result.name}_{table_name}.csv"
            frame.to_csv(path, index=False)

        if result.notes:
            path = self.output_dir / f"{result.name}_notes.txt"
            path.write_text("\n".join(result.notes) + "\n", encoding="utf-8")

        for fig_name, figure in result.figures.items():
            path = self.output_dir / f"{result.name}_{fig_name}.png"
            figure.savefig(path, bbox_inches="tight", dpi=120)
            plt.close(figure)
