# SP10: ciclos por história — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dar ao harness um comando que, entre o `speckit-plan` e o `speckit-tasks`, divide a feature `ws-NNN` em ciclos (um por história), cada um entregável em produção sozinho, com limite de tamanho configurável, registro de feature flags e verificação no `converge`.

**Architecture:** A parte mecânica fica no CLI `tools/ws/ws ciclos ...` (bash, testado offline com a fixture do `tests/lib.sh`): ler e validar o `cycles.md`, calcular o estado a partir do `main`, medir o diff, iniciar a branch do ciclo e manter o registro de flags. A parte de julgamento (ler spec e plan, propor dependências e segurança) é um comando novo da extensão `ws` (`/speckit-ws-cycles`). O preset `multirepo` passa a envolver `speckit.tasks`, `speckit.implement` e `speckit.converge` para trabalharem por ciclo, sem fork do Spec Kit.

**Tech Stack:** bash (Git Bash no Windows), git, awk; testes em `tools/ws/tests/` com `run.sh`; Spec Kit 1.2.0 (extensão `ws` e preset `multirepo` em `tools/speckit/`).

**Spec:** `docs/superpowers/specs/2026-10-29-sp10-ciclos-por-historia-design.md` (neste repo de discovery). O código é implementado e testado no clone `C:\ws\industria-logistica.wms.workspace`. O clone `c:\ws\dsv\industria-logistica.wms.workspace` é o de desenvolvimento do usuário (features): **não é alterado**.

## Global Constraints

- Idioma: documentos, commits, scripts, configuração e o CLI `tools/ws/ws` em **português**; o que o dev digita ou vê (comandos e skills) em **inglês** (SP8). Os textos para o usuário saem em português do Brasil, com acentos.
- Nenhuma linha de atribuição do Claude nos commits e PRs do workspace (política do `.claude/settings.json` do workspace).
- Sem fork do Spec Kit: `speckit.tasks`, `speckit.implement` e `speckit.converge` são envolvidos por preset (`strategy: wrap`, com `{CORE_TEMPLATE}`), como o `speckit.specify` já é.
- O limite de tamanho (arquivos e linhas) vive no arquivo de configuração do harness `workspace.ciclos.ini`, com valores iniciais **provisórios** que o time ajusta. É aviso, não bloqueio.
- Não há biblioteca compartilhada de flag: o harness entrega o registro (`flags/registry.md`), a regra e um padrão obrigatório por stack.
- "Mergeada" é no `main`. Uma história que depende de outra só começa depois de a anterior estar no `main`.
- Os resultados da seção 6 da spec (caso `ws-003`) são ilustrativos, não critério de aceite rígido.
- Só trabalhar fora da branch de uma feature: a mudança do harness vai numa branch própria (`AGENTS.md`, "Harness durante uma feature ou um bug").

## Decisões do construtor neste plano (revisáveis)

- **Ciclo 0 sempre existe ("abertura")** e é a branch da própria feature: leva `specs/ws-NNN-*/` (spec, plan, `cycles.md`, `tasks.md`) e, se houver, a fundação compartilhada. Todo outro ciclo depende dele. Assim a spec chega ao `main` com o primeiro PR, sem conflito entre ciclos paralelos.
- **Estado do ciclo:** `pendente`, `em-andamento` ou `entregue`. O `converge` grava `entregue` no `cycles.md` **dentro do PR do ciclo**; quando o PR chega ao `main`, o `main` passa a dizer `entregue`. Por isso `proximos` lê o `cycles.md` do `origin/main`, sem consultar a API do Azure.
- **Branch do ciclo:** `<branch da feature>-c<N>` (por exemplo `ws-003-b2c-operacao-ecommerce-c2`), criada a partir da `ws/sync` pelo `ws start`. Não pode ser `<feature>/c<N>`: o git não deixa uma ref conviver com a pasta de mesmo nome.
- **Padrão de feature flag por stack** (item 12 do plano de revisão, a confirmar pelo usuário): nome `ws-NNN.c<N>.<nome-kebab>`; **desligada por padrão e, se ausente, vale desligada**; lida em **um único ponto por repo**; o SQL nunca lê flag (a aplicação decide o caminho e chama a procedure certa). Mecanismo: .NET pela `IConfiguration` (`FeatureFlags:<flag>`), Angular pelo `environment` (`featureFlags`), React Native por um módulo de configuração, banco por parâmetro vindo da aplicação.

## Review Focus

Entradas e condições que a spec implica, nenhuma tarefa de teste óbvia cobre, e que mais provavelmente atingem o time; cada linha tem o teste na tarefa dona:

1. `cycles.md` salvo com CRLF no Windows: a leitura e a gravação do estado não podem quebrar nem trocar o fim de linha (Tasks 2 e 3).
2. Primeiro ciclo, com o `origin/main` ainda sem o `cycles.md`: `proximos` devolve só `c0`, sem erro (Task 3).
3. Feature com uma só história (`c0` e `c1`): o plano de ciclos é válido e o `c1` depende do `c0` (Task 2).
4. Diff com arquivo binário, arquivo só excluído (Atlas, specs) ou vazio: a medição conta o certo (Task 4).
5. Branch de ciclo (`...-c2`) não pode ser tomada como outra feature pelo hook `ws-feature.sh` (Task 5).

---

### Task 1: Configuração e classificação de tamanho

**Files:**
- Create: `workspace.ciclos.ini`, `tools/ws/lib/ciclos.sh`, `tools/ws/tests/test_ciclos.sh`
- Modify: `tools/ws/ws` (despacho e linha de uso)

