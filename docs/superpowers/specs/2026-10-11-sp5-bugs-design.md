# SP5: Vertente de bugs e incidentes do harness do workspace WMS (design)

Data: 2026-10-11. Processo: `superpowers:brainstorming`, caminho arquitetural. Decisões tomadas com o usuário na conversa de 2026-10-09 a 2026-10-11.

## 1. Objetivo e critério de sucesso

Dar ao dev do workspace `industria-logistica.wms.workspace` um fluxo para dois casos:
- **bug reportado:** work item do Azure DevOps ou chamado com um comportamento errado;
- **erro em produção ou incidente:** exceção, fila parada, job falhando, dado inconsistente.

O fluxo usa os comandos oficiais de bug do Spec Kit e roda nos trilhos do workspace: branch criada pelo `ws start`, Atlas, envio pelo `ws push` e regra de contratos da constitution.

**Fora do escopo:** o erro que aparece durante o desenvolvimento de uma feature (build ou teste quebrando). Ele continua no fluxo de feature do Spec Kit.

**Sucesso:**
- os quatro casos da validação de ponta a ponta (seção 8.3) passam num workspace descartável;
- a suíte do `tools/ws/tests` continua 100% verde, com testes novos para a instalação, os comandos de branch e envio e as referências da doc.

## 2. Decisões tomadas com o usuário

| Decisão | Valor |
|---|---|
| Casos cobertos | Bug reportado e erro em produção ou incidente |
| Evidência do diagnóstico | O que o dev cola: texto do work item, stack trace, log, print. **Opcionalmente**, SELECT no banco (seção 5.4) |
| Ferramentas externas de debug | Nenhuma. Ficam fora: o método do superpowers (`systematic-debugging`), o formato de bugfix do Kiro, o plugin do Sentry, o MCP do Azure DevOps, o `dotnet-diag` e as coleções da comunidade |
| Base do fluxo | **Componentes oficiais de bug do Spec Kit**, usados como vêm: extensão `bug` (`speckit.bug.assess`, `speckit.bug.fix`, `speckit.bug.test`) e workflow `bugfix`. Instalados separadamente, porque o bundle `bugfix` falha nas versões publicadas (seção 3) |
| Rota para o `/speckit-specify` e spec viva | Fora. Ficam para quando o usuário tratar a documentação das features existentes como specs |
| Onde ficam os relatórios | Pasta própria na raiz, `bugs/<slug>/`, e não `.specify/bugs/<slug>/` |
| Slug | `<id do work item>-<descrição-curta>`; incidente sem work item: `inc-<AAAAMMDD>-<descrição-curta>` |
| Branch | `hotfix/<slug>`, no workspace e nos repos |
| Branch e envio | Três comandos mecânicos na extensão `ws`, chamados pelo preset `bugs` antes e depois dos comandos oficiais (seção 4.3). A extensão `bug` publicada não tem hooks. **Lembrete:** revisar quando o Spec Kit lançar a extensão `bug` 1.0.1 (seção 10) |
| Contrato num bug | A regra II da constitution passa a valer para bug: a lista de consumidores vai numa seção "Impacto" do `assessment.md` |
| Sem correção de código | O relatório vai sempre para o `main`, pelo PR do workspace. Um comando da `ws` oferece o commit e o push (decisão assumida e apresentada ao usuário, sem contestação) |
| Validação | Ponta a ponta num workspace descartável. Sem gabarito de bugs reais e sem piloto com dev |
| Entrega | Branch própria no workspace, mergeada só depois que o piloto do SP4 terminar |

## 3. Pesquisa que embasou a decisão

O Spec Kit tem um caminho oficial para bug, mantido pelo projeto e incluído no pacote:

- **Extensão `bug` v1.0.1** (`speckit_version >=0.9.0`).
  - Três comandos gravam um relatório cada em `.specify/bugs/<slug>/`: `assessment.md`, `fix.md` e `test.md`.
  - O `assess` e o `test` não alteram código.
  - O `test` registra `partial` ou `not-run` quando a verificação não foi feita de fato, e nunca `verified`.
  - Na versão 1.0.1, que está no `main` do Spec Kit e **ainda não foi lançada**, a extensão dispara os hooks `before_`/`after_` de `bug_assess`, `bug_fix` e `bug_test`. As versões publicadas do Spec Kit (1.0.12 e 1.0.13, testadas em 2026-10-11) trazem a extensão `bug` 1.0.0, **sem hooks**.
  - O caminho `.specify/bugs/` está escrito no texto dos três comandos. Não há configuração para mudá-lo.
