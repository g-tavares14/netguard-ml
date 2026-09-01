import sys
from collections.abc import Sequence
from pathlib import Path

from netguard_ml.data.reader import DatasetSource
from netguard_ml.data.schema import feature_schema

DEFAULT_RAW_DIR = Path("data/raw/ciciot2023-neto-subsample")
DEFAULT_SPLITS = ("train.parquet", "validation.parquet", "test.parquet")


def default_split_paths() -> list[Path]:
    return [DEFAULT_RAW_DIR / name for name in DEFAULT_SPLITS]


def inspect_datasets(
    paths: Sequence[Path | str],
) -> dict[str, dict[int, dict[str, str]]]:
    """Carrega cada arquivo e devolve nome/tipo das colunas de feature."""
    result: dict[str, dict[int, dict[str, str]]] = {}
    for raw in paths:
        path = Path(raw)
        frame = DatasetSource(path).load()
        result[path.stem] = {
            index: {"nome": info.name, "tipo": info.dtype}
            for index, info in feature_schema(frame).items()
        }
    return result


def main(argv: Sequence[str] | None = None) -> dict[str, dict[int, dict[str, str]]]:
    args = list(argv) if argv is not None else sys.argv[1:]
    paths: Sequence[Path | str] = args if args else default_split_paths()
    info = inspect_datasets(paths)
    print(info)
    return info


if __name__ == "__main__":
    main()
