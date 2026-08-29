"""Constantes do schema CICIoT2023 usadas pelo loader e pela EDA."""

SPLITS = ("train", "validation", "test")

LABEL_COLUMNS = ("Label", "Label_orig", "attack_class", "label")
TARGET_COLUMN = "label"
TARGET_MAP = {0: "normal", 1: "attack"}
BENIGN_LABEL = "BenignTraffic"
BENIGN_ATTACK_CLASS = "Benign"

# Subconjunto estável para medir overlap entre splits sem materializar 46 floats.
OVERLAP_KEY_COLUMNS = (
    "flow_duration",
    "Header_Length",
    "Rate",
    "IAT",
    "Tot size",
    "ICMP",
    "TCP",
    "Number",
    "Weight",
)

ARTIFACT_FEATURE_CANDIDATES = ("IAT", "Number", "Weight")

TIMESTAMP_NAME_HINTS = ("timestamp", "time", "datetime", "date")
