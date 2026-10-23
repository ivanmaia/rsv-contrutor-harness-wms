# SP8: Padronização dos comandos e nomes do harness (design)

Data: 2026-10-22. Processo: `superpowers:brainstorming`. Decisões tomadas com o usuário na conversa de 2026-10-22. Inventário de partida: `docs/discovery/nomes-em-portugues.md` (levantado no `origin/main` do workspace, commit `801331703`).

## 1. Intenção e porquê

O fim de cada fluxo funciona igual por baixo: o mesmo `ws-commit-push.sh` faz commit e `ws push`, e a mesma oferta abre os PRs. Mas o dev vê nomes diferentes para a mesma coisa:
- na feature, o envio é um passo visível, o `/speckit-ws-commit-push`;
- no bug e no refactor, o envio fica escondido nos hooks `-bug-enviar` e `-refactor-enviar`;
- a oferta dos PRs para homologação está copiada em três comandos, e só a promoção tem comando próprio.

Na lista do `/`, os comandos que o dev digita se misturam com os hooks, que rodam sozinhos. Os nomes misturam inglês e português sem regra: `refactor-assess` está em inglês e `refactor-subida`, em português.

O usuário quer:
- os mesmos comandos de fim em todos os fluxos;
- nomes previsíveis;
- comandos e skills em inglês;
- documentos em português.

## 2. Objetivos, não objetivos e antiobjetivos

**Objetivos:**
- feature, bug e refactor terminam com os mesmos comandos: `/ws-commit-push`, `/ws-pr-homolog`, `/ws-pr-main` e completar os PRs;
- todo comando, skill, hook, evento de hook, subcomando e opção do CLI do harness fica em inglês;
- pastas e arquivos que ainda não existem no origin nascem em inglês;
- a documentação e o conteúdo dos artefatos continuam em português.

**Não objetivos:**
- mudar o comportamento de qualquer comando, exceto a detecção do tipo pela branch no commit-push e a extração da oferta dos PRs para um comando próprio;
- renomear comandos do Spec Kit oficial (`specify`, `clarify`, `plan`, `tasks`, `analyze`, `implement`, `converge`, `checklist`, `constitution`, `taskstoissues`, `agent-context-update`) e da extensão oficial de bug (`bug-assess`, `bug-fix`, `bug-test`);
- renomear funções e variáveis internas de scripts, nomes de arquivo de scripts e módulos, chaves de JSON internas, chaves do `workspace.pr.ini`, arquivos do Atlas e variáveis de ambiente (subcomandos e opções internos entram: seção 8, item 6);
- traduzir documentação, mensagens do `ws`, textos de PR ou do Chat.

**Antiobjetivos:**
- sobrar nome antigo em comando, teste ou documentação, com o dev vendo os dois;
- quebrar dado já gravado no origin;
- duplicar comentários já publicados pela revisão.

## 3. Decisões tomadas com o usuário

| Decisão | Valor |
|---|---|
| Comandos do fim | Os mesmos três em todos os fluxos: commit e envio (mensagem `feat`, `fix` ou `refactor` conforme a branch), PRs para o ramo de teste e PRs para o `main` |
| Idioma | Comandos e skills em inglês, incluindo as extensões nossas. Os documentos ficam em português. Os subcomandos do CLI também vão para o inglês |
| Spec Kit oficial | Os nomes não mudam |
| Prefixo | O usuário sugeriu `ws` para as extensões. O Spec Kit 1.2.0 obriga comando de extensão a se chamar `speckit.<ext>.<nome>` (`EXTENSION_COMMAND_NAME_PATTERN = ^speckit\.([a-z0-9-]+)\.([a-z0-9-]+)$`), então `ws-` puro só vale para skills comuns. Resultado: os comandos que o dev digita no fim do fluxo viram skills `ws-*`, e os comandos que precisam disparar evento continuam na extensão (seção 4) |
| `desacoplar` | Não vira `decouple`. O passo remove o caminho antigo e a leitura da chave depois da validação; o desacoplamento é a fatia inteira. Vira `retire-legacy` (padrão strangler fig). O `remover` vira `remove-flag`, porque o que sai é a chave (feature flag) |
| Pastas e arquivos | O que já está no origin e tem conteúdo fica em português. O que ainda não existe nasce em inglês |
| Valores gravados nos documentos | Etapas da fatia, modos da chave, tipo da fatia, estado do plano e estado do card continuam em português, inclusive quando o dev os digita no CLI. Isso é a "opção (a)" da conversa: é vocabulário do documento, sem tabela de tradução. O usuário não se opôs |

