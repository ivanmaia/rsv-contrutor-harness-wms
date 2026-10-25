# Apresentação v2 do harness: conteúdo (brief)

Brief de conteúdo para a v2 do deck do time WMS (até 70–80 min). Levantado em 2026-10-22, só leitura.

**Fontes e siglas usadas nas citações:**
- `ws:` = workspace `C:/src/wms-workspace`, no `origin/main` (último commit `801331703`, "Merged PR 17261 … (SP7)").
- `disc:` = esta pasta de discovery (`C:/src/00-harness_big_brown_field`).
- `v1:` = `docs/discovery/apresentacao-v2/v1-slides/<slide>.html`.
- Quando um fato não está nas fontes, aparece como **não encontrado**. Propostas que não estão na doc aparecem como **proposta (não está na doc)**.

Objetivo do deck, nas palavras do pedido: deixar claro tudo o que o dev precisa fazer para (1) entregar com mais eficiência e qualidade usando o harness; (2) melhorar o harness e os repos, reforçando as convenções e as definições que **cada repo** precisa ter para melhorar o código gerado e padronizar os repos.

---

## 1. Pré-requisitos e setup do dev

**Uma vez por máquina, nesta ordem** (ws: `docs/harness/1-comecar.md`, "Antes de tudo"):
1. **Claude Code:** no PowerShell, `irm https://claude.ai/install.ps1 | iex`; abrir terminal novo e rodar `claude` (login pelo navegador no primeiro uso). Se `claude` não for reconhecido: fechar e abrir o terminal; senão, https://code.claude.com/docs/en/troubleshoot-install (ws: `2-quando-da-errado.md`).
2. **Git for Windows:** os scripts do workspace rodam no **Git Bash** (ws: `README.md`; `1-comecar.md`). Comandos de terminal (`git`, `tools/ws/ws`) rodam no Git Bash, na raiz do workspace; também dá para pedir ao agente (ws: `2-quando-da-errado.md`).
3. **Caminhos longos do Windows** (PowerShell **como administrador**; o agente não consegue fazer isso, o Windows responde "Acesso ao Registro solicitado não é permitido"):
   `Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled -Value 1 -Type DWord`
   Vale do Windows 10 1607 em diante; reabrir os terminais (ws: `1-comecar.md`). Motivo: o `core.longpaths` do clone só vale para o git; Python, .NET e Node também precisam (ws: `1-comecar.md`; disc: `docs/discovery/sp4-piloto.md`, itens 5 a 8, vindos do piloto).
4. **Clone do workspace:**
   `git clone -c core.longpaths=true -c core.autocrlf=false https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace`
   Na primeira vez o Git Credential Manager pede o login do Azure DevOps; a conta precisa **poder criar branch nos repos de `workspace.repos`** (ws: `1-comecar.md`; `README.md`, "Credencial do Azure DevOps com push de branch").
5. **Abrir o Claude Code na raiz:** `cd industria-logistica.wms.workspace` e `claude` (ws: `1-comecar.md`).
6. **Azure CLI + extensão + PAT** (para o harness abrir e revisar PRs):
   - instalar o Azure CLI e `az extension add --name azure-devops` (ws: `2-quando-da-errado.md`, "O az não está instalado");
   - `az devops login` uma vez, colando um **PAT**. **Não é o `az login`** (ws: `1-comecar.md`, passo 5).
   - **Escopos do PAT:** **Code (Read & write)** e **Work Items (Read)** (memória do projeto `sp7-prs-e-revisao-pausado`; a doc diz "PAT com permissão de código e de PR" em `2-quando-da-errado.md`, "O az não está autenticado", e cita "Work Items (Read)" só em "Não consegui ler o título do card"). Sem Work Items (Read), os PRs abrem, mas a mensagem do Chat sai só com o número do card.
   - Sem `az` autenticado, o harness avisa e não abre nada (ws: `1-comecar.md`).
7. **Python** no PATH: o `ws pr` é Python, só biblioteca padrão (ws: `tools/ws/lib/pr.sh`; `docs/harness/4-manter.md`); Python 3.10+ (ws: `tools/atlas/VERSOES.md`). Versão mínima para o dev não está na camada 1: **não encontrado** na camada 1.
8. **Recomendado: ferramentas do Atlas** (mapas de código; sem elas o fluxo funciona, mas o agente navega com grep e ast-grep) (ws: `README.md`; `docs/harness/3-alem-do-basico.md`, "Mapas de código para o agente"):
   - WSL com Ubuntu (admin): `wsl --install -d Ubuntu`;
   - codebase-memory-mcp (backends, no WSL), no Git Bash na raiz: `bash tools/atlas/instala-cbm.sh` (versão 0.11.0, ws: `tools/atlas/VERSOES.md`);
   - `uv`: `winget install astral-sh.uv`; Graphify (frontends): `uv tool install "graphifyy[sql,mcp]==0.9.77"`;
   - Node.js e ast-grep: `npm i -g @ast-grep/cli@0.45.3`;
   - gerar os mapas: `tools/ws/ws atlas mapas --todos`;
   - conferir em `/mcp` que `codebase-memory` e `graphify-frontends` aparecem conectados (ws: `.mcp.json`). Ponto em aberto do piloto: o Claude Code pede aprovação dos servidores MCP na primeira abertura, e a camada 3 não menciona (disc: `sp4-piloto.md`, "Pontos para conferir").
   - Qual repo usa qual mapa: Graphify nos 4 frontends (`app.frontend`, `ecommerce.frontend`, `picking.frontend`, Fly), cbm nos outros 14 (ws: `docs/atlas/ferramentas-por-repo.yml`).
9. **`uv`/`uvx` para quem mantém o harness:** `tools/ws/ws speckit` usa `uvx` para rodar o Spec Kit 1.2.0; o dev comum não precisa, porque as cópias em `.specify/` e `.claude/skills/` são versionadas (ws: `tools/ws/lib/speckit.sh`; `4-manter.md`, "quem só clona não precisa instalar nada").

**Tempos e custos de referência:**
- `ws start`: cerca de 15 s sem novidade, mais alguns segundos por repo alterado (ws: `3-alem-do-basico.md`); medido 13 s e 21 s com um repo alterado; `.git` de cerca de 67 MB, clone raso (ws: `docs/adr/0001…`, adendo 3).
- **Primeiro `/speckit-specify`:** pode levar **mais de 20 minutos** por causa do Atlas (ws: `1-comecar.md`, passo 1). No piloto: 3 repos mapeados, cerca de 762 mil tokens e cerca de 22 min no maior (disc: `sp4-piloto.md`, item 3).
- Tempo do `git clone` inicial do workspace: **não encontrado**.
- Clone raso: não rodar `git fetch --unshallow` nem `git subtree pull` (o `.git` passaria de cerca de 70 MB para centenas); histórico detalhado de um repo fica no clone do próprio repo ou no Azure DevOps (ws: `3-alem-do-basico.md`, "Histórico de um repo").

**Idioma:** o agente responde em pt-BR; se vier em inglês, peça "responda em português" ou `/clear` e continue do passo (ws: `AGENTS.md`; `2-quando-da-errado.md`).

---

## 2. O fluxo de feature passo a passo

Rode um comando por vez e leia o que ele devolve antes de seguir (ws: `1-comecar.md`).

