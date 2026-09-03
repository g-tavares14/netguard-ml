from abc import ABC, abstractmethod
from pathlib import Path

import polars as pl


class UnsupportedDatasetFormatError(ValueError):
    """Nenhum leitor registrado para a extensão do arquivo."""


class DatasetReader(ABC):
    """Lê um dataset tabular do disco para um DataFrame."""

    @abstractmethod
    def read(self, path: Path) -> pl.DataFrame:
        """Carrega o arquivo em `path`."""


class ParquetDatasetReader(DatasetReader):
    def read(self, path: Path) -> pl.DataFrame:
        return pl.read_parquet(path)


class CsvDatasetReader(DatasetReader):
    def read(self, path: Path) -> pl.DataFrame:
        return pl.read_csv(path)


class TsvDatasetReader(DatasetReader):
    def read(self, path: Path) -> pl.DataFrame:
        return pl.read_csv(path, separator="\t")


class JsonDatasetReader(DatasetReader):
    def read(self, path: Path) -> pl.DataFrame:
        return pl.read_json(path)


_READERS: dict[str, type[DatasetReader]] = {
    ".parquet": ParquetDatasetReader,
    ".csv": CsvDatasetReader,
    ".tsv": TsvDatasetReader,
    ".json": JsonDatasetReader,
}


def register_reader(suffix: str, reader_cls: type[DatasetReader]) -> None:
    """Associa uma extensão de arquivo a um `DatasetReader`."""
    normalized = suffix.lower() if suffix.startswith(".") else f".{suffix.lower()}"
    _READERS[normalized] = reader_cls


def supported_suffixes() -> tuple[str, ...]:
    return tuple(sorted(_READERS))


def reader_for(path: Path) -> DatasetReader:
    suffix = path.suffix.lower()
    try:
        return _READERS[suffix]()
    except KeyError:
        supported = ", ".join(supported_suffixes())
        raise UnsupportedDatasetFormatError(
            f"formato não suportado {suffix!r} em {path}; formatos: {supported}"
        ) from None


class DatasetSource:
    """Abre um dataset sem o chamador conhecer o formato do arquivo."""

    def __init__(
        self,
        path: Path | str,
        *,
        reader: DatasetReader | None = None,
    ) -> None:
        self.path = Path(path)
        self._reader = reader if reader is not None else reader_for(self.path)

    def load(self) -> pl.DataFrame:
        if self.path.is_dir():
            raise IsADirectoryError(self.path)
        if not self.path.is_file():
            raise FileNotFoundError(self.path)
        return self._reader.read(self.path)
