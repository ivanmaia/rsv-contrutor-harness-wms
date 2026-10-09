# SP2: Spec Kit multi-repo no workspace WMS (design)

- **Status:** aprovada pelo usuário em 2026-09-29
- **Subprojeto:** SP2. Depende do SP1 (ADR 0001 com os adendos 1 a 3, workspace `industria-logistica.wms.workspace` e `tools/ws`)
- **Evidências:** `poc/sp2-speckit/README.md` (Spec Kit 1.0.12 com extensão e preset locais) e `docs/discovery/sp1-bootstrap.md`
- **Onde se implementa:** no workspace `C:\src\wms-workspace`, não nesta pasta de discovery
- **Adendo (2026-10-05):** o SP3 renomeia `docs/sistemas/` → `docs/atlas/`, `tools/sistemas/` → `tools/atlas/` e `importa-discovery.sh` → `importa-mapeamento.sh`. O conhecimento dos sistemas passa a se chamar **Atlas** e o processo que o mantém, **mapeamento**. Ver a seção 6.8 de `2026-10-05-sp3-grafo-e-navegacao-design.md`. O texto abaixo mantém os nomes da época
- **Adendo (2026-10-07):** o AWX mantém o Spec Kit e a constitution dele, subordinados ao workspace, e as features do workspace passam a ser `ws-NNN`. Isso substitui a seção 1 (item 5), as linhas "Specs" e "Constitution" da seção 2 e a linha do AWX na seção 5.4. Ver `2026-10-07-sp2-adendo-harness-awx-subordinado-design.md`

## 1. Objetivo e critério de sucesso

Um dev ou agente roda o fluxo do Spec Kit na raiz do workspace. Uma spec pode cobrir vários repos, as tasks dizem em qual repo cada mudança acontece, e a implementação segue as instruções de cada repo tocado.

A feature está pronta quando:
1. `/speckit-specify` cria a branch com `ws start` e a spec em `specs/NNN-<nome>/`, com a seção "Repos afetados".
2. `/speckit-specify`, citando uma feature que já existe, edita a spec dela (living spec por feature) numa branch de revisão, sem sobrescrever nada.
3. Plan e tasks têm uma seção por repo e verificação de build e testes de cada repo.
4. Depois do `/speckit-converge`, o agente oferece `ws push`, que também pode ser rodado à mão a qualquer momento.
5. Os três repos com instruções próprias continuam com elas, subordinadas ao harness, e o AWX perde só a maquinaria de Spec Kit dele.

## 2. Decisões tomadas com o usuário

| Tema | Decisão |
|---|---|
| Agentes | Claude Code como principal; precisa ser possível somar depois qualquer agente que leia `AGENTS.md` |
| Specs | `specs/NNN-<feature>/` na raiz, numa sequência única. As specs `001` e `002` do AWX entram com o mesmo número |
| Living spec | Modelo do Spec Kit, por feature: o `spec.md` da feature é o contrato vivo; mudar a feature é editar esse spec, sem criar número novo |
| Constitution | Curta, só com o que vale para todos os repos. Os 9 princípios do AWX ficam no AWX |
| Conhecimento dos 17 repos | O discovery do SP0 entra no harness, em `docs/sistemas/` |
| Repos com instruções próprias | Transição: o workspace vira o caminho principal, mas os repos mantêm `CLAUDE.md`, `AGENTS.md`, constitution e rules, subordinados ao harness |
| Spec Kit | A versão mais recente (1.0.12 em 2026-09-25), integração `claude`, scripts `sh`, sem a extensão `git` |
| Integração com o `ws` | Uma extensão local `ws` e um preset local `multirepo`, sem editar o núcleo do Spec Kit |

## 3. Estrutura do workspace depois do SP2