| # | Comando | O que o agente/harness faz | O que o dev decide ou revisa |
|---|---|---|---|
| 1 | `/speckit-specify <descrição>` | Hook `speckit-ws-feature`: deriva um nome curto, acha até 5 repos prováveis pelo Atlas, roda `ws start` (sincroniza a `ws/sync` com o `main` de cada repo, envia a `ws/sync`, cria a branch `ws-NNN-<nome>` a partir dela), atualiza o Atlas dos repos que mudaram (pode passar de 20 min) e cria `specs/ws-NNN-<nome>/spec.md` (ws: `tools/speckit/ws/commands/speckit.ws.feature.md`; `1-comecar.md`) | Descrever a demanda como para um colega. Ler a spec (linguagem de negócio) e conferir **"Repos afetados"** (seção obrigatória do template; ws: `tools/speckit/multirepo/templates/spec-template.md`). Se cita sistema fora do workspace: escolher "seguir como externo" ou "parar e pedir a inclusão"; **não indique a pasta ao agente** (ws: `AGENTS.md`, regra 7; `2-quando-da-errado.md`). Avisos do hook (link do PR da `ws/sync`, `main` local à frente) aparecem na resposta |
| 2 | `/speckit-clarify` | Só se o agente disser que a spec tem dúvidas; as respostas entram na spec (ws: `1-comecar.md`) | Responder as ambiguidades agora (evita retrabalho) |
| 3 | `/speckit-plan` | Plano técnico por repo: instruções do repo lidas, constitution do repo, `docs/atlas/<repo>/`, **stack**, **build e testes (comandos exatos)**, mudanças, **contratos com outros sistemas** pelo índice de impacto (ws: `tools/speckit/multirepo/templates/plan-template.md`); conferido contra a constitution (v1: `passo-3`) | Quais repos mudam e por quê; se os comandos de build/teste estão certos; contratos e afetados (regra II). Mais barato corrigir aqui (v1: `passo-3`) |
| 4 | `/speckit-tasks` | Tarefas com marcador `[repos/<repo>]` ou `[workspace]`, agrupadas por repo, cada grupo termina com "Verificar build e testes do repo com as ferramentas dele" (ws: `tools/speckit/multirepo/templates/tasks-template.md`) | Se cada repo tem a tarefa de verificação; tarefas `[workspace]` só vão no PR do workspace |
| 5 | `/speckit-analyze` | Confere consistência spec × plano × tarefas (ws: `1-comecar.md`) | Requisito sem tarefa, tarefa sem requisito, termos divergentes (v1: `passo-5`) |
| 6 | `/speckit-implement` | Implementa as tarefas; antes de mexer em `repos/<repo>/` lê os arquivos de instrução do repo (ws: `AGENTS.md`, regra 1) | Acompanhar e revisar como código de colega (v1: `passo-6`); recusar mudança no harness |
| 7 | `/speckit-converge` | Confere código × spec; se falta algo, acrescenta tarefas (volta ao 6). Sem pendência, hook `speckit-ws-converge` atualiza o Atlas dos repos tocados (commit só de `docs/atlas/`) e pergunta se faz o commit e o envio (ws: `speckit.ws.converge.md`) | Repetir 6–7 até não acrescentar tarefas (ws: `2-quando-da-errado.md`) |
| 8 | `/speckit-ws-commit-push` (ou "sim" no fim do converge) | Mostra `git status --short` e propõe `feat(ws-NNN): <título> [specs/ws-NNN-<nome>]` (+ ` (r<k>)` em revisão); com confirmação, commit e `ws push` para cada repo alterado (ws: `speckit.ws.commit-push.md`) | Conferir lista de arquivos, mensagem e envio. Se falhar, não contornar a guarda nem usar `git push`/`git subtree` |
| 9 | **Oferta dos PRs para o ramo de teste** (no fim do passo 8) | Roda `tools/ws/ws pr plano homolog` e mostra os PRs: um por repo enviado + o do workspace. Destino: `homolog`; **`develop` no Fly** (ws: `workspace.pr.ini`, `[teste]`). Pergunta se abre e pede o **número do card do Azure Boards** (ou "sem card"; o agente não inventa). Com o sim: `tools/ws/ws pr abrir homolog --card <número>`: envia a branch do workspace ao origin, abre os PRs das subtrees e depois o do workspace (com a tabela dos PRs das subtrees), atualiza as descrições, posta no espaço de **homologação** do Google Chat e mostra os links. Com o não: mostra os links `pullrequestcreate` (ws: `speckit.ws.commit-push.md`, passo 7; `1-comecar.md`, passo 9; disc: SP7 design, seção 4.1) | Aceitar ou recusar; informar o card. Se a entrega não muda nenhum repo, o harness oferece só o PR do workspace **direto para o `main`** (`tools/ws/ws pr abrir main [--card <n>]`) |
| 10 | `/speckit-ws-promover` (na branch da entrega, depois que a homologação aprovar) | `tools/ws/ws pr plano main` (avisa PR de teste ainda aberto); pede confirmação e o card de novo (sugere o mesmo); `tools/ws/ws pr abrir main --card <n>`; recria a branch de origem apagada a partir do PR completado para o ramo de teste; posta no espaço de **produção** (ws: `speckit.ws.promover.md`; `1-comecar.md`, passo 10) | **O dev decide** que a homologação passou (o harness não descobre sozinho; disc: SP7, seção 2) |
| 11 | Completar os PRs | — | Completar os PRs dos repos e, **por último, o do workspace** (nos dois destinos). **Não apagar a branch de origem** ao completar os PRs para o ramo de teste: o PR para o `main` sai dela (ws: `1-comecar.md`, passo 11). Cada time segue a política de PR do próprio repo |

**Detalhes do PR e da mensagem (ws: `tools/ws/pr/textos.py`):**
- Título: assunto convencional do commit mais recente (`feat(`, `fix(`, `refactor(`, `docs(`), senão a branch; prefixo `[homolog]` nos PRs para o ramo de teste.
- PR da subtree: origem, resumo, link do PR do workspace, lista de commits; no ramo de teste, o aviso "**Não apague a branch de origem ao completar: o PR para produção sai dela.**"
- PR do workspace: origem, resumo, tabela `| Repo | PR |` entre `<!-- ws-pr:subtrees -->` e `<!-- /ws-pr:subtrees -->` (é ela que o `/ws-revisar` lê) e o aviso "**Complete este PR só depois que todos os PRs acima estiverem completados.**"
- **Mensagem do Google Chat** (uma por destino e por entrega):
  ```
  Pull Request <id do PR do workspace>: <card>: <título do card>
  <título do PR>
  Autor: <autor>
  Workspace: <link|!id>
  Subtrees:
  • <repo>: <link|!id>
  Complete o PR do workspace por último.
  ```
  Sem card, a primeira linha é só `Pull Request <id>`; título do card não lido, `Pull Request <id>: <card>` (ws: `textos.py`; `2-quando-da-errado.md`).
- **Rodar de novo:** não duplica PR da mesma branch e destino, só atualiza a descrição; repo novo na entrega ganha PR e entra na tabela; o Chat não recebe mensagem nova num segundo envio (disc: SP7 design, seção 4.5).
- Espaço de produção: a URL do webhook `producao` está **vazia** em `workspace.pr.ini`; o `ws` avisa e mostra o texto para colar (ws: `workspace.pr.ini`; `2-quando-da-errado.md`, "Não consegui postar no Google Chat"). A de `homolog` está preenchida no `origin/main`.
- **Repos ainda sem `homolog` no origin (2026-10-21):** `print-zebra.utilitario.backend`, `wms.app.frontend`, `wms.hubprodutividade.backend`, `wms.servidor.backend`, `wms.tms-finished.backend`, `wms.tms.backend`, `wms.trakta.backend`. Enquanto faltar, o `ws pr` **não abre nenhum PR** de uma entrega que toque esses repos (ws: `4-manter.md`; disc: SP7 design, seção 3). O status atual desses ramos: **não encontrado** (não conferido no origin hoje).
- Ainda não validado no real: `ws pr abrir main` e a recriação de branch apagada (memória `sp7-prs-e-revisao-pausado`).