## 4. Os nomes novos

### 4.1 Comandos que o dev digita (skills comuns em `.claude/skills/`)

| Hoje | Novo | O que faz |
|---|---|---|
| `/speckit-ws-commit-push` (só feature) | `/ws-commit-push` | Commit e `ws push`. O tipo vem da branch: `ws-NNN-*` vira `feat(ws-NNN): <título> [specs/…]` (` (r<k>)` na revisão); `hotfix/<slug>` vira `fix(<slug>): <título do bug>`; `refactor/<slug>` vira `refactor(<slug>): <título>`; nas branches da fatia, ficam as mensagens de hoje (`refactor(eap-<código>): desacopla …` e `remove a chave`). O aviso de tarefas pendentes do converge continua só na feature. No fim, oferece o `/ws-pr-homolog` |
| oferta copiada no commit-push, no bug-enviar e no refactor-enviar | `/ws-pr-homolog` | `ws pr plan homolog`, pergunta o card (no refactor, propõe o número do slug), `ws pr open homolog --card`. Sem repo na entrega, oferece o PR do workspace direto para o `main`. Serve também para refazer (oferta recusada, PR manual, repo novo) |
| `/speckit-ws-promover` | `/ws-pr-main` | Igual ao promover de hoje, com os subcomandos novos |
| `/ws-revisar` | `/ws-pr-review` | Igual ao de hoje, com os caminhos novos (4.5) |
| `/atlas-consultar` | `/ws-atlas-query` | Igual |
| `/atlas-atualizar` | `/ws-atlas-update` | Igual |

`/codebase-discovery` não muda.

### 4.2 Extensão de refactor (continua extensão, porque dispara eventos)

| Hoje | Novo |
|---|---|
| `/speckit-refactor-assess`, `-apply`, `-verify` | iguais |
| `/speckit-refactor-subida` | `/speckit-refactor-rollout` |
| `/speckit-refactor-validar` | `/speckit-refactor-validate` |
| `/speckit-refactor-desacoplar` | `/speckit-refactor-retire-legacy` |
| `/speckit-refactor-remover` | `/speckit-refactor-remove-flag` |

Eventos: `before_`/`after_refactor_rollout`, `_validate`, `_retire_legacy` e `_remove_flag`. Os eventos de assess, apply e verify não mudam.

### 4.3 Hooks da extensão `ws` (internos: o dev não digita)

Padrão: `speckit-ws-<feature|bug|refactor>-<start|record|end>`.

| Hoje | Novo | Evento |
|---|---|---|
| `speckit.ws.feature` | `speckit.ws.feature-start` | `before_specify` |
| `speckit.ws.converge` | `speckit.ws.feature-end` | `after_converge` |
| `speckit.ws.bug-start` | `speckit.ws.bug-start` | `before_bug_assess` |
| `speckit.ws.bug-sem-correcao` | `speckit.ws.bug-record` | `after_bug_assess` |
| `speckit.ws.bug-enviar` | `speckit.ws.bug-end` | `after_bug_test` |
| `speckit.ws.refactor-start` | `speckit.ws.refactor-start` | `before_refactor_assess`, `_rollout`, `_validate`, `_remove_flag` |
| `speckit.ws.refactor-registro` | `speckit.ws.refactor-record` | `after_refactor_assess`, `_rollout`, `_validate` |
| `speckit.ws.refactor-enviar` | `speckit.ws.refactor-end` | `after_refactor_verify`, `_retire_legacy`, `_remove_flag` |
| `speckit.ws.commit-push`, `speckit.ws.promover` | saem da extensão | viram as skills `ws-commit-push` e `ws-pr-main` |