**Interfaces:**
- Produces:
  - `workspace.ciclos.ini`, na raiz, com este conteúdo:
    ```ini
    # Configuração dos ciclos por história (SP10). Os valores são provisórios: o time os ajusta aqui.
    [limite]
    arquivos = 40
    linhas = 1500
    margem_percentual = 25
    [medicao]
    # Caminhos (prefixos) fora da contagem: o que o harness gera, não o código da história.
    excluir = docs/atlas/ specs/ bugs/ refactors/ flags/
    ```
  - `WS_CICLOS_USO="uso: ws ciclos <limites|classifica|validar|atual|proximos|marca|medir|iniciar|flag-registra|flag-confere|flag-remove> [args]"`
  - `ws_ciclos <sub> [args]` (despacho; subcomando desconhecido → `die "$WS_CICLOS_USO"`).
  - `ws_ciclos_ini <secao> <chave>` → imprime o valor sem espaços nem CR; falha com `chave <chave> ausente em [<secao>] de workspace.ciclos.ini`; arquivo ausente falha com `workspace.ciclos.ini não encontrado`.
  - `ws_ciclos_classifica <arquivos> <linhas>` → imprime `ok`, `aviso` ou `estourou`. Para cada medida: `<= limite` é `ok`; `<= limite * (100 + margem_percentual) / 100` (aritmética inteira) é `aviso`; acima, `estourou`. O resultado é o pior das duas.
  - CLI: `ws ciclos limites` imprime `arquivos=40 linhas=1500 margem_percentual=25`; `ws ciclos classifica <a> <l>`.

- [ ] **Step 1: Criar o worktree de trabalho** (não mexe no checkout da `ws-003` do usuário)

```bash
git -C /c/ws/industria-logistica.wms.workspace fetch origin
git -C /c/ws/industria-logistica.wms.workspace worktree add /c/ws/wt-ciclos -b harness/ciclos-por-historia origin/main
```
Daqui em diante, todos os caminhos são relativos a `/c/ws/wt-ciclos`.

- [ ] **Step 2: Escrever os testes que falham** em `tools/ws/tests/test_ciclos.sh`. Helper `mk_ini` grava o `workspace.ciclos.ini` da fixture com os valores acima. Testes e asserts:

```bash
test_classifica_dentro_do_limite_e_ok()   { mk_ini; assert_eq "$(ws ciclos classifica 40 1500)" "ok"; }
test_classifica_na_margem_e_aviso()       { mk_ini; assert_eq "$(ws ciclos classifica 50 100)" "aviso"; assert_eq "$(ws ciclos classifica 1 1875)" "aviso"; }
test_classifica_acima_da_margem_estoura() { mk_ini; assert_eq "$(ws ciclos classifica 51 100)" "estourou"; assert_eq "$(ws ciclos classifica 1 1876)" "estourou"; }
test_classifica_usa_o_pior_dos_dois()     { mk_ini; assert_eq "$(ws ciclos classifica 10 2000)" "estourou"; }
test_limites_mostra_os_valores()          { mk_ini; assert_eq "$(ws ciclos limites)" "arquivos=40 linhas=1500 margem_percentual=25"; }
test_ini_com_crlf_e_comentario_funciona() { mk_ini; sed -i 's/$/\r/' workspace.ciclos.ini; assert_eq "$(ws ciclos classifica 40 1500)" "ok"; }
test_ini_ausente_explica()                { assert_fails ws ciclos limites; assert_contains "$OUT" "workspace.ciclos.ini não encontrado"; }
test_ini_sem_chave_explica()              { mk_ini; sed -i '/^arquivos/d' workspace.ciclos.ini; assert_fails ws ciclos limites; assert_contains "$OUT" "chave arquivos ausente em [limite]"; }
test_ciclos_sem_subcomando_mostra_o_uso() { assert_fails ws ciclos; assert_contains "$OUT" "uso: ws ciclos"; }
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_ciclos.sh`
Expected: `FALHA` nos 9 testes (`ws ciclos` ainda não existe).

- [ ] **Step 4: Implementar** `ws_ciclos`, `ws_ciclos_ini` e `ws_ciclos_classifica` em `tools/ws/lib/ciclos.sh` (cabeçalho de comentário no estilo de `fatia.sh`; o `ws_ini` pode ser um `awk` que acompanha a seção atual). Em `tools/ws/ws`, acrescentar `ciclos) ws_ciclos "$@" ;;` e `ciclos` na linha de uso (no comentário e no `die`). Criar o `workspace.ciclos.ini` da raiz com o conteúdo acima.

- [ ] **Step 5: Rodar e ver passar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_ciclos.sh`
Expected: `9 ok, 0 falha(s)`

- [ ] **Step 6: Commit**

```bash
git add workspace.ciclos.ini tools/ws/lib/ciclos.sh tools/ws/ws tools/ws/tests/test_ciclos.sh
git commit -m "ciclos: configuração do limite de tamanho e ws ciclos classifica"
```

---

### Task 2: Leitura e validação do `cycles.md`

**Files:**
- Modify: `tools/ws/lib/ciclos.sh`, `tools/ws/tests/test_ciclos.sh`

**Interfaces:**
- Consumes: `ws_ciclos`, `WS_CICLOS_USO` (Task 1).
- Produces:
  - Formato do `specs/ws-NNN-<nome>/cycles.md`: linha `Confirmado: sim (<data>, <quem>)` ou `Confirmado: não`; seção `## Ciclos` com a tabela abaixo (uma linha por ciclo; célula vazia é `-`; sem `|` dentro de célula); seção `## Justificativas` livre.
    ```
    | Ciclo | História | Depende de | Repos | Segurança | Flag | Tamanho | Estado | Bloqueios | Decisão de tamanho |
    ```
  - `WS_CICLOS_CAB` com esse cabeçalho exato; `WS_CICLO_ID='^c[0-9]+$'`; `WS_FLAG_NOME='^ws-[0-9]{3}\.c[0-9]+\.[a-z0-9]+(-[a-z0-9]+)*$'`.
  - Valores válidos: Segurança `ordem|inerte|flag`; Tamanho `ok|aviso|estourou`; Estado `pendente|em-andamento|entregue`; Decisão `-|aceito|dividido|excecao: <motivo>`; Depende de é `-` ou lista de ids separados por vírgula e espaço.
  - `ws_ciclos_le <arquivo>` preenche os arrays `C_ID C_HIS C_DEP C_REP C_SEG C_FLA C_TAM C_EST C_BLO C_DEC` (mesmo índice) e `C_CONF` (`sim` ou `nao`); tolera CRLF e cabeçalho com espaços extras.
  - `ws_ciclos_validar <arquivo> [--confirmado]`: coleta **todos** os erros, imprime cada um em stderr como `ciclos: <regra>: <detalhe>` e sai com 1 se houver algum. Regras e textos: `cabeçalho` (tabela fora do formato), `id duplicado: <id>`, `c0 ausente`, `dependência inexistente: <id> depende de <x>`, `dependência circular: <ids>`, `sem caminho até c0: <id>`, `segurança inválida: <id>`, `flag: <id> tem segurança flag sem nome` / `flag: <id> tem nome mas a segurança não é flag` / `flag: nome inválido: <nome>`, `estado inválido: <id>`, `tamanho inválido: <id>`, `decisão inválida: <id>`, `sem Confirmado`, e, só com `--confirmado`, `não confirmado: o time ainda não confirmou o plano de ciclos`.
  - CLI: `ws ciclos validar <arquivo> [--confirmado]`.