**Mudar uma feature existente:** `/speckit-specify` citando o número ("a 004", "feature 004", "ws-004") ou o nome da pasta sem número; o hook cria `ws-NNN-<nome>-r<k>` e edita a spec existente (living spec, tabela "Revisões"). Feature ainda não mergeada: ficar na branch dela (ws: `3-alem-do-basico.md`; `AGENTS.md`).

**Branch parada que precisa do `main`:** com a árvore limpa, `tools/ws/ws sync && git merge --no-edit ws/sync`; nunca `rebase` nem `git merge origin/main`. Se o `ws sync` falhar, ele **volta para a sua branch** sem trazer nada (ws: `2-quando-da-errado.md`; ADR 0001, adendo 6).

**Fora do Spec Kit (desaconselhado):** `tools/ws/ws start <branch>`, commits, `tools/ws/ws push`, `tools/ws/ws pr plano homolog`, `tools/ws/ws pr abrir homolog [--card <n>]`; depois da homologação, `tools/ws/ws pr plano main` e `tools/ws/ws pr abrir main`. Perde: spec (o porquê), Atlas no fim, conferência contra a constitution (ws: `3-alem-do-basico.md`, "Trabalhar fora do Spec Kit").

---

## 3. Bug, refactor e fatias de desacoplamento

**Bug ou incidente** (ws: `1-comecar.md`; `AGENTS.md`, "Bugs com o Spec Kit"):
1. `/speckit-bug-assess <relato>`: colar work item/incidente com id e evidências (stack trace, log, print, consulta). Slug `<id do work item>-<descrição>` ou `inc-<AAAAMMDD>-<descrição>`, minúsculas e hífens. O hook cria `hotfix/<slug>`; diagnóstico só leitura em `bugs/<slug>/assessment.md` (com seção **Impacto** se mudar contrato, regra II).
2. **Ler o `assessment.md`** e só seguir se concordar com causa e correção.
3. Sem correção de código: o agente registra o relatório e oferece o PR do workspace **direto para o `main`** (`tools/ws/ws pr abrir main`), sem homologação.
4. `/speckit-bug-fix` (grava `fix.md`) → `/speckit-bug-test` (build e testes, `test.md`; só diz `verified` se conferiu; `partial` = parte não verificada, por exemplo repo sem testes; `failed` = sintoma continua) (ws: `2-quando-da-errado.md`).
5. No fim: Atlas, commit `fix(<slug>): …`, `ws push` e a mesma oferta dos PRs (passos 9–11 da feature).
- Banco: só `SELECT`, só com acesso que o dev já tem, consulta mostrada antes; sem acesso, o agente escreve a consulta para o dev rodar; valores sensíveis não vão para os relatórios (ws: `AGENTS.md`; `3-alem-do-basico.md`).
- Investigar sem corrigir: mesmo `assess`, slug `inc-…`, termina no registro em `bugs/` (ws: `3-alem-do-basico.md`).

**Refactor interno** (ws: `1-comecar.md`; constitution VII):
1. `/speckit-refactor-assess <relato>` (work item, motivo, o que mudar). Slug `<id>-<descrição>` ou `rf-<AAAAMMDD>-<descrição>`; branch `refactor/<slug>`; `refactors/<slug>/assessment.md` com o que não pode mudar e o plano dos **testes de caracterização**.
2. **Ler o `assessment.md`**; aprovar exceção à caracterização só se concordar com o motivo e a verificação substituta (exceção é para trecho não testável sem refactor anterior, não para falta de tempo; ws: `3-alem-do-basico.md`).
3. `/speckit-refactor-apply`: commit `test(<slug>): caracterização` antes; depois o refactor.
4. `/speckit-refactor-verify`: build, testes, testes de caracterização inalterados; testes que já falhavam (linha de base no `apply.md`) não barram, falha nova barra (constitution III).
5. Envio e PRs como na feature.
- Se o comportamento observável ou um contrato muda, não é refactor: reclassificar (ws: `AGENTS.md`). Mover código entre repos e migrar para o AWX ainda não entram (ws: `1-comecar.md`).

**Fatia de desacoplamento (ADR 0003, SP6.2; chaves pelo ADR 0002, SP6.1)** (ws: `1-comecar.md`; `3-alem-do-basico.md`; constitution II e VII):
- A fatia é um **item da EAP** (ex.: `1.1.4 Contagem`); cada card é um refactor que informa o **código da EAP** e o título no `assess`; slug usa o **id do card** (`rf-…` não vale).
- **Com chave (padrão):** chave central `eap-<código com hífens>` (ex.: `eap-1-1-4`) na tabela do `AWX.ERP.Connector`; todos os sistemas da fatia a leem; o legado lê uma cópia mantida pela `AWX.IntegracaoLegadoWMS`; chave inexistente vale `antigo`; `ERP.Connector` sem resposta → a operação para com erro. Modos: `antigo`, `paralelo`, `sombra`, `novo`. O `wms.conector.backend` ainda não lê a chave (só fatia sem chave). Cada card vai para produção em "antigo".
- **Sem chave:** só com contratos mantidos, risco baixo e **aprovação do líder**; o código antigo sai na entrega; cada card ganha os PRs dele para o ramo de teste; para o `main`, a promoção sai da **branch de subida**.
- Etapas (em `refactors/fatias.md`, só alterado pelo `tools/ws/ws refactor fatia`): com chave, em andamento → entregue → convivência → validada → desacoplada → chave removida; sem chave, em andamento → entregue → validada.
- Comandos: `/speckit-refactor-subida <código>` (plano de subida; o time completa janela, cenários, plantão, monitoramento e roda de novo para marcar `revisado`); na janela, virada pela tela de chaves e `tools/ws/ws refactor fatia atualiza <código> convivencia` (cria branch e envia; o PR do workspace dela precisa estar mergeado antes do validar); `/speckit-refactor-validar <código> <evidência>`; só com chave: `/speckit-refactor-desacoplar <código>` e, com ele em produção, `/speckit-refactor-remover <código>`.
- Acompanhar: `tools/ws/ws refactor fatia pendentes`, `tools/ws/ws refactor fatia status [<código>]`. Aviso no `ws start` de convivência há mais de 14 dias sem validação.
- **Bloqueio atual:** enquanto a seção "Chaves centrais" da camada 3 tiver `<a definir pela feature>` (tabela de chaves, migração de criar e de remover, leitura por tipo de app), **nenhuma fatia com chave começa**; fatia sem chave e refactor interno seguem (ws: `3-alem-do-basico.md`; `2-quando-da-errado.md`).

---

## 4. O que o dev revisa e decide em cada etapa (qualidade)

Boas práticas tiradas da doc, da constitution e dos templates:
- **Antes de começar:** feature, bug ou refactor? Um erro que aparece durante a feature fica na feature (ws: `1-comecar.md`). Ajuste trivial fora do Spec Kit só em necessidade real (ws: `3-alem-do-basico.md`).
- **Spec (`specify`):**
  - "Repos afetados" é obrigatória; para contrato (endpoint HTTP, fila, tabela/view/proc compartilhada), os consumidores afetados vêm do índice de impacto do Atlas e entram na lista (constitution II; ws: `spec-template.md`).
  - Sistema externo: linha `- externo: <sistema>: <o que a feature espera dele>` (ws: `AGENTS.md`, regra 7).
  - Uma revisão vai na mesma spec (living spec), não numa nova (ws: `3-alem-do-basico.md`).
