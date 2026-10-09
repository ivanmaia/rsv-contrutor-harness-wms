# SP4: Documentação em camadas do harness do workspace WMS (design)

Data: 2026-10-08. Processo: `superpowers:brainstorming`, caminho arquitetural. Decisões tomadas com o usuário na conversa de 2026-10-08.

## 1. Objetivo e critério de sucesso

Ensinar os devs a usar o harness do workspace `industria-logistica.wms.workspace` (fluxo multi-repo, Spec Kit e Atlas) com uma documentação em camadas de profundidade. Quem só quer o fluxo básico lê uma camada curta e linear, e não esbarra em conteúdo avançado.

**Público:** misto. Parte do time usa Claude Code no dia a dia, parte usa outro assistente ou nenhum, e alguns já conhecem o Spec Kit.

**Sucesso:**
- um dev que nunca usou o harness segue a camada 1 sozinho na primeira feature real dele (piloto, seção 7);
- um teste automático impede que a doc cite um comando, uma skill, um caminho ou uma mensagem de erro que não existe mais (seção 6).

**Fora deste SP:** a apresentação para o time, que é o subprojeto seguinte, com design próprio, montada a partir da camada 1 e do porquê do harness.

## 2. Decisões tomadas com o usuário

| Decisão | Valor |
|---|---|
| Onde mora a doc | Markdown no próprio workspace. Muda no mesmo PR que muda o harness |
| Organização | Um arquivo por camada (abordagem 1), com o `README.md` da raiz como porta de entrada |
| Prática guiada | Nenhuma. A camada 1 é só o passo a passo; a primeira feature real é o treino |
| Validação | Piloto com um dev novo **e** teste automático de referências |
| Ferramentas do Atlas | Fora da camada 1: são a primeira receita da camada 3. O `README.md` as lista como pré-requisito, com link para essa receita |
| Suporte | Thread no espaço "Equipe WMS" do Google Chat: https://chat.google.com/room/AAAAKpyvLWs?cls=7 |
| Fluxo fora do Spec Kit | Fica na camada 3 com um aviso de "desaconselhado, só em necessidade real" |
| Porquê das decisões | As specs, os planos e os documentos de validação do SP1 ao SP3 são copiados para `docs/harness/historico/` |
| `docs/workspace.md` | Dissolvido nas camadas e removido |

## 3. Estrutura

```
README.md                            porta de entrada (novo)
docs/harness/1-comecar.md            camada 1
docs/harness/2-quando-da-errado.md   camada 2
docs/harness/3-alem-do-basico.md     camada 3
docs/harness/4-manter.md             camada 4
docs/harness/historico/              specs, planos e validações do SP1 ao SP3, mais LEIA-ME.md
tools/ws/tests/test_docs_referencias.sh   teste de referências (novo)
```

Regras para todas as camadas:
- Cada camada remete às outras por link e nunca exige que se leia uma camada mais profunda para concluir o que ela promete.
- Português do Brasil, frases curtas, comandos em bloco de código prontos para copiar.
- A camada 1 cabe em cerca de uma tela e meia.

## 4. Conteúdo

### 4.1 `README.md`
- O que é o workspace, em 3 frases: os repos do WMS juntos como subtree, o Spec Kit para features e o Atlas como memória dos sistemas.
- **Pré-requisitos:**
  - Git for Windows;
  - credencial do Azure DevOps com push de branch nos repos do `workspace.repos`;
  - Claude Code;
  - ferramentas do Atlas (WSL, codebase-memory-mcp, Graphify, ast-grep), com link para a receita 1 da camada 3.
- Tabela "Quero…":

  | Quero… | Camada |
  |---|---|
  | começar | 1 |
  | resolver um erro | 2 |
  | fazer algo além do básico | 3 |
  | mexer no harness | 4 |

