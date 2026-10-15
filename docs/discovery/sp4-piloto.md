# SP4: piloto da documentação do harness

Spec: `docs/superpowers/specs/2026-10-08-sp4-documentacao-harness-design.md`, seção 7.
Documentação no `main` do workspace desde o PR 16940 (`0cbac04e5`, 2026-10-08).

## Como conduzir

- **Quem:** um dev do time, escolhido durante a apresentação do harness (2026-10-08). Ele roda o fluxo completo numa demanda real e depois dá o feedback.
- **O que ele recebe:** o link do `README.md` do workspace. Ele já viu a apresentação (só teoria), então não parte do zero: o piloto testa se a doc basta para operar, não se ela explica o porquê.
- **Quem observa:** não ajuda enquanto o dev não travar de fato. Anota cada travada, dúvida ou desvio no registro abaixo, com a etapa e as palavras do dev.
- **Ao travar:** primeiro o dev procura na camada 2. Só depois o observador ajuda, e registra se a resposta estava na doc.
- **Depois:** cada linha com ação vira correção num PR de acompanhamento no workspace, na camada 1 ou como entrada nova na camada 2. O teste `tools/ws/tests/test_docs_referencias.sh` precisa continuar passando.

## Dados da sessão

- Data: 2026-10-09 (relato recebido em 2026-10-13)
- Dev (papel, não nome): dev full stack
- Demanda real (id ou título): mover a emissão da NF de devolução de falta para o processamento de divergências da NF de entrada (work item 72694, board WMS - Desacoplamento/Operacional)
- Já conhecia o Spec Kit? (s/n): s
- Feature: `ws-001-devolucao-divergencia-nf`; no primeiro relato, ciclo parcial (só o passo 1); no segundo (2026-10-14), chegou ao envio (`/speckit-ws-commit-push`)
- Repos tocados: `industria-logistica.wms.servidor.backend`; `integracoes.wms.servicos-linx-wms.monorepo` (fora do workspace)
- Instalou as ferramentas do Atlas? (s/n): s

## Registro

| # | Etapa (camada 1, passo) | O que aconteceu (palavras do dev ou mensagem) | Estava na doc? | Ação | PR |
|---|---|---|---|---|---|
| 1 | Passo 1, `/speckit-specify` | A demanda cita "AWX.IntegracaoLinx". O agente não achou no workspace, e o dev explicou que é o repo `integracoes.wms.servicos-linx-wms.monorepo`, que não está no `workspace.repos`. | Em parte: a camada 2 diz para pedir ao time do harness a inclusão de repo, mas nada liga o nome do sistema à pasta | Feito: repo incluído (`ws add`, commit `4164d6c68` do repo) e seção "Nomes dos sistemas" no `AGENTS.md` (regra 7), com teste que exige todos os repos do manifesto na tabela. | PR 17070 |
| 2 | Passo 1, `/speckit-specify` | Sem o código do Linx, a spec só descreve o comportamento esperado e ficou com 2 clarificações abertas. | Não | Feito: regra 7 do `AGENTS.md` e camada 2, "A demanda cita um sistema fora do workspace". O agente não pergunta a pasta ao dev: para e oferece seguir com o sistema como externo (linha `externo:` em "Repos afetados", a feature não o muda) ou parar e pedir a inclusão ao time do harness, sem rodar o plan; com o repo no `main`, o dev sincroniza a branch da feature (`git fetch origin main` e `git merge --no-edit origin/main`) e segue. Teste do `ws push` depois dessa sincronização. (2026-10-14: troca a primeira versão, que pedia ao dev a pasta e mandava refazer a feature.) | PR 17070 |
| 3 | Passo 1, hook `atlas-atualizar` | O primeiro specify mapeou 3 repos no Atlas: ~762 mil tokens, ~22 min no maior. | Em parte: só na camada 3 | Feito: camada 1, passo 1, e camada 2, "O `/speckit-specify` demora no Atlas". | PR 17070 |
| 4 | Passo 1, hook `atlas-atualizar` | O `ecommerce.backend` foi mapeado por "contrato", sem relação com a feature. | Não | Decisão do usuário (2026-10-13): manter a política do SP3; explicado na camada 1 e na entrada da camada 2 do item 3. | PR 17070 |
| 5 | Passo 1, `ws atlas concluir` | `FileNotFoundError` no `tools/atlas/build-map.py` (`le_sql`, linha 56) num `.sql` do `servidor.backend` com 270 caracteres de caminho. | Não | Feito: `build-map.py` lê `repos/` com o prefixo no Windows; teste com caminho de mais de 260 caracteres (nesta máquina a chave está ligada, então ele não reproduz a falha). | PR 17070 |
| 6 | Passo 1, `ws atlas concluir` | Causa: `LongPathsEnabled = 0` no Windows. O `core.longpaths` da doc só vale para o git. | Não: o ADR 0001 e a camada 1 só citam `core.longpaths` | Feito: camada 1, "Antes de tudo", passo 2, e camada 2, "Erro de caminho longo fora do git". | PR 17070 |
| 7 | Passo 1, correção do item 6 | O agente não conseguiu ativar: "Acesso ao Registro solicitado não é permitido". | Não | Feito, nas mesmas entradas do item 6. | PR 17070 |
| 8 | Passo 1, correção do item 6 | Como admin: `Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled -Value 1 -Type DWord`, e o `concluir` passou. | Não | Feito, nas mesmas entradas do item 6. | PR 17070 |
| 9 | Passo 8, `/speckit-ws-commit-push` (relato de 2026-10-14, anterior ao PR 17070) | `ws push` falhou no `industria-logistica.wms.servidor.backend` com `error: unable to rewind rpc post data - try increasing http.postBuffer`, `error: RPC failed; curl 65 HTTP/2 stream 9 was reset` e `ws: erro: subtree push de repos/industria-logistica.wms.servidor.backend falhou`. O `git ls-remote` funcionou. Resolveu com `git config http.postBuffer 524288000` e `git config http.version HTTP/1.1` no clone, sugeridos pela IA, e `ws push` de novo. Sugeriu a entrada na camada 2 e as duas configurações no `git clone` da camada 1. | Não: "Falha no envio a um repo" cita só credencial, permissão e rede, e manda testar o `git ls-remote`, que passa | O `ws push` passa a enviar com `-c http.version=HTTP/1.1 -c http.postBuffer=524288000` no `subtree push`, com teste. A camada 2, "Falha no envio a um repo", ganha a causa, a saída do git e as duas configurações no clone, para branches criadas antes da correção. A camada 1 não muda: a correção no `ws push` cobre os clones já feitos, e a configuração no `git clone` só cobriria os novos. | PR 17072 |