- **Clarify:** responder as dúvidas antes do plano (v1: `passo-2`).
- **Plan:**
  - conferir, por repo, a lista "Instruções do repo lidas", a constitution do repo (no AWX, conflito com a do workspace = pergunta ao humano), a stack, os **comandos exatos de build e testes** e os contratos com os afetados: dependente forte vira tarefa ou risco, app atingido vira ponto a confirmar (ws: `plan-template.md`; `AGENTS.md`, regra 2);
  - **Simplicidade:** a menor mudança que atende a spec, sem refatoração fora do escopo (constitution VI);
  - decisão relevante vira **ADR aprovado por humano**: no repo, se for só dele; em `docs/adr/` do harness, se cruza repos (constitution IV).
- **Tasks:** cada grupo por repo termina com a verificação de build e testes; tarefas `[workspace]` só vão no PR do workspace (ws: `tasks-template.md`).
- **Analyze:** requisito sem tarefa, tarefa sem requisito, termos diferentes (v1: `passo-5`).
- **Implement:** nada de segredo novo em spec, doc ou código; os que já existem são só registrados (constitution V). O agente lê as instruções do repo antes de mexer (ws: `AGENTS.md`, regra 1).
- **Converge:** repetir implement/converge até não surgir tarefa nova; o commit-push avisa se há tarefas pendentes (ws: `speckit.ws.commit-push.md`).
- **Envio:** cada repo afetado passa no **próprio build e nos próprios testes**, com as ferramentas dele; a entrega só termina quando todos passam (constitution III; `AGENTS.md`, regra 6).
- **Bug:** ler o `assessment.md` (causa e correção) antes do fix; conferir a seção Impacto; se ela faltar e a correção mexer em contrato, pedir a consulta ao índice de impacto (ws: `3-alem-do-basico.md`, "Bug que muda contrato"); `partial` é decisão do dev, e o PR do repo é o lugar para o time conferir o que faltou (ws: `2-quando-da-errado.md`).
- **Refactor:** aprovar exceção à caracterização só com verificação substituta; os testes de caracterização usam o framework e as abstrações (interfaces, repositórios, dublês) que o repo já tem (ws: `3-alem-do-basico.md`, "Testes de caracterização"); dívidas de conformidade do repo (como as do AWX) não se aplicam num refactor e vão como fora de escopo (constitution VII).
- **Revisão de código:** `/ws-revisar` (seção 6); o revisor escolhe o que publicar; o harness não vota.
- **Novidade como conhecimento:** regra nova de um repo vai para o arquivo de instrução dele (seção 7).

---

## 5. Regras e guardrails

**O que não fazer** (ws: `1-comecar.md`, "Três regras que não se quebram"; `AGENTS.md`):
1. Nunca `git push` para os repos, `git subtree` à mão ou `git pull` numa branch de trabalho: quem envia é o `ws push` (`AGENTS.md`, regra 5).
2. Dentro de `repos/<repo>/`, não criar nem alterar `.specify/`, `specs/` na raiz do repo e `.claude/skills/speckit-*`: o `ws push` recusa a branch ("ws: GUARDA"); remover é permitido. `CLAUDE.md`, `AGENTS.md`, o resto de `.claude/` e `.github/` do repo **podem** ser editados (ws: `AGENTS.md`, regra 4; `3-alem-do-basico.md`, "Onde gravar uma regra ou decisão"; ADR 0001, adendo 4).
3. Durante uma feature ou um bug, não propor nem fazer mudança no harness: `tools/`, `.specify/`, `.claude/`, `AGENTS.md`, `CLAUDE.md`, `docs/adr/` (ws: `AGENTS.md`). A regra 3 da camada 1 lista só `tools/`, `.specify/`, `.claude/`, `AGENTS.md` (pendência registrada em disc: `sp4-piloto.md`).
- Não criar branch nem `specs/ws-NNN-*` à mão; não commitar spec no `main`; branches `hotfix/` e `refactor/` só pelos hooks (ws: `AGENTS.md`).
- Não usar as skills `speckit-*` de dentro de `repos/` (aparecem como `/repos/<repo>:speckit-*`); specs do AWX são referência, nunca alterar (ws: `AGENTS.md`, regra 2).
- Não editar `docs/atlas/` à mão durante uma feature; não editar `refactors/fatias.md` à mão nem contornar portão (ws: `AGENTS.md`, regra 8; "Refactor com o Spec Kit").
- Não gravar em `.specify/bugs/`; `bugs/` e `refactors/` **não são harness** (ws: `AGENTS.md`).
- Não mudar o objeto do banco de onde um sistema sai enquanto outro sistema o acessar (constitution II).
- Não pôr política de PR na `ws/sync` (ws: `4-manter.md`).

**Regra dos PRs (nova, SP7)** (ws: `AGENTS.md`, seções de feature, bug e refactor; ADR 0001, adendo 8):
- Os PRs saem **pelo harness**: para o ramo de teste no fim do envio e para o `main` com `/speckit-ws-promover`.
- O PR do workspace é **aberto junto** com os dos repos e **completado por último**; nada impõe a ordem (a política é de cada repo).
- **Não apague as branches de origem** ao completar.
- Bug sem correção de código: só o PR do workspace, direto para o `main` (`tools/ws/ws pr abrir main`).
- Fatia sem chave: PRs de cada card para o ramo de teste; para o `main`, `/speckit-ws-promover` **na branch de subida**, e o time completa na ordem do plano, o do workspace por último (ws: `3-alem-do-basico.md`, "O plano de subida").
- PR de um repo abandonado: `git restore --source=main --staged --worktree -- repos/<repo>`, commit `reverte repos/<repo>: PR abandonado`, conferir com `tools/ws/ws pr plano <homolog ou main>` e rodar `tools/ws/ws pr abrir <homolog ou main>` de novo (ws: `3-alem-do-basico.md`).
- Antiobjetivos do design: PR aberto ou mensagem postada sem aceite do dev; comentário publicado sem escolha do revisor; token versionado (disc: SP7 design, seção 2).

---

## 6. Revisão de código com o harness (`/ws-revisar`)

(ws: `.claude/skills/ws-revisar/SKILL.md`; `1-comecar.md`, "Revisar um PR"; disc: SP7 design, seção 5)
- **Quem e onde:** o colega revisor, no workspace dele, dentro do Claude Code: `/ws-revisar <link do PR do workspace>` (link `.../_git/<repo>/pullrequest/<id>`).
- **Contexto:** `tools/ws/ws pr revisao <link>` busca a branch do PR num worktree e grava `.ws/revisao/<id>/contexto.json` com o diff do workspace e o de cada subtree **contra a base da `ws/sync`** (não contra o destino, para não trazer código de outras pessoas).
- **Fontes:** a origem (`spec.md` + `tasks.md`, ou `assessment.md`, ou `plano-subida.md`), a constitution, o `AGENTS.md` e o **`docs/convencoes.md` de cada repo** da entrega.
- **Cinco pontos, um subagente por ponto, em paralelo, só leitura:**
  1. **conformidade:** faz o que a origem pede, nem mais nem menos; o que contraria constitution, `AGENTS.md` ou convenções;
  2. **contratos:** endpoints, DTOs, filas, mensagens, tabelas, views, procedures; consumidores pelo `atlas-consultar`, inclusive fora da entrega (comentário cai no PR do workspace);
  3. **regras:** regras de negócio da origem e do Atlas preservadas; validações, cálculos, estados, fluxos alterados sem pedido;
  4. **defeitos e testes:** bugs, bordas, erro, concorrência, vazamento de recurso; mudança coberta por teste;
  5. **banco:** `.sql` e migrações (EF Core Migrations, Flyway etc.): cada script declara a **ordem de execução** e tem **rollback**; apontar o que não é seguro repetir ou reverter.
