# Adendo ao SP2: harness do AWX subordinado ao workspace, sem migrar o Spec Kit dele

- **Data:** 2026-10-07
- **Status:** aprovada e implementada em 2026-10-07 (workspace `sp3-atlas`, commits `24ff8fdd` a `e3a12018`); validação em `docs/discovery/sp2-validacao.md`, seção "Adendo AWX"
- **Altera:** `2026-09-28-sp2-speckit-multirepo-design.md`, seções 1 (item 5), 2 (linhas "Specs" e "Constitution") e 5.4 (linha do AWX). Também `2026-10-05-sp3-grafo-e-navegacao-design.md`, seção 6.6, num ponto pequeno (skill `atlas-consultar`).
- **Workspace:** `C:\src\wms-workspace`, branch `sp3-atlas`, que já contém a `sp2-speckit`; nada foi publicado.

## 1. Motivo

O SP2 migrou o Spec Kit do AWX para a raiz do workspace (commit `b9f8effe6`, não publicado). Essa migração:
- tirou do AWX `.specify/`, as skills `speckit-*` e `specs/`;
- copiou as specs 001 a 003 para a raiz;
- moveu a constitution para `docs/constitution.md`;
- acrescentou notas de precedência no `CLAUDE.md` e no `AGENTS.md`.

Depois disso, o time do AWX continuou evoluindo o harness dele no caminho padrão. A partir de 01/10, pelo menos 4 branches abertas mexem em quatro arquivos:
- `.specify/memory/constitution.md`;
- `.claude/skills/qualidade-codigo/regras.md`;
- `CLAUDE.md`;
- `AGENTS.md`.

As branches são `HM/En-72566`, `gla/72535`, `JR/en/72554-status-embalado` e `AA/mover-sequencial-identificador-expedicao-b2b`. Publicar a migração geraria conflito com esse trabalho e tiraria do time uma ferramenta que ele usa.

## 2. Decisões do usuário (2026-10-07)

| Tema | Decisão |
|---|---|
| Spec Kit e constitution do AWX | Ficam no AWX, onde o time os mantém. O harness do AWX fica subordinado ao do workspace |
| Onde fica a spec de uma feature | Onde o trabalho começou. Uma feature iniciada no workspace, mesmo tocando só o AWX, fica em `specs/` na raiz. Quem trabalha direto no clone do AWX usa o Spec Kit do AWX |
| Identificação das features do workspace | Prefixo `ws-`: `specs/ws-NNN-nome/` e branch `ws-NNN-nome`, inclusive nos repos depois do `ws push`. O workspace começa em `ws-001` |
| Onde fica escrita a subordinação | Só no workspace (`AGENTS.md` da raiz, preset, constitution do workspace, skills). Nada muda nos arquivos do AWX e não há PR para o time dele |

## 3. Design

### 3.1 AWX volta a ser como o time mantém
- **Commit `b9f8effe6`:** desfeito na parte do AWX. Os caminhos `.specify/`, `.claude/skills/` (as `speckit-*` e a `qualidade-codigo`), `specs/`, `CLAUDE.md`, `AGENTS.md`, `docs/constitution.md` e `src/Integrations/AWX.IntegracaoLegadoWMS/AGENTS.md` ficam idênticos aos do commit do AWX sincronizado no workspace.
- **Resultado:** o diff do workspace contra o AWX fica vazio nesses caminhos. O `ws push` não leva nada disso, e o sync com o trabalho do time não gera conflito.
- **Trava do `ws push`** (adendo 4 à ADR 0001, spec SP2 5.5): fica como está. O workspace não altera `.specify/`, `specs/` nem as skills `speckit-*` de nenhum repo. O motivo passa a ser "não mexer no Spec Kit do time dono", e não mais "o Spec Kit saiu do repo".

### 3.2 Numeração `ws-NNN` no workspace
- **Formato:** spec em `specs/ws-NNN-<nome>/`, branch `ws-NNN-<nome>`, revisão `ws-NNN-<nome>-rK`.
- **Hook `ws-feature.sh`:**
  - **próximo número:** acima do maior `ws-NNN` entre as specs da base e as branches `ws-NNN-*` locais e do origin. Branches `NNN-*` sem prefixo, como as do AWX, não contam;
  - **citação de feature existente:**
    - `ws-004`, `specs/ws-004`, `ws-004-<nome>` e o nome da feature;
    - as formas explícitas que já existiam ("a 004", "feature 004", "spec 004", "#004" etc.), que no workspace sempre querem dizer a `ws-004`;
  - **número citado sem spec `ws-NNN` no base:** erro, como hoje.
- **Spec Kit do workspace:** o hook continua escolhendo o nome da feature (branch e pasta) e passando-o ao core do Spec Kit 1.0.12. Na primeira task, o plano confirma como o core aceita um nome com prefixo, por exemplo os scripts de feature e o `SPECIFY_FEATURE`. Se ele exigir `NNN-` no começo, o hook cria a pasta `specs/ws-NNN-<nome>/` e informa o caminho ao core.
- **Specs 001 a 003 na raiz:** as cópias saem e ficam só no AWX. O texto que citava esses números ou "próxima feature 004" é corrigido: `docs/workspace.md`, os testes e o `AGENTS.md`.