**Impedimento:** o dev não conseguiu terminar a feature porque o repo `integracoes.wms.servicos-linx-wms.monorepo` não está no workspace.

**Ajustes (2026-10-13):** branch `harness/piloto-sp4-ajustes` do workspace, saindo do `main` `6df2664fe`, mergeada no `main` pelo PR 17070 (merge `34dcabb7c`, 2026-10-14), antes de o dev retomar (decisão do usuário). Suíte com 248 ok no último commit da branch. Atlas do repo novo: como o dev retoma sem rodar o `/speckit-specify` de novo, o repo foi mapeado na própria branch antes do PR (2026-10-14). O `/atlas-atualizar` manual não serve aqui, porque parte do `main`, que ainda não tem o repo; foi usado o caminho do converge: `ws atlas plano --gatilho converge` (só o repo do Linx, 231 arquivos, 462 mil tokens estimados), um subagente com o `prompt-mapeamento.md` em modo do-zero (cerca de 400 mil tokens, 16 minutos, 158 arestas no `edges.csv`) e `ws atlas concluir --gatilho converge` (commit `a89a5db32`, que também refaz o índice de impacto com o repo do Linx como consumidor). O `atlas.estado` ficou só com a árvore. **Conferência (2026-10-14, simulação do início do `/speckit-specify` no `main` `6af58e659`):** só com o plano, o repo do Linx sai como `avancar` (0 tokens); mas o `ws atlas incorpora` que vem antes trocava o `docs/atlas` inteiro pelo da `atlas/atualizacao` aberta desde 2026-10-09 (montada antes do PR 17070), apagava o Atlas do Linx da feature e o plano mandava mapeá-lo do zero (`do-zero`, 450 mil tokens). O mesmo valia para qualquer mudança do `main` em `docs/atlas` depois da última publicação, como o Atlas gravado no converge de uma feature. Correção mergeada no `main` do workspace pelo PR 17073 (commit `43062540d`, merge `dbc94c3dc`): com a `atlas/atualizacao` atrasada, o `docs/atlas` parte do `main` e recebe só as pastas dos repos que ela traz e que o `main` não mexeu desde então (a regra que a publicação já usava), e os derivados são refeitos; sem atraso, nada muda. Dois testes novos, suíte com 251 ok. Na simulação com a correção, o Linx sai como `avancar` e o specify mapeia picking.backend, picking.frontend e backoffice (812 mil tokens, pela política de contrato e intervalo). Mapa cbm local com `ws atlas mapas`. Para retomar, o dev segue os passos 3 e 4 da opção "Parar e pedir a inclusão" da entrada "A demanda cita um sistema fora do workspace": sincroniza a branch `ws-001-devolucao-divergencia-nf` com o `main` e pede ao agente a revisão de "Repos afetados".

**Aviso do dev ao time:** no Windows, com `LongPathsEnabled` desativado, o `build-map.py` quebra no início da feature com caminhos de mais de 260 caracteres, porque o `core.longpaths` só cobre o git. Solução: num PowerShell como administrador (Windows 10 1607 ou mais novo, qualquer Windows 11), rodar o `Set-ItemProperty` do item 8 e repetir o que falhou, por exemplo `tools/ws/ws atlas concluir --gatilho start`.

## Pontos para conferir no piloto

- As âncoras `<a id>` e o bloco `<details>` funcionam no preview do Azure DevOps (decisão da execução: se o ADO tirar os ids, o link cai no topo do arquivo).
- O Claude Code pede aprovação dos servidores MCP do `.mcp.json` na primeira abertura; a camada 3 não menciona isso.

## Pendências adiadas da revisão final (candidatas a PR de acompanhamento)

- Camada 2, "Nada a enviar": cita causa impossível (mudanças não commitadas).
- Camada 2, "A branch já existe": prefixo `ws: erro:` errado e erro praticamente inalcançável.
- Perdas pequenas do antigo `docs/workspace.md`: `atlas.estado`, PAT como credencial, `git push` só vai para o workspace, PR do workspace leva o harness; camada 3 diz "proibidos" sem dizer que remover é permitido.
- Verificador: prefixo `./`, skills em bloco, `NATIVOS` fixo, exclusão de `docs/atlas/` sem comentário. (O sintoma que pegava o primeiro bloco depois de `**Sintoma:**` foi corrigido em `harness/piloto-sp4-ajustes`: só vale o bloco antes da **Causa:**.)
- Camada 1, regra 3: não lista `CLAUDE.md` e `docs/adr/` como harness.

## Resultado

(preencher ao fim: travadas por camada, correções feitas, se a camada 1 bastou sozinha, e o feedback do dev depois da entrega)
