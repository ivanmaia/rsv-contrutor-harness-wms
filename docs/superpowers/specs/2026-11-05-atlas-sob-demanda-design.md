# Atlas sob demanda: menos tempo e menos tokens por rodada (design)

Data: 2026-11-05. Processo: `superpowers:brainstorming`. Decisões tomadas com o usuário na conversa de 2026-11-05, a partir do diagnóstico da sessão do bug 65594 (`C:\Users\vital.ivan\Downloads\diagnostico-sessao-65594.md`). O lote de ajustes menores do mesmo diagnóstico já entrou no `main` do workspace (PR 17654, `e7342e042`).

## 1. Intenção e porquê

A reclamação dos devs não é o Atlas rodar no start e no fim do fluxo, mas cada rodada gastar tempo e tokens demais para o que entrega. No bug 65594, **cerca de 83% dos tokens da sessão foram do Atlas** e o trabalho do bug (diagnóstico, correção e testes) ficou em 11%:

- no start, 3 subagentes mapearam 3 repos, 2 deles alheios ao bug (65 M de tokens processados, 19 min);
- no converge, o mesmo repo foi mapeado de novo 50 minutos depois (6,5 M, 10 min bloqueando o envio), e o subagente releu os 14 arquivos da skill `codebase-discovery` para um incremental de 4 arquivos;
- o plano estimou 200 mil tokens por repo; o real foi de 17 a 25 M processados por repo;
- um subagente parou por limite de uso e foi retomado à mão;
- o `ws atlas concluir` pediu a aprovação do PR de `atlas/atualizacao`, com 7 repos de outras entregas.

Causas conferidas no `origin/main` do workspace em 2026-11-05:

1. **O start mapeia por motivos alheios ao trabalho.** `tools/atlas/plano.py` (`gerar`) manda atualizar um repo por `feature` (os `--repos` que o agente supõe), `contrato`, `intervalo` (`intervalo_dias = 7`) e `volume`, até `max(limite_minimo = 3, nº de repos da feature)`.
2. **O converge mapeia todo repo que a feature mudou,** mesmo quando a mudança não altera o que os docs dizem.
3. **"Aprofunde onde mexer"** (`tools/atlas/prompt-mapeamento.md`): área tocada sem `rules-*.md` e `model-*.md` é documentada inteira, a partir do código da área toda.
4. **Custo fixo por subagente:** cada um segue a skill `codebase-discovery` inteira (playbooks, templates, references) e herda o modelo da sessão (Opus).
5. **O cabeçalho do `traceability-index.md` só cresce:** o do AWX é um parágrafo com o histórico de cada incremental, lido em todo mapeamento e em toda consulta.
6. **Contexto inflado:** o `ws atlas plano` imprime o JSON inteiro (32 KB no bug 65594) na sessão do dev.

A regra que o usuário adota: **o Atlas só é atualizado quando o trabalho precisa ou quando o código que ele descreve muda, e só no que mudou. Se o bug, refactor ou feature consegue ser resolvido com o Atlas que existe, nada é atualizado.**

## 2. Objetivos, não objetivos e antiobjetivos

**Objetivos:**
- Nenhum mapeamento no start de bug, refactor ou feature.
- Durante o trabalho, saber de forma barata e determinística se a página do Atlas que o agente está lendo pode estar desatualizada, e em quais afirmações.
- No fim do fluxo, revisar só as afirmações que citam arquivos alterados (e as que o agente conferiu); se nenhuma, o Atlas não muda e nenhum subagente roda.
- O dev não pagar, em tempo nem em tokens, por mudanças de outros times ou de outras entregas.
- O Atlas continuar se atualizando sem rodada agendada.

**Não objetivos:**
- Mudar o nível 2 (codebase-memory, Graphify, ast-grep) ou o índice de impacto, o catálogo do banco e os CSVs do nível 1 além do que a regeneração dos derivados já faz.
- Mudar a skill `codebase-discovery` em si: ela continua sendo a base das execuções completas.
- Automatizar o `ws sync` em pipeline (pode vir depois; o mecanismo deste design serve igual).