Os hooks de fim (`feature-end`, `bug-end` e `refactor-end`) fazem só o que é do fluxo: conferem o resultado (converge sem tarefa nova; teste `verified` ou `partial` confirmado; verify `ok`) e atualizam o Atlas. Depois seguem a skill `ws-commit-push`, que por sua vez oferece a `ws-pr-homolog`. O `bug-record` continua oferecendo o PR do workspace direto para o `main` (pela `ws-pr-homolog`, que já trata a entrega sem repo).

### 4.4 CLI `tools/ws/ws`

- **Subcomandos e opções em inglês:** a lista completa está nas seções 2.2 a 2.5 do inventário, com os ajustes abaixo, que prevalecem sobre as sugestões de lá:
  - `ws refactor fatia` vira `ws refactor slice`, com os subcomandos `pending`, `status`, `create`, `type`, `approve`, `card`, `stage`, `plan`, `update`, `state`, `type-of` e `flag-of` (no lugar de `chave-de`);
  - `ws pr plano|abrir|revisao|comentar` vira `ws pr plan|open|review|comment`;
  - `ws atlas plano|incorpora|concluir|mapas` vira `ws atlas plan|incorporate|finish|maps`;
  - opções: `--title`, `--decoupling`, `--type`, `--depends-on`, `--slice`, `--state`, `--systems`, `--objects`, `--read-at`, `--note`, `--since`, `--reason`, `--trigger`, `--failures`, `--today`, `--from-scratch` e `--all`;
  - os modos do `ws-refactor-start.sh` viram `--rollout`, `--validate`, `--remove-flag` e `--round` (este no lugar de `--rodada`).
- **Valores em português:** os valores que vão para os documentos não mudam, como `entregue`, `convivencia`, `validada`, `desacoplada`, `chave-removida`, `antigo`, `paralelo`, `sombra`, `novo`, `com-chave`, `sem-chave`, `rascunho`, `revisado`, `diagnóstico`, `aplicado` e os demais (seção 3).
- **Módulos Python:** os módulos de `tools/ws/pr/` e os scripts de `tools/` podem manter os nomes, porque o dev não os digita. Se o builder renomear, que evite `open.py`, que colide com o builtin do Python.

### 4.5 Branches, pastas e arquivos

**Branches novas** (nenhuma existe no origin):
- `refactor/eap-<código>-rollout[-k]`, `-validate[-k]` e `-remove-flag`;
- as do `update`: `-coexistence[-k]` e `-legacy[-k]`;
- o prefixo `eap` fica: é o termo do time (a planilha "EAP Desacoplamento") e é o nome das chaves centrais (`eap-1-1-4`);
- `-r<k>`, `rf-`, `inc-` e `hotfix/` ficam.

**Ficam como estão** (existem no origin com conteúdo):
- a branch `atlas/atualizacao`;
- `docs/harness/1-comecar.md` e as demais camadas;
- `docs/adr/*`;
- `docs/atlas/` inteiro, incluindo `impacto/`, `banco/`, os CSVs e os `atlas.estado`;
- os templates em `tools/speckit/refactor/templates/` (`desacoplamento-template.md` e `plano-subida-template.md`);
- o `workspace.pr.ini` e as chaves dele.

**Nascem em inglês** (não existem no origin):
- `refactors/slices.md`;
- `refactors/slices/<código>/` com `rollout-plan.md`, `validation.md`, `retire-legacy.md` e `remove-flag.md`;
- `refactors/decouplings/<nome>.md`;
- `.ws/review/<id>/` com `context.json`, `findings.json` e `tree/`.

As chaves dentro do `context.json` e do `findings.json` não mudam. Elas são contrato interno entre o `ws pr review` e a skill.

**Ficam por compatibilidade:**
- o marcador `<!-- ws-revisao:<id> -->` dos comentários de revisão, porque trocá-lo faria repetir comentários já publicados;
- o marcador `<!-- ws-pr:subtrees -->`;
- os prefixos de commit (`test(<slug>): caracterização` etc.), porque são texto lido por gente e vivem em histórico.

### 4.6 Registro

Adendo novo na ADR 0001 (adendo 9) com a regra de nomes (seção 3) e a tabela "antigo → novo" das seções 4.1 a 4.4. As ADRs antigas não são reescritas.

