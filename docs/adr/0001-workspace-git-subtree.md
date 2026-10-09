# ADR 0001 — Workspace multi-repo com git subtree

- **Status:** aceita (2026-09-24)
- **Data:** 2026-09-23
- **Subprojeto:** SP1, estrutura do workspace
- **Evidências:** `docs/discovery/arquitetura/mapa-arquitetura.md` (SP0) e a PoC descartável em `poc/sp1-subtree/` (`run-poc.sh`, `resultado.log`)

## Contexto

O ecossistema WMS tem 17 repos no Azure DevOps (organização ARECO), todos com branch `main`. As stacks vão de .NET Framework até .NET 10, e há Angular, React Native e Next.js. Cada repo tem pipeline própria (`esteiras/`). O SP0 mostrou que o trabalho cruza repos com frequência: `wms.servidor.backend` tem 14 vizinhos, `wms.ecommerce.backend` tem 10, e o legado se acopla sobretudo por banco.

Precisamos de um workspace em que devs e agentes de IA trabalhem em vários repos de uma vez, com um harness único: specs, skills, grafo e instruções. Restrições definidas pelo usuário:

1. Os repos **continuam independentes**: PRs, pipelines e times de cada um não mudam.
2. O fluxo é uma **branch nova no workspace** e, no fim do trabalho, **push para os repos** via subtree.
3. O **harness fica só no workspace**. Nos repos ficam só convenções, regras, acordos e ADRs específicos de cada repo.

## Decisão

### 1. Estrutura

- Um **repo novo de workspace** no Azure DevOps. Esta pasta de discovery não é o workspace.
- Cada repo entra como **git subtree com `--squash`** em `repos/<nome-completo-do-repo>/`. O prefixo corresponde 1:1 ao nome do repo remoto.
- Um **manifesto versionado** `workspace.repos`, com uma linha por repo (`prefixo url branch-base`), é a única fonte de configuração dos scripts.
- Configuração obrigatória do clone: `core.longpaths=true` (os caminhos passam de 260 caracteres no Windows) e `core.autocrlf=false`, porque o subtree preserva os bytes de cada repo e cada repo já traz o próprio `.gitattributes`.

```
<workspace>/
  CLAUDE.md, AGENTS.md          harness: instruções para agentes
  .claude/, .specify/, specs/   harness: skills, Spec Kit (SP2), specs
  tools/ws/                     scripts ws start / ws push / ws maintain
  workspace.repos               manifesto
  repos/<repo>/                 subtree de cada repo (conteúdo idêntico ao remoto)
    docs/convencoes.md          regras específicas do repo
    docs/adr/NNNN-*.md          decisões específicas do repo
```

### 2. Onde fica cada coisa

| Onde | O quê |
|---|---|
| Raiz do workspace | Todo o harness: `CLAUDE.md`/`AGENTS.md`, skills, `.claude/`, `.specify/`, specs, grafo (SP3), scripts, manifesto e o conhecimento de domínio vindo do discovery |
| `repos/<repo>/docs/convencoes.md` | Convenções, regras e acordos que valem **só** para aquele repo |
| `repos/<repo>/docs/adr/NNNN-*.md` | ADRs específicas daquele repo |

**Critério:** uma regra que vale para um único repo fica nele. Uma regra que vale para mais de um repo, ou que é sobre como o agente trabalha, fica no workspace.

Esse critério precisa estar escrito para o harness:
- na **constitution** do workspace (`.specify/memory/constitution.md`), como princípio fixo;
- no **`CLAUDE.md`/`AGENTS.md` raiz**, em forma operacional: antes de mexer num repo, ler `docs/convencoes.md` e `docs/adr/` dele; ao surgir uma regra nova, gravá-la no repo afetado se for específica dele, ou no harness caso contrário.

A redação final fica para o SP2.

