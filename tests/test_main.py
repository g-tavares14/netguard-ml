from pathlib import Path

import pandas as pd
import pytest

from netguard_ml.data.main import inspect_datasets, main


def test_inspect_datasets_keys_by_stem_and_skips_labels(
    tmp_path: Path, sample_frame: pd.DataFrame
) -> None:
    parquet_path = tmp_path / "train.parquet"
    csv_path = tmp_path / "validation.csv"
    sample_frame.to_parquet(parquet_path, index=False)
    sample_frame.to_csv(csv_path, index=False)

    result = inspect_datasets([parquet_path, csv_path])

    assert set(result) == {"train", "validation"}
    assert result["train"] == {
        0: {"nome": "flow_duration", "tipo": "float64"},
        1: {"nome": "ICMP", "tipo": "int64"},
    }
    assert result["validation"][0]["nome"] == "flow_duration"
    assert "Label" not in {col["nome"] for col in result["train"].values()}


def test_main_prints_schema_for_given_paths(
    tmp_path: Path, sample_frame: pd.DataFrame, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "test.json"
    sample_frame.to_json(path, orient="records")

    returned = main([str(path)])
    printed = capsys.readouterr().out

    assert "flow_duration" in printed
    assert returned["test"][0]["nome"] == "flow_duration"