- [ ] **Step 1: Escrever os testes que falham.** O helper `mk_ciclos <caminho> [estado_do_c0]` grava este arquivo válido (o `c1` e o `c3` dependem do `c0`; o `c2` depende do `c1` e usa flag):

```
# Ciclos da feature ws-001-x

Confirmado: sim (2026-10-29, teste)

## Ciclos

| Ciclo | História | Depende de | Repos | Segurança | Flag | Tamanho | Estado | Bloqueios | Decisão de tamanho |
|---|---|---|---|---|---|---|---|---|---|
| c0 | Abertura: specs e fundação | - | workspace | ordem | - | ok | pendente | - | - |
| c1 | US1 Cadastro | c0 | repos/r1 | inerte | - | ok | pendente | - | - |
| c2 | US2 Tela | c1 | repos/r1, repos/r2 | flag | ws-001.c2.tela-nova | aviso | pendente | aprovação do time X | - |
| c3 | US3 Relatório | c0 | repos/r2 | ordem | - | ok | pendente | - | - |

## Justificativas
```
Testes (cada um altera uma linha do arquivo válido com `sed` e confere a mensagem):
  - `test_validar_aceita_o_plano_valido`: `assert_ok ws ciclos validar specs/ws-001-x/cycles.md --confirmado`
  - `test_validar_aceita_feature_com_uma_historia`: arquivo só com `c0` e `c1` (dependente do `c0`) passa.
  - `test_validar_recusa_cabecalho_errado`, `..._id_duplicado`, `..._sem_c0`, `..._dependencia_inexistente` (`c1` depende de `c9`), `..._dependencia_circular` (`c1` depende de `c2` e `c2` de `c1`), `..._sem_caminho_ate_c0` (`c3` com `Depende de` `-`), `..._flag_sem_nome`, `..._nome_sem_flag`, `..._nome_de_flag_invalido` (`TelaNova`), `..._estado_invalido`, `..._decisao_invalida`: cada um com `assert_fails` e `assert_contains "$OUT"` da mensagem acima.
  - `test_validar_junta_todos_os_erros`: dois defeitos no mesmo arquivo → as duas mensagens na saída.
  - `test_validar_com_confirmado_recusa_nao_confirmado`: `Confirmado: não` passa sem a opção e falha com `--confirmado`.
  - `test_validar_tolera_crlf`: `sed -i 's/$/\r/'` no arquivo válido → passa.

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_ciclos.sh`
Expected: `FALHA` nos testes novos (`validar` cai em `uso: ws ciclos`).

- [ ] **Step 3: Implementar** `ws_ciclos_le` e `ws_ciclos_validar` em `lib/ciclos.sh`, seguindo o padrão de `ws_fatia_le` (arrays globais, `tr -d '\r'`, campo vazio vira `-`). Despachar `validar` em `ws_ciclos`. A detecção de ciclo e do caminho até `c0` é uma busca em profundidade sobre `Depende de`.

- [ ] **Step 4: Rodar e ver passar** — Expected: todos ok, 0 falha.

- [ ] **Step 5: Commit**

```bash
git add tools/ws/lib/ciclos.sh tools/ws/tests/test_ciclos.sh
git commit -m "ciclos: leitura e validação do cycles.md"
```

---

### Task 3: Estado dos ciclos (`atual`, `proximos`, `marca`)

**Files:**
- Modify: `tools/ws/lib/ciclos.sh`, `tools/ws/tests/test_ciclos.sh`

**Interfaces:**
- Consumes: `ws_ciclos_le`, `ws_ciclos_validar`, `current_branch`, `has_origin`, `WS_DESTINO` (de `common.sh`).
- Produces:
  - `ws_ciclos_atual` → imprime o id do ciclo da branch atual: `<feature>-c<N>` → `c<N>`; uma branch `ws-NNN-...` sem sufixo `-c<N>` → `c0`; outra branch → `die "fora de uma branch de feature: <branch>"`. O sufixo `-r<k>` de revisão é ignorado antes.
  - `ws_ciclos_proximos <arquivo>` (caminho relativo à raiz do workspace) → um id por linha: os ciclos cujo `Estado` no arquivo local é `pendente` e cujas dependências estão **todas `entregue` no `cycles.md` do `origin/<WS_DESTINO>`**. Busca antes o destino (`git fetch -q origin "+refs/heads/$WS_DESTINO:refs/remotes/origin/$WS_DESTINO"`; falha → `die "não consegui buscar o $WS_DESTINO do origin"`). Sem origin, ou sem o arquivo no destino, nada está entregue (só o `c0` é próximo).
  - `ws_ciclos_marca <arquivo> <id> <estado>` → regrava só a célula `Estado` do ciclo, preservando o resto do arquivo e o fim de linha (CRLF se a primeira linha tinha); estado fora de `pendente|em-andamento|entregue` ou id inexistente → `die`.
  - CLI: `ws ciclos atual`, `ws ciclos proximos <arquivo>`, `ws ciclos marca <arquivo> <id> <estado>`.

- [ ] **Step 1: Escrever os testes que falham.** Fixture: `fx_ready`, `mk_ciclos`, commit e push no `main`.
  - `test_atual_na_branch_da_feature_e_c0`, `test_atual_em_branch_de_ciclo` (`ws-001-x-c2` → `c2`), `test_atual_ignora_revisao` (`ws-001-x-r1-c2` → `c2`), `test_atual_fora_de_feature_falha` (`main` → `fora de uma branch de feature: main`).
  - `test_proximos_sem_o_arquivo_no_main_so_oferece_c0` (**Review Focus 2**): o arquivo só no workspace local, não no `origin/main` → saída `c0`.
  - `test_proximos_depois_do_c0_entregue_libera_c1_e_c3_em_paralelo`: o `main` tem o arquivo com o `c0` `entregue`; local tudo `pendente` → saída `c1` e `c3`, e **não** `c2`.
  - `test_proximos_c2_espera_o_c1_no_main`: o `c1` só `entregue` localmente, não no `main` → `c2` não aparece.
  - `test_proximos_ignora_o_que_ja_esta_em_andamento`: o `c1` local `em-andamento` → não aparece.
  - `test_marca_muda_so_a_celula_do_estado`: `diff` entre antes e depois mostra uma única linha mudada, com `em-andamento`.
  - `test_marca_preserva_crlf` (**Review Focus 1**): arquivo com CRLF antes → todas as linhas ainda terminam em `\r` depois (`grep -c $'\r$'` igual ao total de linhas).
  - `test_marca_estado_invalido_e_id_inexistente_falham`.

- [ ] **Step 2: Rodar e ver falhar** — `bash tools/ws/tests/run.sh tools/ws/tests/test_ciclos.sh` → `FALHA` nos testes novos.

- [ ] **Step 3: Implementar** as três funções e despachá-las em `ws_ciclos`. Para ler o arquivo do destino: `git show "origin/$WS_DESTINO:<caminho>"` para um arquivo temporário e `ws_ciclos_le` nele (use `mktemp` e limpe com `trap`, como `ws_refactor_temp`). Para a gravação, reaproveite `ws_refactor_grava` (preserva o CRLF).

- [ ] **Step 4: Rodar e ver passar** — todos ok, 0 falha.

- [ ] **Step 5: Commit**

```bash
git add tools/ws/lib/ciclos.sh tools/ws/tests/test_ciclos.sh
git commit -m "ciclos: ciclo atual, próximos ciclos pelo main e marca de estado"
```

---

### Task 4: Medição do tamanho do ciclo

**Files:**
- Modify: `tools/ws/lib/ciclos.sh`, `tools/ws/tests/test_ciclos.sh`

**Interfaces:**
- Consumes: `ws_ciclos_ini`, `ws_ciclos_classifica`, `ws_ciclos_le`.
- Produces: `ws_ciclos_medir <arquivo> <id>` → uma linha `ARQUIVOS=<n> LINHAS=<n> RESULTADO=<ok|aviso|estourou> DECISAO=<valor>`, sempre com código 0 (é informação, não bloqueio). Mede `git diff --numstat <base>...HEAD`, com `<base>` = `origin/$WS_DESTINO` (ou `$WS_DESTINO` sem origin); ignora os caminhos que começam por qualquer prefixo de `[medicao] excluir`; `ARQUIVOS` conta os arquivos restantes (binário, que o numstat mostra como `-`, conta como arquivo com 0 linhas); `LINHAS` soma adicionadas e removidas. `DECISAO` é `-` quando o resultado não é `estourou`; quando é `estourou`, vale a célula `Decisão de tamanho` do ciclo, ou `pendente` se ela for `-`. Id inexistente → `die`. CLI: `ws ciclos medir <arquivo> <id>`.

- [ ] **Step 1: Escrever os testes que falham** (fixture com `fx_ready`, `mk_ini`, `mk_ciclos`, e uma branch com mudanças):
  - `test_medir_conta_arquivos_e_linhas_do_diff`: dois arquivos novos em `repos/r1/` com 3 e 5 linhas → `ARQUIVOS=2 LINHAS=8 RESULTADO=ok DECISAO=-`.
  - `test_medir_ignora_atlas_specs_e_flags`: mudanças só em `docs/atlas/x.md`, `specs/ws-001-x/tasks.md` e `flags/registry.md` → `ARQUIVOS=0 LINHAS=0 RESULTADO=ok` (**Review Focus 4**).
  - `test_medir_diff_vazio_e_zero`.
  - `test_medir_binario_conta_como_arquivo_sem_linhas`: um `.png` de bytes aleatórios → `ARQUIVOS=1 LINHAS=0`.
  - `test_medir_estourou_sem_decisao_fica_pendente`: ini com `arquivos = 1` e `margem_percentual = 0` e dois arquivos → `RESULTADO=estourou DECISAO=pendente`.
  - `test_medir_estourou_com_decisao_mostra_a_decisao`: a célula `Decisão de tamanho` do ciclo é `aceito` → `DECISAO=aceito`.
  - `test_medir_aviso_nao_pede_decisao`: `RESULTADO=aviso DECISAO=-`.
  - `test_medir_id_inexistente_falha`.

- [ ] **Step 2: Rodar e ver falhar** → `FALHA` nos testes novos.

- [ ] **Step 3: Implementar** `ws_ciclos_medir` e despachar `medir`. Para o numstat com nomes de arquivo, use `-z` ou `--numstat` sem renomeação (`--no-renames`) para não somar um rename duas vezes.

- [ ] **Step 4: Rodar e ver passar** — todos ok, 0 falha.

- [ ] **Step 5: Commit**

```bash
git add tools/ws/lib/ciclos.sh tools/ws/tests/test_ciclos.sh
git commit -m "ciclos: medição do diff do ciclo contra o limite"
```

---

### Task 5: Início do ciclo e a branch `-c<N>`

**Files:**
- Modify: `tools/ws/lib/ciclos.sh`, `tools/ws/tests/test_ciclos.sh`, `tools/speckit/ws/scripts/bash/ws-feature.sh` (linhas 107 e 160, o `sed -E 's/-r[0-9]+$//'`), `tools/ws/tests/test_speckit_feature.sh`

**Interfaces:**
- Consumes: `ws_ciclos_proximos`, `ws_ciclos_marca`, `ws_start` (de `start.sh`).
- Produces: `ws_ciclos_iniciar <arquivo> <id>` → cria a branch `<pasta da feature>-<id>` com `ws_start` e marca o ciclo `em-andamento` (mudança não commitada, vai no PR do ciclo); imprime a branch. Falhas com `die`: `c0 é a branch da própria feature: ela já existe`; `ciclo <id> não existe`; `ciclo <id> já está <estado>`; `ciclo <id> espera: <ids das dependências ainda não entregues no main>`. A pasta da feature é o nome do diretório do `cycles.md`. CLI: `ws ciclos iniciar <arquivo> <id>`.
- `ws-feature.sh`: o sufixo `-c<N>` passa a ser removido junto com `-r<k>` ao descobrir a feature da branch atual.

- [ ] **Step 1: Escrever os testes que falham.**
  - `test_iniciar_cria_a_branch_do_ciclo_e_marca_em_andamento`: o `main` tem o arquivo com o `c0` `entregue`; `ws ciclos iniciar specs/ws-001-x/cycles.md c1` → branch atual `ws-001-x-c1`, saída igual a esse nome, e `ws ciclos proximos` não lista mais `c1` (está `em-andamento`).
  - `test_iniciar_c2_espera_o_c1`: falha com `ciclo c2 espera: c1`.
  - `test_iniciar_c0_falha`, `test_iniciar_ciclo_inexistente_falha`, `test_iniciar_ciclo_ja_em_andamento_falha`.
  - Em `test_speckit_feature.sh`, copiar o teste existente que roda o hook na branch de revisão (procure `-r1` no arquivo) trocando a branch por `ws-001-x-c1`: o hook **não** trata a branch de ciclo como outra feature (**Review Focus 5**), com as mesmas asserts do teste de `-r1`.

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_ciclos.sh tools/ws/tests/test_speckit_feature.sh`
Expected: `FALHA` nos testes novos.