### 4.2 Camada 1: `1-comecar.md`
1. **Antes de tudo (só uma vez):**
   - bloco recolhível (`<details>`) "Nunca usou Claude Code?", com instalar, entrar e o básico de conversar com ele;
   - clonar com `core.longpaths=true` e `core.autocrlf=false`;
   - credencial do Azure DevOps;
   - abrir o Claude Code na raiz;
   - uma linha lembrando as ferramentas do Atlas (receita 1 da camada 3).
2. **Uma feature, do início ao PR:** uma linha por passo, dizendo o que digitar e o que esperar.
   - `/speckit-specify <descrição>`
   - `/speckit-clarify`, se o agente pedir
   - `/speckit-plan`
   - `/speckit-tasks`
   - `/speckit-analyze`
   - `/speckit-implement`
   - `/speckit-converge`
   - `/speckit-ws-commit-push`
   - PRs: um por repo e, depois de todos mergeados, o PR do workspace.
3. **Já conhece o Spec Kit? O que muda aqui** (quadro curto):
   - a branch é criada pelo hook com `ws start`;
   - as specs ficam em `specs/ws-NNN-*`, na raiz;
   - as tasks levam o marcador `[repos/<repo>]` ou `[workspace]`;
   - o `converge` atualiza o Atlas e oferece o commit e o push.
4. **Três regras que não se quebram:**
   - nunca `git push` para os repos;
   - não criar nem alterar `.specify/`, `specs/` e `.claude/skills/speckit-*` dentro de `repos/`;
   - não alterar o harness durante uma feature.
5. **Travou?** Link para a camada 2.

### 4.3 Camada 2: `2-quando-da-errado.md`
- **Seções por etapa**, na ordem da camada 1:
  1. preparação e clone;
  2. `/speckit-specify` e a criação da branch;
  3. do `plan` ao `converge`;
  4. `/speckit-ws-commit-push` e `ws push`;
  5. PRs e merge;
  6. Atlas (pendências e avisos de doc defasado).
- **Entrada:**
  - **Sintoma:** a mensagem exata em bloco de código, ou o comportamento observado;
  - **Causa:** uma frase;
  - **O que fazer:** passos numerados, com link para a receita da camada 3 quando houver.
- **Fontes:**
  - as mensagens reais de `die "…"` em `tools/ws/` e as paradas dos hooks em `tools/speckit/` e `.specify/extensions/ws/`, levantadas do código;
  - a seção "Erros no `ws start`" do `docs/workspace.md`;
  - os achados de `sp2-validacao.md` e `sp3-validacao.md`;
  - situações que não são erro, mas confundem: o hook parou e pediu checkout, feature não mergeada, PR abandonado.
- **"Não resolveu?":**
  - o que mandar: o comando, a mensagem completa e a saída do `git status`;
  - para onde: a thread do espaço "Equipe WMS" (seção 2).