- **Workflow `bugfix` v1.0.0:** assess, aprovação humana, fix e test.
- **Bundle `bugfix`:** desde a 1.0.9, deveria instalar a extensão e o workflow de uma vez (`specify bundle add bugfix`). Nas versões 1.0.12 e 1.0.13 ele **falha**: `Extension 'bug' is pinned to version 1.0.1 in the bundle manifest, but the resolved version is 1.0.0`. Já `specify extension add bug` e `specify workflow add bugfix` funcionam (testado em 2026-10-11).
- **Presets** podem sobrescrever comandos com as estratégias `replace`, `prepend`, `append` ou `wrap`. **Testado em 2026-10-11 com o 1.0.12:** um preset com `prepend` em `speckit.bug.assess` gera a skill `speckit-bug-assess` com o preâmbulo antes do texto oficial. O preset troca a `description` da skill pela dele.

Fontes: https://github.com/github/spec-kit/tree/main/extensions/bug, https://github.com/github/spec-kit/blob/main/bundles/bugfix/README.md, https://raw.githubusercontent.com/github/spec-kit/main/workflows/bugfix/workflow.yml, https://github.com/github/spec-kit/pull/4504, https://raw.githubusercontent.com/github/spec-kit/main/presets/README.md.

Fato da máquina de discovery: o `specify` instalado é o 1.0.6, mas o `init-options.json` do workspace registra o 1.0.12.

## 4. Componentes

```
.specify/extensions/bug/            extensão oficial, sem alteração
.specify/workflows/bugfix/          workflow oficial, sem alteração
.specify/presets/bugs/              preset novo: prepend nos três comandos speckit.bug.* e append no assess e no test
.specify/extensions/ws/             três comandos novos (bug-start, bug-sem-correcao, bug-enviar)
.specify/memory/constitution.md     versão 1.2.0, regra II emendada
AGENTS.md                           seção "Bugs com o Spec Kit"
bugs/<slug>/                        relatórios de cada bug (fora do harness)
```

### 4.1 Extensão `bug` e workflow `bugfix` oficiais
- Instalados pelo `ws speckit` com `specify extension add bug` e `specify workflow add bugfix`, e versionados no workspace como o resto do Spec Kit.
- Nenhum arquivo dele é editado.
- Os textos dos comandos ficam em inglês; o agente responde em português do Brasil por causa do `AGENTS.md`.
- O workflow `bugfix` fica instalado, mas não é documentado para o dev. O fluxo documentado são as três skills no Claude Code.

### 4.2 Preset `bugs`
- É um preset novo, separado do `multirepo`, com fonte em `tools/speckit/bugs/`, instalado pelo `ws speckit`.
- **`prepend` nos três comandos** `speckit.bug.assess`, `speckit.bug.fix` e `speckit.bug.test`, com duas regras de armazenamento:
  - onde o comando diz `.specify/bugs/`, use `bugs/`. Isso vale para a criação da pasta, a leitura, a escrita e a busca do slug no disco (`bugs/*/assessment.md`, `bugs/*/fix.md`);
  - o slug segue a convenção da seção 2: o id do work item, quando o relato traz um, e `inc-<AAAAMMDD>-` quando não traz.
- **O `prepend` do `assess`** também manda, depois de definir o slug e antes de qualquer outro passo, seguir `/speckit-ws-bug-start` com o slug.
- **`append` no `assess`:** depois de gravar o `assessment.md`, seguir `/speckit-ws-bug-sem-correcao`.
- **`append` no `test`:** depois de gravar o `test.md`, seguir `/speckit-ws-bug-enviar`.
- O texto oficial fica intacto entre o `prepend` e o `append`. O preset só diz onde gravar e o que chamar antes e depois; a lógica fica na `ws`.
- Cada comando do preset traz uma `description` em português, porque ela substitui a da skill.
- `requires.speckit_version` igual ao do `multirepo` (`>=1.0.12`).