- [ ] **Step 3: Implementar** `ws_ciclos_iniciar` (despachar `iniciar`) e trocar os dois `sed -E 's/-r[0-9]+$//'` de `ws-feature.sh` por `sed -E 's/(-r[0-9]+|-c[0-9]+)+$//'`.

- [ ] **Step 4: Rodar e ver passar** — todos ok, 0 falha, sem regressão nos testes de feature já existentes.

- [ ] **Step 5: Commit**

```bash
git add tools/ws/lib/ciclos.sh tools/ws/tests/test_ciclos.sh tools/speckit/ws/scripts/bash/ws-feature.sh tools/ws/tests/test_speckit_feature.sh
git commit -m "ciclos: ws ciclos iniciar e a branch -c<N> reconhecida pelo hook da feature"
```

---

### Task 6: Registro de feature flags

**Files:**
- Create: `tools/ws/lib/flags.sh`, `flags/registry.md`, `tools/ws/tests/test_flags.sh`
- Modify: `tools/ws/lib/ciclos.sh` (despacho de `flag-*`)

**Interfaces:**
- Consumes: `WS_FLAG_NOME`, `ws_ciclos_le` (Task 2).
- Produces:
  - `flags/registry.md`, criado com esta tabela vazia e um parágrafo curto (não é harness, pode ser editado durante o trabalho):
    ```
    | Flag | Feature | Ciclo | Lida em | Estado | Remoção |
    |---|---|---|---|---|---|
    ```
  - `ws_flag_registra <flag> <repo:arquivo>` → acrescenta a linha `| <flag> | ws-NNN | c<N> | <repo:arquivo> | ativa | - |` (Feature e Ciclo saem do nome da flag), mantém a tabela em ordem por flag; nome fora de `WS_FLAG_NOME` ou repetido → `die`.
  - `ws_flag_confere <arquivo>` → para cada ciclo com `Segurança` `flag`: a flag tem de estar no registro, `ativa`, com o `Ciclo` igual e a `Feature` igual ao número da pasta do arquivo; para cada flag `ativa` do registro dessa feature: tem de aparecer no `cycles.md`. Erros em stderr, `flag: <detalhe>`, e saída 1.
  - `ws_flag_remove <flag> <slug-do-refactor>` → `Estado` vira `removida` e `Remoção` vira o slug; flag inexistente ou já removida → `die`.
  - CLI: `ws ciclos flag-registra`, `flag-confere`, `flag-remove`.

