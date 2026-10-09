# SP4b: apresentação do harness para o time WMS — design

Data: 2026-10-08. Subprojeto seguinte ao SP4 (documentação em camadas, mergeada no workspace pelo PR 16940).

## 1. Objetivo e critério de sucesso

O usuário apresenta o harness ao time WMS. Ao fim, o time:
- entende por que o harness existe e o que ele muda no dia a dia;
- sabe, em teoria, os 9 passos do fluxo básico e as três regras;
- sabe onde procurar quando der errado (camada 2) e onde está o resto da doc.

A apresentação não ensina a operar na prática: o uso real vem com a camada 1 e o piloto (`docs/discovery/sp4-piloto.md`).

## 2. Decisões tomadas com o usuário

| Tema | Decisão |
|---|---|
| Objetivo | Porquê e fluxo básico (opção C) |
| Formato | Só teoria, sem demonstração ao vivo nem gravada |
| Duração | Cerca de 40 min, 18 a 22 slides |
| Modalidade | Remota (compartilhamento de tela) |
| Ferramenta | Deck no claude.ai (Artifact do tipo Slides), privado, com download em .pptx/PDF |
| Narrativa | Jornada de uma feature, com "antes × depois" só na abertura |
| Roteiro | O da seção 3, aprovado sem mudanças |
| Design system | Nenhum na conta; identidade visual própria, sóbria |

## 3. Roteiro (21 slides)

**Abertura: o porquê (~7 min)**
1. Capa: "Harness WMS: como fazer uma feature com o agente".
2. Hoje: 17 repos, conhecimento espalhado, agente sem contexto a cada conversa.
3. Antes × depois em três cenas: entender o impacto, abrir a branch em vários repos, enviar e abrir PRs.
4. O que é o harness: workspace, Spec Kit e Atlas, uma frase cada, num diagrama simples.

**A jornada de uma feature (~18 min).** Exemplo fictício e marcado como tal no slide 5: "bloquear a reserva de um endereço de picking com inventário aberto", tocando o backend do servidor e o app.

5. O exemplo: o pedido em linguagem de negócio e os repos que toca.
6. Passo 1, `/speckit-specify`.
7. Passo 2, `/speckit-clarify`.
8. Passo 3, `/speckit-plan`.
9. Passo 4, `/speckit-tasks`.
10. Passo 5, `/speckit-analyze`.
11. Passo 6, `/speckit-implement`.
12. Passo 7, `/speckit-converge`.
13. Passos 8 e 9, `/speckit-ws-commit-push` e os PRs.
14. Os 9 passos numa linha.
15. Já conhece o Spec Kit? As 4 diferenças.
16. As três regras que não se quebram.

**Quando dá errado e o Atlas (~8 min)**
17. Camada 2: organizada por etapa, busque pela mensagem; 2 ou 3 exemplos reais.
18. O Atlas: o que sabe, quem atualiza, por que você quase nunca mexe nele.
19. Índice de impacto: um exemplo real de "quem toca esta tabela".

**Fechamento (~7 min com perguntas)**
20. Onde está cada coisa: README e as 4 camadas, uma frase cada; thread "Equipe WMS" no Google Chat.
21. Próximos passos: piloto e como pedir ajuda; perguntas.

## 4. Regras de conteúdo

- **Fonte da verdade:** a doc no `main` do workspace (`README.md`, `docs/harness/1-4`). Cada comando, regra, mensagem de erro e caminho citado no deck existe na doc ou no código; o deck não afirma nada que a doc não diga.
- **Exemplos reais:** as mensagens do slide 17 vêm literalmente da camada 2; o exemplo do slide 19 é uma página que existe em `docs/atlas/impacto/`.
- **Feature fictícia:** o que aparece nos slides 5 a 13 (spec, tarefas, repos) é ilustrativo e diz isso; nenhum nome de tabela, endpoint ou regra de negócio é apresentado como real.
- **Remoto:** pouco texto por slide (título + até 4 linhas ou um diagrama), fonte grande, o detalhe nas notas do apresentador. Comandos em fonte monoespaçada.
- **Notas do apresentador** em todos os slides, com o que falar e o tempo sugerido.
- **Sem segredos:** nenhuma credencial, URL com credencial ou dado de produção no deck.
- **Idioma:** português.

## 5. Entrega e validação

- **Entrega:** um Artifact privado do tipo Slides no claude.ai; o link vai para o usuário e é registrado em `docs/discovery/estado-da-sessao.md`. Nada muda no workspace.
- **Validação antes de entregar:**
  - conferir slide a slide os comandos, as regras e as mensagens contra a doc do `main`;
  - percorrer o deck inteiro conferindo que todo slide tem nota e que nenhum estoura o espaço;
  - somar os tempos das notas: entre 35 e 40 min, deixando margem para perguntas.
- **Depois:** o usuário revisa e pede ajustes; o deck é atualizado no mesmo link.

## 6. Riscos

- **A doc muda depois do piloto:** o deck pode ficar desatualizado. Ele cita a doc como referência e não repete detalhes que mudam (números de tempo, versões).
- **Exemplo fictício confundido com real:** mitigado pela marca explícita no slide 5 e pelo uso de nomes genéricos.

## Adendo (2026-10-08): slides de comandos

A pedido do usuário, três slides em tabela entre o índice de impacto e "Onde está cada coisa": comandos do Atlas (comando, quando usar, o que devolve), comandos `ws` (para quê, quem usa, quais são só de diagnóstico) e outras skills. O deck passa a 24 slides; as notas somam 39 min.