### 4.3 Comandos de branch e envio na extensão `ws`

| Chamado por | Comando novo | Faz |
|---|---|---|
| `prepend` do `assess` | `speckit.ws.bug-start` | Roda `tools/ws/ws start hotfix/<slug>`. A branch sai do `main` atualizado, mesmo que o dev esteja em outra, e o Atlas dos repos que mudaram é atualizado. Se falhar, mostra o erro e **para** o `assess` |
| `append` do `assess` | `speckit.ws.bug-sem-correcao` | Se o veredito não pede correção de código (não é bug, duplicado, corrigido fora do código), oferece o commit `docs(<slug>): diagnóstico sem correção de código` e o `git push` só da branch do workspace. Se pede correção, só lembra o próximo passo: ler o `assessment.md` e rodar `/speckit-bug-fix` |
| `append` do `test` | `speckit.ws.bug-enviar` | Atualiza o Atlas dos repos tocados, como o `speckit.ws.converge`, e oferece o commit `fix(<slug>): <título>` e o `ws push` pelo `ws-commit-push.sh` existente. Confirmação humana antes do commit. Se o `test.md` registra falha, não oferece o envio e recomenda rodar o `fix` de novo; com `partial` ou `not-run`, mostra o motivo e deixa o dev decidir |

- Os três comandos também viram skills (`/speckit-ws-bug-start` etc.) e podem ser rodados à mão.
- O nome `hotfix/<slug>` passa no `git check-ref-format --branch` que o `ws start` já faz.
- O `ws-commit-push.sh` já recusa o `main` e aceita a mensagem como argumento, então não precisa mudar.
- O commit sem correção não usa o `ws push`, porque nenhum repo mudou. O `git push` da branch do workspace é permitido pela regra 5 do `AGENTS.md`, que só proíbe `git push` para os repos.

### 4.4 Regras
- **Constitution 1.2.0, regra II, frase nova:** "Num bug, a lista vai numa seção Impacto do `assessment.md`."
- **`AGENTS.md`, seção nova "Bugs com o Spec Kit"**, nos moldes da de features:
  - os três comandos e a ordem: o dev lê o `assessment.md` antes do `fix`;
  - os relatórios ficam em `bugs/<slug>/`, que **não é harness**: o agente cria e altera a pasta durante o trabalho;
  - a branch é `hotfix/<slug>`, criada pelo `/speckit-ws-bug-start` no início do `assess`; nunca à mão;
  - a seção Impacto, com base no índice de impacto do Atlas, quando a correção muda um contrato;
  - o SELECT opcional (seção 5.4).

## 5. Fluxo do dev

### 5.1 Com correção de código
1. Na raiz do workspace, no Claude Code: `/speckit-bug-assess <relato>`. O dev cola o texto do work item ou do incidente e as evidências, e informa o id do work item se houver. O preset define o slug.
2. O preset chama o `/speckit-ws-bug-start`, que cria a branch `hotfix/<slug>`.
3. Diagnóstico, só leitura: o relato, o código, o Atlas (regra 7 do `AGENTS.md`) e, se for o caso, o SELECT opcional. O resultado vai para `bugs/<slug>/assessment.md`, com a seção Impacto quando a correção muda um contrato.
4. O dev lê o `assessment.md` e corrige ou aprova. É a aprovação humana; não há comando para ela.
5. `/speckit-bug-fix`: aplica a correção, limitada ao que a avaliação propôs, e grava o `fix.md`.
6. `/speckit-bug-test`: roda o build e os testes do repo (regra 6 do `AGENTS.md`) e grava o `test.md`.
7. O preset chama o `/speckit-ws-bug-enviar`, que atualiza o Atlas e oferece o commit `fix(<slug>): …` e o `ws push`.
8. O dev abre um PR por repo enviado e, com todos mergeados, o PR do workspace (`bugs/<slug>/` e o Atlas).

### 5.2 Sem correção de código
Passos 1 a 3 iguais. O preset chama o `/speckit-ws-bug-sem-correcao`, que oferece o commit `docs(<slug>): …` e o push da branch do workspace. O dev abre o PR do workspace, e o fluxo termina aí.

### 5.3 Saídas