- [ ] **Step 1: Escrever os testes que falham** em `test_flags.sh` (fixture com `mk_ciclos`; o helper pode ser copiado do `test_ciclos.sh` ou movido para o `tests/lib.sh`):
  - `test_flag_registra_cria_a_linha_ordenada`: duas flags em ordem trocada → a tabela sai ordenada, com `ativa` e `-`.
  - `test_flag_registra_recusa_nome_invalido_e_repetido`.
  - `test_flag_confere_passa_quando_registro_e_ciclos_batem`: `ws-001.c2.tela-nova` registrada → ok.
  - `test_flag_confere_falha_com_flag_nao_registrada` e `..._com_flag_de_outro_ciclo` e `..._com_flag_registrada_que_o_cycles_nao_usa`.
  - `test_flag_confere_ignora_flag_de_outra_feature` e `..._ignora_flag_removida`.
  - `test_flag_remove_marca_removida_com_o_slug`, `..._flag_inexistente_falha`.
  - `test_flags_registry_tolera_crlf`.

- [ ] **Step 2: Rodar e ver falhar** — `bash tools/ws/tests/run.sh tools/ws/tests/test_flags.sh` → `FALHA`.

- [ ] **Step 3: Implementar** `lib/flags.sh` e o despacho; criar `flags/registry.md` (a pasta `flags/` entra na lista de exclusão da medição, já no `workspace.ciclos.ini`).

- [ ] **Step 4: Rodar e ver passar** — todos ok, 0 falha.

- [ ] **Step 5: Commit**

```bash
git add tools/ws/lib/flags.sh tools/ws/lib/ciclos.sh flags/registry.md tools/ws/tests/test_flags.sh
git commit -m "ciclos: registro de feature flags e ws ciclos flag-*"
```

---

### Task 7: Comandos da extensão `ws`

**Files:**
- Create: `tools/speckit/ws/commands/speckit.ws.cycles.md`, `tools/speckit/ws/commands/speckit.ws.cycle-start.md`, `tools/ws/tests/test_speckit_ciclos.sh`
- Modify: `tools/speckit/ws/extension.yml` (versão `1.9.0`; os dois comandos em `provides.commands`), `tools/speckit/ws/commands/speckit.ws.converge.md`

**Interfaces:**
- Consumes: o CLI `ws ciclos ...` das Tasks 1 a 6.
- Produces: as skills `/speckit-ws-cycles` e `/speckit-ws-cycle-start` (geradas na Task 10). Os dois arquivos começam como `speckit.ws.feature.md` (frontmatter com `description`, linha de **Idioma**, bloco `User Input`).

