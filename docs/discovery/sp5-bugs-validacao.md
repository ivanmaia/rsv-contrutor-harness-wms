# SP5: validação da vertente de bugs

Spec: `docs/superpowers/specs/2026-10-11-sp5-bugs-design.md`. Plano: `docs/superpowers/plans/2026-10-11-sp5-bugs.md`.

## Ambiente
- Workspace `C:\src\wms-workspace-e2e5`, origin bare `C:\src\wms-e2e5-origin.git` (main = `harness/bugs` `6a3bd7ad` + o commit que aponta o `tms.backend` para o espelho).
- `tms.backend` no espelho `C:\src\wms-e2e5-tms.git`, com o bug plantado (`is_company == "0"`, commit `dd7370b`). Push para o Azure DevOps bloqueado (`pushInsteadOf`).
- O espelho foi criado sem rede, a partir do último commit do `tms.backend` enviado pelo `ws push` (`caaa525`, PR 10263), já presente no workspace local: o clone do Azure DevOps foi negado pelo classificador de permissões do Claude Code.
- Decisão do usuário (opção B): o `atlas.estado` dos repos que não têm a ver com o bug (awx, ecommerce.backend, picking.backend, picking.frontend, servidor.backend, backoffice.frontend) foi marcado como em dia, só no ambiente, para o Atlas não gastar cerca de 1 milhão de tokens mapeando repos fora do caso.
- `claude -p` com `--permission-mode acceptEdits --allowedTools "Bash Read Edit Write Grep Glob Skill Task Agent"` (o `Task Agent` é para os subagentes do Atlas).

## PoC (spec 8.1)

| # | Item | Resultado | Observação |
|---|---|---|---|
| 1 | `wrap`/`prepend` em comando de extensão | ok | teste `test_speckit_preset_bugs_envolve_os_comandos_oficiais` |
| 2 | redirecionamento para `bugs/` e slug | ok | `bugs/90001-intelipost-pj-invertido/assessment.md`; nada em `.specify/bugs/`; slug com o id do work item; branch `hotfix/90001-intelipost-pj-invertido`. Causa certa (`IntelipostRepository.cs:101`, `== "0"`, commit `dd7370bd`), sem seção Impacto (correção não muda contrato). US$ 3,00, 3 min, Atlas incluído (tms.backend e backoffice.frontend, que o `ws start` trouxe atualizado). |
| 3 | sessão nova acha o bug | ok | `/speckit-bug-fix` sem `--resume`: "o bug foi identificado por ser o único com `assessment.md` em `bugs/`"; grava `fix.md`; diff de uma linha volta `== "1"`; `dotnet build` do projeto sem erro; sem teste automatizado (o repo não tem projeto de testes). US$ 0,54. |
| 4 | chamadas do preset | ok | ordem das ferramentas na sessão: `speckit-ws-bug-start` → `ws-bug-start.sh` → Atlas (`atlas-consultar`, `atlas-atualizar`, subagente de mapeamento) → investigação → `Write assessment.md` → `ws atlas concluir`/`mapas` → `speckit-ws-bug-sem-correcao`, que disse "leia o `assessment.md` … e rode `/speckit-bug-fix`". |

Observação do ambiente de teste: no Git Bash, o argumento `/speckit-bug-fix` sozinho vira `C:/Program Files/Git/speckit-bug-fix` (conversão de caminho do MSYS). O agente entendeu mesmo assim; as rodadas seguintes usam `MSYS_NO_PATHCONV=1`. Não afeta o dev, que digita o comando no Claude Code.

## Ponta a ponta (spec 8.3)

Ambiente atualizado com a `harness/bugs` até `3206b1f8` (tarefas 4 e 5) e com a `atlas/atualizacao` da PoC mergeada no `main`, como o dev faria com o PR do Atlas. Branches `hotfix/*` apagadas no workspace, no origin e no espelho antes dos casos.

| Caso | Resultado | Observação |
|---|---|---|
| Bug com correção em 1 repo (90001) | ok | `assess`, `fix`, `test` e envio na mesma sessão (`--resume`). Slug `90001-intelipost-pj-pf-invertido`. `test.md` com **Result: partial** e o motivo (sem projeto de testes no repo; reprodução depende do banco e da API da Intelipost; build da solução com `dotnet build` sem erro). O agente pediu confirmação por causa do `partial`; com o "sim", o Atlas do fim remapeou o `tms.backend` (commit `e1c42760`) e veio o commit `2f8604d8 fix(90001-…): Intelipost recebe PF e PJ invertidos (is_company)` com a linha e os três relatórios. `hotfix/90001-intelipost-pj-pf-invertido` criada no espelho do `tms.backend`. PRs listados: o do repo, avisando o `partial`, e depois o do workspace. US$ 6,30 (0,92 + 1,17 + 1,40 + 2,81). |
| Não é bug (90002) | ok | Veredito `invalid`: o `Helper.log` grava em `C:\temp` só em `catch` e em resposta não-OK, com as linhas citadas; sugere pedir os arquivos ao usuário se aparecer uma linha por pedido. Mostrou `git status`, propôs `docs(90002-log-pedido-intelipost): diagnóstico sem correção de código` e pediu confirmação; com o "sim", commit `2aaa2e6b` só com `bugs/90002-…/assessment.md`, branch no origin do workspace e nada no espelho. US$ 1,40. |
| Bug que muda contrato (90003) | ok | `assessment.md` com `## Impacto` citando `docs/atlas/impacto/reserva.dbo.pr_rsv_intelipost_dados_pedido.md` e os 2 afetados da página (`tms.backend` db-exec, `ecommerce.backend` db-def), mais o ponto a confirmar sobre executores fora do workspace. O agente também contestou o relato (o campo vem em quilos pela própria procedure), deu veredito `likely valid, needs reproduction` e escreveu dois `SELECT` para o usuário rodar, sem acessar o banco. US$ 1,00. |
| Sessão nova no meio | ok | PoC, item 3: `/speckit-bug-fix` numa sessão limpa achou o bug pela pasta. US$ 0,54. |

**Achados:**
- Nenhum pede correção no harness.
- Ambiente de teste: com `MSYS_NO_PATHCONV=1` (usado na primeira rodada do caso 1 para o Git Bash não converter `/speckit-bug-fix`), os comandos `tools/ws/ws atlas` falham, porque o Python do Windows recebe `C:\c\src\...`. O agente percebeu, rodou sem a variável e avisou como problema do harness. O dev não tem essa variável no fluxo normal; fica registrado aqui, sem correção.
- O mapeamento do Atlas do `tms.backend` voltou a apontar credenciais gravadas no repo (já conhecido; fora do escopo deste trabalho).
- Custo total da validação com LLM: cerca de US$ 12,20 (PoC US$ 3,54; ponta a ponta US$ 8,70).

**Ambientes descartáveis a apagar pelo usuário:** `C:\src\wms-workspace-e2e5`, `C:\src\wms-e2e5-origin.git`, `C:\src\wms-e2e5-tms.git`, os JSON e logs `C:\src\wms-e2e5-*` e o script `C:\src\wms-e2e5-c1.sh`.
