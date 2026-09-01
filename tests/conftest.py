import pandas as pd
import pytest


@pytest.fixture
def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "flow_duration": [1.0, 2.0],
            "ICMP": [0, 1],
            "Label": ["BenignTraffic", "DDoS-ICMP_Flood"],
            "Label_orig": ["BenignTraffic", "DDoS-ICMP_Flood"],
            "attack_class": ["Benign", "DDoS"],
            "label": [0, 1],
        }
    )