### 3.3 Subordinação escrita no workspace
Itens novos ou revistos no `AGENTS.md` da raiz:
- **Repo com Spec Kit próprio** (hoje só o AWX): ele é de quem trabalha no clone do repo. No workspace valem o fluxo e os `/speckit-*` da raiz.
- **Skills `speckit-*` dentro de `repos/`:** não são usadas no workspace, nem na forma qualificada (`/repos/<repo>:speckit-*`). O Claude Code carrega essas skills quando o agente trabalha nos arquivos do repo, e não há configuração para desligar isso.
- **Constitution de um repo:** vale para o código daquele repo. A do AWX fica em `repos/industria-logistica.wms.awx.monorepo/.specify/memory/constitution.md`.
  - O `plan` confere a constitution do workspace e a de cada repo afetado que tiver uma.
  - Num conflito entre as duas, o agente para e pergunta ao humano. É a regra que já existia para conflito entre uma regra de repo e a constitution.
- **Specs de um repo** (`repos/<r>/specs/`): o workspace lê como referência de negócio e nunca as altera. Uma feature do workspace pode citá-las.
- **Instrução de repo que descreve o fluxo dele:** a regra que já existia continua. No workspace, vale o fluxo da raiz.

Outros textos:
- **Preset `multirepo`:** o "Constitution Check" do template de plan ganha uma linha por repo afetado que tem constitution própria.
- **Constitution do workspace:** uma frase sobre a precedência. Ela vale para o que cruza repos, e a do repo vale dentro dele.
- **Skill `atlas-consultar`:** uma linha dizendo que as specs do AWX ficam em `repos/…awx…/specs/` e servem de referência de negócio.
- **Atlas:** o código não muda, porque `.specify/` e `specs/` já são ignorados pela política de atualização.

### 3.4 Repos sem mudança
O Fly (`CLAUDE.md`, `.claude/agents`, `.claude/rules`) e o servidor.backend (`AGENTS.md`) ficam como estão. A subordinação deles já está coberta pelas regras gerais do `AGENTS.md` da raiz.

## 4. Histórico das branches
- Não reescrevo os 36 commits da `sp3-atlas`. Entram commits novos, nesta ordem:
  1. reverter a parte do AWX do `b9f8effe6`, conferindo contra o commit do AWX sincronizado (`af11d6b`);
  2. tirar as cópias 001 a 003 da raiz e corrigir quem as cita;
  3. numeração `ws-NNN` no hook, com testes;
  4. regras de subordinação: `AGENTS.md`, preset, constitution e skills.
- Se o usuário preferir, o PR pode ser mergeado com squash.

## 5. Testes e validação

### 5.1 Testes automáticos (TDD, runner `tools/ws/tests/run.sh`, um arquivo por vez)
- **Hook:**
  - feature nova vira `ws-001-…`;
  - o próximo número ignora branches `NNN-*` sem prefixo;
  - as citações `ws-004`, "a 004" e `specs/ws-004` levam à revisão `ws-004-…-r1`;
  - número sem spec dá erro;
  - os testes que existiam são adaptados ao formato novo.
- **Harness do AWX:** os caminhos da seção 3.1 são iguais aos do commit sincronizado (`git diff --quiet <split> -- …` sobre a árvore do subtree).
- **Preset:** o template de plan tem a linha da constitution por repo.
- **Suíte completa:** sem falhas.

### 5.2 Ponta a ponta (ambiente descartável `e2e3`, AWX num espelho local)
1. **Qual `/speckit-specify` roda.**
   - Numa sessão aberta na raiz, com as skills do AWX presentes, o comando sem qualificação precisa rodar o da raiz: o hook `ws start` dispara e a spec sai em `specs/ws-001-…`.
   - As skills do AWX só aparecem na forma qualificada.
2. **Feature que toca o AWX.**
   - O plan confere a constitution do workspace e a do AWX.
   - O agente não usa as skills `speckit-*` do AWX.
   - O `.specify/` e o `specs/` do AWX ficam intactos.
   - O `ws push` leva `ws-001-…` para o espelho do AWX.
   - Rodado no espelho, o Spec Kit do AWX numera a próxima feature dele como `004` e ignora a `ws-001`.

### 5.3 Se o item 5.2.1 falhar
Se o comando sem qualificação rodar o do AWX, a validação para e o resultado vai para o usuário. Mitigação proposta: o workspace passa a expor o fluxo por comandos que não colidem (os da extensão `ws`, por exemplo), e o `AGENTS.md` manda usá-los.

## 6. Riscos
- **Instruções do AWX.** O `CLAUDE.md` e o `AGENTS.md` do AWX descrevem o fluxo do Spec Kit dele e não dizem nada sobre o workspace. Quem resolve é a regra da raiz, que é carregada primeiro e é explícita. Se o ponta a ponta mostrar o agente seguindo o fluxo do AWX, a alternativa C da conversa (nota curta no AWX, combinada com o time) volta à mesa.
- **Número citado sem prefixo.** "A 004" no workspace quer dizer `ws-004`. Uma spec do AWX só é citada pelo caminho dela.
