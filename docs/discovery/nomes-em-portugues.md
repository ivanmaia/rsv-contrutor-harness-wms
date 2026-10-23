# Inventário dos nomes em português do harness

Fonte: `origin/main` do clone `C:/src/wms-workspace` (lido só com `git show` e `git ls-tree`), mais os nomes de branch remota (`git branch -r`). Fora do inventário: `repos/` e `docs/harness/historico/`. Os nomes oficiais do Spec Kit (`speckit.specify`, `speckit.plan`, `speckit.bug.assess`, `speckit.refactor.assess`, `speckit.refactor.apply`, `speckit.refactor.verify`, `converge`, `bug-start`, `commit-push` etc.) já estão em inglês e ficam como estão. Texto corrido (mensagens de erro, descrições, instruções dentro dos comandos) não entra: só nomes que um dev vê ou que um script lê.

Limite da leitura: só o que está no `origin`. Branches e arquivos locais do clone (que tem trabalho local) e o repo de discovery não foram olhados.

## Resumo

| # | Categoria | Linhas de tabela (cada linha pode agrupar vários nomes) | Quem vê |
|---|---|---|---|
| 1 | Comandos, skills e eventos de hook | 16 (9 comandos/skills em português de 21, 8 eventos em português de 16) | Dev (digita e vê) |
| 2 | CLI `tools/ws/ws` (subcomandos, opções, palavras) | 55 (12 subcomandos de `fatia`, 12 opções, 4 de `atlas`, 4 de `pr`) | Dev (digita e vê) |
| 3 | Scripts, módulos e arquivos de `tools/` | 21 | Interno (time do harness); `relevancia.ini` e os scripts chamados pelos comandos aparecem ao dev |
| 4 | Branches (padrões e fixas) | 16 | Dev (cria, vê no Azure DevOps) |
| 5 | Pastas e arquivos de artefato do workspace | 26 | Dev |
| 6 | Valores enumerados, estados, cabeçalhos e rótulos lidos por script | 29 (mais de 70 valores) | Dev (documentos e saída) e script |
| 7 | Configuração, variáveis de ambiente e chaves de JSON | 28 (mais de 60 nomes) | `.ini` e variáveis: dev/time; JSON: interno, exceto `achados.json` (o agente escreve) |
| 8 | Prefixos de commit e marcadores fixos | 25 | Dev (histórico e PRs) |
| 9 | Funções e variáveis de shell/Python | 18 linhas; cerca de 200 funções em 31 arquivos | Interno |
| 10 | Outros (CSV do Atlas, âncoras da doc, rótulos da doc) | 25 | Misto |

Visível ao dev, sem filtro: categorias 1, 2, 4, 5, 6 (parte), 8. Interno: 3 (quase tudo), 7 (JSON de contexto e plano), 9.

### O que quebra se renomear (dados já commitados ou no origin)

Verificado no `origin`:

- `refactors/`, `bugs/` e `specs/` **não existem no `origin/main`**. Não há `refactors/fatias.md`, nenhum plano de subida, nenhuma fatia ou card gravado. Logo, renomear estados, cabeçalhos e nomes de arquivo de refactor **não quebra dado commitado no main**. Isso vale só enquanto nenhum dev tiver `refactors/` em branch local ainda não enviada (não dá para ver daqui). Quanto antes a troca, mais barata.
- Existem 2 branches `hotfix/inc-20261021-*` com `bugs/<slug>/assessment.md|fix.md|test.md`. Os campos dessas pastas já estão em inglês (`Slug`, `Verdict`, `Result: verified|partial|failed`, `Status: applied`) porque vêm da extensão `bug` oficial. Não mudam.
- **Dados em português que já estão no `origin/main`:**
  - 18 arquivos `docs/atlas/<repo>/_discovery/atlas.estado` com as chaves `split=`, `arvore=`, `data=`. Renomear `arvore`/`data` exige migrar os 18 arquivos (ou ler as duas grafias por um tempo).
  - 4 `docs/atlas/<repo>/project-readme.md` com a linha `> **Atlas:** mapeamento pendente desde ... nas áreas: ...` (marcador lido pelo `plano.py`). Trocar o texto sem migrar deixa duplicado ao próximo `concluir`.
  - `docs/atlas/ferramentas-por-repo.yml` (chaves são nomes de repo, valores `cbm|graphify`: sem português, não quebra).
  - `docs/atlas/impacto/indice.csv`, `ciclos.csv`, `filas.csv`, `servico-servico.csv`, `objetos-compartilhados.csv`, `nao-resolvidos.csv`: gerados por `build-map.py` e `impacto.py`; regeneram por inteiro, só dá diff grande. `procs-escopo.csv` e `jobs-sqlagent.csv` **não são gerados** por esses scripts (vêm da importação do SP0): renomear cabeçalho exige migrar à mão.
  - 18 `docs/atlas/<repo>/edges.csv` (e `edges-consolidado.csv`, `edges-sqlagent.csv`, `edges-sqldef.csv`): cabeçalho `repo,app,tipo,alvo,detalhe,evidencia` lido por `build-map.py`, `build-viz.py`; o prompt do mapeamento manda o subagente escrever `app,tipo,alvo,detalhe,evidencia`. Renomear exige migrar os CSV, o prompt e os dois scripts juntos.
  - `.gitattributes`: `/refactors/fatias.md merge=union` (renomear o arquivo exige mudar essa linha).
  - `workspace.pr.ini` (seções `azure`, `chat`, `teste`; chaves `organizacao`, `projeto`, `padrao`, `homolog`, `producao`) e `workspace.repos` (só prefixo/url/branch, sem português).
  - `.specify/extensions.yml`, `.specify/extensions/*/extension.yml`, `.specify/extensions/.registry`, `.specify/integrations/*.manifest.json` e as `.claude/skills/speckit-*` e `speckit-ws-*` **são gerados** por `ws speckit`: renomear comando exige mudar a fonte em `tools/speckit/` e rodar `ws speckit` de novo (e fazer commit de `.specify/` e `.claude/skills/`). Os clones dos devs precisam rodar `ws speckit` depois do merge.
- **Branches no `origin` com nome em português ou fixo:** `atlas/atualizacao` (nome fixo, `WS_ATLAS_BRANCH`; existe no origin, com PR possivelmente aberto), `atlas/atualizacao-ws-002` (sobra), `ws/sync` (inglês, não muda), `homolog` (ramo de teste, existe nos repos do Azure DevOps: é o nome real do ramo, não é só do harness). Não existe nenhuma `refactor/*` no origin (as `harness/*` são branches de desenvolvimento do harness, não vão para a lista). `hotfix/inc-20261021-*`: o prefixo `hotfix/` é inglês; `inc-` é abreviação de incidente (pt) e está em 2 branches e 2 pastas `bugs/` existentes.
- PRs já abertos no Azure DevOps: os comentários da revisão levam `<!-- ws-revisao:<id> -->`. Renomear o marcador faz o `ws pr comentar` não reconhecer o que já foi publicado e duplicar comentários nesses PRs. O `<!-- ws-pr:subtrees -->` já é inglês.
- Testes: `tools/ws/tests/` (28 arquivos) usa quase todos os nomes abaixo (cabeçalhos da tabela, estados, mensagens). Qualquer renomeação de nome visível quebra testes e precisa de atualização junto, inclusive `docs_referencias.py`, que confere a doc contra subcomandos, skills e mensagens do código.