`speckit.ws.cycles.md` precisa mandar o agente, nesta ordem:
1. **Antes de tudo:** estar numa branch `ws-NNN-*` (`tools/ws/ws ciclos atual` devolve `c0`); existir `spec.md` e `plan.md` na pasta da feature; **não** existir `tasks.md` (senão parar: o comando vale antes do `/speckit-tasks`). Com `cycles.md` já existente, revisá-lo sem perder o `Estado`.
2. **Ler** a spec (histórias, prioridades, FRs, "Repos afetados", bloqueios), o plan (plano por repo, contratos) e a constitution.
3. **Mapa por história:** repos, objetos de banco compartilhados, FRs, cards, e a estimativa de arquivos e linhas pelo plan (módulos, controllers, telas, scripts), classificada com `tools/ws/ws ciclos classifica <arquivos> <linhas>`; dizer a incerteza.
4. **Ciclo 0 (abertura):** leva a pasta da feature e a fundação compartilhada (o que não pertence a nenhuma história).
5. **Dependências:** propor lendo a spec e o plan; quem depende de quem só começa com o anterior no `main`.
6. **Segurança de cada ciclo, nesta ordem de preferência:** (a) `ordem` (a posição no grafo basta); (b) `inerte` (o caminho novo só é alcançável quando algo o liga e o padrão mantém o comportamento de hoje); (c) `flag` (nome `ws-NNN.c<N>.<nome>`, com a justificativa, e a task de criar a flag dentro do ciclo, com `ws ciclos flag-registra`). Nunca uma regra fixa de "interruptor por último": a ordem sai da análise da feature.
7. **Bloqueios externos** do texto da spec e do plan; perguntar ao time quando não achar. Não assumir um card por história.
8. **Gravar** o `cycles.md` no formato da Task 2 com `Confirmado: não` e rodar `tools/ws/ws ciclos validar`; corrigir os erros.
9. **Confirmação:** mostrar a tabela e as justificativas e pedir que o time confirme ou corrija dependências, segurança e avisos de tamanho. Para cada ciclo com `Tamanho` `estourou`, oferecer **aceitar**, **dividir a história na spec** (o usuário roda `/speckit-specify` e volta) ou **marcar uma exceção registrada** (grava `excecao: <motivo>` na coluna `Decisão de tamanho`).
10. **Depois da confirmação:** `Confirmado: sim (<data>, <usuário do git>)` e `ws ciclos validar --confirmado`; dizer que o próximo passo é `/speckit-tasks`.
11. **Nunca** alterar `spec.md` nem `plan.md`.

`speckit.ws.cycle-start.md`: rodar `tools/ws/ws ciclos proximos specs/<pasta>/cycles.md`; sem argumento e com mais de um próximo, perguntar qual (lembrar que dá para dois devs trabalharem em paralelo); rodar `tools/ws/ws ciclos iniciar`; informar a branch e que o próximo passo é `/speckit-implement`.

`speckit.ws.converge.md`: acrescentar, depois do passo do envio, que, existindo `cycles.md`, o agente mostra `tools/ws/ws ciclos proximos` para o time saber o que destrava depois do merge.

- [ ] **Step 1: Escrever os testes estáticos que falham** em `test_speckit_ciclos.sh` (leem os arquivos da fonte, sem rede):
  - `test_extensao_ws_lista_os_comandos_de_ciclos`: `extension.yml` contém `version: "1.9.0"`, `name: speckit.ws.cycles` e `name: speckit.ws.cycle-start`.
  - `test_comando_cycles_cobre_o_roteiro`: o arquivo contém `ws ciclos classifica`, `ws ciclos validar`, `--confirmado`, `Confirmado: sim`, `aceitar`, `dividir`, `exceção`, `/speckit-tasks`, `flag-registra`, `tasks.md`.
  - `test_comando_cycle_start_roda_o_cli`: contém `ws ciclos proximos`, `ws ciclos iniciar` e `/speckit-implement`.
  - `test_converge_da_ws_mostra_os_proximos_ciclos`: `speckit.ws.converge.md` contém `ws ciclos proximos`.
  - `test_comandos_de_ciclos_pedem_portugues_e_nao_propoem_mudar_o_harness`: os dois arquivos contêm `português do Brasil` e `Não proponha mudanças no harness`.

- [ ] **Step 2: Rodar e ver falhar** — `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_ciclos.sh` → `FALHA`.

- [ ] **Step 3: Escrever** os dois comandos, o ajuste do converge e o `extension.yml` (sem hooks novos).

- [ ] **Step 4: Rodar e ver passar** — todos ok, 0 falha.

- [ ] **Step 5: Commit**

```bash
git add tools/speckit/ws tools/ws/tests/test_speckit_ciclos.sh
git commit -m "ciclos: comandos speckit.ws.cycles e speckit.ws.cycle-start na extensão ws"
```

---

### Task 8: Preset `multirepo`: tasks, implement e converge por ciclo

**Files:**
- Create: `tools/speckit/multirepo/commands/speckit.tasks.md`, `tools/speckit/multirepo/commands/speckit.implement.md`, `tools/speckit/multirepo/commands/speckit.converge.md`
- Modify: `tools/speckit/multirepo/preset.yml` (versão `1.1.0`; três comandos `strategy: wrap`), `tools/speckit/multirepo/templates/tasks-template.md`, `tools/ws/tests/test_speckit_ciclos.sh`

**Interfaces:**
- Consumes: `cycles.md` e o CLI `ws ciclos`.
- Produces: o formato do `tasks.md` por ciclo e as regras dos três comandos, cada arquivo no molde de `speckit.specify.md` (frontmatter, linha de **Idioma**, regras numeradas e `{CORE_TEMPLATE}` no fim).