| Onde | O quê |
|---|---|
| `bugs/<slug>/` | `assessment.md` sempre; `fix.md` e `test.md` quando houve correção |
| Workspace | branch `hotfix/<slug>` com um commit `docs(...)` ou `fix(...)` |
| Repos tocados | branch `hotfix/<slug>`, criada pelo `ws push` |
| `docs/atlas/` | atualização dos repos tocados, só quando há correção |

Casos de borda, todos do comportamento oficial:
- **Slug já existe:** o comando pergunta antes de sobrescrever. Uma nova tentativa vira `<slug>-2`.
- **Teste falhou:** rodar o `fix` de novo, que pergunta antes de sobrescrever o `fix.md`.
- **Sessão nova:** o comando resolve o slug pelo disco.

### 5.4 SELECT opcional
- O harness não fornece credencial nem pede acesso ao DBA.
- **Se o dev já tem acesso a um banco na máquina dele:** o agente pode rodar só `SELECT`. Antes, mostra a consulta e espera a confirmação do dev.
- **Se o dev não tem acesso:** o agente escreve a consulta, e o dev roda e cola o resultado.
- Os valores sensíveis do resultado não vão para o `assessment.md` (regra V da constitution).

## 6. Documentação nas camadas

| Onde | O que muda |
|---|---|
| `README.md` | Uma frase na abertura sobre os comandos de bug. Uma linha nova na tabela "Quero…": "corrigir um bug ou investigar um incidente", apontando para a camada 1 |
| Camada 1, `1-comecar.md` | Seção nova "Um bug, do relato ao PR", depois da de feature: os passos da seção 5 em formato curto e o que colar no relato. As "Três regras" não mudam |
| Camada 2, `2-quando-da-errado.md` | Grupo novo "Comandos de bug e `hotfix/`": a branch `hotfix/<slug>` já existe; o slug já existe e o comando pede para sobrescrever; numa sessão nova, o comando não acha o bug; o `test` deu `not-run` ou `partial`; o agente quer rodar SELECT e o dev não tem acesso. Os erros do envio usam as entradas existentes do `ws push` |
| Camada 3, `3-alem-do-basico.md` | Três seções: "Investigar sem corrigir", "Evidência do banco" e "Bug que muda contrato" |
| Camada 4, `4-manter.md` | "Como as peças se ligam" e "Onde fica cada coisa" ganham a extensão `bug`, o workflow `bugfix`, o preset `bugs`, os três comandos da `ws` e `bugs/`. "Atualizar o Spec Kit" ganha dois passos: conferir se os comandos `speckit.bug.*` ainda usam `.specify/bugs/`, porque o preâmbulo depende disso; e conferir se a extensão `bug` instalada já é a 1.0.1 ou mais nova, o gatilho do lembrete da seção 10 |
| `AGENTS.md` e constitution | Seção 4.4 |

O `tools/ws/tests/test_docs_referencias.sh` precisa passar e cobrir as entradas novas. O deck da apresentação do SP4 não muda.

## 7. O que fica fora
- Ferramentas externas de debug (seção 2).
- Rota para o `/speckit-specify`, spec viva e documentação das features existentes como specs.
- Validação com bugs reais e piloto com dev.
- Apresentação da vertente ao time.

## 8. Validação e entrega

### 8.1 PoC (primeiro passo do plano, num workspace descartável)

| # | O que confirmar | Critério |
|---|---|---|
| 1 | O preset consegue fazer `prepend` em comando de extensão | **confirmado em 2026-10-11** (seção 3); o plano só reconfirma com o preset real, incluindo o `append` |
| 2 | O agente obedece ao redirecionamento | o `assess` grava em `bugs/<slug>/`, com o slug na convenção, e nada vai para `.specify/bugs/` |
| 3 | Uma sessão nova acha o bug | o `fix` numa sessão limpa resolve o slug por `bugs/*/assessment.md` |
| 4 | O agente segue as chamadas do preset | o `assess` roda o `/speckit-ws-bug-start` antes de criar a pasta e o `/speckit-ws-bug-sem-correcao` no fim; o `test` roda o `/speckit-ws-bug-enviar` no fim |