## 5. O que muda junto

- **Extensões:** as fontes em `tools/speckit/ws/` e `tools/speckit/refactor/`, com os comandos, o `extension.yml` (versões: `ws` 1.8.0 e `refactor` com bump de minor) e o `hooks.md`, mais as cópias regeneradas por `tools/ws/ws speckit`.
- **Skills:** as novas `ws-commit-push`, `ws-pr-homolog`, `ws-pr-main` e `ws-pr-review`, e as `ws-atlas-query` e `ws-atlas-update`, renomeadas a partir das `atlas-*`. Saem as antigas, incluindo `speckit-ws-promover` e `ws-revisar`.
- **CLI e scripts:** `tools/ws/ws`, `tools/ws/lib/*.sh`, `tools/ws/pr/*`, `tools/speckit/*/scripts/bash/*` e `tools/atlas/plano.py` (subcomandos e opções).
- **Testes:** os 28 arquivos de `tools/ws/tests/`, mais um teste novo que procura os nomes antigos de comando, subcomando e opção em `tools/`, `.claude/`, `.specify/`, `AGENTS.md` e `docs/harness/` (fora de `historico/`) e falha se achar algum. A lista de nomes proibidos vem das seções 4.1 a 4.4.
- **Documentação:**
  - o conteúdo continua em português;
  - mudam os nomes citados em `AGENTS.md`, `README.md`, nas quatro camadas e nos templates do preset `multirepo` e da extensão de refactor;
  - os fluxos da camada 1 passam a terminar todos em commit-push → pr-homolog → pr-main → completar;
  - ADR 0001, adendo 9.
- **Deck v2:** publicado em `https://claude.ai/artifact/TMrcFBWrbLJvaMMyXuP4vf` (fonte em `docs/discovery/apresentacao-v2/`), com todos os nomes trocados e os passos 8 a 10 da feature, o bug e o refactor terminando nos mesmos comandos. O deck v1 não muda.

## 6. Impactos e riscos

- **Dados gravados:** nada a migrar. Não há `refactors/`, nenhuma branch `refactor/*` nem fatia no origin. Os 2 bugs existentes usam nomes da extensão oficial.
- **Trabalho aberto:** as cópias do Spec Kit e as skills são versionadas. Uma branch aberta recebe os nomes novos ao trazer a `ws/sync` (`tools/ws/ws sync && git merge --no-edit ws/sync`). Até lá, ela usa os nomes velhos. O dia do merge é avisado no Chat, e a camada 2 ganha uma entrada "comando não encontrado depois da atualização", com essa solução.
- **Skills fora da extensão:** as skills `ws-*` dependem da descrição para não serem disparadas fora de hora. A descrição de cada uma diz quando usar e quando não usar.
- **Risco principal:** sobrar nome antigo. O teste de nomes proibidos é a rede de segurança.

## 7. Testes e validação

- **Testes primeiro:** seguem o padrão de sempre, com cada teste visto falhando antes da mudança. A suíte inteira roda antes do PR.
- **Validação de ponta a ponta no workspace real,** com a mesma limpeza do SP7 (PRs abandonados e branches apagadas):
  - uma feature de teste até o `/ws-pr-homolog`;
  - um bug de teste até o `/ws-commit-push`;
  - um refactor de teste até o `/ws-commit-push`;
  - um `/ws-pr-review` num PR de teste.

## 8. Respostas ao builder check

1. **Avisos de depois do envio.** A skill `ws-commit-push` concentra a mensagem por tipo de branch e também os avisos de depois do push, para que o dev que a digita sozinho veja os mesmos avisos. Os avisos são estes:
   - no card sem chave, o `git push -u origin <branch>` e a explicação dos PRs da fatia;
   - no card com chave, que ele pode ir para produção mesmo no congelamento;
   - depois do retire-legacy, o próximo passo `/speckit-refactor-remove-flag`;
   - depois do remove-flag, que a cópia do legado perde a chave.
   
   Os hooks `*-end` só conferem o resultado, atualizam o Atlas e seguem a skill. (Decisão minha.)