### 4.4 Camada 3: `3-alem-do-basico.md`
- **Formato de cada receita:** **Quando usar** (uma frase), **Passos** (numerados) e **Cuidado** (opcional, no máximo 2 linhas).
- **Receitas, nesta ordem:**
  1. **Mapas de código para o agente.**
     - instalar WSL, `tools/atlas/instala-cbm.sh`, Graphify e ast-grep nas versões de `tools/atlas/VERSOES.md`;
     - rodar `ws atlas mapas --todos`;
     - conferir em `/mcp`.
  2. **Consultar o Atlas.**
     - `/atlas-consultar`;
     - como ler uma página de `docs/atlas/impacto/`: distância, caminho, grupo "fora do escopo", resumo por repo e a regra de só objetos tocados pelo WMS;
     - onde ficam os docs de cada repo.
  3. **Mudar uma feature que já existe:**
     - citar o número ou o nome;
     - branch `-r<k>`;
     - feature não mergeada, que exige checkout da branch dela.
  4. **Trabalhar fora do Spec Kit:** `ws start <branch>`, commits, `ws push` e PR. Começa com este aviso destacado:
     > ⚠️ **Desaconselhado.** Use só em necessidade real, como um hotfix urgente ou um ajuste trivial que não justifica spec. Fora do Spec Kit:
     > - a mudança fica sem spec, ou seja, sem registro do porquê;
     > - o Atlas não é atualizado no fim (só no próximo `ws start` ou com `/atlas-atualizar`);
     > - nada confere o plan contra a constitution.
  5. **PR de um repo abandonado:** devolver o prefixo ao `main` com `git restore --source=main` antes do PR do workspace.
  6. **Repo com Spec Kit próprio (AWX):** o que vale no workspace e o que vale no clone.
  7. **Atualizar o Atlas à mão:** `/atlas-atualizar` e `--do-zero`, e como o `ws start` decide quando remapear:
     - relevância;
     - `intervalo_dias`;
     - `limiar_arquivos`;
     - `limite_minimo`;
     - o exemplo dos dias 1 a 8 do `docs/workspace.md`.
  8. **Onde gravar uma regra ou decisão:**
     - o que vale só para um repo vai no arquivo de instrução dele ou em `docs/convencoes.md`;
     - as ADRs vão em `repos/<repo>/docs/adr/`;
     - o resto vai para o harness.
  9. **Histórico de um repo** (`log`, `blame`):
     - o clone raso;
     - não rodar `git fetch --unshallow` nem `git subtree pull`;
     - usar o clone do repo ou o Azure DevOps.

### 4.5 Camada 4: `4-manter.md`
1. **Como as peças se ligam:**
   - diagrama Mermaid: `/speckit-specify` → hook `before_specify` → `ws start` → `ws atlas plano` → mapeamento; e depois `/speckit-converge` → hook `after_converge` (`speckit.ws.converge`) → Atlas → `/speckit-ws-commit-push` → `ws push`;
   - um parágrafo por peça:
     - workspace com subtree `--squash` (ADR 0001 e adendos);
     - `tools/ws`;
     - Spec Kit: `tools/speckit/VERSION`, extensão `ws` e preset `multirepo`;
     - Atlas: skill `codebase-discovery`, `tools/atlas/` e `docs/atlas/`.
2. **Onde fica cada coisa:** tabela com caminho e papel. Cobre:
   - `tools/ws/` (`ws`, `lib/`, `tests/`);
   - `tools/speckit/`;
   - `tools/atlas/` (`build-map.py`, `impacto.py`, `plano.py`, `relevancia.ini`, `VERSOES.md`, `prompt-mapeamento.md`, `importa-mapeamento.sh`, `instala-cbm.sh`);
   - `.specify/`;
   - `.claude/skills/`;
   - `AGENTS.md`, `CLAUDE.md` e a constitution em `.specify/memory/constitution.md`;
   - `docs/atlas/`;
   - `docs/adr/`;
   - `workspace.repos`.
3. **Tarefas de manutenção**, como receitas:
   - atualizar o Spec Kit;
   - `ws maintain`;
   - adicionar um repo;
   - atualizar as versões das ferramentas do Atlas;
   - reimportar o catálogo do banco (`importa-mapeamento.sh --banco`);
   - regenerar os derivados do Atlas (`build-map.py`);
   - rodar os testes (todos, um arquivo, um teste e os de rede).
4. **Evoluir o harness:**
   - nunca dentro de uma feature: numa branch própria, com PR no workspace;
   - a suíte de testes passa antes do PR;
   - toda mudança de comportamento atualiza a camada correspondente. O teste de referências pega o que foi renomeado ou removido, mas não comportamento novo, então isso entra como item de checklist do PR;
   - uma decisão relevante vira ADR em `docs/adr/`;
   - para o porquê das decisões já tomadas, ver `historico/`.