Regras de cada wrap:
- **`speckit.tasks`:** parar se não existir o `cycles.md` ou se `tools/ws/ws ciclos validar <cycles.md> --confirmado` falhar, pedindo o `/speckit-ws-cycles`. Gerar o `tasks.md` **uma vez**, com uma fase por ciclo na ordem do `cycles.md`: `## Ciclo <id>: <história>`; dentro dele, os grupos por repo (marcadores `[repos/<repo>]` e `[workspace]`), cada um terminando na verificação de build e testes do repo. O `c0` leva a abertura e a fundação. Uma task de criar a flag fica no ciclo da flag e roda `tools/ws/ws ciclos flag-registra <flag> <repo:arquivo>`. Nenhuma task depende de task de ciclo posterior.
- **`speckit.implement`:** descobrir o ciclo com `tools/ws/ws ciclos atual` e executar **só** as tasks da seção desse ciclo (o `speckit-implement` continua rodando os testes e validando que passam); parar se a seção estiver vazia.
- **`speckit.converge`:** limitar a leitura da spec, do plan e das tasks à história do ciclo atual; acrescentar as tasks de convergência **dentro da seção do ciclo**, nunca como fase final da feature inteira; rodar `tools/ws/ws ciclos medir <cycles.md> <id>` e, com `RESULTADO=estourou` e `DECISAO=pendente`, perguntar ao time (aceitar, dividir na spec ou exceção registrada) e gravar a decisão na coluna `Decisão de tamanho`; conferir a segurança prometida (`inerte`: o caminho novo só é alcançável quando algo o liga e o padrão mantém o comportamento de hoje; `flag`: a leitura segue o padrão do `docs/harness/3-alem-do-basico.md` e `tools/ws/ws ciclos flag-confere` passa); com tudo certo e sem tasks pendentes, rodar `tools/ws/ws ciclos marca <cycles.md> <id> entregue`.
- `tasks-template.md` (do preset): acrescentar a convenção "uma fase por ciclo, com os grupos por repo dentro dela".

- [ ] **Step 1: Escrever os testes estáticos que falham** (em `test_speckit_ciclos.sh`):
  - `test_preset_multirepo_envolve_tasks_implement_e_converge`: `preset.yml` contém `version: "1.1.0"` e, para cada um, `name: "speckit.tasks"`, `"speckit.implement"`, `"speckit.converge"` com `strategy: "wrap"`.
  - `test_wrap_tasks_exige_cycles_confirmado`: contém `ws ciclos validar`, `--confirmado`, `/speckit-ws-cycles`, `## Ciclo`, `flag-registra`, `{CORE_TEMPLATE}`.
  - `test_wrap_implement_so_executa_o_ciclo_atual`: contém `ws ciclos atual` e `{CORE_TEMPLATE}`.
  - `test_wrap_converge_limita_ao_ciclo_e_mede`: contém `ws ciclos atual`, `ws ciclos medir`, `DECISAO=pendente`, `ws ciclos flag-confere`, `ws ciclos marca`, `entregue`, `{CORE_TEMPLATE}`.
  - `test_template_de_tasks_tem_a_convencao_de_ciclos`: `tasks-template.md` contém `uma fase por ciclo`.

- [ ] **Step 2: Rodar e ver falhar** — `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_ciclos.sh` → `FALHA` nos testes novos.

- [ ] **Step 3: Escrever** os três wraps, o `preset.yml` e o `tasks-template.md`.

- [ ] **Step 4: Rodar e ver passar** — todos ok, 0 falha.

- [ ] **Step 5: Commit**

```bash
git add tools/speckit/multirepo tools/ws/tests/test_speckit_ciclos.sh
git commit -m "ciclos: preset multirepo envolve tasks, implement e converge por ciclo"
```

---

### Task 9: Documentação, `AGENTS.md` e ADR

**Files:**
- Create: `docs/adr/0004-ciclos-por-historia.md`
- Modify: `AGENTS.md`, `docs/harness/3-alem-do-basico.md`, `docs/harness/1-comecar.md`, `README.md`

**Interfaces:**
- Consumes: o comportamento das Tasks 1 a 8.
- Produces: o texto que o time lê.

Conteúdo:
- **ADR 0004** (status **proposta**, até a aprovação humana, como a constitution IV exige): contexto (PRs gigantes), decisão (ciclo por história, ciclo 0, estado pelo `main`, flag só quando a ordem e o padrão não bastam), consequências (um PR a mais para a abertura; o `converge` e o `implement` passam a ser por ciclo).
- **`AGENTS.md`:** nova seção "Ciclos por história", no molde das de bug e refactor: quando usar, o fluxo `specify → plan → /speckit-ws-cycles → /speckit-tasks → (por ciclo) /speckit-ws-cycle-start → /speckit-implement → /speckit-converge → /ws-commit-push → /ws-pr-homolog → /ws-pr-main`, onde ficam `cycles.md`, `workspace.ciclos.ini` e `flags/registry.md` (**não é harness**: pode ser editado durante o trabalho), e "nunca edite o `Estado` à mão: use `tools/ws/ws ciclos marca`".
- **`docs/harness/3-alem-do-basico.md`:** duas seções novas: "Dividir a feature em ciclos" (o fluxo, o paralelismo, o limite e as três saídas quando estoura) e "Feature flag de feature nova" (o padrão por stack das **Decisões do construtor** deste plano, o registro e que remover a flag exige um ciclo de refactor, que roda `tools/ws/ws ciclos flag-remove <flag> <slug>`).
- **`docs/harness/1-comecar.md` e `README.md`:** uma linha no "Quero…" apontando para a seção nova.

- [ ] **Step 1: Escrever o teste que falha** em `test_speckit_ciclos.sh`: `test_agents_e_docs_citam_o_fluxo_de_ciclos` confere que `AGENTS.md` contém `## Ciclos por história`, `/speckit-ws-cycles`, `/speckit-ws-cycle-start`, `flags/registry.md`; que `docs/harness/3-alem-do-basico.md` contém `## Dividir a feature em ciclos` e `## Feature flag de feature nova`; e que `docs/adr/0004-ciclos-por-historia.md` existe e contém `Status:** proposta`.

- [ ] **Step 2: Rodar e ver falhar** — `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_ciclos.sh` → `FALHA` no teste novo.

- [ ] **Step 3: Escrever** os textos acima, em português, sem referenciar caminhos que não existam.

