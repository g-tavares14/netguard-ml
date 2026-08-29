from abc import ABC, abstractmethod

from netguard_ml.data.dataset import CiciotDataset
from netguard_ml.data.eda.result import InspectorResult


class EdaInspector(ABC):
    """Um inspector cobre um item do checklist da EDA e não grava arquivo."""

    name: str

    @abstractmethod
    def inspect(self, dataset: CiciotDataset) -> InspectorResult:
        raise NotImplementedError
