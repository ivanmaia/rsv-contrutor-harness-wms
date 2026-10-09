# SP2: validação de ponta a ponta com o agente (Task 8)

- **Data:** 2026-09-30.
- **Quem:** o usuário rodou o checklist no Claude Code, em `C:\src\wms-workspace-e2e`. O origin era descartável (`C:\src\wms-e2e-origin.git`, `main` = `sp2-speckit` em `f9f4547`), e os repos reais foram só lidos.

| Item | Resultado | Observação |
|---|---|---|
| 1. `/speckit-specify` de feature nova em dois repos | ok | |
| 2. Hook antes de tudo, branch `004-…`, spec com "Repos afetados" | ok | |
| 3. Árvore suja faz o `specify` parar sem spec | ok | |
| 4. Plan com uma seção por repo; tasks com `[repos/…]` e verificação | ok | |
| 5. `implement`/`converge`; `/speckit-ws-push` oferecido com confirmação | ok, com ressalva | O agente reclamou que não havia nada commitado: o `ws push` só envia commits. O usuário sugeriu um `speckit-ws-commit-push` e pediu que o projeto configure o Claude para não pôr o trailer `Co-Authored-By: Claude …` nos commits |
| 6. Revisão da "a 004" gera `004-…-r1` e edita o `spec.md` | **não ok** | A 004 ainda não estava no `main`. O hook só procura features no `origin/main`, então criou a `005-checkout-ecommerce` a partir do `main`, sem o trabalho da 004. O usuário observou que devia ter integrado a 004 no `main` antes |

## Achados
1. **Push sem commit.** O fluxo do Spec Kit não faz commit, e o `ws push` só envia o que está commitado. Falta um passo de commit antes do push.
2. **Atribuição do Claude nos commits.** O workspace precisa desligar o trailer `Co-Authored-By` e a linha de atribuição nos PRs, na configuração de projeto do Claude Code.
3. **Revisão de feature que ainda não está no `main`.** Com uma citação explícita ("a 004", "feature 004") e sem a 004 no `origin/main`, o hook criou uma feature nova em silêncio. Esperado: não criar outra feature. Ou o hook continua a 004 na própria branch dela, ou para com um erro explicando que a 004 precisa ser mergeada antes.

## Reteste dos itens 5 e 6 (2026-10-05, em `C:\src\wms-workspace-e2e2`, depois das correções)

| Item | Resultado | Observação |
|---|---|---|
| 5. `speckit-ws-commit-push`, commit sem `Co-Authored-By` | ok | |
| 6a. Na branch da feature, `specify` citando a feature continua nela e registra a revisão | ok | Antes, um caso intermediário (branch criada sem spec escrita) parava com erro. Foi corrigido no hook (`15c8f81`) |
| 6b. No `main`, citar uma feature não mergeada para com erro | ok, com ressalvas | (1) "feat 005" não foi reconhecido como citação, então o hook criou a `006-…`, que o agente apagou. (2) O agente respondeu em inglês. (3) O agente ofereceu mudar o harness (o regex do hook) no meio da feature |
| 6c. Número inexistente para com erro | ok | |

**Segundo reteste do 6b (2026-10-05):** ok. "feat 005" foi reconhecido, a resposta veio em português e o agente não ofereceu mudar o harness. **Validação da Task 8 concluída:** todos os itens ok.

## Pontos menores adiados (revisão final do SP2)

- M2 r<k> pode repetir se a branch da revisão anterior for apagada no origin e localmente
- M3 numa revisão, o core regenera checklists/requirements.md; o preset não manda atualizar o checklist existente
- M4 o sed do context_files do agent-context não é conferido; se o formato mudar, AGENTS.md sai da seção gerenciada sem aviso
- M5 json_str não remove outros caracteres de controle vindos da saída do ws start
- M6 regex de segredos do importa-discovery não pega YAML/JSON (password:, "Password":), AccountKey=, SharedAccessKey=, api_key/token, Bearer
- M7 as specs 001-003 migradas do AWX têm caminhos relativos à raiz do AWX e não têm "Repos afetados"
- M8 mudança no preset/extensão só pode ser testada com /speckit-specify depois de mergeada no main (o hook volta ao main); documentar em docs/workspace.md

## Decisões tomadas na execução (ledger do SP2)