- **Lista numerada:** `N. ponto · gravidade · repo/PR · arquivo:linha · título` + texto; ordenada alta → média → baixa; sem os já publicados.
- **Escolha:** o revisor diz quais números publicar e pode editar o texto. **Sem escolha, nada é publicado**; "todos" nunca é presumido.
- **Publicação:** `tools/ws/ws pr comentar .ws/revisao/<id>/contexto.json .ws/revisao/<id>/achados.json`, com a credencial do revisor; código de `repos/<repo>/` vai no PR do repo, o resto no do workspace; achado sem linha ou fora do diff vira comentário geral.
- **Rodar de novo** (depois de uma correção do autor) não repete os achados já publicados (id = sha1 de `ponto|arquivo|titulo`).
- **Não aprova, não reprova, não vota.**
- Só revisa PR do workspace aberto pelo harness (com a tabela). Erro: `ws: erro: o PR !<id> não tem a tabela das subtrees: ele não veio do harness`; solução: link do PR do **workspace**, ou o autor roda `tools/ws/ws pr abrir homolog` na branch (ws: `2-quando-da-errado.md`).
- Par a revisar: o de `homolog`, que nasce primeiro; o de `main` sai da mesma branch (suposição do design, disc: SP7, seção 5.6).
- Observações factuais para o time do harness (não mudam o uso): o ponto "contratos" cita "as arestas de `docs/sistemas/`", nome antigo do Atlas (hoje `docs/atlas/`; disc: `estado-da-sessao.md`, SP3); o passo 2 lê constitution, `AGENTS.md` e `docs/convencoes.md`, mas não cita `CLAUDE.md`, `.github/copilot-instructions.md` nem `.claude/rules/`, onde estão as regras do Fly (ws: `SKILL.md` × tabela da seção 7).

---

## 7. Convenções e definições por repo

### 7.1 O que o harness espera de cada repo (fatos)

- **Princípio:** o harness fica só no workspace; nos repos ficam só convenções, regras, acordos e ADRs **específicos de cada repo** (ADR 0001, restrição 3 e seção 2).
- **Arquivos de instrução de um repo** reconhecidos pelo harness: `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `docs/convencoes.md`, `docs/adr/` e a constitution do repo (`.specify/memory/constitution.md` ou `docs/constitution.md`) (ws: `AGENTS.md`, regra 1; ADR 0001, adendo 4).
- **Subordinação:** a constitution e o `AGENTS.md` da raiz governam o que cruza repos e o jeito de trabalhar do agente; dentro de `repos/<repo>/`, as instruções do repo valem para o código dele; conflito → o agente para e pergunta ao humano (constitution I; `AGENTS.md`, "Hierarquia").
- **Onde gravar regra nova** (ws: `AGENTS.md`, regra 3; `3-alem-do-basico.md`, "Onde gravar uma regra ou decisão"):
  - vale só para um repo → no arquivo de instrução que ele **já tem**; se não tiver nenhum → `repos/<repo>/docs/convencoes.md` ("só é criado quando o repo não tem nenhum dos outros", ADR 0001, adendo 4);
  - decisão de arquitetura do repo → `repos/<repo>/docs/adr/NNNN-<titulo>.md` (constitution IV: ADR aprovado por humano);
  - vale para mais de um repo ou para o jeito de trabalhar → harness, registrado para o time do harness, fora da feature.
- **Criação do `docs/convencoes.md`:** "sob demanda" (ADR 0001, pendência 4; disc: SP2 design, "Os outros 14 … ganham `docs/convencoes.md` quando surgir uma regra específica").
- **Template de `docs/convencoes.md`:** **não existe** no workspace (nenhum arquivo em `tools/`, `.specify/` ou `docs/` com modelo; grep por "convencoes" no `origin/main` só acha as regras citadas). Também **não há template** de ADR de repo.
- **Como o agente usa:**
  - **implement/qualquer mudança:** lê explicitamente os arquivos de instrução do repo antes de mexer, "sem contar com o carregamento automático" (ws: `AGENTS.md`, regra 1);
  - **plan:** registra por repo as "Instruções do repo lidas" (`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `docs/convencoes.md`, `docs/adr/`), a constitution do repo, a **stack** e os **comandos exatos de build e testes** (ws: `plan-template.md`). Quando o repo não documenta stack e comandos, o agente os deduz a cada plano (consequência do template; nenhum repo além de AWX e Fly os documenta, ver 7.2);
  - **review (`/ws-revisar`):** lê constitution, `AGENTS.md` e `docs/convencoes.md` de cada repo e usa as convenções no ponto "conformidade" (ws: `ws-revisar/SKILL.md`);
  - **Atlas:** `docs/atlas/<repo>/` (project-readme, domain, business, tech, `_discovery/traceability-index.md`) é conhecimento de apoio, gerado pelo mapeamento; não substitui as convenções do time (ws: `plan-template.md`; `4-manter.md`).
- **Exemplos internos que já existem** (servem de modelo para o time):
  - AWX `AGENTS.md` (257 linhas): regra principal, precedência, onde adicionar instruções, contexto, **comandos** (`dotnet build AWX.slnx`, `dotnet test AWX.slnx`, teste isolado com `--filter`, testes de arquitetura), mapa do repositório, coding standards, Sonar, "Antes de commitar" (skill `qualidade-codigo`), house rules (nomenclatura, reutilização, mensageria) (ws: `repos/…awx.monorepo/AGENTS.md`); o `CLAUDE.md` só importa o `AGENTS.md`.
  - Fly `CLAUDE.md` (97 linhas): projeto, ambiente, **comandos essenciais** (`npx tsc --noEmit`, `npm run lint`, `npm run type:check`, `npm run test:unit:ci` obrigatórios antes do commit; Biome, não Prettier), testes, mapa de diretórios, convenções de código, fluxo de feature, autorização, hooks (Lefthook), gotchas; mais `.claude/rules/` (4 arquivos) e `docs/TESTING.md` (ws: `repos/integracoes.core.plataforma.backoffice.frontend/`).
  - Linx `AGENTS.md` (93 linhas): padrão de repositórios (Dapper), nomenclatura, contratos de borda, logging, fronteiras entre camadas, stack canônica; build e deploy remetidos ao README (ws: `repos/integracoes.wms.servicos-linx-wms.monorepo/AGENTS.md`).
  - Servidor `AGENTS.md` (54 linhas): tecnologias e camadas, idioma PT-BR no código, execução de testes, `.editorconfig`, regras de revisão (sufixo `Async`, `Requisicao`/`Resposta`, `IEnumerable<T>`, SOLID). Cita `run-tests-unitarios.ps1` e `run-tests-integracao.ps1` com caminhos absolutos `file:///C:/Projetos/...`; no repo só existe `run-tests.ps1`. O `.github/copilot-instructions.md` está vazio (0 linhas) (ws: `repos/industria-logistica.wms.servidor.backend/`).

### 7.2 O que existe hoje em cada repo (fatos, `origin/main` de 2026-10-22)

Levantado por `git ls-tree` em `repos/`. "Testes" = projeto de teste ou arquivos de teste encontrados pelo nome; "Lint/format" = `.editorconfig`, ESLint, Prettier, Biome, `Directory.Build.props`; "SQL" = arquivos `.sql` (e, entre parênteses, nomes com rollback/revert/undo/down).

