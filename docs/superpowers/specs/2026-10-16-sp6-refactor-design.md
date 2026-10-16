# SP6: Vertente de refactor do harness do workspace WMS (design)

Data: 2026-10-16. Processo: `superpowers:brainstorming`, caminho arquitetural. Decisões tomadas com o usuário na conversa de 2026-10-15 e 2026-10-16. O antigo "SP6" (portões de repos da feature) foi descartado pelo usuário em 2026-10-15; este é o SP6.

## 1. Objetivo e critério de sucesso

O time faz quatro tipos de refactor que não são feature nem bug:
1. **interno:** dentro de um projeto, num repo;
2. **entre projetos ou repos:** mover código, extrair, mudar fronteiras;
3. **desacoplamento:** tirar a dependência do WMS no banco `Reserva` do LINX e passá-la para os serviços de integração (AWX ERP Connector e Serviços Integração LINX WMS);
4. **migração do legado para o AWX.**

O SP6 cobre o **tipo 3** e o **tipo 1**, nessa ordem de prioridade. Os tipos 2 e 4 ficam para um **SP7**.

Hoje um refactor não tem caminho no workspace. O `AGENTS.md` só conhece feature, bug e o fluxo manual. O fluxo de feature exige user stories e para com "Cannot determine user scenarios". O fluxo de bug é feito para corrigir um defeito.

O SP6 dá ao dev:
- um fluxo de refactor nos trilhos do workspace: branch pelo `ws start`, Atlas, envio pelo `ws push` e regras da constitution;
- **uma entrega de código por fatia**, com a **prova de que o comportamento não mudou**;
- no desacoplamento, **marcos em produção** que podem ficar meses separados da entrega do código.

O SP6 também atualiza o Spec Kit do workspace para a 1.2.0 e faz a revisão do SP5 que estava no lembrete da seção 10 da spec dele.

**Sucesso:**
- os casos de ponta a ponta da seção 10.3 passam num workspace descartável;
- a suíte do `tools/ws/tests` continua 100% verde, com testes novos para a instalação, os comandos de branch e envio, o `ws refactor pendentes`, o aviso do `ws start` e as referências da doc;
- o fluxo de bug do SP5 continua funcionando depois da atualização do Spec Kit.

## 2. Decisões tomadas com o usuário

| Decisão | Valor |
|---|---|
| Escopo | Tipos 3 (desacoplamento) e 1 (interno). Tipos 2 e 4 no SP7 |
| Unidade do desacoplamento | A **fatia**: um consumidor deixa de acessar um objeto do `Reserva` e passa pelo caminho novo. O conjunto das fatias fica num **documento do desacoplamento**, leve e sem comando próprio (`refactors/desacoplamentos/<nome>.md`) |
| Entrega da fatia | **Uma entrega de código**, seguida de marcos em produção: M1 entregue, M2 convivência, M3 validado, M4 contraído (seção 4.2) |
| Congelamento da Black Friday | O deploy de código inativo atrás de uma chave **é permitido** durante o congelamento. A convivência em produção só começa depois da Black Friday |
| Contração | Só depois de o caminho desacoplado estar **validado em produção**, com evidência registrada |
| Evidência do M3 | O que o dev cola: consultas, logs, prints, contagens. O agente pode rodar só `SELECT` com o acesso que o dev já tem, mostrando a consulta antes, como no SP5. Sem formato padronizado de divergência e sem integração com ferramenta de observabilidade |
| Teste de caracterização | **Obrigatório, com exceção registrada.** Quando o trecho não é testável sem um refactor anterior, o `assessment.md` registra o motivo e a verificação manual que substitui o teste, e o dev aprova antes do código |
| Abordagem | **Extensão própria `refactor`**, no molde da extensão oficial `bug`, com hooks próprios. Branch e envio por comandos da extensão `ws` |
| Contratos | O tipo 1 não cria nem muda contrato. O tipo 3 **cria** contrato (endpoint ou evento), e esse é o objetivo dele. A tabela, view, proc ou outro mecanismo do banco de onde o consumidor sai não muda enquanto outro sistema ainda acessá-lo (texto da regra II na seção 5.4) |
| Caminho novo do legado até o LINX | Já definido pelo time. É registrado uma vez no documento do desacoplamento, com ADR (regra IV), e não faz parte desta spec |
| Dívidas de Conformidade do AWX | **Refactors são exceção.** As obrigações de repo de corrigir dívidas ao tocar o código não se aplicam, e o `assessment.md` as lista como fora do escopo |
| Acompanhamento entre marcos | Seção "Para retomar" no `assessment.md`, linha da fatia no documento do desacoplamento, `ws refactor pendentes` e aviso no `ws start` (seção 7) |
| Ferramentas externas | **Nenhuma.** Verify, ApprovalTests, Scientist.NET, ArchUnitNET, NetArchTest, Pact e code-modernization não são necessários: a caracterização usa o framework de testes do repo, a comparação é código simples ou consulta, e a fronteira é o índice de impacto do Atlas. O code-modernization fica anotado para a pesquisa do SP7 |
| Spec Kit | **Atualizar para a 1.2.0 no SP6**, com a revisão do SP5 (hooks nativos da extensão `bug`) |
| Entrega | Dois PRs: `harness/speckit-1.2` primeiro e `harness/refactor` depois (seção 10.4) |

