import polars as pl

from netguard_ml.data import ColumnInfo, feature_schema


def test_feature_schema_skips_label_columns(sample_frame: pl.DataFrame) -> None:
    schema = feature_schema(sample_frame)

    assert schema == {
        0: ColumnInfo(name="flow_duration", dtype="Float64"),
        1: ColumnInfo(name="ICMP", dtype="Int64"),
    }


def test_feature_schema_keeps_original_column_index() -> None:
    frame = pl.DataFrame(
        {
            "Label": ["BenignTraffic"],
            "rate": [1.5],
            "label": [0],
            "IAT": [0.2],
        }
    )

    schema = feature_schema(frame)

    assert list(schema) == [1, 3]
    assert schema[1].name == "rate"
    assert schema[3].name == "IAT"


def test_feature_schema_empty_when_only_labels() -> None:
    frame = pl.DataFrame({"Label": ["BenignTraffic"], "label": [0]})

    assert feature_schema(frame) == {}
