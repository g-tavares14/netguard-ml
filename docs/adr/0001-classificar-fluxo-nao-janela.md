# Classificar Fluxo, não janela temporal

O Subsample CICIoT não tem timestamp de captura; cada linha já é um Fluxo agregado pelo CIC. Janelas de N segundos mudariam a pergunta para “o comportamento nos últimos N segundos é Attack?” e, nesta fonte, só poderiam usar a ordem das linhas — que o projeto recusa como tempo. O classificador permanece: este Fluxo é Normal ou Attack. Janelas só voltam se houver outra fonte com ordenação temporal real.

## Considered Options

- Agregar Fluxos em janelas mesmo sem relógio (rejeitado: inventa tempo)
- Deixar janelas como etapa “depois da EDA” neste subsample (rejeitado: o schema já basta para dizer não)
- Não usar janelas neste fonte (escolhido)
