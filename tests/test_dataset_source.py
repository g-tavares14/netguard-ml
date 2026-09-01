from pathlib import Path

import pandas as pd
import pytest

from netguard_ml.data import (
    DatasetReader,
    DatasetSource,
    UnsupportedDatasetFormatError,
    register_reader,
)


def _assert_loaded(frame: pd.DataFrame, expected: pd.DataFrame) -> None:
    pd.testing.assert_frame_equal(
        frame.reset_index(drop=True),
        expected.reset_index(drop=True),
        check_dtype=False,
    )


def test_dataset_source_loads_parquet(
    tmp_path: Path, sample_frame: pd.DataFrame
) -> None:
    path = tmp_path / "split.parquet"
    sample_frame.to_parquet(path, index=False)

    loaded = DatasetSource(path).load()

    _assert_loaded(loaded, sample_frame)


def test_dataset_source_loads_csv(tmp_path: Path, sample_frame: pd.DataFrame) -> None:
    path = tmp_path / "split.csv"
    sample_frame.to_csv(path, index=False)

    loaded = DatasetSource(path).load()

    _assert_loaded(loaded, sample_frame)


def test_dataset_source_loads_tsv(tmp_path: Path, sample_frame: pd.DataFrame) -> None:
    path = tmp_path / "split.tsv"
    sample_frame.to_csv(path, index=False, sep="\t")

    loaded = DatasetSource(path).load()

    _assert_loaded(loaded, sample_frame)


def test_dataset_source_loads_json(tmp_path: Path, sample_frame: pd.DataFrame) -> None:
    path = tmp_path / "split.json"
    sample_frame.to_json(path, orient="records")

    loaded = DatasetSource(path).load()

    _assert_loaded(loaded, sample_frame)


def test_dataset_source_is_case_insensitive_for_suffix(
    tmp_path: Path, sample_frame: pd.DataFrame
) -> None:
    path = tmp_path / "split.CSV"
    sample_frame.to_csv(path, index=False)

    loaded = DatasetSource(path).load()

    _assert_loaded(loaded, sample_frame)


def test_dataset_source_rejects_unknown_suffix(tmp_path: Path) -> None:
    path = tmp_path / "split.txt"
    path.write_text("not a dataset", encoding="utf-8")

    with pytest.raises(UnsupportedDatasetFormatError, match="formato não suportado"):
        DatasetSource(path)


def test_dataset_source_rejects_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "missing.parquet"

    with pytest.raises(FileNotFoundError):
        DatasetSource(path).load()


def test_dataset_source_rejects_directory(tmp_path: Path) -> None:
    directory = tmp_path / "folder.parquet"
    directory.mkdir()

    with pytest.raises(IsADirectoryError):
        DatasetSource(directory).load()


def test_dataset_source_uses_injected_reader(
    tmp_path: Path, sample_frame: pd.DataFrame
) -> None:
    path = tmp_path / "ignored.bin"
    path.write_bytes(b"not tabular")

    class FakeReader(DatasetReader):
        def read(self, path: Path) -> pd.DataFrame:
            _ = path
            return sample_frame

    loaded = DatasetSource(path, reader=FakeReader()).load()

    _assert_loaded(loaded, sample_frame)


def test_register_reader_extends_supported_formats(
    tmp_path: Path, sample_frame: pd.DataFrame
) -> None:
    path = tmp_path / "split.fakedata"
    path.write_text("ignored", encoding="utf-8")

    class FakeReader(DatasetReader):
        def read(self, path: Path) -> pd.DataFrame:
            _ = path
            return sample_frame

    register_reader(".fakedata", FakeReader)

    loaded = DatasetSource(path).load()

    _assert_loaded(loaded, sample_frame)