---

## 1. Comandos, skills e eventos de hook

Definidos em `tools/speckit/<ext>/extension.yml` e `tools/speckit/<ext>/commands/*.md`; instalados em `.specify/extensions/` e `.claude/skills/speckit-*/SKILL.md` (gerados). O dev vê como `/speckit-...` no Claude Code.

### 1.1 Comandos da extensão `refactor` (nossa)

| Nome atual | Definido em | Aparece ao dev | Sugestão |
|---|---|---|---|
| `speckit.refactor.subida` / `/speckit-refactor-subida` | `tools/speckit/refactor/extension.yml`, `commands/speckit.refactor.subida.md` | slash command, branch, docs | `speckit.refactor.rollout` |
| `speckit.refactor.validar` / `/speckit-refactor-validar` | idem, `...validar.md` | slash command, branch | `speckit.refactor.validate` |
| `speckit.refactor.desacoplar` / `/speckit-refactor-desacoplar` | idem, `...desacoplar.md` | slash command, doc | `speckit.refactor.decouple` |
| `speckit.refactor.remover` / `/speckit-refactor-remover` | idem, `...remover.md` | slash command, branch | `speckit.refactor.remove` |

Em inglês, sem mudar: `speckit.refactor.assess`, `apply`, `verify`. Também aparece o texto da extensão: `id: refactor`, nome "Refactor do workspace WMS" (prosa).

### 1.2 Comandos da extensão `ws` (nossa)

| Nome atual | Definido em | Aparece ao dev | Sugestão |
|---|---|---|---|
| `speckit.ws.bug-enviar` / `/speckit-ws-bug-enviar` | `tools/speckit/ws/extension.yml`, `commands/speckit.ws.bug-enviar.md` | hook automático | `speckit.ws.bug-submit` |
| `speckit.ws.bug-sem-correcao` | idem | hook automático | `speckit.ws.bug-no-fix` |
| `speckit.ws.refactor-enviar` | idem | hook automático | `speckit.ws.refactor-submit` |
| `speckit.ws.refactor-registro` | idem | hook automático | `speckit.ws.refactor-record` |
| `speckit.ws.promover` / `/speckit-ws-promover` | idem | o dev digita | `speckit.ws.promote` |

Em inglês: `speckit.ws.feature`, `commit-push`, `converge`, `bug-start`, `refactor-start`.

### 1.3 Skills avulsas (`.claude/skills/`)

| Nome atual | Definido em | Aparece ao dev | Sugestão |
|---|---|---|---|
| `ws-revisar` (`/ws-revisar <link>`) | `.claude/skills/ws-revisar/SKILL.md` | o dev digita | `ws-review` |
| `atlas-atualizar` | `.claude/skills/atlas-atualizar/SKILL.md` | chamada pelos hooks, citada na doc | `atlas-update` |
| `atlas-consultar` | `.claude/skills/atlas-consultar/SKILL.md` | chamada pelos comandos | `atlas-query` |

`codebase-discovery` e as `speckit-*` oficiais: inglês.

### 1.4 Eventos de hook (`hooks:` do `extension.yml`, `.specify/extensions.yml`, `tools/speckit/refactor/hooks.md`)

| Nome atual | Definido em | Hook registrado | Sugestão |
|---|---|---|---|
| `before_refactor_subida` / `after_refactor_subida` | `refactor/hooks.md` (regra), `ws/extension.yml` | `refactor-start` / `refactor-registro` | `before_refactor_rollout` / `after_refactor_rollout` |
| `before_refactor_validar` / `after_refactor_validar` | idem | idem | `before_refactor_validate` / `after_refactor_validate` |
| `before_refactor_desacoplar` / `after_refactor_desacoplar` | idem (o `before` é disparado, sem hook ws) | `refactor-enviar` (after) | `before_refactor_decouple` / `after_refactor_decouple` |
| `before_refactor_remover` / `after_refactor_remover` | idem | `refactor-start` / `refactor-enviar` | `before_refactor_remove` / `after_refactor_remove` |

Em inglês: `before_specify`, `after_converge`, `before_bug_assess`, `after_bug_assess`, `after_bug_test`, `before_refactor_assess`, `after_refactor_assess`, `after_refactor_verify`.

Rótulo no texto dos presets/comandos que não é nome: `**Idioma:**` (prosa). O arquivo `hooks.md` cita `Automatic Hook`/`Executing:` (inglês, do Spec Kit).

---

## 2. CLI `tools/ws/ws`

Definido em `tools/ws/ws` (despacho), `tools/ws/lib/*.sh` e `tools/ws/pr/__main__.py`. O dev digita e vê em `AGENTS.md`, `docs/harness/*` e nos comandos.

### 2.1 Subcomandos de primeiro nível e grupos

| Nome atual | Definido em | Aparece ao dev | Sugestão |
|---|---|---|---|
| `ws add`, `start`, `sync`, `push`, `maintain`, `speckit`, `atlas`, `refactor`, `pr` | `tools/ws/ws` | digita | já em inglês |
| `ws refactor fatia` | `lib/refactor.sh` (`ws_refactor`) | digita | `ws refactor slice` |

### 2.2 `ws refactor fatia <sub>` (`lib/fatia.sh`)

| Nome atual | Aparece ao dev | Sugestão |
|---|---|---|
| `pendentes` | digita | `pending` |
| `status` | digita | já inglês |
| `cria` | digita | `create` |
| `tipo` | digita | `type` |
| `aprova` | digita | `approve` |
| `card` | digita | já inglês |
| `etapa` | digita | `stage` |
| `plano` | digita | `plan` |
| `atualiza` | digita | `update` |
| `estado` | digita (consulta) | `state` |
| `tipo-de` | digita (consulta) | `type-of` |
| `chave-de` | digita (consulta) | `toggle-of` |

### 2.3 Opções e palavras posicionais de `ws refactor fatia`

| Nome atual | Em qual subcomando | Sugestão |
|---|---|---|
| `--titulo` | `cria` | `--title` |
| `--desacoplamento` | `cria` | `--decoupling` |
| `--tipo` | `cria` | `--type` |
| `--depende` | `cria` | `--depends-on` |
| `--fatia` | `card` | `--slice` |
| `--estado` | `card` | `--state` |
| `--sistemas` | `card` | `--systems` |
| `--objetos` | `card` | `--objects` |
| `--onde` | `card` | `--read-at` (ou `--where`) |
| `--nota` | `etapa` | `--note` |
| `--desde` | `atualiza` | `--since` |
| `--motivo` | `atualiza` | `--reason` |
| alvo `convivencia` / `antigo` | `atualiza` | `coexistence` / `legacy` |
| alvo `entregue`, `validada`, `validacao-falhou`, `desacoplada`, `chave-removida` | `etapa` | `delivered`, `validated`, `validation-failed`, `decoupled`, `toggle-removed` |
| valor `rascunho` / `revisado` | `plano` | `draft` / `reviewed` |
| valor `com-chave` / `sem-chave` | `cria`, `tipo`, saída de `tipo-de` | `with-toggle` / `without-toggle` |
| valor `diagnóstico` / `aplicado` / `entregue` | `card --estado` | `diagnosis` / `applied` / `delivered` |

### 2.4 `ws atlas <sub>` (`lib/atlas.sh`, `tools/atlas/plano.py`)

