from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from netguard_ml.data import (
    DatasetReader,
    DatasetSource,
    UnsupportedDatasetFormatError,
    register_reader,
)


def _assert_loaded(frame: pl.DataFrame, expected: pl.DataFrame) -> None:
    assert_frame_equal(frame, expected, check_dtypes=False)


def test_dataset_source_loads_parquet(
    tmp_path: Path, sample_frame: pl.DataFrame
) -> None:
    path = tmp_path / "split.parquet"
    sample_frame.write_parquet(path)

    loaded = DatasetSource(path).load()

    _assert_loaded(loaded, sample_frame)


def test_dataset_source_loads_csv(tmp_path: Path, sample_frame: pl.DataFrame) -> None:
    path = tmp_path / "split.csv"
    sample_frame.write_csv(path)

    loaded = DatasetSource(path).load()

    _assert_loaded(loaded, sample_frame)


def test_dataset_source_loads_tsv(tmp_path: Path, sample_frame: pl.DataFrame) -> None:
    path = tmp_path / "split.tsv"
    sample_frame.write_csv(path, separator="\t")

    loaded = DatasetSource(path).load()

    _assert_loaded(loaded, sample_frame)


def test_dataset_source_loads_json(tmp_path: Path, sample_frame: pl.DataFrame) -> None:
    path = tmp_path / "split.json"
    sample_frame.write_json(path)

    loaded = DatasetSource(path).load()

    _assert_loaded(loaded, sample_frame)


def test_dataset_source_is_case_insensitive_for_suffix(
    tmp_path: Path, sample_frame: pl.DataFrame
) -> None:
    path = tmp_path / "split.CSV"
    sample_frame.write_csv(path)

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
    tmp_path: Path, sample_frame: pl.DataFrame
) -> None:
    path = tmp_path / "ignored.bin"
    path.write_bytes(b"not tabular")

    class FakeReader(DatasetReader):
        def read(self, path: Path) -> pl.DataFrame:
            _ = path
            return sample_frame

    loaded = DatasetSource(path, reader=FakeReader()).load()

    _assert_loaded(loaded, sample_frame)


def test_register_reader_extends_supported_formats(
    tmp_path: Path, sample_frame: pl.DataFrame
) -> None:
    path = tmp_path / "split.fakedata"
    path.write_text("ignored", encoding="utf-8")

    class FakeReader(DatasetReader):
        def read(self, path: Path) -> pl.DataFrame:
            _ = path
            return sample_frame

    register_reader(".fakedata", FakeReader)

    loaded = DatasetSource(path).load()

    _assert_loaded(loaded, sample_frame)
