# Como a gente abre e revisa PR

Processo do grupo no NetGuard ML (projeto acadêmico, 3º semestre de Ciência da Computação).

## Regras

1. **Um PR = uma entrega.** Não misture EDA com treino de modelo no mesmo PR.
2. **Quem abre o PR não aprova o próprio PR.** Outro integrante com write precisa aprovar.
3. O template é de checkbox de propósito: marca a entrega, escreve duas frases, marca um revisor, marca o checklist.
4. Um comentário automático de code review pode aparecer no PR. **Isso não conta como aprovação.** O colega humano ainda precisa ler e aprovar.

## Passos

1. Abre o PR contra `main` pelo GitHub (o template já vem preenchido).
2. Marca a entrega e um revisor que não implementou aquela parte.
3. Se você esquecer o revisor, o GitHub pede review para outro integrante automaticamente.
4. Espera o comentário automático e a aprovação do colega.
5. Só então merge.

## O que o review automático olha

Barra de colega de 3º semestre, não de sênior:

| Saída | O que precisa estar ok |
| --- | --- |
| Completude | A entrega marcada bate com o que o PR mudou |
| Correção | Faz o que promete; sem erro óbvio |
| Reprodução | Dá para outro aluno rodar (ou é só doc) |
| Integridade | Sem CSV/parquet grande, senha ou `.pkl` |
| Escopo | Não pula etapa do projeto (ver `AGENTS.md`) |
| Clareza | Dá para um colega entender |
| ML | Só se treinou: split intacto, não só accuracy |

O bot no máximo aponta 5 coisas. Não cobra padrão de empresa, microsserviço nem teste sofisticado.