| Nome atual | Sugestão |
|---|---|
| `ws atlas plano` | `plan` |
| `ws atlas incorpora` | `incorporate` |
| `ws atlas concluir` | `finish` |
| `ws atlas mapas` | `maps` |
| `--gatilho start|converge|manual` | `--trigger` |
| `--repos`, `--falhas`, `--hoje`, `--base` | `--repos` (inglês), `--failures`, `--today`, `--base` (inglês) |
| `--do-zero` | `--from-scratch` |
| `--todos` (em `mapas`) | `--all` |
| `--acoes`, `--mudou`, `--sem` (`plano.py lista`) | `--actions`, `--changed`, `--without` |
| subcomandos do `plano.py`: `gerar`, `lista`, `grava-estado` | `generate`, `list`, `write-state` |
| `--raiz` (`build-map.py`, `build-viz.py`) | `--root` |
| `--banco`, `--clones` (`importa-mapeamento.sh`) | `--database`, `--clones` (inglês) |
| valores de ação do plano: `atualizar`, `do-zero`, `avancar`, `adiar`, `pendente`, `nada` | `update`, `from-scratch`, `advance`, `defer`, `pending`, `none` |

### 2.5 `ws pr <sub>` (`lib/pr.sh`, `tools/ws/pr/__main__.py`)

| Nome atual | Aparece ao dev | Sugestão |
|---|---|---|
| `plano` | digita | `plan` |
| `abrir` | digita | `open` |
| `revisao` | digita (pelo `/ws-revisar`) | `review` |
| `comentar` | digita (pelo `/ws-revisar`) | `comment` |
| `homolog` (destino) | digita | `staging` (decidir: é também o nome real do ramo `homolog`; ver 7.4) |
| `main` (destino) | digita | já inglês |
| `--card` | digita | já inglês |

### 2.6 Outros subcomandos e modos de scripts de comando

| Nome atual | Definido em | Sugestão |
|---|---|---|
| `ws-refactor-start.sh --fatia <código> --subida|--validar|--remover` | `tools/speckit/ws/scripts/bash/ws-refactor-start.sh` | `--slice`, `--rollout`, `--validate`, `--remove` |
| `ws-refactor-start.sh <slug> --rodada` | idem | `--round` |
| `ws-refactor-confere.sh <commit>` | `ws-refactor-confere.sh` | ver 3 |
| `ws maintain`, `ws sync`, `ws push`, `ws start`, `ws add` | inglês | sem mudança |

---

## 3. Scripts e arquivos de `tools/`

Interno, salvo indicação. Renomear arquivo exige atualizar `ws speckit`, `AGENTS.md`, `docs/harness/4-manter.md` (tabela de arquivos), os testes e as chamadas nos comandos `.md`.

| Nome atual | Onde | Sugestão |
|---|---|---|
| `tools/speckit/ws/scripts/bash/ws-bug-registro.sh` | chamado por `speckit.ws.bug-sem-correcao` | `ws-bug-record.sh` |
| `ws-refactor-confere.sh` | chamado por `speckit.refactor.verify` (o dev vê o comando) | `ws-refactor-check.sh` |
| `ws-refactor-registro.sh` | chamado por `speckit.ws.refactor-registro` | `ws-refactor-record.sh` |
| `tools/atlas/plano.py` | `ws atlas plano` | `plan.py` |
| `tools/atlas/impacto.py` | usado por `build-map.py` | `impact.py` |
| `tools/atlas/relevancia.ini` | lido por `plano.py` e `ws_atlas_cfg`; o time edita | `relevance.ini` |
| `tools/atlas/importa-mapeamento.sh` | script único de importação do SP0 | `import-mapping.sh` |
| `tools/atlas/instala-cbm.sh` | instalador do codebase-memory-mcp | `install-cbm.sh` |
| `tools/atlas/prompt-mapeamento.md` | prompt da skill `atlas-atualizar` | `mapping-prompt.md` |
| `tools/atlas/grafo-template.html` | `build-viz.py` | `graph-template.html` |
| `tools/atlas/VERSOES.md` | tabela de versões fixadas | `VERSIONS.md` |
| `tools/speckit/refactor/templates/desacoplamento-template.md` | `ws_refactor_assess` copia | `decoupling-template.md` |
| `tools/speckit/refactor/templates/plano-subida-template.md` | idem | `rollout-plan-template.md` |
| `tools/ws/pr/abrir.py` | módulo | `open.py` (cuidado: `open` é builtin; melhor `open_prs.py`) |
| `tools/ws/pr/entrega.py` | módulo | `delivery.py` |
| `tools/ws/pr/revisao.py` | módulo | `review.py` |
| `tools/ws/pr/textos.py` | módulo | `texts.py` |
| `tools/ws/pr/azure.py`, `config.py` | módulo | já inglês |
| `tools/ws/lib/fatia.sh` | grupo `fatia` | `slice.sh` |
| `tools/ws/tests/test_atlas_concluir.sh`, `test_atlas_impacto.sh`, `test_atlas_instala.sh`, `test_atlas_mapas.sh`, `test_atlas_plano.sh`, `test_ciclo.sh`, `test_docs_referencias.sh`, `test_fatia.sh`, `test_importa_mapeamento.sh` | testes | acompanham o nome da peça testada |
| `tools/ws/tests/atlas_lib.sh`, `pr_lib.sh`, `docs_referencias.py` | helpers de teste | `docs_references.py`; os `_lib` já são neutros |

Já em inglês: `tools/ws/ws`, `lib/{add,atlas,common,maintain,pr,push,refactor,remote,speckit,start}.sh`, `build-map.py`, `build-viz.py`, `tools/speckit/*/preset.yml`, `extension.yml`, `hooks.md`, `vendor/git-subtree-ws`.

---

## 4. Branches

Criadas por `ws start` e por `ws-*-start.sh`, `ws refactor fatia atualiza`, `atlas-atualizar`. O dev vê no `git branch`, nos PRs e no Azure DevOps.

| Padrão atual | Definido em | Sugestão |
|---|---|---|
| `refactor/eap-<código com hífens>-subida[-k]` | `ws-refactor-start.sh` (`$pre-subida`), `abrir.py` (regex `-subida(-\d+)?$`) | `refactor/wbs-<code>-rollout[-k]` |
| `refactor/eap-<código>-validar[-k]` | idem | `...-validate[-k]` |
| `refactor/eap-<código>-remover` | idem | `...-remove` |
| `refactor/eap-<código>-convivencia[-k]` | `fatia.sh` (`ws_fatia_atualiza`) | `...-coexistence[-k]` |
| `refactor/eap-<código>-antigo[-k]` | idem | `...-legacy[-k]` |
| `refactor/eap-<código>-desacoplar` (citado na pergunta do pedido) | não existe: o desacoplar roda na branch `-validar` | sem ação |
| `refactor/<slug>` e `refactor/<slug>-r<k>` | `ws-refactor-start.sh` (o `-r<k>` é "rodada") | `-r<k>` pode ficar (é letra, não palavra); se trocar, `-round<k>` |
| `rf-<AAAAMMDD>-<descrição>` (slug de refactor sem work item) | `ws-refactor-start.sh`, `fatia.sh` (`rf-*`) | `rf-` pode ficar (refactor); AAAAMMDD vira `YYYYMMDD` só na prosa |
| `inc-<AAAAMMDD>-<descrição>` (slug de bug sem work item) | `ws-bug-start.sh` | `inc-` (incidente) vira `inc-` mesmo em inglês (incident); pode ficar |
| `hotfix/<slug>` | `ws-bug-start.sh`, `ws-bug-registro.sh` | já inglês |
| `atlas/atualizacao` (nome fixo, `WS_ATLAS_BRANCH`) | `lib/atlas.sh` | `atlas/update` (existe no origin: migrar a branch) |
| `atlas/manual-<AAAAMMDDHHMM>` | `atlas-atualizar/SKILL.md` | `atlas/manual-...` já inglês |
| `ws-NNN-<nome>[-r<k>]` (features) | `ws-feature.sh` | `ws-NNN` já neutro |
| `ws/sync` | `WS_BASE` | já inglês |
| `homolog` (ramo de teste de cada repo) | `workspace.pr.ini` (`[teste] padrao = homolog`) | **não renomear**: é o ramo real nos repos do Azure DevOps |
| `develop` (ramo de teste do backoffice frontend) | `workspace.pr.ini` | já inglês |