```
<workspace>/
  AGENTS.md                      regras gerais (fonte única), com a seção gerenciada pelo agent-context
  CLAUDE.md                      @AGENTS.md
  .claude/skills/                speckit-* (geradas pelo Spec Kit), speckit-ws-feature, speckit-ws-push
  .specify/                      gerado pelo Spec Kit e versionado
    memory/constitution.md       constitution do workspace
    extensions/ws/, presets/multirepo/   instalados a partir de tools/speckit/
  tools/ws/                      já existe; ganha o comando `ws speckit`
  tools/speckit/VERSION          versão fixada do Spec Kit (1.0.12)
  tools/speckit/ws/              fonte da extensão ws
  tools/speckit/multirepo/       fonte do preset multirepo
  specs/NNN-<feature>/           sequência única
  docs/sistemas/
    mapa-arquitetura.md, *.csv   mapa cross-repo do SP0
    <repo>/                      domínio, business, tech e project-readme de cada um dos 17
  repos/<repo>/                  conteúdo de cada repo, incluindo as instruções próprias dele
```

## 4. Fluxo de uma feature

### 4.1 Feature nova
1. **`/speckit-specify <descrição>`**
   - O hook `before_specify`, obrigatório, roda `speckit-ws-feature`. O script calcula o próximo `NNN` em `specs/`, gera um nome curto e chama `tools/ws/ws start NNN-<nome>`.
   - Se o `ws start` falhar (conflito, rede, árvore suja), o script devolve JSON com `ERROR`. O `specify` para sem criar spec.
   - O núcleo cria `specs/NNN-<nome>/spec.md` com o template resolvido pelo preset.
   - A seção **"Repos afetados"** é obrigatória: um item `repos/<repo>` por repo, dizendo o que muda nele. Os consumidores de contratos saem de `docs/sistemas/mapa-arquitetura.md`.
2. **`/speckit-plan`**
   - Uma seção por repo afetado, com stack, comandos de build e teste e regras.
   - As fontes, nesta ordem: os arquivos de instrução do repo (seção 5.2), depois `docs/sistemas/<repo>/`, depois a constitution.
   - Se o plano mexe num contrato entre sistemas, ele lista os consumidores afetados.
3. **`/speckit-tasks`**
   - Cada tarefa leva `[repos/<repo>]` ou `[workspace]`, e as tarefas ficam agrupadas por repo.
   - `[workspace]` marca tarefas que mudam arquivos fora de `repos/`: `docs/sistemas/<repo>/` quando o comportamento documentado muda, `AGENTS.md`, uma ADR do harness ou `tools/`. Essas mudanças vão só no PR do workspace, não no `ws push`. Muitas features não terão nenhuma tarefa assim.
   - Cada grupo termina com uma tarefa de verificação: build e testes daquele repo, com as ferramentas dele.
4. **`/speckit-implement`**, depois **`/speckit-converge`**. O converge compara o código com spec, plan e tasks e acrescenta o que faltar.
5. **Push:**
   - O hook `after_converge`, **opcional**, oferece `speckit-ws-push`, que roda `tools/ws/ws push` e lista os PRs a abrir, um por repo.
   - Se o converge acrescentou tarefas, o hook sugere rodar `implement` e `converge` de novo antes do push.
   - O push também pode ser rodado à mão, com `/speckit-ws-push` ou `tools/ws/ws push`.
6. **Fechamento**, como no SP1, feito à mão pelo dev no Azure DevOps. O `ws` só envia as branches e lista os PRs a abrir.
   - O dev abre um PR por repo, e cada um passa pela revisão e pelo merge normais do time dono do repo.
   - Com todos mergeados, o dev abre o PR do workspace, que leva a spec e o harness.
   - O próximo `ws start` traz o resultado.

### 4.2 Mudança numa feature que já existe (living spec)
1. **`/speckit-specify` citando a feature** (número ou nome). Não há comando novo.
2. O hook `speckit-ws-feature` detecta que a feature existe em `specs/` e roda `ws start NNN-<nome>-r<k>`, com `k` = próxima revisão ainda sem branch local nem no origin do workspace.
3. O preset acrescenta ao comando `specify` a regra para feature existente:
   - usar a pasta dela como `SPECIFY_FEATURE_DIRECTORY`;
   - **não** copiar o template de novo;
   - editar o `spec.md` que já existe e atualizar os "Repos afetados";
   - registrar a revisão na seção **"Revisões"**, com data, branch e motivo.
