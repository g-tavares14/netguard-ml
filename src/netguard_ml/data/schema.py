from dataclasses import dataclass

import polars as pl

LABEL_COLUMNS = frozenset({"Label", "Label_orig", "attack_class", "label"})


@dataclass(frozen=True, slots=True)
class ColumnInfo:
    name: str
    dtype: str


def feature_schema(frame: pl.DataFrame) -> dict[int, ColumnInfo]:
    """Nome e dtype de cada coluna que não é rótulo, na ordem original."""
    schema: dict[int, ColumnInfo] = {}
    for index, (name, dtype) in enumerate(frame.schema.items()):
        if name in LABEL_COLUMNS:
            continue
        schema[index] = ColumnInfo(name=name, dtype=str(dtype))
    return schema
