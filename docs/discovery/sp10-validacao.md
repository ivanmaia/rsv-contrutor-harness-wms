# SP10: validação dos ciclos por história

Validação feita em 2026-10-29 na feature real `ws-003-b2c-operacao-ecommerce` (8 histórias, 76 FRs, 5 repos), num clone descartável (`C:\ws\wt-ciclos-e2e`, branch `ws-003-b2c-operacao-ecommerce`, com o harness novo mergeado). O checkout do usuário em `c:\ws\dsv\...` não foi tocado. Código em `C:\ws\industria-logistica.wms.workspace`, branch `harness/ciclos-por-historia`.

Os comandos foram executados por agentes que seguiram as skills instaladas (`.claude/skills/speckit-ws-cycles` e `speckit-tasks`) passo a passo, e não pelo Claude Code chamando a skill: é uma simulação fiel do texto, não a invocação real.

## O que foi validado

| Item | Resultado |
|---|---|
| `/speckit-ws-cycles` na `ws-003` | ok: `cycles.md` com 9 ciclos (c0 a c8), passou no `ws ciclos validar`; 14 tool calls |
| `ws ciclos validar --confirmado` depois da confirmação simulada | ok |
| `ws ciclos proximos` | `c0` (o único possível sem o `cycles.md` no `main`) |
| `ws ciclos flag-confere` | falha esperada: a flag `ws-003.c1.modo-sku` ainda não foi registrada (a task do c1 faz isso) |
| `/speckit-tasks` na `ws-003` | ok: `tasks.md` com 96 tasks em 9 fases `## Ciclo cN`, `c0` com a fundação, flag no c1, tasks agrupadas por repo com a verificação de cada um, sem task dependendo de ciclo posterior; 12 tool calls |
| `/speckit-implement` e `/speckit-converge` por ciclo, ponta a ponta | **não rodados**: implementariam código nos repos da `ws-003`. Cobertos só pelos testes estáticos dos wraps |

## O plano de ciclos que a `ws-003` gerou (resumo)

| Ciclo | História | Depende de | Segurança | Tamanho |
|---|---|---|---|---|
| c0 | abertura e fundação compartilhada | - | ordem | ok |
| c1 | US1 modo por armazém e marca | c0 | flag `ws-003.c1.modo-sku` | aviso |
| c2 | US2 recebimento | c1 | inerte | ok |
| c3 | US3 transferência | c2 | inerte | ok |
| c4 | US4 auditoria | c2, c3 | inerte | ok |
| c5 | US5 separação e fila FIFO | c1 | inerte | ok |
| c6 | US6 colmeia | c1 | inerte | aviso |
| c7 | US7 checkout | c5, c6 | inerte | aviso |
| c8 | US8 devolução | c1, c2 | inerte | ok |

Bateu com a expectativa ilustrativa: fundação no c0 (`CodigoBarra`, movimentação por ID de item, `prConsultaDadosMovimentacao` aditiva); dependências coerentes com a spec (US2→US3→US4; US5 e US6→US7; US8 depende do modo e do saldo); bloqueio externo da emenda à constitution do AWX no c1; aviso de tamanho em US6 e US7; nenhum card assumido por história (US6 tem três, US1 e US5 nenhum).

Divergências, que o time confirma ou corrige na confirmação do plano:
- **US1 saiu como c1, a primeira depois da abertura, e não por último.** O agente escolheu proteger o interruptor com uma flag (`ws-003.c1.modo-sku`, que faz a API do AWX recusar o valor SKU até as histórias c2 a c8 estarem no `main`) em vez de reordenar. É o resultado da análise da feature, não uma regra do comando; a alternativa que o usuário citou (US1 por último) continua possível e é uma decisão do time.
- A US1 também saiu com aviso de tamanho (3 repos, cerca de 32 arquivos e 1.700 linhas, estimados pelo plan).
- US6 não depende de US5, e US8 depende só de US1 e US2, porque é o que a spec sustenta.

## Achados da validação e o que foi feito

| # | Achado | Tratamento |
|---|---|---|
| 1 | A skill `/speckit-ws-cycles` não descrevia o formato do `cycles.md` (título, linha `Confirmado:`, seção `## Ciclos`, ids `c<N>`, separador de `Depende de`) nem como estimar arquivos e linhas; o agente teve de deduzir lendo os testes e o código | corrigido com teste (ver "Passe de correção da validação") |
| 2 | O `setup-tasks.sh` falha com "Feature directory not found" numa branch `ws-NNN-…` quando não há `.specify/feature.json`. O arquivo é ignorado pelo git; um segundo dev, num clone novo, que pegue um ciclo em paralelo não o tem | corrigido com teste: o `cycle-start` e os wraps gravam o `.specify/feature.json` |
| 3 | A ordem dos marcadores nas tasks (`[lugar]`, `[P]`, `[USn]`) era ambígua entre o template do preset e o do Spec Kit | corrigido com teste: o wrap de tasks fixa `TNNN [lugar] [P] [USn]` |
| 4 | Conflito entre "Setup, Foundational, uma fase por história e Polish" do Spec Kit e a regra de uma fase por ciclo | já resolvido pela regra do wrap (o agente seguiu o wrap) |
| 5 | Os caminhos de arquivo nas tasks combinam pastas do plan com nomes plausíveis, porque o plan só cita pastas e classes | não é do harness: é a precisão do plan; o `/speckit-analyze` e o implement conferem |

## Passe de correção da validação

Os três primeiros achados viraram teste que falhou e passou (`test_speckit_ciclos.sh`):

- `test_cycles_descreve_o_formato_do_cycles_md`: a skill traz o esqueleto do `cycles.md`, os ids `c<N>`, o separador por vírgula e como estimar arquivos e linhas pelo plan.
- `test_cycle_start_e_wraps_gravam_o_feature_json`: o `cycle-start` e os wraps de tasks, implement e converge gravam o `.specify/feature.json` com a pasta da feature.
- `test_wrap_tasks_fixa_a_ordem_dos_marcadores`: `TNNN [lugar] [P] [USn]`.

Commits no workspace: `048084cd` (fontes) e `5ed99802` (reinstalação do Spec Kit). O clone descartável foi removido.

## Suíte

Suíte completa (26 arquivos, em paralelo, com rede e Python no PATH): a primeira rodada deu 3 falhas, todas asserções presas a valores antigos (`version: "1.8.0"` da extensão ws em `test_harness.sh` e `test_speckit_refactor.sh`, e a descrição sem o SP10). A versão subiu de propósito para 1.9.0; os testes foram atualizados. Depois disso, todos os arquivos passam, incluindo `test_ciclos` (62), `test_flags` (12), `test_speckit_ciclos` (21), `test_speckit_install` (14) e `test_harness` (41).

Ambiente: `python` não está no PATH do Git Bash desta estação; sem ele, `test_saida_e_json_de_uma_linha_mesmo_com_aspas_no_erro` falha (também no `main`).
