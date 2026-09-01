from dataclasses import dataclass

import pandas as pd

LABEL_COLUMNS = frozenset({"Label", "Label_orig", "attack_class", "label"})


@dataclass(frozen=True, slots=True)
class ColumnInfo:
    name: str
    dtype: str


def feature_schema(frame: pd.DataFrame) -> dict[int, ColumnInfo]:
    """Nome e dtype de cada coluna que não é rótulo, na ordem original."""
    schema: dict[int, ColumnInfo] = {}
    for index, column in enumerate(frame.columns):
        name = str(column)
        if name in LABEL_COLUMNS:
            continue
        series = frame.iloc[:, index]
        schema[index] = ColumnInfo(name=name, dtype=str(series.dtype))
    return schema