Os arquivos na raiz estão fora de qualquer prefixo, e o `subtree push` só envia o conteúdo do prefixo. A PoC confirmou que um `CLAUDE.md` alterado na raiz não chega ao remoto.

### 3. Fluxo de trabalho

| Passo | Comando | O que faz |
|---|---|---|
| Iniciar | `ws start <branch>` | Faz `git pull` do `main` do workspace. Para cada repo do manifesto, roda `git subtree pull --prefix=repos/<r> <url> main --squash` e para no primeiro conflito. Roda `ws maintain` quando precisar. Faz push do `main` do workspace. Cria `<branch>`. |
| Trabalhar | commits normais | Uma branch pode tocar vários repos e o harness. |
| Enviar | `ws push` | Calcula os prefixos alterados (`git diff --name-only main...HEAD`), aplica a guarda e roda `git subtree push --prefix=repos/<r> <url> <branch>` só nesses prefixos, com o mesmo nome de branch. Lista os repos enviados. |
| PR | manual | Um PR por repo, no Azure DevOps, no fluxo normal de revisão de cada time. |
| Fechar | PR do workspace | Depois que **todos** os PRs dos repos forem mergeados, a branch é mergeada no `main` do workspace por um PR do workspace, que também leva as mudanças no harness. Se o PR de algum repo for abandonado, a branch reverte aquele prefixo antes do merge. |
| Voltar | `ws start` seguinte | O `subtree pull --squash` traz o `main` de cada repo. A PoC mostrou que isso não conflita com a mudança que já chegou pela branch: o conteúdo do prefixo ficou idêntico ao do remoto, com o mesmo hash de tree. |

**Guarda do `ws push`:** o push de um prefixo é recusado se a branch **adicionar ou alterar**, dentro dele, `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.specify/`, `specs/`, `.github/copilot-instructions.md` ou `.github/agents/`. A guarda olha o diff da branch, não os arquivos que já existem. Assim, os repos que ainda têm arquivos de agente continuam aceitando push até a migração (seção 5). A PoC validou isso; a primeira versão, que olhava os arquivos existentes, bloqueava o servidor, que tem `AGENTS.md`.

### 4. Manutenção: `ws maintain`

O `git subtree split`, que roda dentro do `push`, percorre todos os commits alcançáveis desde o último marcador de split daquele prefixo. Os commits de `--squash` do `add`/`pull` **não** servem como marcador. Na PoC, o custo foi de cerca de 0,2 s por commit do workspace, por prefixo, no Windows.

`ws maintain` faz duas coisas no `main` do workspace:

1. **Rejoin:** roda `git subtree split --prefix=repos/<r> --rejoin --squash` para cada prefixo com mais de 100 commits desde o último marcador. Na PoC, isso derrubou o split de 44 s para 2 s. Sem `--squash`, o `--rejoin` falha com "refusing to merge unrelated histories".
2. **Verificação de deriva:** compara o hash da tree de cada prefixo (`git rev-parse HEAD:repos/<r>`) com o do `main` remoto (`<sha>^{tree}`) e lista os prefixos que divergem.

**Adendo (2026-09-24, ao escrever o plano):** num prefixo sem mudança local desde o último squash, o `split --rejoin --squash` não grava nada. Ele gasta o split inteiro (cerca de 0,28 s por commit do workspace) e não cria marcador. Nesse caso, o `ws maintain` grava ele mesmo o commit que o rejoin gravaria: um merge do HEAD com o squash, sem mudar a tree, com os trailers `git-subtree-dir`, `git-subtree-mainline` e `git-subtree-split`. Medido: o split de um prefixo parado depois de 100 commits caiu de 28 s para 2 s. Detalhes em `docs/superpowers/plans/2026-09-24-sp1-workspace-multi-repo.md`.