Nome de chave `eap-<código com hífens>` (ex.: `eap-1-1-4`): ver 8.

---

## 5. Pastas e arquivos de artefato do workspace

Criados pelos comandos de refactor/bug/feature. Estado no `origin/main`: nenhum existe ainda (ver resumo).

| Nome atual | Definido em | Aparece ao dev | Sugestão |
|---|---|---|---|
| `refactors/fatias.md` | `fatia.sh` (`WS_FATIAS`), `.gitattributes`, `ws-refactor-start.sh`, `entrega.py` | dev lê; nunca edita | `refactors/slices.md` |
| `refactors/fatias/<código>/` | comandos refactor, `entrega.py` (`_ORIGENS`) | dev lê | `refactors/slices/<code>/` |
| `refactors/fatias/<código>/plano-subida.md` | `speckit.refactor.subida`, `entrega.py`, `revisao.py` (resumo do PR) | dev lê/edita (o time completa) | `rollout-plan.md` |
| `refactors/fatias/<código>/validacao.md` | `speckit.refactor.validar` | dev lê | `validation.md` |
| `refactors/fatias/<código>/desacoplar.md` | `speckit.refactor.desacoplar`, lido pelo `refactor-enviar` | dev lê | `decouple.md` |
| `refactors/fatias/<código>/remover.md` | `speckit.refactor.remover`, lido pelo `refactor-enviar` | dev lê | `remove.md` |
| `refactors/desacoplamentos/<nome>.md` | `speckit.refactor.assess`, `AGENTS.md`, camada 3 | dev lê/edita | `refactors/decouplings/<name>.md` |
| `refactors/chaves.md` | ADR 0002 (substituído pelo ADR 0003; só resta em texto e em teste que confere ausência) | histórico | `toggles.md` se um dia voltar |
| `refactors/<slug>/{assessment,apply,verify}.md` | extensão refactor | dev lê | já inglês |
| `bugs/<slug>/{assessment,fix,test}.md` | extensão bug oficial | dev lê | já inglês |
| `specs/ws-NNN-<nome>/` | feature | dev lê | já neutro |
| `.ws/revisao/<id>/` (`contexto.json`, `achados.json`, `<repo>.diff`, `workspace.diff`, `arvore/`) | `revisao.py`, `.gitignore` (`.ws/`), `ws-revisar/SKILL.md` | dev vê | `.ws/review/<id>/`, `context.json`, `findings.json`, `tree/` |
| `.ws/graphify/frontends.json` | `ws_atlas_mapas` | interno | já neutro |
| `.git/atlas-plano.json` | `plano.py` | interno | `atlas-plan.json` |
| `docs/atlas/impacto/indice.csv` | `impacto.py` | consultado pelo agente | `index.csv` |
| `docs/atlas/impacto/ciclos.csv` | `impacto.py` | agente | `cycles.csv` |
| `docs/atlas/impacto/<slug>.completo.md` | `impacto.py` | agente | `<slug>.full.md` |
| `docs/atlas/<repo>/_discovery/atlas.estado` | `plano.py`, `atlas.sh` (`importa-mapeamento.sh` cria) | interno | `atlas.state` |
| `docs/atlas/mapa-arquitetura.md`, `mapa.mmd` | `build-map.py` | dev/agente | `architecture-map.md`, `map.mmd` |
| `docs/atlas/servico-servico.csv`, `objetos-compartilhados.csv`, `filas.csv`, `nao-resolvidos.csv`, `procs-escopo.csv`, `jobs-sqlagent.csv`, `grafo.html` | `build-map.py`, `build-viz.py` | agente | `service-service.csv`, `shared-objects.csv`, `queues.csv`, `unresolved.csv`, `procs-scope.csv`, `sqlagent-jobs.csv`, `graph.html` |
| `docs/atlas/ferramentas-por-repo.yml` | `ws_atlas_mapa_de` | time edita | `tools-by-repo.yml` |
| `docs/atlas/banco/<db>/{dependencies,objects,synonyms}.csv` | importação | agente | já inglês (`banco/` vira `database/`) |
| `docs/atlas/impacto/` (pasta) e `docs/atlas/banco/` (pasta) | `impacto.py`, `atlas-consultar` | agente | `impact/`, `database/` |
| `docs/harness/1-comecar.md`, `2-quando-da-errado.md`, `3-alem-do-basico.md`, `4-manter.md` | `docs/harness/`, `README.md`, `docs_referencias.py` | dev lê | `1-getting-started.md`, `2-when-it-goes-wrong.md`, `3-beyond-the-basics.md`, `4-maintaining.md` |
| `docs/adr/0002-chaves-centrais.md`, `0003-fatias-pela-eap.md` | ADRs | dev lê | `0002-central-toggles.md`, `0003-slices-by-wbs.md` |
| modelos: `desacoplamento-template.md`, `plano-subida-template.md` | `tools/speckit/refactor/templates/`, `.specify/extensions/refactor/templates/` | agente copia | ver 3 |

---

## 6. Valores enumerados, estados e cabeçalhos que script lê

### 6.1 Documento `refactors/fatias.md` (`fatia.sh`; `ws-refactor-start.sh` repete os valores no awk)

Cabeçalhos exatos (comparados literalmente por `ws_fatia_le` e por `no_ref()` no `ws-refactor-start.sh`; `entrega`/testes repetem):

| Nome atual | Sugestão |
|---|---|
| Tabela de fatias: `Fatia`, `Título`, `Desacoplamento`, `Chave`, `Etapa`, `Desde`, `Plano`, `Depende de`, `Nota` | `Slice`, `Title`, `Decoupling`, `Toggle`, `Stage`, `Since`, `Plan`, `Depends on`, `Note` |
| Tabela de cards: `Card`, `Fatia`, `Sistemas`, `Objetos`, `Onde a chave é lida`, `Estado` | `Card`, `Slice`, `Systems`, `Objects`, `Where the toggle is read`, `State` |
| Seções do arquivo: `# Fatias de desacoplamento`, `## Fatias`, `## Cards` | `# Decoupling slices`, `## Slices`, `## Cards` |

Etapa da fatia (coluna `Etapa`; `ws_fatia_ordem_etapa`, `ordem_etapa()` em `ws-refactor-start.sh`, `ws refactor fatia estado`):