Se algum item falhar, a execução para e volta ao usuário com as saídas: sobrescrever os comandos inteiros (`replace`) ou aceitar `.specify/bugs/`. Nenhum contorno é feito sem decisão.

### 8.2 Testes automatizados (`tools/ws/tests`)
- **Instalação:** a extensão `bug`, o workflow `bugfix` e o preset estão no workspace; as skills `speckit-bug-*` trazem o `prepend` e o `append`; as skills `speckit-ws-bug-*` existem.
- **Branch e envio:** a branch `hotfix/<slug>`; a recusa no `main`; o commit `fix(...)` e o `docs(...)`; o push só do workspace quando não há correção.
- **Docs:** o `test_docs_referencias.sh` cobre as entradas novas.

### 8.3 Ponta a ponta (workspace descartável, origem e repos de teste locais)

| Caso | Esperado |
|---|---|
| Bug com correção em 1 repo | branch `hotfix/<slug>` no workspace e no repo; os três relatórios; Atlas atualizado; `ws push` ok |
| Não é bug | só o `assessment.md`; commit `docs(...)`; push só do workspace, sem `ws push` |
| Bug que muda contrato | seção Impacto preenchida a partir do índice do Atlas |
| Sessão nova no meio | o `fix` e o `test` acham o bug pelo disco |

O resultado fica registrado em `docs/discovery/sp5-bugs-validacao.md`, na pasta de discovery.

### 8.4 Entrega
- Branch própria no workspace, saindo do `main`: `harness/bugs`.
- Merge só depois que o piloto do SP4 terminar. O PR leva a emenda da constitution, que exige aprovação humana.
- Ordem: primeiro a branch dos ajustes do piloto do SP4, depois esta, rebaseada. Os conflitos nas camadas ficam do lado do harness, não do dev.
- Os ambientes descartáveis do PoC e da validação ficam listados para o usuário apagar.
- O `docs/discovery/estado-da-sessao.md` ganha o SP5.

## 9. Riscos

| Risco | Mitigação |
|---|---|
| O agente pula as chamadas do preset (branch ou envio) | PoC 8.1, item 4; casos de ponta a ponta |
| O agente ignora o preâmbulo em parte dos passos e grava em `.specify/bugs/` | PoC 8.1, itens 2 e 3; caso de ponta a ponta "sessão nova" |
| Uma atualização do Spec Kit muda o caminho no texto oficial | Passo na camada 4, "Atualizar o Spec Kit" |
| O dev pula a leitura do `assessment.md` e roda o `fix` direto | A camada 1 destaca a leitura como passo próprio. O `fix` já limita a correção ao que a avaliação propôs |
| Um bug que muda contrato passa sem a seção Impacto | Regra no `AGENTS.md` e na constitution; caso de ponta a ponta "bug que muda contrato" |

## 10. Lembrete: revisar quando a extensão `bug` 1.0.1 for lançada

**Resolvido no SP6 (2026-10-16):** o Spec Kit 1.2.0 traz a extensão `bug` 1.0.1 com hooks. A extensão `ws` 1.3.0 registra `before_bug_assess`, `after_bug_assess` e `after_bug_test`, e o preset `bugs` ficou só com o caminho e o slug. O bundle `bugfix` funciona, mas não foi adotado: ele baixa o manifesto do `main` do Spec Kit e recusa reinstalar com outra versão registrada (ver `docs/superpowers/specs/2026-10-16-sp6-refactor-design.md`, seção 5.1, e `docs/discovery/sp6-refactor-validacao.md`).

Decisão do usuário em 2026-10-11: as chamadas pelo preset são provisórias e devem ser revistas no futuro.

- **Gatilho:** uma versão publicada do Spec Kit que traga a extensão `bug` 1.0.1 ou mais nova, com hooks, ou em que o `specify bundle add bugfix` funcione.
- **O que revisar:** trocar as chamadas do preset por hooks nativos (`before_bug_assess`, `after_bug_assess`, `after_bug_test`) registrados no `extension.yml` da `ws`; avaliar instalar pelo bundle; deixar o preset só com o caminho e o slug.
- **Onde o lembrete fica registrado:** nesta seção, no passo "Atualizar o Spec Kit" da camada 4 e no `docs/discovery/estado-da-sessao.md`.
