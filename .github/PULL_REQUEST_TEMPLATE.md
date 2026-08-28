## Tarefa do grupo

<!-- Qual entrega ou parte do trabalho este PR cobre? Ex.: dataset, EDA, baseline Decision Tree. -->

- **Tarefa:**
- **Quem fez:**
- **Revisor sugerido:** <!-- colega que não implementou esta parte -->

## O que este PR faz

<!-- Em 3–6 linhas, para quem não acompanhou o código. O que mudou e por quê. -->

## Tipo

- [ ] Dataset / dados
- [ ] Análise exploratória
- [ ] Preprocessing / features
- [ ] Experimento de modelo (treino, métricas, comparação)
- [ ] Documentação / relatório
- [ ] Correção
- [ ] Outro: <!-- especifique -->

## Para o colega que for revisar

Este PR será aprovado por outro integrante do grupo. Deixe explícito o que ele precisa conferir.

1. Como reproduzir (comandos, a partir da raiz do repo):

   ```bash
   # exemplo: .venv/bin/python scripts/prepare_dataset.py
   ```

2. O que deve acontecer se estiver certo:
3. O que **não** precisa ser revisado neste PR (fica para outra tarefa):
4. Dúvida ou decisão em aberto para o grupo discutir:

## Contexto do experimento

<!-- Preencha se o PR mexer em dataset, features, treino ou avaliação. Apague a seção se não se aplicar. -->

- **Dataset/versão:** CICIoT2023 subsample HuggingFace `random_3way` (revision em `data/raw/ciciot2023-neto-subsample/SOURCE.json`, se local)
- **Split usado:** train / validation / test (não reembaralhar o conjunto)
- **Target:** `label` 0 → `normal`, 1 → `attack`
- **Modelo(s):**
- **Métricas antes → depois** (accuracy, precision, recall, F1, FPR, FNR):
- **Risco de vazamento avaliado?** (ex.: teste não usado no ajuste; sem misturar Atlas como teste)

## Checklist

- [ ] O PR cobre **uma** tarefa; mudanças não relacionadas ficam para outro PR
- [ ] Um colega que não escreveu o código consegue seguir a seção “Para o colega que for revisar”
- [ ] Rodei localmente o que este PR introduz
- [ ] Não commitamos CSV/parquet grande, credenciais nem modelo `.pkl` / `.joblib`
- [ ] Documentação (`README.md` / `docs/`) atualizada se a decisão do grupo mudou
- [ ] Se for experimento: a seção de contexto acima está preenchida