| Nome atual | Sugestão |
|---|---|
| `em andamento` | `in progress` |
| `entregue` | `delivered` |
| `convivência` | `coexistence` |
| `validada` | `validated` |
| `desacoplada` | `decoupled` |
| `chave removida` | `toggle removed` |

Estado do card (coluna `Estado`): `diagnóstico` (`diagnosis`), `aplicado` (`applied`), `entregue` (`delivered`).

Estado do plano (coluna `Plano`): `-` (vazio, fica `-`), `rascunho` (`draft`), `revisado` (`reviewed`), `executado` (`executed`).

Coluna `Chave`: `eap-<código>` (`wbs-<code>`; o teste `[[ == eap-* ]]` define "com chave"), `sem chave (pendente)` (`no toggle (pending)`), `sem chave (aprovada AAAA-MM-DD)` (`no toggle (approved YYYY-MM-DD)`; a junção procura `*aprovada*`).

Coluna `Nota` (texto gerado): `validação falhou em <data>: <motivo>`, `antigo em <data>: <motivo>`, `sem motivo registrado` (prosa gerada; vira inglês junto).

Valores de tipo: `com-chave` / `sem-chave` (ver 2.3). Valores de modo da chave (ADR 0002, camada 3, `assessment.md`, tela do legado): `antigo`, `paralelo`, `sombra`, `novo`, com a troca direta `antigo`→`novo` → `legacy`, `parallel`, `shadow`, `new`. A tela da chave é do produto (AWX.ERP.Connector), então esses valores passam pelo código de produto, não só pelo harness.

Prazo/variável: `WS_FATIA_PRAZO_CONVIVENCIA=14` (ver 7.2).

### 6.2 Rótulos dos relatórios (`**Campo:** valor`), lidos pelo agente e, pelo `refactor-enviar`, pelo comando

| Nome atual | Onde | Sugestão |
|---|---|---|
| `**Resultado:** ok|falhou` | `verify.md`, `desacoplar.md`, `remover.md` (lido por `refactor-enviar`) | `**Result:** ok|failed` |
| `**Resultado:** validado|falhou` | `validacao.md` | `**Result:** validated|failed` |
| `**Veredito:** refactor|reclassificar` | `assessment.md` (lido por `refactor-registro` e `apply`) | `**Verdict:** refactor|reclassify` |
| `**Tipo:** interno | desacoplamento` | `assessment.md` | `**Type:** internal | decoupling` |
| `**Aprovada pelo líder:** pendente|sim, <data>` | `assessment.md` (fatia sem chave) | `**Approved by lead:** pending|yes, <date>` |
| `**Aprovada pelo usuário:** pendente|sim, <data>` | `assessment.md` (exceção) | `**Approved by user:** ...` |
| `**Slug:**`, `**Work item:**`, `**Data:**`, `**Desacoplamento:**`, `**Fatia (EAP):**`, `**Estado:**`, `**Depende de:**` | modelos de `assessment.md` e de `plano-subida.md` | `**Date:**`, `**Decoupling:**`, `**Slice (WBS):**`, `**State:**`, `**Depends on:**` |
| Seções: `Para retomar`, `## Rodada <k>`, `Caminho novo`, `Estado atual e alvo`, `Afetados`, `Caracterização`, `Linha de base`, `Cards e PRs`, `Ordem de deploy`, `Scripts de banco`, `Reversão`, `Critérios de validação`, `Para o time completar` | modelos e comandos | nomes em inglês correspondentes |
| Marcador de lado do `bug`: `Verdict`, `Result`, `Status` | já inglês | sem ação |

### 6.3 Plano do Atlas (`.git/atlas-plano.json`, `plano.py`) e relatório de impacto

| Nome atual | Sugestão |
|---|---|
| `acao`: `nada`, `atualizar`, `do-zero`, `avancar`, `adiar`, `pendente` | `none`, `update`, `from-scratch`, `advance`, `defer`, `pending` |
| `motivo`: `feature`, `manual`, `sem-estado`, `split-ausente`, `fetch-falhou`, `sem-mudanca`, `irrelevante`, `contrato`, `intervalo`, `volume`, `interno`, `limite` | `feature`, `manual`, `no-state`, `split-missing`, `fetch-failed`, `no-change`, `irrelevant`, `contract`, `interval`, `volume`, `internal`, `limit` |
| marcador no `project-readme.md`: `> **Atlas:** mapeamento pendente desde <data> nas áreas: ...` | `> **Atlas:** mapping pending since <date> in areas: ...` (migrar 4 arquivos) |
| `tipo` das páginas de impacto: `tabela`, `trigger`, `procedure`, `objeto SQL`, `endpoint`, `sinônimo`, `view`, `função`, `fila`, `procedure, fora do escopo: ...` | `table`, `trigger`, `procedure`, `SQL object`, `endpoint`, `synonym`, `view`, `function`, `queue`, `procedure, out of scope: ...` |
| `tipo` das arestas (`edges-*.csv`): `http-in`, `http-out`, `db-read`, `db-write`, `db-exec`, `job`, `mq-pub`, `mq-sub`, `other-out`; no mapa `fila` | já inglês, salvo `fila` (`queue`) |
| `escopo` em `procs-escopo.csv`: `fora` | `out` |
| `gatilho`: `start`, `converge`, `manual` | já inglês |

### 6.4 Achados da revisão (`achados.json`, `revisao.py`, `ws-revisar/SKILL.md`)

| Nome atual | Sugestão |
|---|---|
| `ponto`: `conformidade`, `contratos`, `regras`, `defeitos`, `banco` | `compliance`, `contracts`, `rules`, `defects`, `database` |
| `gravidade`: `alta`, `média`, `baixa` | `high`, `medium`, `low` |

### 6.5 Marcadores `[existe: !id]` e `[novo]` (saída de `ws pr plano`, `abrir.py`)

| Nome atual | Sugestão |
|---|---|
| `[existe: !<id>]` | `[exists: !<id>]` |
| `[novo]` | `[new]` |

---

## 7. Configuração, variáveis de ambiente e chaves de JSON

### 7.1 Arquivos de configuração

| Nome atual | Definido em | Sugestão |
|---|---|---|
| `workspace.pr.ini`: seção `[azure]`, chave `organizacao`, `projeto` | `workspace.pr.ini`, `config.py` | `organization`, `project` |
| `[chat]` com `homolog`, `producao` | idem | `staging`, `production` (e a palavra que `ws pr` aceita, ver 2.5) |
| `[teste]` com `padrao` e `<prefixo do repo> = <ramo>` | idem | `[test]`, `default` |
| `workspace.repos` | manifesto (prefixo, url, branch) | já neutro |
| `relevancia.ini`: seções `[ignorar]`, `[contrato]`, `[politica]` | `tools/atlas/relevancia.ini`, `plano.py`, `atlas.sh` | `[ignore]`, `[contract]`, `[policy]` |
| `relevancia.ini`: chaves `padroes`, `caminhos`, `palavras` | idem | `patterns`, `paths`, `words` |
| `relevancia.ini` `[politica]`: `intervalo_dias`, `limiar_arquivos`, `limite_minimo`, `tokens_por_arquivo`, `tokens_minimo_repo`, `tokens_do_zero`, `pr_max_repos`, `pr_max_dias` | idem | `interval_days`, `file_threshold`, `minimum_limit`, `tokens_per_file`, `minimum_tokens_per_repo`, `tokens_from_scratch`, `pr_max_repos`, `pr_max_days` |
| `docs/atlas/ferramentas-por-repo.yml` | sem português nas chaves | arquivo: ver 5 |
| `atlas.estado`: chaves `split`, `arvore`, `data` | `plano.py` | `split`, `tree`, `date` (migrar 18 arquivos) |
| `.gitattributes`: `/refactors/fatias.md merge=union` | `.gitattributes` | acompanha o arquivo (ver 5) |
| `.gitignore`: `.ws/`, `docs/atlas/*/_discovery/*` (e a exceção `atlas.estado`) | `.gitignore` | acompanha |

