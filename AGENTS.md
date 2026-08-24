# NetGuard ML — Guia para Agentes de IA

Sistema para analisar métricas de tráfego de rede e classificar o estado da rede como **normal** ou **sob ataque**. Projeto acadêmico que combina experimentação em Machine Learning com engenharia de software.

Leia [README.md](README.md) e, para o planejamento completo (dataset, modelos, métricas, arquitetura, roadmap), [docs/escopo-inicial.md](docs/escopo-inicial.md) antes de propor mudanças estruturais.

## Status atual

Planejamento e seleção do dataset. Ainda não há pipeline de ML implementado, nem backend, nem frontend. **A implementação dos serviços (backend TypeScript, dashboard, simulador) só começa depois que o pipeline de ML estiver funcional e avaliado** — não adiante essa etapa mesmo que pareça mais simples de demonstrar.

## Ordem de execução do projeto

```
Dataset → preprocessing → baseline (Decision Tree) → Random Forest → Boosting
   → comparação de modelos → análise temporal (se aplicável) → explicabilidade
   → exportação do modelo → API de ML → backend TypeScript → simulador → dashboard
```

Não pule etapas nem introduza infraestrutura (containers, múltiplas instâncias, microserviços) antes da hora — isso é explicitamente prioridade 4 ("se houver tempo").

## Arquitetura (planejada)

- **Serviço de ML (Python):** scikit-learn, pandas, NumPy; possivelmente XGBoost e SHAP; FastAPI para expor `/predict`.
- **Backend (TypeScript):** Fastify/NestJS (ainda não definido); orquestra o fluxo, agrega eventos em janelas temporais, fala com o serviço de ML, publica atualizações via WebSocket/SSE.
- **Frontend:** React/Next.js, dashboard em tempo real.

O backend em TypeScript existe por separação de responsabilidades, não porque TypeScript seria "mais rápido". Não crie esses serviços antes que o pipeline de ML esteja validado.

## Princípios de ML do projeto

- Accuracy isolada nunca é suficiente (dataset provavelmente desbalanceado). Priorize recall da classe de ataque e falsos negativos, sem ignorar falsos positivos.
- Janelas temporais só devem ser implementadas se o dataset tiver ordenação temporal **real** — a ordem das linhas por si só não conta como tempo.
- Sempre avaliar risco de vazamento de dados entre treino/teste, inclusive entre janelas sobrepostas ou eventos da mesma sessão/host.
- O artefato do modelo exportado deve carregar ou referenciar de forma versionada todo o preprocessing usado no treino, para evitar divergência treino/produção.
- Target inicial é binário (`normal` / `attack`); um tipo específico de ataque (ex.: DoS) só deve aparecer na saída se o modelo tiver sido treinado e avaliado especificamente para isso.

## Convenções de código e colaboração

- Commits e nomes de branch: sejam consistentes com o histórico existente (`git log` para conferir o estilo).
- Não commitar datasets grandes, credenciais ou artefatos de modelo pesados.
- Não introduzir abstrações, containers ou serviços além do que a etapa atual do roadmap exige.
- Ao abrir um Pull Request, siga o template em `.github/PULL_REQUEST_TEMPLATE.md` — preencha a seção de contexto do experimento (dataset, métricas antes/depois) sempre que a mudança afetar dados, features ou modelos.
- Projeto multi-integrante: evite mudanças amplas e não relacionadas em um único PR, para facilitar revisão pelos colegas.

## Escopo por ferramenta

Este arquivo (`AGENTS.md`) é a fonte de verdade para qualquer agente de IA que trabalhe neste repositório. `CLAUDE.md` existe apenas como ponteiro para este arquivo, para compatibilidade com o Claude Code.