## 3. Pesquisa que embasou a decisão

O registro completo está em `docs/discovery/sp6-refactor-pesquisa.md`. Os pontos que decidiram:

- **O Spec Kit não tem caminho oficial para refactor.** Não há extensão, workflow, bundle nem preset de refactor, migração ou brownfield no `main` (`f6e72bc`, release 1.2.0). A issue de tech debt #1158 foi fechada como not_planned. O guia `existing-projects.md` manda tratar modernização como um pedaço de feature.
- **O fluxo de feature não serve para refactor.** O `spec-template.md` exige User Scenarios, FR e Success Criteria sem detalhe técnico. O `specify.md` para com `ERROR "Cannot determine user scenarios"`. Um preset que trocasse o template de spec valeria também para as features, porque o template é um só.
- **A comunidade só cobre pedaços**: architecture-guard, improve, fx-to-dotnet, aide-in-place, golden-demo. Todos são de mantenedor único e de 0 a 72 estrelas, e alguns têm manifesto ou preset quebrado no parser atual.
- **O Spec Kit 1.1.3 (PR #4878) fez os comandos `speckit.bug.*` dispararem hooks `before_`/`after_bug_*`.** É o gatilho do lembrete da seção 10 da spec do SP5. A 1.2.0 (#4942) também passou a aceitar patch mais novo nos bundles.
- **Uma extensão pode disparar hooks com nomes próprios**, como a `bug` faz: o texto do comando lê o `.specify/extensions.yml`. O item 2 do PoC confirma isso numa extensão nossa.
- **Ferramentas externas:** nenhuma é necessária para o SP6 (seção 2).

## 4. Conceitos

### 4.1 Tipos e fatia
- **Tipo 1, interno:** uma entrega, um repo, sem contrato novo nem mudado. Termina no M1.
- **Tipo 3, desacoplamento:**
  - a **fatia** tira o acesso direto de **um consumidor** a **um objeto** do `Reserva` (tabela, view, proc ou outro mecanismo do banco) e o leva para o caminho novo;
  - em geral toca dois ou três repos: o **provedor**, que ganha o contrato novo, e o **consumidor**, que passa a usá-lo;
  - o objeto continua igual para os outros sistemas. Ele só muda ou sai numa fatia própria, quando o Atlas não mostrar mais nenhum consumidor.

### 4.2 Marcos da fatia do tipo 3

| Marco | O que acontece | Quando | Como |
|---|---|---|---|
| **M1 entregue** | Caracterização, contrato novo no provedor e caminho novo no consumidor, atrás da **chave** em "antigo". Em produção, nada muda | A qualquer momento, inclusive no congelamento | `apply` e `verify`, envio e PRs |
| **M2 convivência** | O time vira a chave para o modo escolhido | Depois da data "convivência a partir de" | Configuração; sem comando |
| **M3 validado** | Os critérios do `assessment.md` foram atingidos, com evidência registrada | Depois do M2 | `/speckit-refactor-validar` |
| **M4 contraído** | O caminho acoplado e a chave saem do consumidor | Depois do M3 | `/speckit-refactor-contrair`, com dois portões |

### 4.3 Chave e modos de convivência
- **Chave:** o mecanismo que escolhe entre o caminho antigo e o novo. Ele varia por repo (configuração no AWX, `appSettings` ou tabela de parâmetros no legado), e o `assess` o escolhe por fatia. O harness exige três coisas: que a chave exista, que comece em "antigo" e que o modo de virar esteja escrito na seção "Para retomar".
- **Modos**, escolhidos no `assess` por fatia:
  - **paralelo:** os dois caminhos rodam, o antigo vale e as divergências são registradas;
  - **sombra:** o novo calcula e compara sem gravar. Serve para escrita;
  - **troca direta:** a chave vai para "novo", e a volta é pela própria chave.

### 4.4 Documento do desacoplamento
`refactors/desacoplamentos/<nome>.md`, por exemplo `linx.md`. Contém:
- **objetivo e critério de fim:** "o WMS não depende do banco `Reserva` para funcionar";
- **padrão do caminho novo**, com link para o ADR;
- **inventário** tirado do Atlas: objeto, consumidores, leitura ou escrita;
- **tabela de fatias em formato fixo**, lida pela `ws`:

```
| Fatia | Consumidor | Objeto | Marco | Data do marco | Convivência a partir de |
|---|---|---|---|---|---|
| [72694-faturamento-servidor](../72694-faturamento-servidor/) | wms.servidor.backend | Reserva.dbo.FATURAMENTO | M1 | 2026-11-10 | 2026-12-01 |
```

- **Marco:** `M1`, `M3`, `M4` ou `M3-falhou`. Muda **só pelos comandos**.
- **Convivência a partir de:** uma data `AAAA-MM-DD`. O `assess` pergunta ao dev e grava. É a única coluna que um humano pode editar à mão.
- **Dívidas fora do escopo:** as dívidas de repo listadas pelos `assess` das fatias, só como registro.

## 5. Componentes

```
tools/speckit/VERSION                    1.2.0
tools/speckit/refactor/                  fonte da extensão refactor (instalada pelo ws speckit)
.specify/extensions/refactor/            extensão refactor, nossa
.specify/extensions/ws/                  versão 1.3.0: refactor-start, refactor-enviar e hooks de bug e de refactor
.specify/presets/bugs/                   só o caminho bugs/ e o slug (sem as chamadas da ws)
.specify/memory/constitution.md          versão 1.3.0
AGENTS.md                                regra 5 e seção "Refactor com o Spec Kit"
tools/ws/                                ws refactor pendentes e aviso no ws start
refactors/<slug>/                        relatórios de cada refactor ou fatia (fora do harness)
refactors/desacoplamentos/<nome>.md      documento de cada desacoplamento (fora do harness)
```

### 5.1 Atualização do Spec Kit e revisão do SP5
- O `tools/speckit/VERSION` passa para a 1.2.0. O `ws speckit` reinstala o core e as extensões.
- O plano reconfere o que os nossos presets assumem do texto oficial: o `wrap` do `speckit.specify` e o `append` nos templates do `multirepo`, e o caminho `.specify/bugs/` nos comandos `speckit.bug.*`.
- **Revisão do SP5:**
  - a `ws` registra `before_bug_assess` → `speckit.ws.bug-start`, `after_bug_assess` → `speckit.ws.bug-sem-correcao` e `after_bug_test` → `speckit.ws.bug-enviar`;
  - o preset `bugs` perde o trecho que chama a `ws` e fica só com o caminho `bugs/` e o slug;
  - o plano avalia instalar pelo bundle `bugfix`. Se o bundle funcionar na 1.2.0, a instalação passa a ser por ele;
  - a seção 10 da spec do SP5 é marcada como resolvida, e o passo "conferir a extensão `bug` 1.0.1" sai da camada 4.

### 5.2 Extensão `refactor`
- `extension.yml` com `requires.speckit_version: ">=1.2.0"` e os cinco comandos da tabela abaixo. Os textos são em português, porque a extensão é nossa.
- Cada comando, no início e no fim, lê o `.specify/extensions.yml` e dispara `before_refactor_<comando>` e `after_refactor_<comando>`, do mesmo jeito que o core e a `bug` 1.1.3.
- Modelos: `assessment.md` e documento do desacoplamento.

| Comando | Tipo | Faz | Grava |
|---|---|---|---|
| `speckit.refactor.assess` | 1 e 3 | Só leitura. Define o slug e o tipo. Se for tipo 3, lê o documento do desacoplamento (ou oferece criá-lo, com o inventário do Atlas) e mostra as fatias pendentes no mesmo objeto ou consumidor. Grava o relatório (seção 6.4). Se concluir que o comportamento ou um contrato existente muda, recomenda reclassificar e termina | `assessment.md`; no tipo 3, a linha da fatia ou o documento novo |
| `speckit.refactor.apply` | 1 e 3 | Commit `test(<slug>): caracterização` só com os testes de caracterização, que passam no código atual; ou registra que a exceção aprovada vale. Depois aplica o refactor. No tipo 3, primeiro o provedor e depois o consumidor, atrás da chave em "antigo". Uma subseção por repo, com build e testes de cada um | `apply.md`, com o hash do commit de caracterização e a lista dos arquivos de teste |
| `speckit.refactor.verify` | 1 e 3 | Build e testes de cada repo tocado. Confere com `git diff <commit de caracterização>..HEAD` que os testes de caracterização não mudaram. Se tudo passar, marca o **M1**, completa a seção "Para retomar" e, no tipo 3, atualiza a linha da fatia | `verify.md` |
| `speckit.refactor.validar` | 3 | Recebe a evidência colada e, se for o caso, roda o `SELECT` opcional. Confere contra os critérios do `assessment.md`. Marca **M3** ou **M3-falhou** | `validacao.md` e a linha da fatia |
| `speckit.refactor.contrair` | 3 | **Portões:** o M3 registrado, e o índice de impacto do Atlas sem o consumidor acessando o objeto por outro caminho. Se um portão falhar, para e diz qual. Se passar, remove o caminho acoplado e a chave do consumidor, roda build e testes e marca o **M4** | `contracao.md` e a linha da fatia |

### 5.3 Extensão `ws` 1.3.0 e `tools/ws`

| Hook | Comando | Faz |
|---|---|---|
| `before_refactor_assess` | `speckit.ws.refactor-start` | `ws start refactor/<slug>`. Numa nova rodada da mesma fatia (seção 6.3), usa `refactor/<slug>-r<k>`. Se falhar, mostra o erro e **para** o comando |
| `before_refactor_validar` | `speckit.ws.refactor-start` | `ws start refactor/<slug>-contrair` |
| `after_refactor_assess` | `speckit.ws.refactor-enviar` | Só quando o `assess` termina sem refactor (reclassificar): commit `docs(<slug>): …` e push só da branch do workspace |
| `after_refactor_verify` | `speckit.ws.refactor-enviar` | Atlas dos repos tocados **sem o adiamento** de código interno (`relevancia.ini`), commit `refactor(<slug>): …` e `ws push` |
| `after_refactor_validar` | `speckit.ws.refactor-enviar` | Só no M3-falhou: commit `docs(<slug>): validação …` e push só da branch do workspace. No M3 ok, lembra o `/speckit-refactor-contrair` na mesma branch |
| `after_refactor_contrair` | `speckit.ws.refactor-enviar` | Atlas, commit `refactor(<slug>): contração …` e `ws push` |

- O `refactor-enviar` sempre pede confirmação humana antes do commit e usa o `ws-commit-push.sh` existente.
- Se o `ws atlas` não tiver uma opção para ignorar o adiamento, o plano acrescenta uma.
- Os comandos também viram skills (`/speckit-ws-refactor-start` etc.) e podem ser rodados à mão.
- **`ws refactor pendentes`:** lê `refactors/desacoplamentos/*.md` na branch atual e lista as fatias em `M1` ou `M3`, com a idade e o próximo passo:
  - `M1` antes da data: "aguardando a data de convivência";
  - `M1` depois da data: "virar a chave e rodar `/speckit-refactor-validar`";
  - `M3`: "rodar `/speckit-refactor-contrair`".

  Quando uma linha não segue o formato, o comando avisa qual é e continua.
- **Aviso no `ws start`:** depois de criar a branch, que já sai atualizada, roda a mesma leitura. Quando há fatia em `M1` com a data de convivência vencida, mostra uma linha, por exemplo: `2 fatias do desacoplamento linx aguardando validação desde 2026-12-01 (ws refactor pendentes)`. O aviso não bloqueia nada.

### 5.4 Regras

**Constitution 1.3.0** (o PR exige aprovação humana):
- **II, frases novas no fim:**
  - "Num refactor, a lista vai no `assessment.md`."
  - "Num desacoplamento, o contrato novo (endpoint ou evento) segue esta regra. A tabela, view, proc ou outro mecanismo do banco de dados de onde o consumidor sai não muda enquanto outro sistema ainda a acessar: a fatia muda só o caminho daquele consumidor, e o dado gravado pelo caminho novo tem de ser igual ao do antigo. O importante é que o WMS não dependa do banco Reserva para funcionar. Essa dependência será migrada para serviços de integração."
- **III:** "Uma feature, um bug ou um refactor só termina quando todos os repos afetados passam."
- **VI:** "A menor mudança que atende a spec, sem refatoração fora do escopo. Refatoração é escopo só quando é a própria demanda, pelos comandos de refactor."
- **VII (nova), Refactor não muda comportamento:**
  - "O comportamento observável não muda. A prova são testes de caracterização que passam antes e depois sem alteração, ou uma exceção aprovada pelo humano, com a verificação que a substitui."
  - "Num desacoplamento, o caminho acoplado só é removido depois de a convivência em produção ser validada e registrada."
  - "Num refactor, obrigações de repo de corrigir dívidas ao tocar o código (como as Dívidas de Conformidade do AWX) não se aplicam; o `assessment.md` as lista como fora do escopo."
- **Governança:** "Versão 1.3.0 … emendada em 2026-10-16 (refactor)."

**`AGENTS.md`:**
- **Regra 5** ganha: "**refactor ou desacoplamento:** os comandos de refactor do Spec Kit (seção 'Refactor com o Spec Kit')".
- **Seção nova "Refactor com o Spec Kit"**, nos moldes da de bugs:
  - **Iniciar:** `/speckit-refactor-assess <relato>`. O hook cria a branch `refactor/<slug>`; nunca à mão.
  - **Diagnóstico:** só leitura, com o Atlas pela skill `atlas-consultar`. Se o comportamento ou um contrato existente mudar, não é refactor: recomende reclassificar.
  - **Caracterização:** obrigatória, com exceção registrada e aprovada.
  - **Desacoplamento:** leia o documento do desacoplamento antes do `assess`, mostre as fatias pendentes no mesmo objeto ou consumidor, siga o padrão do caminho novo registrado nele e nunca mude o objeto do banco de onde o consumidor sai.
  - **Seguir:** o usuário lê o `assessment.md` antes do `apply`; depois vem o `verify`.
  - **Marcos e portões:** `validar` e `contrair`. O agente nunca contorna um portão nem muda a coluna Marco à mão.
  - **Banco:** o `SELECT` opcional, igual ao dos bugs.
  - **Onde ficam:** `refactors/` **não é harness**: crie e altere durante o trabalho.
  - **PRs:** um por repo e depois o do workspace.

## 6. Fluxo do dev

### 6.1 Tipo 1: refactor interno
1. `/speckit-refactor-assess <relato>`, com o work item e o motivo. O hook cria a branch `refactor/<slug>`.
2. O agente grava o `assessment.md` (seção 6.4).
3. **O dev lê e aprova**, inclusive a exceção, se houver. É o portão humano, sem comando.
4. `/speckit-refactor-apply`: o commit de caracterização e depois o refactor.
5. `/speckit-refactor-verify`: marca o M1. O hook atualiza o Atlas e oferece o commit e o `ws push`.
6. PR por repo e, depois, PR do workspace.

### 6.2 Tipo 3: fatia de desacoplamento
1. A primeira fatia de um desacoplamento cria o documento dele (seção 4.4). O padrão do caminho novo é preenchido com o time, com ADR.
2. Passos 1 a 6 do tipo 1, com o `assessment.md` do tipo 3. O `apply` vai do provedor para o consumidor, e o caminho novo fica atrás da chave em "antigo". O `verify` marca a fatia em `M1` no documento. O deploy pode ir durante o congelamento.
3. **M2:** a partir da data, o time vira a chave por configuração.
4. **M3:** `/speckit-refactor-validar <evidência>`. O hook cria a branch `refactor/<slug>-contrair`.
   - **Se não passou** (`M3-falhou`): o registro vai para o workspace, a chave volta para "antigo" e a fatia segue para uma nova rodada (seção 6.3).
   - **Se passou** (`M3`): segue na mesma branch.
5. **M4:** `/speckit-refactor-contrair`, que confere os dois portões, remove o caminho acoplado e a chave, e marca `M4`. O hook faz o envio.

### 6.3 Nova rodada da mesma fatia
Rodar `/speckit-refactor-assess` citando o slug de uma fatia em `M3-falhou` abre uma nova rodada:
- a branch é `refactor/<slug>-r<k>`;
- o `assessment.md` ganha a seção "Rodada k", com as divergências do `validacao.md`;
- depois seguem `apply` e `verify`, e a fatia volta a `M1`.

### 6.4 Conteúdo do `assessment.md`
- **Cabeçalho:** slug, work item, tipo e, no tipo 3, o nome do desacoplamento.
- **Estado atual e alvo.**
- **O que não pode mudar no comportamento.**
- **Afetados**, pelo índice de impacto do Atlas (regra II).
- **Plano de caracterização**, ou **exceção**: o motivo e a verificação manual que substitui o teste.
- **Dívidas de repo fora do escopo**, se houver (regra VII).
- **Só no tipo 3:**
  - provedor e consumidor;
  - objeto do banco;
  - contrato novo;
  - chave e como virá-la;
  - modo de convivência;
  - critérios do M3, com as consultas que o dev vai rodar;
  - data "convivência a partir de".
- **Para retomar**, preenchida pelo `verify`: data do M1, chave e como virá-la por modo, critérios do M3 com as consultas e o que o `contrair` vai remover. Quem retomar a fatia meses depois, humano ou agente, não precisa de mais nada.

### 6.5 Saídas

| Onde | O quê |
|---|---|
| `refactors/<slug>/` | `assessment.md`, `apply.md`, `verify.md`; no tipo 3, também `validacao.md` e `contracao.md` |
| `refactors/desacoplamentos/<nome>.md` | a linha da fatia com o marco |
| Workspace e repos tocados | branches `refactor/<slug>`, `refactor/<slug>-contrair` e `refactor/<slug>-r<k>` |
| `docs/atlas/` | atualização dos repos tocados no M1 e no M4 |

### 6.6 Slug e casos de borda
- **Slug:** `<id do work item>-<descrição-curta>`; sem work item, `rf-<AAAAMMDD>-<descrição-curta>`.
- **Slug já existe:** se a fatia está em `M3-falhou`, abre uma nova rodada (seção 6.3). Nos outros casos, o comando pergunta antes de sobrescrever.
- **Sessão nova:** o comando resolve o slug pelo disco (`refactors/*/assessment.md`).
- **Teste de caracterização alterado durante o refactor:** o `verify` acusa e não marca o M1.

## 7. Acompanhamento entre marcos

Entre o M1 e o M3 podem passar meses, com troca de dev e com outra sessão do agente. O estado nunca depende da memória de ninguém:
1. **A fatia se explica sozinha:** a seção "Para retomar" do `assessment.md`.
2. **Estado num só lugar:** a tabela de fatias do documento do desacoplamento, atualizada só pelos comandos.
3. **O lembrete aparece sozinho:** o `ws refactor pendentes`, o aviso no `ws start` depois da data de convivência e a regra do `AGENTS.md`, que manda mostrar as fatias pendentes no `assess` do tipo 3.

O work item do Azure DevOps continua sendo o acompanhamento oficial do time. O harness não integra com ele, como no SP5; o slug traz o id, para cruzar os dois.

## 8. Documentação nas camadas

| Onde | O que muda |
|---|---|
| `README.md` | Uma frase na abertura sobre os comandos de refactor. Linha nova na tabela "Quero…": "fazer um refactor ou uma fatia de desacoplamento", apontando para a camada 1 |
| Camada 1, `1-comecar.md` | "Um refactor, do relato ao PR" e "Uma fatia de desacoplamento, do relato à contração", em formato curto |
| Camada 2, `2-quando-da-errado.md` | Grupo novo "Comandos de refactor e `refactor/`": o portão do `contrair` recusou; a exceção de caracterização; a branch `refactor/` já existe; o aviso de pendentes no `ws start`; o `pendentes` não leu uma linha; a validação falhou e a fatia vai para nova rodada |
| Camada 3, `3-alem-do-basico.md` | Testes de caracterização com o framework do repo; os modos de convivência e a chave; o documento do desacoplamento |
| Camada 4, `4-manter.md` | A extensão `refactor`, os comandos e hooks novos da `ws`, `refactors/` e o `pendentes` em "Como as peças se ligam" e "Onde fica cada coisa". "Atualizar o Spec Kit" revisto para a 1.2.0, sem o lembrete do SP5 |
| `AGENTS.md` e constitution | Seção 5.4 |

O `tools/ws/tests/test_docs_referencias.sh` cobre as entradas novas. O deck do SP4 não muda.

## 9. O que fica fora
- Tipos 2 (entre projetos ou repos) e 4 (migração do legado para o AWX): SP7, onde o plugin code-modernization entra na pesquisa.
- Ferramentas externas de caracterização, comparação, fronteira e contrato (seção 2).
- O padrão do caminho novo até o LINX, já definido pelo time e registrado no documento do desacoplamento.
- Integração com o Azure DevOps e com ferramentas de observabilidade.
- Remoção do objeto do banco, que é uma fatia própria quando não sobra consumidor.
- Validação com fatia real e piloto com dev.

## 10. Validação e entrega

### 10.1 PoC (primeiro passo do plano, num workspace descartável)

| # | O que confirmar | Critério |
|---|---|---|
| 1 | A atualização para a 1.2.0 não quebra o que existe | As skills do `multirepo` e do `bugs` são geradas como hoje, e a suíte do `tools/ws/tests` passa |
| 2 | Uma extensão nossa dispara hooks com nomes próprios | A `refactor` instala; a `ws` registra `before_refactor_assess` no `.specify/extensions.yml`; o agente roda o `refactor-start` antes do `assess` |
| 3 | Os hooks nativos da `bug` funcionam | O `before_bug_assess` chama o `bug-start` sem o trecho do preset |
| 4 | O agente respeita os portões | O `contrair` recusa sem o M3 e recusa com o Atlas mostrando o consumidor |

Se algum item falhar, a execução para e volta ao usuário com as saídas. Nenhum contorno é feito sem decisão.

### 10.2 Testes automatizados (`tools/ws/tests`)
- **Instalação:**
  - a extensão `refactor` e as skills `speckit-refactor-*` e `speckit-ws-refactor-*`;
  - os hooks de refactor e de bug no `.specify/extensions.yml`;
  - o preset `bugs` sem as chamadas da `ws`.
- **Branch e envio:**
  - as três formas da branch e a recusa no `main`;
  - o commit de cada marco;
  - quando nenhum repo mudou, push só da branch do workspace.
- **Pendentes:**
  - leitura da tabela;
  - linha fora do formato;
  - o aviso do `ws start` só depois da data e só em `M1`.
- **Atlas:** o `refactor-enviar` atualiza sem o adiamento.
- **Docs:** o `test_docs_referencias.sh` cobre as entradas novas.

### 10.3 Ponta a ponta (workspace descartável, com origem e repos de teste locais)

| Caso | Esperado |
|---|---|
| Tipo 1 com caracterização | Commit `test(...)` antes do refactor; `verify` ok; Atlas atualizado; `ws push` |
| Tipo 1 com teste de caracterização alterado | O `verify` acusa e não marca o M1 |
| Tipo 1 com exceção | A exceção fica no `assessment.md`, e o fluxo segue depois da aprovação |
| Não é refactor | Recomenda reclassificar; commit só do `assessment.md` e push só do workspace |
| Tipo 3, fatia completa | Documento criado; provedor e consumidor atrás da chave; `M1`; `pendentes` e aviso depois da data; `validar` com falha e nova rodada `-r2`; `validar` ok; `contrair` ok; `M4` |
| Portões do `contrair` | Recusa sem M3; recusa com o consumidor ainda no Atlas |
| Sessão nova no meio | O `validar` numa sessão limpa retoma pela seção "Para retomar" |
| Regressão do bug | Bug com correção em 1 repo, com os hooks nativos |

O resultado fica em `docs/discovery/sp6-refactor-validacao.md`. Custo estimado com LLM: US$ 25 a 35.

### 10.4 Entrega
1. **PR 1, `harness/speckit-1.2`:** a atualização do Spec Kit e a revisão do SP5 (seção 5.1), com os itens 1 e 3 do PoC, a suíte e a regressão do bug. Vai primeiro e sozinho, porque mexe no fluxo de feature em piloto.
2. **PR 2, `harness/refactor`:** a vertente, saindo do `main` com o PR 1 mergeado. Leva a constitution 1.3.0, que exige aprovação humana.

Os ambientes descartáveis do PoC e da validação ficam listados para o usuário apagar. O `docs/discovery/estado-da-sessao.md` é atualizado no fim.

## 11. Riscos

| Risco | Mitigação |
|---|---|
| A atualização do Spec Kit quebra o fluxo de feature durante o piloto do SP4 | PR 1 separado; item 1 do PoC; suíte |
| A 1.2.0 não aceita hooks com nomes próprios de uma extensão nossa | Item 2 do PoC. Saída, com decisão do usuário: o próprio comando chama a `ws` no texto, como no SP5 |
| O agente pula um portão e contrai sem M3 | Portão no texto do comando e na regra VII; item 4 do PoC; caso de ponta a ponta |
| Alguém edita a tabela de fatias à mão e quebra o formato | O `pendentes` aponta a linha; a camada 2 explica |
| Duas fatias atualizam o mesmo documento em paralelo | Cada fatia muda só a própria linha; um conflito de merge fica restrito à tabela e é resolvido no PR do workspace |
| Fatia esquecida entre o M1 e o M3 | Seção 7 |
| A convivência por chave não cabe numa escrita específica | O `assess` escolhe o modo por fatia; a troca direta com volta pela chave é sempre possível |
| O objeto do banco muda dentro de uma fatia e quebra outro consumidor | Regra II; seção Afetados do `assessment.md`; regra do `AGENTS.md` |