### 7.2 Variáveis de ambiente (leitura ou escrita pelo harness; as de teste ficam por último)

| Nome atual | Definido em | Aparece ao dev | Sugestão |
|---|---|---|---|
| `WS_ATLAS_<CHAVE>` (sobrepõe uma chave de `[politica]`, ex.: `WS_ATLAS_PR_MAX_DIAS`) | `ws_atlas_cfg` | dev/time | `WS_ATLAS_PR_MAX_DAYS` etc., acompanha 7.1 |
| `WS_HOJE` (data de hoje) | `refactor.sh`, `fatia.sh` | testes | `WS_TODAY` |
| `WS_CHAT_SAIDA` (grava a mensagem em vez de postar) | `abrir.py` | testes | `WS_CHAT_OUTPUT` |
| `WS_ATLAS_REPOS_SEGREDO` (interno) | `atlas.sh` | interno | `WS_ATLAS_SECRET_REPOS` |
| `WS_ATLAS_SEGREDO` (regex, interno) | `atlas.sh` | interno | `WS_ATLAS_SECRET` |
| `WS_SYNC_TENTATIVAS` | `start.sh` | time | `WS_SYNC_ATTEMPTS` |
| `WS_SYNC_ERRO` (interno) | `start.sh` | interno | `WS_SYNC_ERROR` |
| `WS_FATIAS`, `WS_FATIA_CAB`, `WS_FATIA_CAB_CARDS`, `WS_FATIA_CODIGO`, `WS_FATIA_CARD`, `WS_FATIA_PRAZO_CONVIVENCIA`, `WS_FATIA_CONECTOR`, `WS_FATIA_USO` | `fatia.sh` (variáveis de shell, não do ambiente) | interno | `WS_SLICES`, `WS_SLICE_HEADER`, `WS_SLICE_CARDS_HEADER`, `WS_SLICE_CODE`, `WS_SLICE_CARD`, `WS_SLICE_COEXISTENCE_DAYS`, `WS_SLICE_CONNECTOR`, `WS_SLICE_USAGE` |
| `WS_REFACTOR_AWK_DATA` | `refactor.sh` | interno | `WS_REFACTOR_AWK_DATE` |
| `WS_TEST_REDE`, `WS_FAKE_AZ_ESTADO` (testes) | `tools/ws/tests/` | testes | `WS_TEST_NETWORK`, `WS_FAKE_AZ_STATE` |

Em português e muito usadas:

| Nome atual | Definido em | Sugestão |
|---|---|---|
| `WS_DESTINO` (branch de destino dos PRs, padrão `main`; 70 ocorrências, lida por `common.sh`, por todos os scripts de `tools/speckit/ws/scripts/bash/`, por `entrega.py` e pelos testes) | `lib/common.sh` | `WS_TARGET` |
| `WS_RAIZ` (só testes, 68 ocorrências) | `tools/ws/tests/` | `WS_ROOT` |

Já em inglês (ficam): `WS_BASE`, `WS_BIN`, `WS_BASH`, `WS_LIB`, `WS_REJOIN_THRESHOLD`, `WS_ATLAS_BRANCH`, `WS_CBM`, `WS_CBM_DISTRO`, `WS_CBM_SHA256`, `WS_GRAPHIFY`, `WS_SPECKIT_SRC`, `WS_AZ`, `WS_DIR`, `WS_TEST`.

### 7.3 Chaves de JSON que os scripts emitem ou leem

| Nome atual | Definido em | Sugestão |
|---|---|---|
| Saída dos `ws-*-start.sh`: `BRANCH_NAME`, `REFACTOR_DIRECTORY`, `BUG_DIRECTORY`, `FEATURE_NUM`, `FEATURE_DIRECTORY`, `EXISTING`, `ERROR` | `ws-refactor-start.sh`, `ws-bug-start.sh`, `ws-feature.sh` | já inglês |
| `AVISOS` | idem | `WARNINGS` |
| `contexto.json`: `pr{id,url,destino,branch}`, `base`, `origem`, `arvore`, `repos[{prefixo,nome,pr_id,pr_url,diff,arquivos}]`, `workspace{nome,pr_id,diff,arquivos}`, `publicados` | `revisao.py`, `ws-revisar/SKILL.md` | `destination`, `source`, `tree`, `prefix`, `name`, `files`, `published` |
| `achados.json`: `ponto`, `gravidade`, `repo`, `arquivo`, `linha`, `titulo`, `texto` | `revisao.py` (validação), `ws-revisar/SKILL.md` | `point`, `severity`, `repo`, `file`, `line`, `title`, `text` |
| `atlas-plano.json`: `gatilho`, `head`, `hoje`, `repos[{repo,prefixo,acao,motivo,split_atual,arvore_atual,split_gravado,mudou,arquivos,areas,tokens_estimados}]`, `tokens_estimados` | `plano.py` | `trigger`, `today`, `prefix`, `action`, `reason`, `current_split`, `current_tree`, `recorded_split`, `changed`, `files`, `areas`, `estimated_tokens` |

### 7.4 Observação sobre `homolog` / `producao`

`homolog` e `producao` aparecem como (a) argumento de `ws pr`, (b) chave do `[chat]`, (c) prefixo do título `[homolog] ...`, (d) nome real do ramo nos repos. Só (a), (b) e (c) são do harness; (d) não muda. Sugestão: `staging` e `production` nos três primeiros, mantendo `homolog` como valor de `[test] default`.

---

## 8. Prefixos de commit, mensagens e marcadores fixos

