from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from netguard_ml.data.columns import SPLITS
from netguard_ml.data.dataset import CiciotDataset
from netguard_ml.data.eda.inspectors import SchemaInspector, TargetInspector
from netguard_ml.data.eda.pipeline import EdaPipeline, default_inspectors
from netguard_ml.data.eda.writer import EdaArtifactWriter


def _tiny_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "flow_duration": [0.1, 0.2, 0.1, 0.3],
            "Header_Length": [10.0, 20.0, 10.0, 30.0],
            "Rate": [1.0, 2.0, 1.0, 3.0],
            "Srate": [1.0, 2.0, 1.0, 3.0],
            "IPv": [1.0, 1.0, 1.0, 1.0],
            "LLC": [1.0, 1.0, 1.0, 1.0],
            "Telnet": [0.0, 0.0, 0.0, 0.0],
            "ICMP": [0.0, 1.0, 0.0, 0.0],
            "TCP": [1.0, 0.0, 1.0, 1.0],
            "IAT": [1.0, 8.0e7, 2.0, 3.0],
            "Number": [5.5, 9.5, 5.5, 5.5],
            "Weight": [38.5, 141.55, 38.5, 38.5],
            "Tot size": [40.0, 50.0, 40.0, 45.0],
            "Label": ["BenignTraffic", "DDoS-ICMP_Flood", "BenignTraffic", "Recon-PingSweep"],
            "Label_orig": ["BenignTraffic", "DDoS-ICMP_Flood", "BenignTraffic", "Recon-PingSweep"],
            "attack_class": ["Benign", "DDoS", "Benign", "Recon"],
            "label": np.array([0, 1, 0, 1], dtype=np.int8),
        }
    )


@pytest.fixture
def dataset(tmp_path: Path) -> CiciotDataset:
    raw = tmp_path / "data" / "raw" / "ciciot2023-neto-subsample"
    raw.mkdir(parents=True)
    frame = _tiny_frame()
    for split in SPLITS:
        frame.to_parquet(raw / f"{split}.parquet", index=False)
    return CiciotDataset(root=tmp_path)


def test_load_and_column_groups(dataset: CiciotDataset) -> None:
    train = dataset.load("train")
    assert len(train) == 4
    assert "ICMP" in dataset.feature_columns()
    assert "label" in dataset.label_columns()
    assert "label" not in dataset.feature_columns()


def test_schema_and_target(dataset: CiciotDataset) -> None:
    schema = SchemaInspector().inspect(dataset)
    assert schema.name == "schema"
    assert not schema.tables["colunas"].empty
    target = TargetInspector().inspect(dataset)
    consistencia = target.tables["consistencia"]
    assert consistencia["label0_eq_BenignTraffic"].all()


def test_pipeline_writes_artifacts(dataset: CiciotDataset, tmp_path: Path) -> None:
    out = tmp_path / "artifacts" / "eda"
    results = EdaPipeline(dataset, EdaArtifactWriter(out), default_inspectors()).run()
    assert len(results) == 8
    assert (out / "schema_colunas.csv").exists()
    assert (out / "target_notes.txt").exists()
    assert (out / "vazamento_overlap_chaves.csv").exists()