| Repo (`repos/…`) | Instrução de agente | `docs/convencoes.md` | `docs/adr/` | README | Testes | Lint/format | Build/test documentado no repo | SQL |
|---|---|---|---|---|---|---|---|---|
| `print-zebra.utilitario.backend` | nenhuma | não | não | sim | nenhum | nenhum | não | 17 |
| `reserva-net.api-gateway.backend` | nenhuma | não | não | **não** | nenhum | nenhum | não | 0 |
| `reserva-net.autenticacao.monolito` | nenhuma | não | não | sim | 3 projetos (`SSO.Unit.Tests`, `SSO.Integration.Tests`, `SSO.Presentation.SSO.Tests`) | só de libs de terceiros em `wwwroot` | não | 37 (2) |
| `reserva-net.b2b.backend` | nenhuma | não | não | sim | `ReservaNet.B2B.UnitTests` | nenhum | só Docker no README | 5 |
| `wms.app.frontend` | nenhuma | não | não | sim (`readme.md`) | `jest.config.js`, 1 arquivo de teste | ESLint, Prettier | scripts npm no README (sem teste) | 0 |
| `wms.awx.monorepo` | `AGENTS.md`, `CLAUDE.md`, `.claude/` (hooks, skills), constitution em `.specify/memory/` | não | não | sim | muitos projetos (unit, integração, arquitetura) | `.editorconfig`, `Directory.Build.props`, `Directory.Packages.props` | **sim** (`AGENTS.md`) | 12 (+ migrações) |
| `wms.conector.backend` | nenhuma | não | não | sim | `ReservaNet.Linx.UnitTests` | nenhum | não | 5 |
| `wms.ecommerce.backend` | nenhuma | não | não | sim | pasta `tests/ReservaNet.ECommerce.UnitTests` com `.cs`, **sem `.csproj`** na árvore | nenhum | não | 122 |
| `wms.ecommerce.frontend` | nenhuma | não | não | sim | `karma.conf.js`, 69 arquivos `.spec` | ESLint, Prettier | não | 0 |
| `wms.hubprodutividade.backend` | nenhuma | não | não | sim | `Reserva.HubProdutividadeWMS.Test` | nenhum | não | 9 |
| `wms.picking.backend` | nenhuma | não | não | sim | `Reserva.WMS.Picking.Tests` | nenhum | só Docker no README | 81 (11) |
| `wms.picking.frontend` | nenhuma | não | não | sim | 2 arquivos `.spec` | `.editorconfig` | não | 0 |
| `wms.servidor.backend` | `AGENTS.md`, `.github/copilot-instructions.md` (vazio) | não | não | sim | `Reserva.WMS3.Testes` | `.editorconfig` | parcial (scripts citados não batem com `run-tests.ps1`) | 630 (116) |
| `wms.tms-finished.backend` | nenhuma | não | não | **não** | nenhum | nenhum | não | 0 |
| `wms.tms.backend` | nenhuma | não | não | **não** | nenhum | nenhum | não | 0 |
| `wms.trakta.backend` | nenhuma | não | não | sim | `Wms.Trakta.Test` | nenhum | não | 7 |
| `integracoes.core.plataforma.backoffice.frontend` (Fly) | `CLAUDE.md`, `.claude/agents`, `.claude/rules` (4) | não | não | sim | Vitest (374 arquivos), Playwright | ESLint, Biome | **sim** (`CLAUDE.md`, `docs/TESTING.md`) | 0 |
| `integracoes.wms.servicos-linx-wms.monorepo` | `AGENTS.md` | não | não | sim | 2 projetos de unit test | `Directory.Build.props`, `Directory.Packages.props` | remete ao README | 6 |

**Leitura da tabela:**
- **Nenhum dos 18 repos tem `docs/convencoes.md` nem `docs/adr/`.**
- **14 repos não têm nenhum arquivo de instrução**: para eles, o agente só tem o código e o Atlas; a regra nova iria para `docs/convencoes.md`.
- 4 repos têm instruções próprias (AWX, Fly, servidor, Linx): neles a regra nova vai para o arquivo que já existe (`AGENTS.md`/`CLAUDE.md`), não para `docs/convencoes.md` (ws: `AGENTS.md`, regra 3).
- Só AWX e Fly documentam build e testes de forma completa; nos outros, o plano deduz os comandos.
- 5 repos sem testes encontrados (`print-zebra`, `api-gateway`, `tms`, `tms-finished`; `ecommerce.backend` com testes sem projeto); no bug, isso leva a `partial` (ws: `2-quando-da-errado.md`).
- Scripts de banco: 11 repos têm `.sql`; só 3 têm algum arquivo com nome de rollback, e nenhum repo declara uma convenção de ordem de execução e rollback, que é exatamente o que o ponto "banco" do `/ws-revisar` cobra.
- Pipelines (`esteiras/` ou YAML) não encontradas em `print-zebra`, `servidor.backend` e `tms-finished` (apenas observação do `ls-tree`).

### 7.3 Proposta (não está na doc): o que um bom `docs/convencoes.md` deveria cobrir

Para os 14 repos sem instrução. Nos 4 com instrução, os mesmos tópicos no arquivo que já existe. Cada item responde a algo que o harness já pede (plano, tasks, revisão):
1. **Stack e versões:** linguagem, framework, runtime (.NET Framework × .NET 5–10, Angular, React Native, Next.js; disc: ADR 0001, contexto), SDK fixado (`global.json`, `.nvmrc`) → alimenta o "Stack" do plano.
2. **Comandos de build, teste e lint exatos**, incluindo como rodar um teste isolado e o que a pipeline exige → alimenta "Build e testes" do plano e a tarefa de verificação por repo (constitution III).
3. **Estrutura de pastas e camadas**, e onde cada tipo de coisa entra (controller, serviço, repositório, DTO, tela).
4. **Nomenclatura:** idioma do código (ex.: o PT-BR do servidor), sufixos (`Async`, `Requisicao`/`Resposta`), nomes de arquivos, rotas, filas.
5. **Tratamento de erro e logging:** padrão de exceção, retorno de erro na API, o que logar e o que nunca logar (segredos, dados sensíveis).
6. **Acesso a dados:** ORM ou Dapper, repositórios, transações, connection strings por configuração (nada de segredo novo, constitution V), objetos compartilhados do banco e o aviso da regra II.
7. **Testes:** framework, onde ficam, padrão de nome, dublês, o mínimo esperado num PR, como escrever caracterização no repo.
8. **Scripts de banco:** pasta, nome com **ordem de execução**, **script de rollback** correspondente, idempotência ("seguro repetir"), quem roda em homolog e em produção → é o ponto 5 do `/ws-revisar`.
9. **Contratos expostos:** endpoints, filas e eventos que o repo publica, versionamento e compatibilidade.
10. **Checklist de PR do repo:** build, testes, lint, prints de tela (como o Fly pede no card), scripts com rollback, ramo de teste (`homolog`/`develop`).
11. **Gotchas** do repo (o que quebra fácil, configuração local, caminhos longos).
12. **ADRs:** índice de `docs/adr/` e quando abrir um (decisão de arquitetura só do repo, aprovada por humano).

**Proposta (não está na doc), para o deck:** um modelo de `docs/convencoes.md` no harness (por exemplo em `tools/` ou na camada 3) e uma tarefa por time para preencher o seu repo, começando pelos repos com mais vizinhos (`servidor.backend`, `ecommerce.backend`; disc: ADR 0001, contexto). Criar ou mudar esse arquivo num repo é mudança no repo (não é harness) e sai pelo fluxo normal com PR do repo; criar o modelo no harness é mudança de harness (branch própria, fora de feature).