4. O resto segue a seção 4.1, a partir do passo 2. Plan e tasks são regerados.

### 4.3 Onde a spec fica
- As specs ficam só no workspace: estão fora dos prefixos, e o `ws push` não as envia.
- O PR de cada repo cita `specs/NNN` e a revisão.

## 5. Constitution, `AGENTS.md` e repos com instruções próprias

### 5.1 Constitution do workspace (`.specify/memory/constitution.md`)
1. **Hierarquia.** A constitution e o `AGENTS.md` da raiz governam o que cruza repos e o jeito de trabalhar do agente. Dentro de `repos/<repo>/`, as instruções daquele repo valem para o código dele.
2. **Contratos entre sistemas.** Mudar um endpoint HTTP, uma fila, ou uma tabela, view ou procedure compartilhada exige listar os consumidores afetados, com base em `docs/sistemas/mapa-arquitetura.md`, e incluí-los nos "Repos afetados".
3. **Cada repo passa no próprio build e nos próprios testes**, com as ferramentas dele.
4. **Decisão relevante vira ADR aprovado por humano**, no repo se for só dele, ou no harness.
5. **Nada de segredo versionado.** Segredos que já existem são só registrados, nunca copiados.
6. **Simplicidade.** A menor mudança que atende a spec, sem refatoração fora do escopo.