2. **Mensagem do commit por branch.** O tipo vem da branch. Na branch de validação, o arquivo de relatório decide. (Decisão minha.)

   | Branch | Mensagem proposta |
   |---|---|
   | `ws-NNN-<nome>[-r<k>]` | `feat(ws-NNN): <título> [specs/ws-NNN-<nome>]` (+ ` (r<k>)`) |
   | `hotfix/<slug>` | `fix(<slug>): <título do bug>` |
   | `refactor/<slug>[-r<k>]` | `refactor(<slug>): <título do assessment.md>` (+ ` (r<k>)`) |
   | `refactor/eap-<código>-validate[-k]` com `refactors/slices/<código>/retire-legacy.md` alterado na branch | `refactor(eap-<código>): desacopla <título da fatia>` |
   | `refactor/eap-<código>-remove-flag` | `refactor(eap-<código>): remove a chave` |
   | `-rollout`, `-validate` sem retire-legacy, `-coexistence` e `-legacy` | o commit é feito pelo próprio comando (`refactor-record` ou `ws refactor slice update`). A skill diz isso, mostra o que está pendente e, se ainda houver mudança, propõe `docs(eap-<código>): <resumo>` para o dev confirmar ou corrigir |

3. **Deck v2.** Faz parte da construção, como tarefa final: a fonte fica no repo de discovery (`docs/discovery/apresentacao-v2/`), e a mudança é publicada no mesmo deck. É outro repo e outro jeito de entregar (commit no discovery e publicação), separado do PR do workspace.
4. **Base e entrega.**
   - O SP7 já está no `origin/main` (PR 17261, mergeado em 2026-10-22). A memória que dizia "pausado" está desatualizada.
   - A base é o `origin/main`, num worktree novo, na branch `harness/sp8-nomes`, com PR no Azure DevOps para o `main`. O clone do usuário em `C:/src/wms-workspace` não é tocado.
   - A validação real é uma etapa do plano, feita com o usuário, como no SP7.
5. **Teste de nomes proibidos.** Casa só em contexto de comando: `/speckit-<nome antigo>`, `/ws-revisar`, `/atlas-consultar`, `/atlas-atualizar`, `ws refactor fatia`, `ws pr plano|abrir|revisao|comentar`, `ws atlas plano|incorpora|concluir|mapas`, as opções antigas (`--titulo`, `--gatilho` …) e os nomes de evento antigos. Prosa e valores em português não entram no teste. Uma lista de exceções no próprio teste cobre os nomes que ficam por decisão (`ws-revisao`, `atlas/atualizacao`, os templates). (Decisão minha.)
6. **Subcomandos e opções internos (decisão do usuário, 2026-10-22): também vão para o inglês.** Valem os nomes do inventário, seção 2.4:
   - **`plano.py`:** os subcomandos viram `generate`, `list` e `write-state`;
   - **opções:** `--actions`, `--changed`, `--without`, `--root` (no `build-map.py` e no `build-viz.py`) e `--database` (no `importa-mapeamento.sh`);
   - **valores de ação do plano:** `update`, `from-scratch`, `advance`, `defer`, `pending` e `none`, junto com os motivos que o script grava. O `.git/atlas-plano.json` é local e é gerado a cada execução, então não há o que migrar. A skill `ws-atlas-update` e os testes mudam junto;
   - **o que fica:** os nomes de arquivo dos scripts e módulos, as funções e as chaves de JSON (seção 2).
7. **Sem apelidos.** Os nomes antigos somem de uma vez. Uma branch aberta não quebra, porque o CLI, as skills e as cópias do Spec Kit são versionados na própria branch: ela continua com os nomes velhos e consistentes até trazer a `ws/sync`. A entrada da camada 2 cobre o "não achei o comando" de quem misturar.
8. **Detalhes que o builder decide:** o adendo da ADR 0001 é o próximo número livre (conferir), e o destino `homolog` continua como argumento de `ws pr plan|open`.

## 9. O que fica com o builder

- a redação das descrições das skills;
- a ordem das tarefas;
- se renomeia ou não os módulos internos;
- como o teste de nomes proibidos guarda a lista.
