from __future__ import annotations

from netguard_ml.data.dataset import CiciotDataset
from netguard_ml.data.eda.inspector import EdaInspector
from netguard_ml.data.eda.result import InspectorResult
from netguard_ml.data.eda.writer import EdaArtifactWriter


def default_inspectors() -> list[EdaInspector]:
    from netguard_ml.data.eda.inspectors import (
        CollinearityInspector,
        DistributionInspector,
        IcmpInspector,
        LeakageInspector,
        QualityInspector,
        SchemaInspector,
        TargetInspector,
        TemporalInspector,
    )

    return [
        SchemaInspector(),
        TargetInspector(),
        DistributionInspector(),
        QualityInspector(),
        CollinearityInspector(),
        IcmpInspector(),
        TemporalInspector(),
        LeakageInspector(),
    ]


class EdaPipeline:
    """Orquestra inspectores e o writer; não calcula estatística."""

    def __init__(
        self,
        dataset: CiciotDataset,
        writer: EdaArtifactWriter,
        inspectors: list[EdaInspector] | None = None,
    ):
        self.dataset = dataset
        self.writer = writer
        self.inspectors = inspectors if inspectors is not None else default_inspectors()

    def run(self) -> list[InspectorResult]:
        results: list[InspectorResult] = []
        for inspector in self.inspectors:
            print(f"EDA: {inspector.name}")
            result = inspector.inspect(self.dataset)
            self.writer.write(result)
            results.append(result)
        print(f"artefatos em {self.writer.output_dir}")
        return results