### 5.2 Arquivos de instrução de um repo
São `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `docs/convencoes.md`, `docs/adr/` e, no AWX, `docs/constitution.md`.

### 5.3 `AGENTS.md` da raiz (regras operacionais)
- **Antes de mexer num repo, ler de forma explícita os arquivos de instrução dele.** Não depender do carregamento automático do Claude Code: com um `CLAUDE.md` na raiz, o `AGENTS.md` de um repo pode não ser carregado.
- **Instrução de repo que descreve o fluxo dele fora do workspace:** no workspace, vale o fluxo da raiz.
- **Conflito entre uma regra do repo e a constitution:** parar e perguntar ao humano.
- **Regra nova:** se vale para um único repo, vai para o arquivo de instrução que ele já tem, ou para `docs/convencoes.md` se ele não tiver nenhum. O resto vai para o harness.
- **Fluxo:** o fluxo do Spec Kit da seção 4 e os caminhos de `docs/sistemas/`.
- **Seção gerenciada:** a extensão `agent-context` mantém a seção do Spec Kit no `AGENTS.md`. O `CLAUDE.md` continua sendo só `@AGENTS.md`.

### 5.4 O que acontece em cada repo

| Repo | Fica, subordinado | Sai | PR |
|---|---|---|---|
| `industria-logistica.wms.awx.monorepo` | `CLAUDE.md`, ajustando só as referências ao Spec Kit; a constitution movida para `docs/constitution.md`, com as "dívidas de conformidade"; `.claude/skills/qualidade-codigo` | `.specify/`, `.claude/skills/speckit-*` e `specs/`, que vão para `specs/001-*` e `specs/002-*` na raiz | 1 |
| `integracoes.core.plataforma.backoffice.frontend` (Fly) | `CLAUDE.md`, `.claude/agents`, `.claude/rules`, `.github/agents` | nada | 0 |
| `industria-logistica.wms.servidor.backend` | `AGENTS.md`, `.github/copilot-instructions.md` | nada | 0 |
| Os outros 14 | nada muda; ganham `docs/convencoes.md` quando surgir uma regra específica | nada | 0 |

### 5.5 Adendo 4 à ADR 0001 (guarda do `ws push`)
- **Deixa de bloquear**, dentro dos prefixos: `CLAUDE.md`, `AGENTS.md`, `.claude/` (fora `skills/speckit-*`), `.github/copilot-instructions.md` e `.github/agents/`. Esses arquivos são instruções legítimas de cada repo, e editá-los vira PR no repo.
- **Continua bloqueando** adicionar, alterar ou trocar o tipo de: `.specify/`, `specs/` na raiz do repo, e `.claude/skills/speckit-*`.
- **Remover continua permitido.**
- A seção 2 da ADR passa a valer como está na seção 5 desta spec.

## 6. Componentes

### 6.1 Extensão `ws` (`tools/speckit/ws/`)
- **`extension.yml`:** `id: ws`, `requires.speckit_version: ">=1.0.12"`, com dois comandos e dois hooks:
  - `speckit.ws.feature` no `before_specify`, com `optional: false`;
  - `speckit.ws.push` no `after_converge`, com `optional: true` e prompt.
- **`scripts/bash/ws-feature.sh "<descrição>"`:**
  - identifica feature existente (um `NNN` ou nome citado que casa com `specs/NNN-*`) ou calcula o próximo `NNN`;
  - chama `tools/ws/ws start`;
  - imprime JSON com `BRANCH_NAME`, `FEATURE_NUM`, `FEATURE_DIRECTORY`, `EXISTING` (true/false) e `ERROR` (vazio se deu certo).
- **`scripts/bash/ws-push.sh`:** roda `tools/ws/ws push` e repassa a saída e o código de saída.
- **Comandos (`commands/*.md`):** dizem ao agente para rodar o script, ler o JSON e parar se `ERROR` vier preenchido.

### 6.2 Preset `multirepo` (`tools/speckit/multirepo/`)
Não edita o núcleo do Spec Kit. Usa as estratégias `append` e `wrap` do Spec Kit 1.0.12:
- **`spec-template`:** seções "Repos afetados" (obrigatória) e "Revisões".
- **`plan-template`:** uma seção por repo afetado, com instruções do repo, stack, build e testes, e consumidores de contratos.
- **`tasks-template`:** marcador `[repos/<repo>]`/`[workspace]`, agrupamento por repo e tarefa final de verificação por repo.
- **Comando `speckit.specify`, com `wrap`:** a regra para feature existente (seção 4.2) e a regra de parar quando o hook devolver `ERROR`.

### 6.3 `tools/ws/ws speckit`
- Lê `tools/speckit/VERSION` e roda `uvx --from git+https://github.com/github/spec-kit.git@v<versão> specify`. Não instala nada global.
- **Instalação nova, nesta ordem:**
  1. `init --here --force --non-interactive --integration claude --script sh`;
  2. `extension add --dev tools/speckit/ws`;
  3. `extension add agent-context`, com `context_files: [AGENTS.md]`;
  4. `preset add --dev tools/speckit/multirepo`.
- **Rodado de novo:** reinstala a extensão e o preset. É o caminho de atualização, trocando o `VERSION`.
- **Checagens:** sem `uv`, explica como instalar. Com versão inexistente, para antes de mexer em qualquer arquivo. Não sobrescreve `.specify/memory/constitution.md` quando ela já existe.
- **O que é versionado:** `.specify/` e `.claude/skills/speckit-*`, para quem só clona não precisar do `uv`. O `uv` só é requisito para quem atualiza o Spec Kit.
- **Por que a versão é fixada (fixar não é congelar):**
  - Todo mundo usa exatamente as skills e os templates que estão commitados.
  - O preset envolve o comando `specify` do núcleo, e uma versão nova pode mudar esse comando e quebrar o preset sem aviso. O Spec Kit lançou a 1.0.11 e a 1.0.12 em dias seguidos.
  - Atualizar é deliberado:
    1. trocar o `VERSION`;
    2. rodar `ws speckit`;
    3. rodar os testes e a validação manual;
    4. abrir um PR no workspace.

### 6.4 `docs/sistemas/` (cópia única no SP2)
- **Script de cópia:** copia de `C:\src\00-harness_big_brown_field\docs\discovery\`:
  - `arquitetura/*` para `docs/sistemas/`;
  - `repos/<repo>/{domain,business,tech,project-readme.md}` para `docs/sistemas/<repo>/`;
  - `repos/<repo>/_discovery/edges.csv`.
- **Não copia:** as outras pastas `_discovery/`, `docs/credentials/` e `segredos-para-rotacao.md`.
- **Filtro de segredos:** recusa copiar qualquer arquivo que case com padrões de segredo (`password=`, `pwd=`, `User ID=.*;Password`, chaves privadas) e lista o que recusou.
- **Depois da cópia:** o conteúdo passa a ser mantido no workspace.

## 7. Tratamento de erros

| Situação | Comportamento |
|---|---|
| `ws start` falha no hook (conflito, rede, árvore suja, nome inválido) | JSON com `ERROR`; o `specify` para sem criar spec nem pasta |
| Feature citada que não existe | É tratada como feature nova; o JSON informa `EXISTING=false` |
| Revisão `r<k>` já existe como branch | Usa o próximo `k` livre |
| `ws push` falha (guarda, rede) | O `speckit-ws-push` repassa a mensagem do `ws` sem tentar de novo |
| `uv` ausente ou versão inexistente em `ws speckit` | Mensagem clara, sem alterar nenhum arquivo |
| Arquivo com padrão de segredo na cópia do discovery | Não copia e lista o arquivo |

## 8. Testes

Mesmo estilo bash do `tools/ws/tests`, com fixtures locais e sem rede, salvo onde indicado:
- **`ws-feature.sh`:**
  - próximo `NNN` com `specs/` vazio e com features existentes;
  - detecção de feature existente por número e por nome;
  - revisão `r<k>` com branches já existentes;
  - `ERROR` e nenhuma pasta criada quando o `ws start` falha;
  - JSON válido em todos os casos.
- **`ws-push.sh`:** repassa a saída e o código do `ws push`.
- **Guarda do `ws push` (adendo 4):**
  - aceita adicionar ou alterar `CLAUDE.md`, `AGENTS.md`, `.claude/rules/x`, `.github/agents/x` e `.github/copilot-instructions.md` num prefixo;
  - recusa `.specify/`, `specs/` e `.claude/skills/speckit-*`;
  - remoção continua permitida.
- **Preset:** `resolve-template.sh` para spec, plan e tasks contém as seções e marcadores da seção 6.2.
- **`ws speckit`** (integração, com rede para o `uvx`), num workspace de teste:
  - cria `.specify/extensions.yml` com os hooks `before_specify` e `after_converge`;
  - gera as skills `speckit-ws-feature` e `speckit-ws-push`;
  - rodado de novo, não altera a constitution.
- **Cópia do discovery:** copia as pastas esperadas, recusa um arquivo de teste com padrão de segredo e não copia `_discovery/` (exceto o `edges.csv`).
- **Validação manual de ponta a ponta:**
  - um `/speckit-specify` de uma feature de teste que toque dois repos, passando por `plan`, `tasks`, `implement` e `converge`, sem push para repos reais sem o OK do usuário;
  - depois, um `/speckit-specify` citando a mesma feature, para conferir revisão e não sobrescrita.

  É a única forma de conferir que o agente segue os hooks, que são instruções e não execução automática.

## 9. Fora do escopo
- Spec do sistema inteiro no estilo OpenSpec: o usuário escolheu o living spec por feature.
- Integração com outros agentes além do Claude Code: fica possível, com `specify integration install codex` e o `AGENTS.md` como fonte única, mas não é feita no SP2.
- Grafo de arquitetura, indexação e memória: SP3.
- `docs/convencoes.md` nos 14 repos sem instruções próprias: sob demanda.

## 10. Riscos
- **Hooks não são execução automática.** O agente pode deixar de rodar o `before_specify`. Mitigações: o `optional: false`, a instrução no `AGENTS.md` e a guarda do `ws push`, que continua sendo a garantia de que o harness não vaza para os repos.
- **A regra de feature existente depende do `wrap` do preset** sobre o comando `specify` do núcleo. Uma versão futura do Spec Kit pode mudar esse comando. Mitigações: o teste do preset e a validação manual a cada troca de `VERSION`.
- **O Spec Kit muda rápido** (1.0.11 e 1.0.12 saíram em dias seguidos). Mitigação: versão fixada e atualização só via `ws speckit`.