- Task 2: Ruling: extension.yml e comandos (Step 6) copiados junto com os scripts antes do GREEN — não afetam os testes da Task 2 — custo: nenhum.
- Task 3: Ruling: o Expected 'os testes de rede imprimem pulado' não se verifica — o runner só mostra a saída de testes que falham; os 4 testes de rede passam sem fazer nada quando WS_TEST_REDE não está definida — custo: nenhum (texto do plano).
- Task 4: Ruling: a reinstalação alterou só timestamps installed_at nos registries e no manifest — aceito e incluído no commit (o plano admitia diferença sem efeito) — custo: nenhum.
- Task 6: Ruling: o sync de hoje trouxe uma spec nova no AWX (specs/003-nf-faturamento-b2c); movida para specs/ na raiz junto com a 001 e a 002 — a spec manda o specs/ inteiro do AWX para a raiz; a próxima feature nova passa a ser 004 (Task 8) — custo se errado: renumerar uma spec.
- Task 6: Ruling: o sync trouxe também um AGENTS.md novo no AWX, e as skills qualidade-codigo citam .specify/memory/constitution.md; troquei todas as referências para docs/constitution.md, ajustei as frases sobre o SpecKit (.specify/) para o Spec Kit do workspace e acrescentei ao AGENTS.md do AWX a mesma nota de precedência do CLAUDE.md — Step 3 do plano manda trocar referências — custo se errado: texto a ajustar no PR do AWX.
- Task 7: Ruling: a verificação de referências pegava "/speckit-" de ".claude/skills/speckit-*" (glob no texto); o regex passou a exigir uma letra depois do hífen — custo: nenhum.
- Task 8: Ruling: revisão final despachada em paralelo com a validação manual e a suíte completa — o código está completo; se a validação exigir correção, ela entra no mesmo fix pass — custo: o revisor pode não ver uma correção vinda da validação. Ambiente e2e: C:/src/wms-e2e-origin.git (main = sp2-speckit 3c1df8b) e C:/src/wms-workspace-e2e. Próxima feature nova esperada: 004.
- Final: Ruling: M1 (--short-name sem valor trava o hook em loop infinito) reclassificado para Important — um hook que trava deixa o agente parado sem mensagem — entra no fix pass.
- Final: Ruling: I3 (texto do preset e do AGENTS.md sobre o hook) é correção de texto; verificação por inspeção e por um grep nos arquivos gerados, sem teste RED→GREEN — não há comportamento de script a testar.
- Final: Ruling: e2e (Task 8) preparado com o código anterior às correções (3c1df8b); precisa ser recriado com f9f4547 antes da validação — custo: a validação rodaria o hook antigo.

## Adendo AWX (2026-10-07): harness do AWX subordinado, features `ws-NNN`

Ambiente descartável `C:\src\wms-workspace-e2e4`:
- origin bare local;
- AWX num espelho local, clonado do Azure DevOps em 07/10, já com o harness atual do time e a spec `004-reemissao-nf-pre-checkout`;
- push para o Azure DevOps bloqueado;
- Atlas de todos os repos marcado como em dia.

O agente rodou em `claude -p`. Spec: `docs/superpowers/specs/2026-10-07-sp2-adendo-harness-awx-subordinado-design.md`.

| Item | Resultado | Observação |
|---|---|---|
| 1. Skills `speckit-specify` visíveis depois de ler o `CLAUDE.md` do AWX | ok | `speckit-specify` (raiz) e `repos/industria-logistica.wms.awx.monorepo:speckit-specify`. A do AWX só aparece na forma qualificada |
| 2. `/speckit-specify` sem qualificação, numa feature só do AWX | ok | Rodou o da raiz. O hook criou a branch `ws-001-log-caixa-fechar-volume` e a spec `specs/ws-001-log-caixa-fechar-volume/`. Nada mudou no `.specify/` nem no `specs/` do AWX. A spec citou o princípio VI da constitution do AWX. US$ 1,12 |
| 3. `/speckit-plan` confere a constitution do AWX | ok | A seção do repo traz "Constitution do repo: `.specify/memory/constitution.md`" com os princípios II, V, VI, VIII e IX conferidos. O Constitution Check do workspace também passou. US$ 0,89 |
| 4. `ws push` leva `ws-001-…` para o AWX | ok | A branch `ws-001-log-caixa-fechar-volume` foi criada no espelho, com um commit trivial de teste |
| 5. O Spec Kit do AWX ignora a `ws-001` na numeração | ok | O `create-new-feature.ps1 -DryRun` num clone do espelho propôs `005-teste-numeracao`, o próximo depois da `004` do time. A `ws-001` não contou |

**Validação do adendo concluída:** todos os itens ok. Custo total: cerca de US$ 2,40.