**Adendo 2 (2026-09-24, revisão da implementação):** o `split --rejoin --squash` de verdade **não é usado**. Ele grava no `main` um `git-subtree-split` que aponta para um commit sintético, que só existe no clone que rodou o rejoin e nunca chega ao Azure DevOps. Com isso, os outros clones deixam de conseguir fazer `subtree pull` e `push` daquele prefixo, para sempre. O `ws maintain` só grava o marcador próprio quando o prefixo é igual ao último squash. Nos outros casos, adia o marcador até o próximo `ws start`, que sincroniza o prefixo com o repo.

**Adendo 3 (2026-09-25, depois do bootstrap):** no bootstrap real, o `subtree add`/`pull` baixava o histórico completo de cada repo para o clone local (253 MB) e o `ws start` levava cerca de 3 min.
- **Como ficou:** o `ws` roda `git ls-remote` em paralelo e só baixa os repos que mudaram, com `git fetch --depth=1` do commit novo e do atual, um de cada vez. Depois aplica com `git subtree merge --squash`. O `ws add` também faz fetch raso, e o `ws push` busca raso os commits citados nos squashes que faltam no clone.
- **Medido no Azure DevOps:** `ws start` de 13 s sem novidade e 21 s com um repo alterado; `.git` em cerca de 67 MB.
- **Consequência:** o clone do workspace é raso (`.git/shallow`). `git subtree pull` e `git fetch --unshallow` não devem ser usados.
- **Evidência:** `docs/discovery/sp1-bootstrap.md`.

