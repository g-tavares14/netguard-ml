from pathlib import Path

import polars as pl
import pytest

from netguard_ml.data.main import inspect_datasets, main


def test_inspect_datasets_keys_by_stem_and_skips_labels(
    tmp_path: Path, sample_frame: pl.DataFrame
) -> None:
    parquet_path = tmp_path / "train.parquet"
    csv_path = tmp_path / "validation.csv"
    sample_frame.write_parquet(parquet_path)
    sample_frame.write_csv(csv_path)

    result = inspect_datasets([parquet_path, csv_path])

    assert set(result) == {"train", "validation"}
    assert result["train"] == {
        0: {"nome": "flow_duration", "tipo": "Float64"},
        1: {"nome": "ICMP", "tipo": "Int64"},
    }
    assert result["validation"][0]["nome"] == "flow_duration"
    assert "Label" not in {col["nome"] for col in result["train"].values()}


def test_main_prints_schema_for_given_paths(
    tmp_path: Path, sample_frame: pl.DataFrame, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "test.json"
    sample_frame.write_json(path)

    returned = main([str(path)])
    printed = capsys.readouterr().out

    assert "flow_duration" in printed
    assert returned["test"][0]["nome"] == "flow_duration"