| Nome atual | Onde é escrito | Sugestão |
|---|---|---|
| `ws: add <prefixo>` | `lib/add.sh` | já inglês |
| `ws: sync <prefixo>` | `lib/start.sh` | já inglês |
| `ws: traz o main para a ws/sync` (mensagem de merge) | `ws_sync_traz` | `ws: bring main into ws/sync` |
| `ws maintain: marcador sem mudança no prefixo.` | `ws_mark_split` | `ws maintain: marker without change in the prefix.` |
| `atlas: atualiza mapeamento de <repos> (estado avançado: ...)` | `ws_atlas_mensagem` | `atlas: update mapping of ...` |
| `atlas: avança o estado de <repos>` | idem | `atlas: advance state of ...` |
| `atlas: atualiza os derivados` | idem | `atlas: update derived files` |
| `docs(eap-<código>): chave virada, convivência desde <data>` | `ws_fatia_atualiza` | `docs(wbs-<code>): toggle switched, coexistence since <date>` |
| `docs(eap-<código>): chave de volta em antigo` | idem | `docs(wbs-<code>): toggle back to legacy` |
| `docs(eap-<código>): plano de subida <rascunho|revisado>` | `speckit.ws.refactor-registro` (proposta) | `docs(wbs-<code>): rollout plan <draft|reviewed>` |
| `docs(eap-<código>): fatia validada` | idem | `docs(wbs-<code>): slice validated` |
| `docs(eap-<código>): validação sem sucesso` | idem | `docs(wbs-<code>): validation failed` |
| `docs(<slug>): diagnóstico, não é refactor` | idem | `docs(<slug>): assessment, not a refactor` |
| `docs(<slug>): diagnóstico sem correção de código` | `speckit.ws.bug-sem-correcao` | `docs(<slug>): assessment without code fix` |
| `test(<slug>): caracterização` | `speckit.refactor.apply` | `test(<slug>): characterization` |
| `refactor(eap-<código>): desacopla <título da fatia>` | `speckit.ws.refactor-enviar` | `refactor(wbs-<code>): decouple <slice title>` |
| `refactor(eap-<código>): remove a chave` | idem | `refactor(wbs-<code>): remove the toggle` |
| `reverte repos/<repo>: PR abandonado` (mensagem sugerida na doc, não escrita por script) | `docs/harness/3-alem-do-basico.md` (seção "PR de um repo abandonado"), `test_ciclo.sh` | `revert repos/<repo>: abandoned PR` |
| Marcadores de PR: `<!-- ws-revisao:<id> -->` e o texto `_Revisão do harness_` | `revisao.py` | `<!-- ws-review:<id> -->`, `_Harness review_` |
| `<!-- ws-pr:subtrees -->`, `<!-- /ws-pr:subtrees -->`, cabeçalho `| Repo | PR |` | `textos.py` | já inglês |
| Título do PR: prefixo `[homolog] ` | `textos.py` | `[staging] ` (ver 7.4) |
| Prefixo de mensagens do `ws`: `ws: erro:`, `ws: aviso:`, `ws: GUARDA:` (lidos por `grep -E 'aviso:|pullrequestcreate'` nos scripts de comando, e conferidos pelo `docs_referencias.py`) | `common.sh` (`die`), `push.sh`, scripts | `ws: error:`, `ws: warning:`, `ws: GUARD:` |
| Nome da chave: `eap-<código com hífens>` (ex.: `eap-1-1-4`) | `ws_fatia_nome_chave`, ADR 0002/0003 | `wbs-1-1-4`; **as chaves futuras já nascem com esse nome no AWX.ERP.Connector**, então a troca tem de ocorrer antes da primeira fatia |
| Convencional aceito para o título do PR: `^(feat|fix|refactor|docs)\(` | `textos.py` | já inglês |
| Aviso fixo do PR: `**Complete este PR só depois que todos os PRs acima estiverem completados.**` e `**Não apague a branch de origem...**` | `textos.py` | prosa; traduzir se o time quiser PR em inglês |

---

## 9. Funções e variáveis em `tools/`

Só contagem e exemplos.

| Arquivo | Funções | Exemplos |
|---|---|---|
| `tools/ws/lib/fatia.sh` | 30 | `ws_fatia`, `ws_fatia_le`, `ws_fatia_junta`, `ws_fatia_escreve`, `ws_fatia_pendentes`, `ws_fatia_atualiza`, `ws_fatia_nome_chave`, `ws_fatia_confere_conector`, `ws_fatia_tipo_de`, `ws_fatia_aviso` |
| `tools/ws/lib/atlas.sh` | 20 | `ws_atlas_plano`, `ws_atlas_incorpora`, `ws_atlas_concluir`, `ws_atlas_publica`, `ws_atlas_monta`, `ws_atlas_filtra_segredos`, `ws_atlas_busca_bases`, `ws_atlas_mapa_de`, `ws_atlas_aviso_pr`, `ws_atlas_caminho_wsl` |
| `tools/ws/lib/refactor.sh` | 5 | `ws_refactor_hoje`, `ws_refactor_dias`, `ws_refactor_grava`, `ws_refactor_temp`; variável `RF_TMP` |
| `tools/ws/lib/start.sh` | 9 | `ws_sync_traz`, `ws_sync_prepara`, `ws_sync_repos`, `ws_sync_envia`, `ws_sync_avisos`, `ws_sync_na_falha`; var `WS_SYNC_TENTATIVAS` |
| `tools/ws/lib/maintain.sh`, `push.sh`, `remote.sh`, `common.sh` | 9 + 4 + 2 + 9 | `ws_commits_since_rejoin` (inglês); português só em variáveis locais (`ws_remote_heads` tem `bad`, ok) |
| `tools/speckit/ws/scripts/bash/ws-refactor-start.sh` | 11 | `no_ref`, `no_main`, `no_origin`, `local_existe`, `ordem_etapa`, `branches_dos_cards`, `exige_etapa`, `avisos_do_start`, `json_str`, `emit`; vars `fatia`, `modo`, `juntar`, `cards`, `chave` |
| `ws-feature.sh` | 14 | quase todos em inglês (`feat_num`, `cited_nums`, `spec_names`); `avisos_do_start` |
| `ws-bug-start.sh`, `ws-bug-registro.sh`, `ws-commit-push.sh`, `ws-refactor-registro.sh`, `ws-refactor-confere.sh` | 3 + 4 + 2 + 3 + 3 | `avisos_do_start`, `cresce_ok`, `alterados`, `fora`, `lista` |
| `tools/atlas/plano.py` | 17 | `gerar`, `lista`, `carrega`, `grava_estado`, `marca_pendencia`, `le_estado`, `caminho_plano`, `lista_cfg`, `manifesto`, `casa`, `existe`, `linhas_do_diff`, `arvore_do_split`; constantes `ACOES_MAPEAR`, `AVISO`, `SEM_COMMIT` |
| `tools/atlas/impacto.py` | 12 | `gera`, `_catalogo`, `_arestas`, `_triggers`, `_busca`, `_ciclos`, `_linha`, `_segmentos`, `_casa_rota`, `_slug`; constantes `LIMITE_PAGINA`, `TIPOS_SQL`, `FORA` |
| `tools/atlas/build-map.py`, `build-viz.py` | 9 + 5 | já em inglês na maior parte (`le_csv`, `le_sql` são português); constantes `CAMPOS` |
| `tools/ws/pr/abrir.py` | 12 | `abrir`, `plano`, `itens_do_plano`, `links_manuais`, `card_valido`, `posta_chat`, `recria_branches`, `ramo_existe`; classe `Item(prefixo, nome, url, ramo)` |
| `tools/ws/pr/entrega.py` | 14 | `le_entrega`, `acha_origem`, `le_resumo`, `base_nome`, `destino_nome`, `branch_atual`, `nome_da_url`, `manifesto`, `arquivos_alterados`, `prefixos_alterados`; classes `Entrega`, `Repo`; campos `raiz`, `origem`, `titulo`, `resumo` |
| `tools/ws/pr/revisao.py` | 10 | `revisao`, `comentar`, `id_achado`, `_publicados`, `_hunks`, `_alvo`, `_nomes`, `_ramo`; constantes `PONTOS`, `GRAVIDADES` |
| `tools/ws/pr/textos.py` | 6 | `titulo`, `descricao_subtree`, `descricao_workspace`, `le_tabela`, `mensagem_chat`; constantes `AVISO_ORDEM`, `AVISO_BRANCH`, `TABELA_INI`, `LIMITE` |
| `tools/ws/pr/config.py` | 3 | `le_config`, `ErroWs`, `Config(org, projeto, chat, ramo_padrao, ramos)`, `ramo_teste` |
| `tools/ws/pr/azure.py` | 6 | classes `ErroAzure`, `AzAusente`; métodos `listar_prs`, `criar_pr`, `atualizar_descricao`, `titulo_card`, `criar_thread`, `criar_ref`, `logado` |
| `tools/atlas/importa-mapeamento.sh`, `instala-cbm.sh` | 2 + 1 | variáveis `banco`, `clones`, `src`; `VERSAO`, `ARQUIVO`, `DESTINO` |