**Adendo 4 (SP2, 2026-09-29):** os repos mantêm as instruções de agente que já têm, subordinadas ao harness do workspace. A constitution e o `AGENTS.md` da raiz governam o que cruza repos; dentro de `repos/<repo>/`, valem as instruções daquele repo.
- **Na seção 2:** os arquivos de instrução de um repo são `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `docs/convencoes.md`, `docs/adr/` e `docs/constitution.md`. `docs/convencoes.md` só é criado quando o repo não tem nenhum dos outros.
- **Guarda do `ws push`:** bloqueia adicionar, alterar ou trocar o tipo apenas de `.specify/`, `specs/` na raiz do repo e `.claude/skills/speckit-*`, que colidiriam com o Spec Kit da raiz. O resto passa, e a remoção é permitida.
- **Seção 5:** só a maquinaria de Spec Kit do AWX sai do repo. As specs `001` a `003` vão para `specs/` na raiz, e a constitution do AWX vai para `docs/constitution.md` do próprio repo, com as referências ajustadas no `CLAUDE.md`, no `AGENTS.md` e na skill `qualidade-codigo`. O Fly e o servidor.backend não mudam.
- **Spec:** `docs/superpowers/specs/2026-09-28-sp2-speckit-multirepo-design.md`.

### 5. Migração dos arquivos de agente que já existem

| Repo | Arquivos | Destino |
|---|---|---|
| `wms.awx.monorepo` | `CLAUDE.md`, `.claude/skills/` (13), `.specify/` (constitution em `memory/`, scripts, templates, workflows), `specs/001-picking-b2c-consumer`, `specs/002-sku-multiplo-codigo-barra` | Skills, Spec Kit e specs vão para o workspace; o formato é definido no SP2. As regras só do AWX vão para `repos/…awx.monorepo/docs/convencoes.md`. |
| Fly (`integracoes.core.plataforma.backoffice.frontend`) | `CLAUDE.md`, `.claude/agents`, `.claude/rules`, `.github/agents` | Agentes e regras gerais vão para o workspace. As regras só do Fly vão para `docs/convencoes.md` do Fly. |
| `wms.servidor.backend` | `AGENTS.md`, `.github/copilot-instructions.md` | As regras só do WMS3 vão para `docs/convencoes.md`. O restante vai para o harness. |

A remoção nos repos segue o fluxo normal: `ws push` e um PR por repo. A execução fica no plano de implementação.

## Resultados da PoC (descartável)

Setup: 4 repos (picking.backend com 589 arquivos, servidor.backend com 5.374, autenticação com 5.638, ecommerce.backend com 1.775), totalizando 13.378 arquivos. Os remotos foram repos bare locais criados a partir do HEAD de cada clone, com 30 commits sintéticos. Windows, Git 2.54.

| Operação | Resultado |
|---|---|
| `subtree add --squash` | 2,4 a 7,8 s por repo; workspace com `.git` de 59 MB |
| `subtree push` (histórico curto) | 2,7 a 3,8 s; a branch no remoto descende do `main` e traz só os arquivos alterados |
| Merge do PR no remoto, mais um commit direto de outro time, e depois `subtree pull --squash` | 1,4 a 4,4 s por repo, sem conflito |
| Segundo ciclo (branch nova depois do pull) | push limpo, 1 commit à frente do `main` |
| Branch mergeada no `main` do workspace e depois `subtree pull --squash` do remoto (com PR mergeado e mais um commit de outro time) | sem conflito; tree do prefixo idêntica à do remoto |
| Guarda contra `CLAUDE.md` num prefixo | push recusado |
| `CLAUDE.md` da raiz no remoto | não vazou |
| `split` com 200 commits no workspace | cerca de 40 s por prefixo, igual para repo pequeno e grande; sem ganho de cache em execução repetida |
| `split` depois de `--rejoin --squash` e mais 5 commits | 2 s |
| `push` depois do rejoin | 2 s; a branch descende do `main` do remoto (65 commits à frente, um por commit do workspace que tocou o prefixo) |

Limites da PoC: sem rede nem Azure DevOps (o `add` real faz fetch remoto), histórico sintético nos remotos e 4 dos 17 repos.

## Alternativas descartadas

| Alternativa | Motivo |
|---|---|
| git submodule | Fixa um commit por repo e exige atualizar o ponteiro a cada mudança; o usuário optou por subtree. Dev e agente veem só um ponteiro até rodar `submodule update`, e o harness fica mais difícil de manter coeso. |
| Multi-root (pasta com clones lado a lado, sem histórico comum) | Não há branch única do workspace nem um ponto de envio para vários repos, e o harness fica separado do código. |
| Monorepo real | Viola a restrição 1, porque mudaria o fluxo de PR e as pipelines dos times. |
| Subtree com histórico completo | O workspace passaria a pesar a soma dos `.git` (cerca de 150 MB) e o `split` percorreria todo o histórico de cada repo. `log`/`blame` detalhados continuam disponíveis no repo de origem. |

## Consequências

- **Positivas:** uma branch cobre um trabalho que cruza repos; o harness é único; os repos não mudam de fluxo; os PRs trazem só os arquivos do repo, sem histórico estranho.
- **Negativas:**
  - O `split` cresce com o histórico do workspace e exige `ws maintain`.
  - `ws start` e `ws push` passam a ser o caminho obrigatório: um `git push` direto do workspace não chega aos repos.
  - Um conflito no `subtree pull` tem de ser resolvido no workspace.
  - O push gera um commit no remoto por commit do workspace que tocou o prefixo; a política de merge do PR (squash ou não) fica com cada time.
- **Operacionais:** credencial do Azure DevOps (PAT ou GCM) com permissão de push de branch nos 17 repos para quem usa o workspace; `core.longpaths` e `core.autocrlf=false` no clone.

## Pendências para o plano de implementação

1. Criar o repo do workspace e fazer o `subtree add --squash` dos 17 repos a partir do Azure DevOps, medindo o tempo real com rede.
2. Implementar `tools/ws/` (`start`, `push`, `maintain`) e o manifesto, em bash (Git Bash no Windows). Os scripts da PoC servem de base.
3. `CLAUDE.md`/`AGENTS.md` raiz com a regra da seção 2. A constitution fica para o SP2.
4. Migração da seção 5 (3 repos) e criação do `docs/convencoes.md` nos repos, sob demanda.