**Antiobjetivos:**
- O agente usar uma afirmação do Atlas que o código já desmentiu, sem saber.
- O dev esperar um mapeamento para começar o diagnóstico.
- Um bug pequeno disparar a documentação de uma área inteira.
- Uma pendência de outro time (PR de `atlas/atualizacao`, repo `contrato`) aparecer no fluxo do dev.

## 3. Decisões

### 3.1 Start sem mapeamento

- O `/speckit-ws-bug-start`, o `/speckit-ws-refactor-start` e o start do `/speckit-ws-feature` (`/speckit-specify`) deixam de chamar a `atlas-atualizar --gatilho start`. O agente começa com o Atlas que está no `main`.
- Os motivos `contrato`, `intervalo` e `volume` deixam de existir como gatilho de mapeamento, assim como o `limite_minimo`.
- O `ws atlas mapas` (reindexação do nível 2, sem LLM) continua onde faz sentido para o nível 2; não é escopo deste design mudá-lo (decisão do builder onde chamá-lo, desde que não bloqueie o início do diagnóstico).

### 3.2 Conferência na leitura

- Novo comando determinístico, sem LLM (nome sugerido `ws atlas confere <doc>`): para o doc do Atlas indicado, lista as afirmações (`C-n`) que o doc usa e cujos arquivos de evidência mudaram entre a `arvore` gravada no `atlas.estado` do repo e a árvore atual da branch.
- Saída curta: as afirmações suspeitas, com os arquivos alterados de cada uma. Sem suspeitas, uma linha dizendo que o doc está em dia.
- A skill `atlas-consultar` passa a mandar rodar a conferência antes de confiar num doc de repo. Afirmação suspeita: o agente confere no código só o que precisa, o que já faria para resolver o trabalho. Nada é remapeado.
- O agente registra as afirmações que conferiu e o que achou (vale / não vale mais / mudou para X), para o converge aproveitar. O registro fica versionado na pasta da feature (`specs/<feature>/`), para sobreviver a uma compactação ou a uma sessão nova.
- Código que nenhuma página cobre: o agente lê o código direto e registra a lacuna (área e arquivos) no mesmo registro.

**Por que o commit por repo basta:** cada execução reafirma o repo inteiro na `arvore` gravada (invariante da seção 3.5), então `git diff <arvore> HEAD -- <arquivos da afirmação>` responde se a afirmação pode ter envelhecido. Não é preciso commit por página.

### 3.3 Converge revisa só o que mudou

- Entrada do converge, por repo:
  1. o diff da entrega (só as mudanças da própria feature, ver 3.5), filtrado pelo `[ignorar]` do `relevancia.ini`;
  2. as afirmações que citam arquivos desse diff;
  3. as afirmações conferidas e as lacunas do registro da feature naquele repo.
- **Nada nas três listas:** o repo não é revisado, nenhum subagente roda, e o `atlas.estado` avança (o código mudou só onde o Atlas não descreve nada).
- **Algo nas listas:** um subagente por repo, com **Sonnet**, e um **prompt enxuto próprio** (não a skill `codebase-discovery` inteira). Ele:
  - revisa as afirmações listadas e os trechos dos docs que as usam;
  - acrescenta afirmações novas só para o comportamento que a entrega criou ou mudou;
  - área sem página: cria uma página mínima só com o que a entrega mexeu, no formato da skill, e registra a lacuna da área (3.4);
  - atualiza `edges.csv` e `tech/integrations.md` só nas linhas afetadas.
- O "aprofunde onde mexer" sai do prompt do converge.
- O commit vai na branch da feature, como hoje no converge.

### 3.4 Lacunas

- Cada repo ganha uma lista de lacunas versionada (sugestão: `docs/atlas/<repo>/_discovery/lacunas.md` ou `.csv`): área, arquivos que a entrega tocou, data e entrega de origem.
- Áreas inteiras só são documentadas em execuções completas, nunca no fluxo do dev:
  - **no PR do `ws/sync` para o `main`** (3.5): o plano mostra as lacunas abertas com o custo estimado e o time do harness decide na hora quais preencher;
  - **numa execução manual** (`/atlas-atualizar --gatilho manual`), quando o time do harness quiser, escolhendo as lacunas.
