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
- a suíte do `tools/ws/tests` continua 100% verde, com testes novos para a instalação, os hooks e as referências da doc.

## 2. Decisões tomadas com o usuário

| Decisão | Valor |
|---|---|
| Casos cobertos | Bug reportado e erro em produção ou incidente |
| Evidência do diagnóstico | O que o dev cola: texto do work item, stack trace, log, print. **Opcionalmente**, SELECT no banco (seção 5.4) |
| Ferramentas externas de debug | Nenhuma. Ficam fora: o método do superpowers (`systematic-debugging`), o formato de bugfix do Kiro, o plugin do Sentry, o MCP do Azure DevOps, o `dotnet-diag` e as coleções da comunidade |
| Base do fluxo | **Bundle oficial `bugfix` do Spec Kit**, usado como vem: extensão `bug` (`speckit.bug.assess`, `speckit.bug.fix`, `speckit.bug.test`) e workflow `bugfix` |
| Rota para o `/speckit-specify` e spec viva | Fora. Ficam para quando o usuário tratar a documentação das features existentes como specs |
| Onde ficam os relatórios | Pasta própria na raiz, `bugs/<slug>/`, e não `.specify/bugs/<slug>/` |
| Slug | `<id do work item>-<descrição-curta>`; incidente sem work item: `inc-<AAAAMMDD>-<descrição-curta>` |
| Branch | `hotfix/<slug>`, no workspace e nos repos |
| Branch e envio | Hooks mecânicos na extensão `ws` (seção 4.3) |
| Contrato num bug | A regra II da constitution passa a valer para bug: a lista de consumidores vai numa seção "Impacto" do `assessment.md` |
| Sem correção de código | O relatório vai sempre para o `main`, pelo PR do workspace. Um hook oferece o commit e o push (decisão assumida e apresentada ao usuário, sem contestação) |
| Validação | Ponta a ponta num workspace descartável. Sem gabarito de bugs reais e sem piloto com dev |
| Entrega | Branch própria no workspace, mergeada só depois que o piloto do SP4 terminar |

## 3. Pesquisa que embasou a decisão

O Spec Kit tem um caminho oficial para bug, mantido pelo projeto e incluído no pacote:

- **Extensão `bug` v1.0.1** (`speckit_version >=0.9.0`).
  - Três comandos gravam um relatório cada em `.specify/bugs/<slug>/`: `assessment.md`, `fix.md` e `test.md`.
  - O `assess` e o `test` não alteram código.
  - O `test` registra `partial` ou `not-run` quando a verificação não foi feita de fato, e nunca `verified`.
  - A extensão dispara os hooks `before_`/`after_` de `bug_assess`, `bug_fix` e `bug_test`. Eles rodam na mesma sessão e reaproveitam `BUG_SLUG` e `BUG_DIR` da conversa.
  - O caminho `.specify/bugs/` está escrito no texto dos três comandos. Não há configuração para mudá-lo.
- **Workflow `bugfix` v1.0.0:** assess, aprovação humana, fix e test.
- **Bundle `bugfix`:** desde a 1.0.9, instala a extensão e o workflow de uma vez (`specify bundle add bugfix`).
- **Presets** podem sobrescrever comandos com as estratégias `replace`, `prepend`, `append` ou `wrap`. A doc não diz explicitamente se isso vale para comandos de extensão, além dos do core (seção 8.1).

Fontes: https://github.com/github/spec-kit/tree/main/extensions/bug, https://github.com/github/spec-kit/blob/main/bundles/bugfix/README.md, https://raw.githubusercontent.com/github/spec-kit/main/workflows/bugfix/workflow.yml, https://github.com/github/spec-kit/pull/4504, https://raw.githubusercontent.com/github/spec-kit/main/presets/README.md.

Fato da máquina de discovery: o `specify` instalado é o 1.0.6, mas o `init-options.json` do workspace registra o 1.0.12.

## 4. Componentes