### 4.6 `docs/harness/historico/`
- **O que é copiado**, como está, desta pasta de discovery:
  - as specs `2026-09-28-sp2-speckit-multirepo-design.md`, `2026-10-05-sp3-grafo-e-navegacao-design.md` e `2026-10-07-sp2-adendo-harness-awx-subordinado-design.md`;
  - os planos `2026-09-24-sp1-workspace-multi-repo.md`, `2026-09-29-sp2-speckit-multirepo.md`, `2026-10-05-sp3-atlas.md` e `2026-10-07-sp2-adendo-awx-subordinado.md`;
  - os documentos de validação `sp1-bootstrap.md`, `sp2-validacao.md`, `sp3-validacao.md`, `sp3-ledger-execucao.md` e `sp2-adendo-awx-ledger.md`.
- **`LEIA-ME.md`:**
  - é registro histórico e não é atualizado;
  - o estado atual está nas camadas;
  - os links internos apontam para a pasta de discovery original e podem não abrir no workspace.
- **Antes de copiar:** conferir que nenhum arquivo traz valor de credencial, token ou dado sensível. Eles só citam segredos por nome e local, e qualquer achado é removido da cópia.
- **Fora do teste de referências** (seção 6).

## 5. Migração
- Redistribuir o conteúdo do `docs/workspace.md` nas camadas e remover o arquivo. Nenhum trecho dele se perde sem decisão explícita.
- Atualizar toda referência a `docs/workspace.md` fora de `repos/`, `.git/` e `.superpowers/`. Hoje: `AGENTS.md` ("Uso humano"), `tools/atlas/relevancia.ini` e `tools/ws/tests/test_harness.sh`. O destino é o `README.md` ou a camada certa.

## 6. Teste de referências (`tools/ws/tests/test_docs_referencias.sh`)

Roda sobre o `README.md` e `docs/harness/*.md`, sem o `historico/`. Falha, listando arquivo e trecho, quando:
1. um caminho citado entre crases que começa com `tools/`, `docs/`, `.specify/` ou `.claude/` não existe. `specs/` fica de fora porque só existe depois da primeira feature. Caminhos com `<…>`, `NNN` ou `*` são genéricos e ficam de fora;
2. um subcomando citado como `ws <x>` ou `tools/ws/ws <x>` não está no uso do `tools/ws/ws` (`add|start|push|maintain|speckit|atlas`, e `plano|incorpora|concluir|mapas` para `atlas`);
3. uma skill citada como `/<nome>` não existe em `.claude/skills/<nome>/`;
4. uma mensagem citada como **Sintoma** na camada 2 não aparece em `tools/`, `.specify/` ou `.claude/`. A mensagem fica num bloco de código logo abaixo de `**Sintoma:**`, e o teste ignora as partes variáveis marcadas com `<…>`;
5. um link Markdown relativo aponta para um arquivo que não existe.

Segue o padrão da suíte (`run.sh`, funções `test_*`) e não acessa a rede. Também ganha casos de teste próprios com fixtures, para garantir que cada regra realmente falha quando deve.

## 7. Entrega e validação
- **Entrega:** branch no workspace a partir do `main`, com PR. Nenhum repo em `repos/` muda, então não há `ws push`.
- **Antes do PR:**
  - a suíte completa passa;
  - leio as camadas contra o código uma última vez: cada comando descrito existe e faz o que a doc diz.
- **Piloto, depois do merge:** um dev que nunca usou o harness segue a camada 1 na primeira feature real dele. Cada travada ou pergunta vira correção num PR de acompanhamento, na camada 1 ou como entrada nova na camada 2. O piloto é registrado nesta pasta de discovery.

## 8. Riscos
- **A camada 1 crescer até perder a simplicidade.** Mitigação: limite de cerca de uma tela e meia; o que não couber vai para a camada 3.
- **Doc desatualizada por mudança de comportamento.** O teste só pega nomes. Mitigação: o item de checklist do PR (seção 4.5).
- **O histórico confundir quem lê.** Mitigação: o `LEIA-ME.md` e a ausência de links das camadas 1 a 3 para o `historico/`.