- Lacuna preenchida sai da lista.

### 3.5 Quem mantém o Atlas em dia

| Por onde a mudança entra | Quem atualiza | Base | Modelo |
|---|---|---|---|
| Bug, refactor ou feature pelo harness | o converge da entrega | o diff da entrega | Sonnet |
| Commit direto no repo (outros times, hotfix) | o time do harness, ao levar o `ws/sync` para o `main` | o diff que o sync trouxe | o mais forte (o da sessão) |
| Afirmação suspeita conferida pelo agente | o converge da mesma entrega | o registro da feature | Sonnet |
| Lacuna de área | execução completa (sync ou manual) | a lista de lacunas | o mais forte |

- O `ws sync` de cada dev **só traz o código**; não mexe no Atlas. A branch do dev pode ficar com código mais novo que o Atlas, e a conferência na leitura (3.2) cobre isso.
- **Invariante:** no `main`, o Atlas de cada repo está revisado contra o código do `main` daquele repo, na `arvore` gravada. Para isso, no PR do `ws/sync` para o `main`, as afirmações tocadas pelo diff do sync são **sempre** revistas; só o preenchimento de lacunas de área é opcional.
- **O dev não paga por mudanças de fora:** o diff do converge é o da própria entrega, não o que entrou pelo `ws sync` dele. Se o dev trouxe `ws/sync` à frente do `main`, essas mudanças ficam para o PR do sync, não para o converge dele.
- **O que a `arvore` do `atlas.estado` significa** (decisão do builder check): "revisado até aqui", nunca "código visto". O converge só avança a `arvore` quando a base do repo na branch da entrega é a `arvore` revisada do `main` (a branch não trouxe mudança externa ainda não revisada). Se trouxe, o converge revisa as afirmações da entrega e **mantém a `arvore`**; o PR seguinte do sync revisa o diff a partir dela, o que inclui as mudanças da entrega de novo (custo pequeno, do time do harness, e a invariante continua valendo).
- **Topologia da revisão do sync** (decisão do builder check): a `ws/sync` continua compartilhada e só fast-forward, sem commits do Atlas. O time do harness cria uma branch a partir da ponta da `ws/sync` (sugestão `atlas/sync-<data>`), roda a revisão nela e abre o PR dessa branch para o `main`, que leva o código do sync e a revisão juntos. Ela substitui o PR direto da `ws/sync` para o `main`. O `ws sync` seguinte traz o `main` para a `ws/sync` como hoje.
- **Obrigatoriedade** (decisão do builder check): um comando do `ws` faz o caminho inteiro (branch, plano, revisão, commit, PR) e a camada 4 documenta; sem política nem check de máquina no `main`. Quem leva o sync ao `main` é só o time do harness.
- A `atlas/atualizacao` **continua existindo**: a execução manual (inclusive a que preenche lacunas) publica nela, como hoje, e o PR dela para o `main` segue com o time do harness. O que sai é o start publicando nela; com isso, o aviso do PR de `atlas/atualizacao` deixa de aparecer no fluxo do dev (item 2.7 do diagnóstico). O conteúdo atual da branch segue o caminho normal, sem passo de transição.

### 3.6 Formato da rastreabilidade