```
.specify/extensions/bug/            extensão oficial (via bundle), sem alteração
.specify/workflows/bugfix/          workflow oficial (via bundle), sem alteração
.specify/presets/bugs/              preset novo: preâmbulo nos três comandos speckit.bug.*
.specify/extensions/ws/             três comandos de hook novos e o registro no extension.yml
.specify/extensions.yml             três hooks novos
.specify/memory/constitution.md     versão 1.2.0, regra II emendada
AGENTS.md                           seção "Bugs com o Spec Kit"
bugs/<slug>/                        relatórios de cada bug (fora do harness)
```

### 4.1 Bundle oficial `bugfix`
- Instalado com `specify bundle add bugfix`, pelo CLI 1.0.9 ou mais novo, e versionado no workspace.
- Nenhum arquivo dele é editado.
- Os textos dos comandos ficam em inglês; o agente responde em português do Brasil por causa do `AGENTS.md`.
- O workflow `bugfix` fica instalado, mas não é documentado para o dev. O fluxo documentado são as três skills no Claude Code.

### 4.2 Preset `bugs`
- É um preset novo, separado do `multirepo`.
- Usa a estratégia `prepend` nos comandos `speckit.bug.assess`, `speckit.bug.fix` e `speckit.bug.test`.
- O preâmbulo, curto e igual nos três, diz só isto:
  - onde o comando diz `.specify/bugs/`, use `bugs/`. Isso vale para a criação da pasta, a leitura, a escrita e a busca do slug no disco (`bugs/*/assessment.md`, `bugs/*/fix.md`);
  - o slug segue a convenção da seção 2: o id do work item, quando o relato traz um, e `inc-<AAAAMMDD>-` quando não traz.
- O texto oficial fica intacto por baixo.
- `requires.speckit_version` igual ao do `multirepo` (`>=1.0.12`).

### 4.3 Hooks na extensão `ws`

| Hook | Comando novo | Faz | Obrigatório |
|---|---|---|---|
| `before_bug_assess` | `speckit.ws.bug-start` | Roda `tools/ws/ws start hotfix/<slug>`. A branch sai do `main` atualizado, mesmo que o dev esteja em outra, e o Atlas dos repos que mudaram é atualizado | sim |
| `after_bug_assess` | `speckit.ws.bug-sem-correcao` | Se o veredito não pede correção de código (não é bug, duplicado, corrigido fora do código), oferece o commit `docs(<slug>): diagnóstico sem correção de código` e o `git push` só da branch do workspace. Se pede correção, não faz nada | sim |
| `after_bug_test` | `speckit.ws.bug-enviar` | Atualiza o Atlas dos repos tocados, como o `speckit.ws.converge`, e oferece o commit `fix(<slug>): <título>` e o `ws push` pelo `ws-commit-push.sh` existente. Confirmação humana antes do commit. Se o `test.md` registra falha, não oferece o envio e recomenda rodar o `fix` de novo; com `partial` ou `not-run`, mostra o motivo e deixa o dev decidir | sim |

- O nome `hotfix/<slug>` passa no `git check-ref-format --branch` que o `ws start` já faz.
- O `ws-commit-push.sh` já recusa o `main` e aceita a mensagem como argumento, então não precisa mudar.
- O commit sem correção não usa o `ws push`, porque nenhum repo mudou. O `git push` da branch do workspace é permitido pela regra 5 do `AGENTS.md`, que só proíbe `git push` para os repos.

### 4.4 Regras
- **Constitution 1.2.0, regra II, frase nova:** "Num bug, a lista vai numa seção Impacto do `assessment.md`."
- **`AGENTS.md`, seção nova "Bugs com o Spec Kit"**, nos moldes da de features:
  - os três comandos e a ordem: o dev lê o `assessment.md` antes do `fix`;
  - os relatórios ficam em `bugs/<slug>/`, que **não é harness**: o agente cria e altera a pasta durante o trabalho;
  - a branch é `hotfix/<slug>`, criada pelo hook; nunca à mão;
  - a seção Impacto, com base no índice de impacto do Atlas, quando a correção muda um contrato;
  - o SELECT opcional (seção 5.4).

