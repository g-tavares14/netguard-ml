from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class InspectorResult:
    name: str
    tables: dict[str, pd.DataFrame] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    figures: dict[str, Any] = field(default_factory=dict)