---

## 8. Como melhorar o harness

- **Durante uma feature, bug ou refactor:** não mudar o harness. Se o agente propõe mexer em `tools/`, `.specify/`, `.claude/` ou `AGENTS.md`: recusar e registrar o problema na thread de suporte; a correção é feita fora (ws: `2-quando-da-errado.md`, "O agente quer mudar o harness"; `AGENTS.md`). Todos os comandos `speckit.ws.*` e a `ws-revisar` repetem: "descreva o problema e sugira registrá-lo para o time do harness".
- **Onde registrar:** thread no espaço **Equipe WMS** do Google Chat: https://chat.google.com/room/AAAAKpyvLWs?cls=7, com o comando/skill rodado, a mensagem completa e a saída de `git status` e `git log --oneline -3` (ws: `2-quando-da-errado.md`, "Não resolveu?"). Padrão de segredo nos docs do Atlas: registrar com o nome do repo, **sem colar o trecho** (idem).
- **Ciclo de feedback (como funcionou no piloto):** o observador anota cada travada com etapa e palavras do dev; o dev procura primeiro na camada 2; cada linha com ação vira PR de acompanhamento no workspace (camada 1 ou entrada nova na camada 2), com `tools/ws/tests/test_docs_referencias.sh` passando (disc: `sp4-piloto.md`, "Como conduzir"). Exemplos que viraram correção:
  - sistema fora do workspace → regra 7 do `AGENTS.md` e entrada na camada 2 (PR 17070);
  - caminhos longos fora do git → passo 2 da camada 1 (PR 17070);
  - `ws push` caindo no HTTP/2 do Azure DevOps → HTTP/1.1 e buffer de 500 MB (PR 17072);
  - Atlas do Linx apagado no início da feature (PR 17073);
  - avisos do `ws start` não chegavam ao dev (PR 17103) (disc: `sp4-piloto.md`; `estado-da-sessao.md`).
  - **Mais recentes (2026-10-21/22):** `ws push` parava com `fatal: cache for <sha> already exists!` por marcador de split repetido → cópia `tools/ws/vendor/git-subtree-ws` (Git 2.54.0 com `cache_set` tolerante); `ws sync`/`ws start` deixavam a árvore na `ws/sync` na falha de rede ("volta: unbound variable") → agora voltam para a branch (PR 17254; ADR 0001, adendo 7); bit de execução do `git-subtree-ws` para Linux e macOS (PR 17255) (ws: `git log origin/main`).
- **Quem mantém e como (camada 4):** "time do harness" (sem nomes na doc: **não encontrado**). Regras (ws: `4-manter.md`, "Evoluir o harness"):
  - nunca dentro de uma feature; branch própria a partir do `main`, PR no workspace;
  - a suíte passa antes do PR (`bash tools/ws/tests/run.sh`, cerca de 15 min no Windows);
  - a documentação muda junto (o teste de referências não pega comportamento novo);
  - decisão relevante vira ADR em `docs/adr/`;
  - nunca editar as cópias em `.specify/`: mudar a fonte em `tools/speckit/` e rodar `tools/ws/ws speckit`;
  - mudar a constitution exige PR no workspace aprovado por humano (constitution, "Governança").
  - Checklist do PR: branch própria; suíte passou; camada da doc atualizada; ADR registrado.
- **Pedidos que só o time do harness resolve:** incluir um repo no workspace (camada 4, "Adicionar um repo"); conflito no sync de um repo; política na `ws/sync` (`TF402455`); mudar o ramo de teste de um repo em `workspace.pr.ini` (ws: `2-quando-da-errado.md`; `4-manter.md`).
- **O que é do time de cada repo (não é harness):** criar o ramo `homolog`; escrever as convenções e ADRs do repo (seção 7); política de PR e revisores.
- **Inconsistências da doc vistas neste levantamento** (registro, para o time do harness): `4-manter.md` diz que as duas URLs do Chat "estão vazias", mas a de `homolog` está preenchida; a lista de `tools/ws/lib/` em `4-manter.md` não cita `pr`; a regra 3 da camada 1 não lista `CLAUDE.md` e `docs/adr/` (já anotado em disc: `sp4-piloto.md`); a `ws-revisar` cita `docs/sistemas/` (ver seção 6).

---

## 9. Quando dá errado: as mensagens mais prováveis

Formato: `ws: erro:` = parou; `ws: aviso:` = seguiu, mas avisa. Tudo em ws: `docs/harness/2-quando-da-errado.md`.

| Mensagem (texto exato) | O que fazer |
|---|---|
| `ws: erro: há mudanças não commitadas; faça commit ou stash antes` | `git status`; commit na branch certa, `git stash` ou `git restore .`; rodar de novo |
| `ws: erro: a branch <branch> já existe` | `git switch <branch>` se for desta feature; senão outro nome |
| `a feature <NNN> ainda não está no main: faça checkout da branch <branch> …` | Fazer checkout da branch da feature (camada 3, "Mudar uma feature que já existe") |
| `ws: erro: conflito no sync de <prefixo> na <ws/sync>. …` | `git merge --abort`, voltar para a branch e pedir ajuda ao time do harness |
| `ws: erro: não consegui ler <repos>: verifique a rede, a URL no manifesto e a credencial` | Rede/VPN; `git ls-remote <url>`; renovar credencial |
| `ws: erro: push de <ws/sync> recusado por política do Azure DevOps (TF402455); …` | Pedir ao time do harness |
| `ws: aviso: seu <main> local tem <n> commit(s) que não estão no origin; …` | `git log origin/main..main --oneline`; se só sync, `git switch main && git reset --hard origin/main` |
| `ws: erro: ws-commit-push não roda no <main>; use a branch da feature` | `git switch <branch>` |
| `ws: GUARDA: <prefixo>: a branch adiciona ou altera arquivos de harness:` / `ws: erro: push recusado; o harness fica na raiz do workspace (ADR 0001, seção 2)` | `git restore --source=main -- repos/<repo>/<arquivo>` (ou apagar o novo), commit, enviar de novo |
| `ws: erro: subtree push de <prefixo> falhou` (com `RPC failed; curl 65 HTTP/2 stream … was reset`) | `git ls-remote`; branch antiga: `git config http.postBuffer 524288000` e `git config http.version HTTP/1.1`; `tools/ws/ws push` de novo |
| `fatal: cache for <sha> already exists!` | `tools/ws/ws sync && git merge --no-edit ws/sync` e `tools/ws/ws push` |
| `ws: nenhum repo alterado nesta branch; nada a enviar` | Usar `/speckit-ws-commit-push`; se só muda o workspace, PR do workspace direto |
| `ws: erro: o az não está autenticado no Azure DevOps: rode az devops login e tente de novo; nenhum PR foi aberto` | `az devops login` com PAT (não `az login`); links `pullrequestcreate` vêm abaixo |
| `ws: erro: não encontrei o az (Azure CLI): instale o Azure CLI e a extensão azure-devops (az extension add --name azure-devops) e tente de novo; nenhum PR foi aberto` | Instalar e logar |
| `ws: erro: sem o ramo de teste no origin: <repos>; o time do repo precisa criá-lo. Nenhum PR foi aberto` | Pedir ao time do repo a `homolog`; ou abrir à mão pelos links |
| `ws: aviso: PR para o ramo de teste ainda aberto: <repo> !<id>` | Confirmar homologação; não bloqueia |
| `ws: recriada a branch <branch> em <repo> a partir do PR !<id>` / `ws: erro: a branch <branch> não existe mais em <repo> e não achei o PR completado para o ramo de teste; nenhum PR foi aberto` | Nada / recriar a branch no repo e rodar de novo |
| `ws: aviso: não consegui postar no Google Chat (<espaço>); cole o texto abaixo no espaço:` | Colar o texto (produção está sem URL) |
| `ws: aviso: não consegui ler o título do card <número> no Azure Boards; a mensagem vai só com o número` | Conferir o número; PAT com Work Items (Read) |
| `ws: erro: o PR !<id> não tem a tabela das subtrees: ele não veio do harness` | Passar o link do PR do workspace |
| `slug inválido: <slug>. Use <id do work item>-<descrição> ou inc-<AAAAMMDD>-<descrição>, …` | Aceitar o slug corrigido |
| `ws: erro: testes de caracterização alterados depois do commit <hash>: <arquivos>. …` | `git restore --source <hash> <arquivo>`, ajustar o código, verify de novo |
| `ws: aviso: o mapeamento falhou em <repos>; esses repos continuam pendentes` | Seguir; `/atlas-atualizar` fora da feature se precisar |
| `ws: aviso: mapa não atualizado em <repos>; o agente usa grep e ast-grep nesses repos` | Conferir instalação das ferramentas do Atlas |
| `Filename too long` / `FileNotFoundError`, `Could not find a part of the path`, `ENOENT` | Clonar com `core.longpaths`; `LongPathsEnabled` como admin |