## 5. Fluxo do dev

### 5.1 Com correção de código
1. Na raiz do workspace, no Claude Code: `/speckit-bug-assess <relato>`. O dev cola o texto do work item ou do incidente e as evidências, e informa o id do work item se houver. O preset define o slug.
2. O hook `before_bug_assess` cria a branch `hotfix/<slug>`.
3. Diagnóstico, só leitura: o relato, o código, o Atlas (regra 7 do `AGENTS.md`) e, se for o caso, o SELECT opcional. O resultado vai para `bugs/<slug>/assessment.md`, com a seção Impacto quando a correção muda um contrato.
4. O dev lê o `assessment.md` e corrige ou aprova. É a aprovação humana; não há comando para ela.
5. `/speckit-bug-fix`: aplica a correção, limitada ao que a avaliação propôs, e grava o `fix.md`.
6. `/speckit-bug-test`: roda o build e os testes do repo (regra 6 do `AGENTS.md`) e grava o `test.md`.
7. O hook `after_bug_test` atualiza o Atlas e oferece o commit `fix(<slug>): …` e o `ws push`.
8. O dev abre um PR por repo enviado e, com todos mergeados, o PR do workspace (`bugs/<slug>/` e o Atlas).

### 5.2 Sem correção de código
Passos 1 a 3 iguais. O hook `after_bug_assess` oferece o commit `docs(<slug>): …` e o push da branch do workspace. O dev abre o PR do workspace, e o fluxo termina aí.

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
| Camada 4, `4-manter.md` | "Como as peças se ligam" e "Onde fica cada coisa" ganham o bundle, o preset `bugs`, os três hooks e `bugs/`. "Atualizar o Spec Kit" ganha um passo: conferir se os comandos `speckit.bug.*` ainda usam `.specify/bugs/`, porque o preâmbulo depende disso. O CLI precisa ser 1.0.9 ou mais novo, e isso vale só para quem mantém o harness |
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
| 1 | O preset consegue fazer `prepend` em comando de extensão | as skills `speckit-bug-*` instaladas trazem o preâmbulo antes do texto oficial |
| 2 | O agente obedece ao redirecionamento | o `assess` grava em `bugs/<slug>/`, com o slug na convenção, e nada vai para `.specify/bugs/` |
| 3 | Uma sessão nova acha o bug | o `fix` numa sessão limpa resolve o slug por `bugs/*/assessment.md` |
| 4 | A pasta criada antes do hook não atrapalha | o `ws start hotfix/<slug>` roda sem erro depois que o `assess` criou a pasta |

Se algum item falhar, a execução para e volta ao usuário com as saídas: sobrescrever os comandos inteiros (`replace`) ou aceitar `.specify/bugs/`. Nenhum contorno é feito sem decisão.

### 8.2 Testes automatizados (`tools/ws/tests`)
- **Instalação:** o bundle e o preset estão no workspace; as skills `speckit-bug-*` trazem o preâmbulo; o `extensions.yml` tem os três hooks.
- **Hooks:** a branch `hotfix/<slug>`; a recusa no `main`; o commit `fix(...)` e o `docs(...)`; o push só do workspace quando não há correção.
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
| O preset não sobrescreve comando de extensão | PoC 8.1, item 1, antes de qualquer outra tarefa |
| O agente ignora o preâmbulo em parte dos passos e grava em `.specify/bugs/` | PoC 8.1, itens 2 e 3; caso de ponta a ponta "sessão nova" |
| Uma atualização do Spec Kit muda o caminho no texto oficial | Passo na camada 4, "Atualizar o Spec Kit" |
| O dev pula a leitura do `assessment.md` e roda o `fix` direto | A camada 1 destaca a leitura como passo próprio. O `fix` já limita a correção ao que a avaliação propôs |
| Um bug que muda contrato passa sem a seção Impacto | Regra no `AGENTS.md` e na constitution; caso de ponta a ponta "bug que muda contrato" |
