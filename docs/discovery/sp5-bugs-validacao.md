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