**Não resolveu?** Thread no espaço Equipe WMS (seção 8).

---

## 10. Onde está cada coisa

- **Entrada:** `README.md` do workspace, com a tabela "Quero… / Leia" (ws: `README.md`).
- **Camadas** (ws: `docs/harness/`): 1. Começar (setup, feature, bug, refactor, fatia, **revisar um PR**); 2. Quando dá errado (por etapa; inclui "PRs e merge"); 3. Além do básico (mapas, Atlas, mudar feature, fora do Spec Kit, chaves, fatias, plano de subida, PR abandonado, AWX, onde gravar regra); 4. Manter o harness (peças, tabela de caminhos, tarefas, `workspace.pr.ini`, evoluir); `historico/` com as specs e planos.
- **Regras do agente:** `AGENTS.md` (o `CLAUDE.md` só importa); princípios: `.specify/memory/constitution.md` (versão **1.5.0**).
- **Decisões:** `docs/adr/0001` (workspace, adendos 1–8), `0002` (chaves centrais), `0003` (fatias pela EAP).
- **Configuração:** `workspace.repos` (18 repos, branch-base `main`); `workspace.pr.ini` (Azure, webhooks do Chat, ramo de teste por repo).
- **Trabalho do dev:** `specs/ws-NNN-*`, `bugs/<slug>/`, `refactors/<slug>/`, `refactors/fatias.md`, `refactors/fatias/<código>/`, `refactors/desacoplamentos/`.
- **Atlas:** `docs/atlas/` (docs por repo, `impacto/`, `indice.csv`, `grafo.html`); skills `/atlas-consultar` e `/atlas-atualizar`.
- **Revisão:** `.claude/skills/ws-revisar/`; contexto em `.ws/revisao/<id>/`.
- **Suporte:** thread no espaço Equipe WMS do Google Chat (link na seção 8).
- **Versões:** Spec Kit 1.2.0 (ws: `tools/speckit/VERSION`); ferramentas do Atlas em `tools/atlas/VERSOES.md`.

---

## 11. Diferenças em relação à v1 do deck

**O que entrou desde a v1** (v1 = deck de 29 slides, atualizado até o SP6.2; disc: `estado-da-sessao.md`, "Deck atualizado (v29)"):
- **SP7, PRs pelo harness** (PR 17261, 2026-10-22): oferta no fim do envio, card do Azure Boards, PRs para `homolog` (`develop` no Fly), PR do workspace aberto junto e completado por último, mensagem no Chat, `/speckit-ws-promover`, recriação da branch apagada, `workspace.pr.ini`, comandos `ws pr plano|abrir|revisao|comentar` (ws: `AGENTS.md`; `1-comecar.md`; ADR 0001, adendo 8).
- **SP7, revisão:** `/ws-revisar` com os cinco pontos e publicação escolhida.
- **Setup novo:** Azure CLI + `azure-devops` + `az devops login` (PAT Code Read & write + Work Items Read); Python para o `ws pr`.
- **Correções de feedback:** `ws push` com `tools/ws/vendor/git-subtree-ws` (marcador repetido); `ws sync`/`ws start` voltam para a branch na falha de rede; bit de execução do `git-subtree-ws` (PRs 17254, 17255; ADR 0001, adendo 7).
- **Constitution 1.5.0** (2026-10-18 chaves centrais; 2026-10-20 fatias pela EAP) (ws: constitution, "Governança").

**O que na v1 está desatualizado ou errado:**
- `passo-8-9`: "Abra um PR por repo; com todos mergeados, o PR do workspace para o `main`" e a nota "O PR do workspace só entra depois de todos os PRs dos repos mergeados" → **errado**: agora o harness abre os PRs; o do workspace é aberto **junto** e completado **por último**.
- `resumo`: "9 PRs nos repos e no workspace" → agora passo 9 (oferta para o ramo de teste), 10 (`/speckit-ws-promover`) e 11 (completar, workspace por último, sem apagar a branch).
- `bug`: "você abre só o PR do workspace" e a nota "Os PRs seguem como na feature: um por repo e, com todos mergeados, o do workspace" → agora o harness oferece o PR do workspace direto para o `main` (sem correção) e a mesma oferta da feature (com correção).
- `antes-depois`: "Enviar e abrir PRs → `/speckit-ws-commit-push` envia" e "os PRs seguem o fluxo normal de cada time" → agora também abre os PRs e posta no Chat; a política de PR continua de cada repo.
- `desacoplamento` (nota): "os PRs ficam abertos até a janela, testados na homolog" → agora cada card tem os PRs dele para o ramo de teste abertos pelo harness, e a promoção para o `main` roda na branch de subida.
- `cmd-ws`: `ws refactor pendentes` → o comando atual é `tools/ws/ws refactor fatia pendentes` (e `status`); faltam `ws pr …` e `ws sync`/`ws start` voltando à branch na falha.
- `cmd-skills`: faltam `/speckit-ws-promover` e `/ws-revisar`.
- `novidades`: "constitution foi para a 1.3.0" → hoje 1.5.0; "Spec Kit 1.2.0" continua certo.
- `regras`, regra 3: "tools, .specify, .claude e AGENTS.md" → o `AGENTS.md` inclui também `CLAUDE.md` e `docs/adr/`.
- `onde`: falta "revisar um PR" (camada 1) e "PRs e merge" (camada 2).
- `erros`: os três exemplos continuam válidos; vale acrescentar os de PR (`az` não autenticado, sem ramo de teste).
- `proximos`: "O piloto continua" → o registro do piloto ainda não tem "Resultado" preenchido (disc: `sp4-piloto.md`), então continua verdadeiro, mas sem novidade.
- Ainda não coberto na v1: convenções e definições por repo (seção 7 deste brief), o que o dev revisa por etapa (seção 4) e como dar feedback ao harness (seção 8).

**Proposta (não está na doc), distribuição de tempo para 70–80 min:** abertura e novidades (5); setup com `az` e PAT (6); fluxo da feature com PRs e promoção (15); o que revisar em cada etapa (8); bug, refactor e fatias (10); revisão com `/ws-revisar` (7); convenções por repo, tabela e proposta de `docs/convencoes.md` (12); como melhorar o harness (4); erros e onde está cada coisa (5); perguntas (até 8).
