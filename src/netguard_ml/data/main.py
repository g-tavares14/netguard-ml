import pandas as pd
from pathlib import Path

colunas_info = {}
listaRotulos = ['Label', 'Label_orig', 'attack_class', 'label']

paths = [
    r"C:\Users\Kauan\Desktop\GitHub\netguard-ml\data\raw\ciciot2023-neto-subsample\test.parquet",
    r"C:\Users\Kauan\Desktop\GitHub\netguard-ml\data\raw\ciciot2023-neto-subsample\train.parquet",
    r"C:\Users\Kauan\Desktop\GitHub\netguard-ml\data\raw\ciciot2023-neto-subsample\validation.parquet"
]

for path in paths:
    nome_arquivo = Path(path).stem  # "test", "train", "validation"
    dataFrame = pd.read_parquet(path)

    colunas_info[nome_arquivo] = {}
    for idx_coluna, nome_coluna in enumerate(dataFrame.columns):

        if nome_coluna in listaRotulos:
            continue
        else:
            colunas_info[nome_arquivo][idx_coluna] = {
                "nome": nome_coluna,
                "tipo": str(dataFrame[nome_coluna].dtype)
            }

print(colunas_info)