- A conferência precisa ligar afirmação → doc → arquivos por máquina. Hoje o `traceability-index.md` liga, mas com caminhos irregulares (prefixos como `CK/`, `ERP/`, nomes soltos como `SolicitacaoMessage.cs:13`, coluna de doc como `tech/*`).
- Cada afirmação passa a ter caminhos completos relativos ao repo e os docs exatos que a usam, num formato legível por máquina (sugestão: um `_discovery/afirmacoes.csv` com `id,doc,arquivo,linhas`, mantido junto com o índice). O formato exato é do builder.
- **Evidência em outro repo** (decisão do builder check): o formato tem a coluna do repo de cada arquivo (o índice do AWX cita `picking.backend/…` e `LW/`). A conferência compara cada arquivo com a `arvore` do repo dele, e o converge de uma entrega que muda o repo B revisa também as afirmações de outros repos que citam arquivos de B. Evidência fora dos repos (`extract/`, catálogo do banco) não entra na conferência.
- Migração dos índices existentes: script que resolve prefixos e nomes soltos pelo `git ls-files` do repo; o que não resolver fica marcado e a afirmação é tratada como suspeita na conferência até uma execução completa resolver.
- **Ligação afirmação → doc na migração** (decisão do builder check): `tech/*` e outros curingas viram os docs que casam; `README` vira `project-readme.md`; `(histórico)` e `register ...` ficam sem doc (não são lidos como fonte). O que sobrar é listado por repo e resolvido na primeira execução completa daquele repo; até lá, a afirmação conta como usada por todos os docs da pasta indicada, para errar para mais e não para menos.
- O cabeçalho do `traceability-index.md` guarda só o estado atual (commit e data); o histórico dos incrementais sai dele (já está no git).

### 3.7 Custos, limites e contexto

- **Estimativa:** a do converge passa a ser por afirmações a revisar, calibrada com números reais; a das execuções completas é calibrada com o diagnóstico do 65594 (17 a 25 M processados por repo num incremental com a skill inteira). O converge não pede confirmação; a execução completa mostra o custo e pede.
- **Limite de uso (item 2.4):** subagente do converge que para por limite ou não termina não bloqueia o envio da entrega. As afirmações dele entram como pendentes na lista do repo (mesmo lugar das lacunas ou equivalente) e são revistas no próximo PR do sync ou na próxima execução completa. A skill diz isso explicitamente.
- **Contexto da sessão do dev:** o plano grava o JSON em arquivo e imprime só a tabela curta; os relatórios dos subagentes voltam resumidos.
- **Teto por subagente:** número máximo de chamadas ou de arquivos lidos por subagente do converge, com o valor definido pelo builder a partir de uma medição.

## 4. Restrições

- Tudo em bash e Python no padrão de `tools/ws` e `tools/atlas`, com testes em `tools/ws/tests` (`bash tools/ws/tests/run.sh`).
- Docs do harness (camadas 1 a 4) e `AGENTS.md` atualizados no mesmo PR; `docs_referencias.py` verde.
- Skills do Spec Kit da extensão `ws` mudam na fonte (`tools/speckit/ws/commands/`, `.specify/extensions/ws/`) e nas cópias em `.claude/skills/`, como hoje.
- Commits e PRs do workspace sem atribuição ao Claude; o `main` do workspace exige PR.
- Os repos de `repos/` são só leitura para o Atlas.

## 5. O que fica para o builder

- Nomes dos comandos, arquivos e colunas (`ws atlas confere`, `lacunas`, `afirmacoes.csv`).
- Como o converge separa o diff da própria entrega do que veio pelo `ws sync` do dev.
- O nome e os passos do comando do `ws` que faz a revisão do sync.
- O que fazer com os avisos de mapeamento pendente do mecanismo antigo (`project-readme.md`, ações `adiar` e `pendente` do plano): manter para a execução manual ou converter em lacunas.
- O texto do prompt enxuto do converge e o teto por subagente.
- A calibração das estimativas.
- Onde chamar o `ws atlas mapas`.
- Como tratar dois converges do mesmo repo em paralelo (o `ws_atlas_merge` já trata `docs/atlas`; conferir que o `afirmacoes.csv` e as lacunas também mesclam).

## 6. Validação

- Testes de unidade do plano, da conferência, da migração do índice e do converge sem afirmações tocadas.
- De ponta a ponta, num bug real ou de teste: start sem mapeamento; conferência numa página com e sem suspeitas; converge com zero afirmações (nenhum subagente) e com algumas (um subagente Sonnet); medir tokens e tempo contra o 65594.
- Um PR do `ws/sync` para o `main` com mudança externa num repo, conferindo que as afirmações tocadas são revistas e que o dev seguinte vê o doc em dia.