- [ ] **Step 4: Rodar a suíte da doc e os testes**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_ciclos.sh tools/ws/tests/test_docs_referencias.sh tools/ws/tests/test_nomes_antigos.sh` e `python tools/ws/tests/docs_referencias.py .`
Expected: `0 falha(s)` e o verificador sem erros (se ele acusar um caminho, o texto referencia algo que não existe).

- [ ] **Step 5: Commit**

```bash
git add docs/adr/0004-ciclos-por-historia.md AGENTS.md docs/harness README.md tools/ws/tests/test_speckit_ciclos.sh
git commit -m "ciclos: documentação em camadas, AGENTS.md e ADR 0004 (proposta)"
```

---

### Task 10: Reinstalação do Spec Kit e testes de instalação

**Files:**
- Modify: `tools/ws/tests/test_speckit_install.sh`; gerados pela reinstalação: `.specify/`, `.claude/skills/`

**Interfaces:**
- Consumes: as fontes das Tasks 7 e 8.
- Produces: `.specify/extensions/ws` (1.9.0), `.specify/presets/multirepo` (1.1.0) e as skills `speckit-ws-cycles` e `speckit-ws-cycle-start` instaladas e commitadas.

- [ ] **Step 1: Escrever o teste de instalação que falha** (só roda com `WS_TEST_REDE=1`, como os vizinhos): `test_speckit_instala_os_ciclos` em `test_speckit_install.sh` — depois de `fx_speckit`, confere que existem `.claude/skills/speckit-ws-cycles/SKILL.md` e `.claude/skills/speckit-ws-cycle-start/SKILL.md`, que `.claude/skills/speckit-tasks/SKILL.md` contém `## Ciclo` e `ws ciclos validar`, que `speckit-implement` contém `ws ciclos atual` e que `speckit-converge` contém ``ws ciclos medir``.

- [ ] **Step 2: Rodar e ver falhar**

Run: `WS_TEST_REDE=1 WS_TEST=test_speckit_instala_os_ciclos bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_install.sh`
Expected: `FALHA` (as skills ainda não existem na fixture instalada).

- [ ] **Step 3: Reinstalar no worktree** e conferir que o wrap funcionou (se o Spec Kit recusar o `wrap` de `speckit.tasks`, `speckit.implement` ou `speckit.converge`, **pare e avise o usuário**: o desenho assume que esses três são envolvíveis como o `speckit.specify`):

```bash
tools/ws/ws speckit
git status --short .specify .claude/skills
```
Expected: mudanças só em `.specify/` e `.claude/skills/` (as novas skills e os três `speckit-*` reescritos).

- [ ] **Step 4: Rodar a suíte inteira, com a rede**

Run: `WS_TEST_REDE=1 bash tools/ws/tests/run.sh`
Expected: `0 falha(s)`.

- [ ] **Step 5: Commit**

```bash
git add tools/ws/tests/test_speckit_install.sh .specify .claude/skills
git commit -m "ciclos: reinstala o Spec Kit com a extensão ws 1.9.0 e o preset multirepo 1.1.0"
```

---

### Task 11: Validação na `ws-003`

**Files:**
- Create (neste repo de discovery): `docs/discovery/sp10-validacao.md`

**Interfaces:**
- Consumes: tudo acima. Roda num clone **descartável** da branch `ws-003-b2c-operacao-ecommerce` com o harness novo (o checkout do usuário não é tocado).

- [ ] **Step 1: Preparar o clone descartável** em `C:\ws\wt-ciclos-e2e`, criado a partir do clone `C:\ws\industria-logistica.wms.workspace` (nunca do `dsv`): `git worktree add` da `origin/ws-003-b2c-operacao-ecommerce` e `git merge --no-edit harness/ciclos-por-historia` (traz o harness novo; o conflito, se houver, só pode estar em `.specify/` e `.claude/skills/`).

- [ ] **Step 2: Rodar `/speckit-ws-cycles`** na `ws-003` e conferir, **como ilustração e não como critério rígido**:
  - o `cycles.md` passa em `ws ciclos validar`;
  - `c0` de abertura com a fundação (`CodigoBarra`, movimentação por ID de item, `prConsultaDadosMovimentacao` aditiva);
  - as dependências coerentes com a spec (US2 → US3 → US4; US5 e US6 → US7; US8 depende do modo e do saldo);
  - a US1 em último, com a justificativa de que a gravação do modo SKU liga o comportamento (**resultado da análise, não regra**);
  - o bloqueio externo da emenda do AWX na US1;
  - o aviso de tamanho para a US6 e a US7;
  - nenhum card assumido por história.

- [ ] **Step 3: Rodar o ciclo de ponta a ponta no `c0` e no primeiro ciclo seguinte** (`/speckit-tasks` uma vez, `/speckit-ws-cycle-start`, `/speckit-implement` só no ciclo, `/speckit-converge`): conferir que o `implement` e o `converge` ficam no ciclo, que o `converge` mede o diff e grava `entregue`, e que `ws ciclos proximos` libera o que depende do `c0`. Registrar o custo.

- [ ] **Step 4: Registrar** o resultado e os achados em `docs/discovery/sp10-validacao.md` (itens ok, falhas, custo), no molde de `sp9-validacao.md`. Corrigir no harness o que falhar, com teste, antes de seguir.

- [ ] **Step 5: Limpar** o worktree descartável (`git worktree remove`) e **avisar o usuário** do que sobrou. Abrir o PR da `harness/ciclos-por-historia` fica a cargo do usuário (`/ws-pr-homolog` e `/ws-pr-main`).

---

## Self-review

- **Cobertura da spec:** comando entre `plan` e `tasks` (Tasks 7, 8); ciclo por história com tasks, implement e converge (8); uma feature, N histórias (7); limite parametrizável no arquivo do harness, como aviso (1, 4); tasks uma vez, agrupadas (8); dependências propostas e confirmadas, paralelismo e "só depois do merge no `main`" (3, 5, 7); segurança decidida no plano de ciclos e conferida no `converge` (7, 8); flag atrás quando a 1 só faz sentido com a 2 (7); flag criada no ciclo, registro próprio, remoção por refactor (6, 9); padrão obrigatório, sem biblioteca (9); história que estoura o limite, com três saídas (4, 7, 8); a `ws-003` como exemplo, não regra (11). Não-metas respeitadas: nenhum comando de verify novo, nenhuma biblioteca, retomada de feature com tasks fora.
- **Consistência de nomes:** `ws_ciclos_*` e `ws_flag_*`; `WS_CICLOS_CAB`, `WS_CICLO_ID`, `WS_FLAG_NOME`; estados `pendente|em-andamento|entregue`; `c<N>`; `<feature>-c<N>`; `DECISAO=pendente` aparece igual nas Tasks 4 e 8.
- **Risco aberto:** o `wrap` de `speckit.tasks`, `speckit.implement` e `speckit.converge` só se confirma na Task 10 (Step 3), que manda parar e avisar se o Spec Kit recusar.
- **A confirmar pelo usuário na revisão do plano:** o ciclo 0 sempre presente; o estado `entregue` gravado no PR do ciclo; o padrão de flag por stack; os valores iniciais do limite (40 arquivos, 1500 linhas, 25% de margem).