Total aproximado: 200 funções/métodos (cerca de 150 com nome parcial ou totalmente em português).

---

## 10. Outros nomes em português

| Nome atual | Onde | Aparece ao dev | Sugestão |
|---|---|---|---|
| Cabeçalho de `edges*.csv`: `repo,app,tipo,alvo,detalhe,evidencia` | `build-map.py`, `build-viz.py`, `prompt-mapeamento.md`, 18 `edges.csv` | agente/interno | `repo,app,type,target,detail,evidence` (migrar CSV) |
| Cabeçalho de `servico-servico.csv`: `origem,destino,via,n_arestas,exemplos` | `build-map.py` | agente | `source,target,via,n_edges,examples` |
| Cabeçalho de `objetos-compartilhados.csv`: `objeto,n_repos,escritores,leitores,executores` | idem | agente | `object,n_repos,writers,readers,executors` |
| Cabeçalho de `filas.csv`: `fila,publicadores,consumidores` | idem | agente | `queue,publishers,consumers` |
| Cabeçalho de `nao-resolvidos.csv`: `repo,tipo,alvo,no_atribuido` | idem | agente | `repo,type,target,assigned_node` |
| Cabeçalho de `indice.csv`: `objeto,tipo,pagina,afetados,profundidade` | `impacto.py` | agente | `object,type,page,affected,depth` |
| Cabeçalho de `ciclos.csv`: `ciclo,membros` | idem | agente | `cycle,members` |
| Cabeçalho de `jobs-sqlagent.csv`: `job,habilitado,agenda,bancos,escritas,leituras,procs,passos_nao_analisados` | importação (não gerado) | agente | `job,enabled,schedule,databases,writes,reads,procs,unanalyzed_steps` |
| Cabeçalho de `procs-escopo.csv`: `db,schema,proc,escopo,motivo` | importação | agente | `db,schema,proc,scope,reason` |
| Seções das páginas de impacto: `# Impacto:`, `## Por repo`, `## Ciclos`, `## Resumo por repo`, `Tipo:`, `Afetados:`, `Profundidade máxima:` | `impacto.py` | agente lê | `# Impact:`, `## By repo`, `## Cycles`, ... (prosa, nada lê por script) |
| Nomes de página de impacto: `fila-*`, `http-*`, `connectionstrings-*` (slug do objeto) | `impacto.py` | agente | `queue-*` (`http-*`, `connectionstrings-*` já inglês) |
| Pastas de doc por repo no Atlas: `docs/atlas/<repo>/{domain,business,tech,areas,_discovery}` | prompt do mapeamento, `codebase-discovery` | agente | já inglês |
| Rótulos da doc lidos por `docs_referencias.py`: `**Sintoma:**`, `**Causa:**`, `**O que fazer:**` | `docs/harness/2-quando-da-errado.md`, `docs_referencias.py` | dev lê | `**Symptom:**`, `**Cause:**`, `**What to do:**` (script e doc juntos) |
| Âncoras da doc (links `#chaves-centrais`, `#convivencia-e-a-chave`, `#o-documento-das-fatias`, `#o-plano-de-subida`, `#o-documento-do-desacoplamento`, `#atualizar-o-atlas-a-mao`, `#mapas-de-codigo-para-o-agente` etc.), conferidas pelo `docs_referencias.py` e citadas nos comandos | `docs/harness/*.md`, comandos `.md` | dev | mudam com os títulos em inglês |
| Nomes dos princípios da constitution: `I. Hierarquia` ... `VII. Refactor não muda comportamento` | `.specify/memory/constitution.md` | dev/agente ("regra II") | numerais romanos ficam; títulos em inglês |
| Siglas e termos do domínio nos nomes: `EAP` (estrutura analítica do projeto), `fatia`, `card`, `convivência`, `rodada` (`-r<k>`) | tudo acima | dev | `WBS`, `slice`, `card`, `coexistence`, `round` |
| `Idioma:` e o parágrafo "responda em português do Brasil" nos comandos | todos os `.md` | é regra de idioma, não nome | não renomear; decidir se continua |
| Campos do manifesto do Atlas por repo: `recon-manifest.md`, `traceability-index.md` | codebase-discovery | agente | já inglês |
| Nomes de ADR e títulos: `0001-workspace-git-subtree` | ADRs | dev | já inglês |
| `ws pr` chat: `[chat] producao` (ver 7.1) | idem | idem | idem |
| `README.md` raiz, `AGENTS.md`, `CLAUDE.md` | raiz | dev | nomes inglês; conteúdo em português (prosa) |
| Chaves de saída de `ws refactor fatia status`: `card`, `sistemas:`, `objetos:`, `chave lida em:`, `depende de:`, `plano:`, `nota:`, `falta:`, `desde`, `plano <estado>` | `fatia.sh` (`ws_fatia_resumo`, `ws_fatia_status`) | dev vê | `systems:`, `objects:`, `toggle read at:`, `depends on:`, `plan:`, `note:`, `missing:`, `since` (o comando `/speckit-refactor-*` e `refactor-start` não leem esses textos por script; só humanos) |
| Texto de saída de `pendentes`: `<código>  <título>  <etapa> desde <data> (N dia(s)): <passo>` e `[convivência há mais de 14 dias sem validação]` | `fatia.sh` | dev vê | prosa; traduzir junto |
| Aviso do `ws start`: `ws: aviso: N fatia(s) em convivência há mais de 14 dias sem validação: ...` | `ws_fatia_aviso` | dev vê | prosa |
| Nomes de módulos `ErroWs`, `ErroAzure`, `AzAusente` (exceções que o `__main__.py` captura) | `config.py`, `azure.py` | interno | `WsError`, `AzureError`, `AzMissing` |

---

## Ordem sugerida para a troca (só o que decorre dos achados)

1. Primeiro o que ainda não tem dado commitado: estados e cabeçalhos de `fatias.md`, nomes de arquivo de `refactors/`, branches `refactor/eap-*`, nome da chave `eap-*`, comandos/hooks de refactor, subcomandos de `ws refactor fatia`. Nenhuma fatia existe no `origin`; é a janela mais barata e a única em que a chave `eap-*` pode mudar sem migração no AWX.ERP.Connector.
2. Depois os que têm dado ou estado no `origin`, com migração: `atlas.estado` (18), marcador de pendência (4), cabeçalhos de CSV do Atlas (regenerados por script, mais `edges.csv` e os CSV importados), `atlas/atualizacao` (mover a branch e fechar o PR aberto), marcador `ws-revisao`.
3. Por último ou nunca: `homolog` como ramo real, `WS_DESTINO`/`WS_BASE` se houver scripts fora do repo que os usem (CI), e a prosa.
4. Em qualquer ordem, regenerar com `ws speckit` e atualizar `docs_referencias.py` e os 28 arquivos de `tools/ws/tests/` na mesma mudança.
