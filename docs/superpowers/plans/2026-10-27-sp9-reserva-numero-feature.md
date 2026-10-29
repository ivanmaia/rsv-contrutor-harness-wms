# SP9: Reserva atômica do número da feature — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Duas estações rodando `/specify` ao mesmo tempo nunca mais saem com o mesmo número `ws-NNN` para features diferentes.

**Architecture:** Antes de montar o nome da branch nova, a estação reserva o número no `origin` com um push atômico de um commit órfão único numa ref fora de `refs/heads` (`refs/ws-reserved/<NNN>`); se a ref já existir (outra estação chegou primeiro), tenta o número seguinte. Sem origin, pula a reserva.

**Tech Stack:** bash (Git for Windows), harness de testes próprio em `tools/ws/tests/` (fixtures com remotos bare locais, sem rede).

**Spec:** `docs/superpowers/specs/2026-10-27-sp9-reserva-numero-feature-design.md` (repo de discovery), seções 3, 3.1 e 4. O mecanismo já foi testado contra o Azure DevOps real antes deste plano: `docs/discovery/sp9-teste-azure.md`. O código fica em `C:\src\wms-workspace`, fonte em `tools/speckit/ws/scripts/bash/ws-feature.sh` (copiado para `.specify/extensions/ws/...` pelo `ws speckit`).

## Global Constraints

- **Base:** um worktree novo `C:\src\wms-workspace-sp9`, a partir do `origin/main` mais novo, na branch `harness/sp9-reserva-numero`. Não mexa em `C:\src\wms-workspace`.
- **Escopo:** só `tools/speckit/ws/scripts/bash/ws-feature.sh` e sua cópia instalada em `.specify/extensions/ws/scripts/bash/ws-feature.sh`. Não mexer em `ws-bug-start.sh` nem `ws-refactor-start.sh` (fora de escopo, seção 2 do design).
- **Ref de reserva:** `refs/ws-reserved/<NNN>` (três dígitos, sem o prefixo `ws-`), criada com `git commit-tree` sobre a árvore vazia (`git hash-object -t tree /dev/null`), mensagem única por tentativa (inclui `$$` e `$RANDOM`), sem pai.
- **Sem origin:** nenhuma tentativa de push; comportamento idêntico ao atual.
- Nada no CLI `tools/ws/ws` muda; só o hook `ws-feature.sh`.
- **Colisão = só três padrões** na saída do push: `non-fast-forward`, `fetch first` e `TF401028` (as três formas que o teste no Azure mostrou, spec seção 3.1). Qualquer outra falha, inclusive outro `[remote rejected]`, para o fluxo com `fail`. Nunca casar com `*rejected*` genérico.

## Review Focus

- Duas estações disputando o mesmo número com o **mesmo commit de base** (caso comum: ambas acabaram de sincronizar o mesmo `origin/main`) — se a reserva usasse o commit da base em vez de um commit órfão único, o segundo push sairia "Everything up-to-date" (sucesso falso), devolvendo a mesma colisão que o SP9 existe para resolver.
- Três ou mais estações disputando o mesmo número em sequência (não só duas) — o laço de retry precisa avançar por todos os números já reservados, não só tentar uma vez a mais.
- Workspace sem origin (uso local, sem rede) — não pode tentar nenhum push nem falhar por falta de remoto.
- Erro de push por motivo diferente de colisão (rede caiu, credencial expirou, permissão negada, política do repositório) — não pode ser silenciosamente interpretado como "número já reservado" e pular pro próximo, incrementando sem fim; tem que parar e avisar. Atenção especial a `[remote rejected]` com código TF diferente de `TF401028`: contém a palavra "rejected", mas não é colisão.
- A corrida simultânea de verdade (`TF401028`) não acontece com remoto bare local; os testes da Task 1 só a simulam com um hook `pre-receive`. A prova real é a Task 3, contra o Azure.
- As refs de reserva não podem vazar para `git ls-remote --heads` nem para qualquer lugar que liste branches (é o motivo de usar `refs/ws-reserved/`, fora de `refs/heads`).

---

### Task 1: Reservar o número antes de montar o nome da feature

**Files:**
- Modify: `tools/speckit/ws/scripts/bash/ws-feature.sh:179-199` (bloco `existing=false` até o `branch_taken` final)
- Test: `tools/ws/tests/test_speckit_feature.sh` (novos `test_*` no fim do arquivo)

**Interfaces:**
- Consumes: variável `base` já calculada em `ws-feature.sh:152` (`base=$(base_ref)`); função `branch_taken()` já existente (linhas 127-133); função `fail()` já existente (linha 44).
- Produces: função nova `reserve_num(n) -> bool` (0 = reservou, 1 = número já tomado por outra estação); a única consumidora é o próprio `ws-feature.sh`.

- [ ] **Step 1: Escrever o teste da colisão evitada**

Em `tools/ws/tests/test_speckit_feature.sh`, acrescentar (reaproveitando o padrão `outro_dev_spec` já existente no arquivo, linhas ~150-157, para criar o clone `$T/outro`):

```bash
# Outro dev reserva o número n no origin antes desta estação rodar o feature.
outro_dev_reserva() {
  rm -rf "$T/outro"
  git clone -q "$T/origin.git" "$T/outro"
  local tree sha
  tree=$(git -C "$T/outro" hash-object -t tree /dev/null)
  sha=$(git -C "$T/outro" commit-tree "$tree" -m "ws: reserva ws-$1 (outro dev)")
  git -C "$T/outro" push -q origin "$sha:refs/ws-reserved/$1"
}

test_duas_estacoes_nao_colidem_no_numero() {
  fx_ready
  outro_dev_reserva 001
  assert_ok feature --short-name "nova coisa" "Uma coisa nova"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "ws-002-nova-coisa"
}

test_varias_reservas_em_sequencia_avancam_o_numero() {
  fx_ready
  outro_dev_reserva 001
  outro_dev_reserva 002
  assert_ok feature --short-name "nova coisa" "Uma coisa nova"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "ws-003-nova-coisa"
}

test_reserva_nao_aparece_na_lista_de_branches() {
  fx_ready
  assert_ok feature --short-name "nova coisa" "Uma coisa nova"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "ws-001-nova-coisa"
  [ -n "$(git ls-remote origin "refs/ws-reserved/001")" ] || fail "a reserva ws-001 devia estar no origin"
  [ -z "$(git ls-remote --heads origin | grep ws-reserved)" ] || fail "a reserva vazou para refs/heads"
}

test_sem_origin_nao_tenta_reservar() {
  fx_ready
  git remote remove origin
  assert_ok feature --short-name "nova coisa" "Uma coisa nova sem origin"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "ws-001-nova-coisa"
}

# Trava a decisão do design (seção 3, ressalva técnica): mesmo quando a reserva do outro dev usa
# exatamente o commit da base (o caso que quebraria uma implementação ingênua, onde um segundo
# push do mesmo commit sai "Everything up-to-date" em vez de ser rejeitado), a reserva desta
# estação ainda assim não pode colidir.
test_reserva_do_outro_dev_com_o_commit_da_base_tambem_bloqueia() {
  fx_ready
  local outro="$T/outro" base_sha
  git clone -q "$T/origin.git" "$outro"
  base_sha=$(git -C "$outro" rev-parse HEAD)
  git -C "$outro" push -q origin "$base_sha:refs/ws-reserved/001"
  assert_ok feature --short-name "nova coisa" "Uma coisa nova"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "ws-002-nova-coisa"
}

# Hook pre-receive no origin bare que rejeita os pushes para a ref $1 (padrão de case) imprimindo $2
# (simula a mensagem do Azure).
origin_rejeita() {
  cat > "$T/origin.git/hooks/pre-receive" <<HOOK
#!/bin/sh
while read old new ref; do
  case "\$ref" in $1) echo "$2" >&2; exit 1 ;; esac
done
HOOK
  chmod +x "$T/origin.git/hooks/pre-receive"
}

# Simula a corrida de verdade no Azure (spec 3.1): o servidor rejeita a segunda estação com TF401028.
test_corrida_tf401028_avanca_o_numero() {
  fx_ready
  origin_rejeita "refs/ws-reserved/001" "TF401028: The reference 'refs/ws-reserved/001' has already been updated by another client, so you cannot update it. Please try again."
  assert_ok feature --short-name "nova coisa" "Uma coisa nova"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "ws-002-nova-coisa"
}

# Outro [remote rejected] (aqui, permissão negada) não é colisão: tem que parar, não avançar sem fim.
test_rejeicao_que_nao_e_colisao_para_o_fluxo() {
  fx_ready
  origin_rejeita "refs/ws-reserved/*" "TF401027: You need the Git 'CreateBranch' permission to perform this action."
  assert_fails feature --short-name "nova coisa" "Uma coisa nova"
  assert_contains "$OUT" "não consegui reservar o número"
  assert_contains "$OUT" "TF401027"
}
```

- [ ] **Step 2: Rodar os testes novos e ver que falham**

Run (a partir de `C:\src\wms-workspace-sp9`): `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_feature.sh`
Expected: `FALHA` em `test_duas_estacoes_nao_colidem_no_numero`, `test_varias_reservas_em_sequencia_avancam_o_numero`, `test_reserva_do_outro_dev_com_o_commit_da_base_tambem_bloqueia` e `test_corrida_tf401028_avanca_o_numero` (todos saem com `ws-001-nova-coisa`, porque hoje ninguém reserva nada), em `test_reserva_nao_aparece_na_lista_de_branches` (a ref de reserva não existe) e em `test_rejeicao_que_nao_e_colisao_para_o_fluxo` (hoje o feature não dá push, então não falha). Só `test_sem_origin_nao_tenta_reservar` passa por enquanto.

- [ ] **Step 3: Implementar `reserve_num` e o laço de reserva em `ws-feature.sh`**

Logo antes do bloco `existing=false` (linha 179 atual), acrescentar:

```bash
# n -> tenta reservar ws-$n no origin: cria um commit órfão com conteúdo único e dá push dele
# numa ref fora de refs/heads. 0 se conseguiu; 1 se $n já estava reservado por outra estação.
reserve_num() {
  local n=$1 tree sha out
  tree=$(git hash-object -t tree /dev/null)
  sha=$(git commit-tree "$tree" -m "ws: reserva $P$n ($$-$RANDOM)") \
    || fail "não consegui preparar a reserva de $P$n"
  out=$(git push origin "$sha:refs/ws-reserved/$n" 2>&1) && return 0
  # Só estas três formas são colisão (testado no Azure, spec 3.1); qualquer outra falha para o fluxo.
  case "$out" in
    *"(non-fast-forward)"*|*"(fetch first)"*|*TF401028*) return 1 ;;
    *) fail "não consegui reservar o número $P$n no origin: $out" ;;
  esac
}
```

(O remote chama-se sempre `origin` neste script — ver `base_ref()`, linha 58-64, e `branch_taken()`, linha 127-133, que já assumem isso.)

Trocar o bloco existente:

```bash
  existing=false
  slug=$(slugify "${short:-$desc}")
  [ -n "$slug" ] || fail "não consegui gerar um nome curto a partir de: ${short:-$desc}"
  name="$P$(next_num)-$slug"
  branch=$name
  ! branch_taken "$branch" || fail "a branch $branch já existe"
```

por:

```bash
  existing=false
  slug=$(slugify "${short:-$desc}")
  [ -n "$slug" ] || fail "não consegui gerar um nome curto a partir de: ${short:-$desc}"
  n=$(next_num)
  if git remote get-url origin >/dev/null 2>&1; then
    # Teto de tentativas: um origin que responde colisão a tudo não pode prender o laço para sempre.
    tries=1
    while ! reserve_num "$n"; do
      [ "$tries" -lt 20 ] || fail "não consegui reservar um número livre depois de 20 tentativas (último: $P$n)"
      tries=$((tries + 1))
      n=$(printf '%03d' $((10#$n + 1)))
    done
  fi
  name="$P$n-$slug"
  branch=$name
  ! branch_taken "$branch" || fail "a branch $branch já existe"
```

**Adendo de 2026-10-28 (teto de tentativas):** a versão original deste bloco não tinha teto (`while ! reserve_num "$n"; do n=...; done`). A revisão da implementação mostrou que um origin que responde colisão a tudo prende o laço para sempre, e que a regressão `*rejected*` no `case` só era pega porque o teste travava, não por uma FALHA. O teto de 20 entrou junto com o teste `test_colisao_sem_fim_para_no_teto_de_tentativas` (hook `pre-receive` que rejeita toda reserva com `TF401028`; espera `fail` com "depois de 20 tentativas" e o número `ws-020`). Spec, seção 4.

As mensagens do `case` foram capturadas no Azure real com Git 2.54.0 para Windows (`docs/discovery/sp9-teste-azure.md`): `(non-fast-forward)` e `(fetch first)` vêm do cliente; `TF401028` vem do servidor, como `[remote rejected]`. Não troque nenhuma delas por um padrão mais genérico.

- [ ] **Step 4: Rodar os testes de novo e ver que passam**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_feature.sh`
Expected: os oito testes novos (os sete acima e o do teto, ver adendo) `ok` e nenhuma regressão nos testes já existentes do arquivo.

- [ ] **Step 5: Rodar a suíte inteira do `ws` para checar que nada mais quebrou**

Run: `bash tools/ws/tests/run.sh`
Expected: todos os testes `ok`, `0 falha(s)`.

- [ ] **Step 6: Commit**

```bash
git add tools/speckit/ws/scripts/bash/ws-feature.sh tools/ws/tests/test_speckit_feature.sh
git commit -m "ws-feature: reserva atomica do numero da feature via refs/ws-reserved"
```

---

### Task 2: Propagar para a extensão instalada

**Files:**
- Modify (gerado): `.specify/extensions/ws/scripts/bash/ws-feature.sh` (via `tools/ws/ws speckit`)

**Interfaces:**
- Consumes: `tools/ws/ws speckit` (comando já existente, `tools/ws/lib/speckit.sh`), que reinstala a extensão `ws` a partir de `tools/speckit/ws/` — nenhuma interface nova.
- Produces: nada consumido por outra task.

- [ ] **Step 1: Regenerar a extensão instalada**

Run (na raiz do worktree `C:\src\wms-workspace-sp9`, árvore limpa): `bash tools/ws/ws speckit`
Expected: termina com `Spec Kit <versão> instalado com as extensões ws, agent-context, bug e refactor...`, sem erro.

- [ ] **Step 2: Conferir que a cópia instalada bateu com a fonte**

Run: `diff tools/speckit/ws/scripts/bash/ws-feature.sh .specify/extensions/ws/scripts/bash/ws-feature.sh`
Expected: sem diferença (saída vazia).

- [ ] **Step 3: Revisar o que o `ws speckit` tocou além do esperado**

Run: `git status --short`
Expected: só arquivos dentro de `.specify/` e `.claude/skills/` (regerados pelo `specify init`/`extension add`) além do `ws-feature.sh` da Task 1 — nada em `tools/`, `repos/` ou fora de `.specify`/`.claude`. Se aparecer algo inesperado, pare e investigue antes de commitar (pode ser deriva de uma versão do Spec Kit diferente da fixada em `tools/speckit/VERSION`).

- [ ] **Step 4: Commit**

```bash
git add .specify .claude/skills
git commit -m "ws speckit: regenera a extensao ws com a reserva de numero"
```

- [ ] **Step 5: (movido) PR para o main**

Não há PR de homologação para a branch do harness. A `homolog` do workspace está parada (em 2026-10-28: 0 commits à frente e 160 atrás do `main`; a última mudança de harness que passou por ela foi o PR 17222). Desde o SP8, as mudanças de harness vão direto para o `main`, como o PR 17341 (SP8) e o PR 17411 (Atlas). O `/ws-pr-homolog` é o fluxo das features dos repos do WMS, não o da branch do harness. O PR `harness/sp9-reserva-numero` → `main` é a Task 4, depois da Task 3.

---

### Task 3: Validação de ponta a ponta contra o Azure

O caminho `TF401028` (as duas estações enviando ao mesmo tempo) só existe contra o Azure; os testes da Task 1 apenas o simulam. Esta task prova o `ws-feature.sh` real, não só o mecanismo, que já foi provado em `docs/discovery/sp9-teste-azure.md`. Ela roda a partir da branch **local** `harness/sp9-reserva-numero`: não precisa de push da branch nem de PR.

**Files:**
- Create: `docs/discovery/sp9-validacao.md` (repo de discovery), no formato do `sp8-validacao.md`.

**O que vai ao Azure, e o que não vai:**
- Vão: só as refs `refs/ws-reserved/<NNN>` criadas pelas corridas (Steps 1 e 2) e, no Step 3, o que um `ws start` real envia (a `ws/sync`, ver abaixo).
- Não vão: a branch `harness/sp9-reserva-numero`, as branches `ws-NNN-*` das features de teste (ficam só locais e são apagadas no fim) e nenhum PR.

**Decisões já tomadas:**
- **Estações = clones separados, não worktrees.** Worktrees do mesmo repo compartilham o banco de objetos, então uma estação já teria o commit de reserva da outra e o caso `(fetch first)` nunca apareceria. Os clones são locais (`git clone C:\src\wms-workspace-sp9 -b harness/sp9-reserva-numero`), com o `origin` trocado para o Azure. Não use clone parcial (`--filter`): ele busca sob demanda o objeto que falta e mascara o caso real (`sp9-teste-azure.md`, seção Setup).
- **`ws start` substituído por um stub nos Steps 1 e 2.** O `ws-feature.sh` aceita `WS_BIN` (é como os testes o isolam). O stub só sai com código 0 e não cria branch, para a estação continuar na `harness/sp9-reserva-numero` e a rodada seguinte não "continuar" na feature anterior. Sem o stub, cada corrida rodaria um `ws start` de verdade, que sincroniza a `ws/sync` e dá push nela (`ws_sync_base` → `ws_sync_envia`, `tools/ws/lib/start.sh`). A `ws/sync` é compartilhada com o time. O que o SP9 mudou é só a reserva, que acontece antes do `ws start`.
- **Qual caminho de rejeição apareceu:** cada execução roda com `GIT_TRACE_PACKET` apontando para um arquivo próprio. A linha `ng refs/ws-reserved/<NNN> <motivo>` da resposta do servidor mostra o `TF401028`. A ausência de `ng` com push recusado indica rejeição pelo cliente: `(fetch first)` ou `(non-fast-forward)`.
- **Números de teste não ficam queimados.** Em 2026-10-28 o origin tinha `ws-001` a `ws-003`, então as corridas vão reservar a partir do `ws-004`. No fim, cada reserva criada pela validação é apagada **pelo SHA que ela tinha** (`git push --force-with-lease=refs/ws-reserved/<NNN>:<sha> origin :refs/ws-reserved/<NNN>`). Assim uma reserva de outra pessoa feita no meio do teste nunca é apagada. O spec continua dizendo que o *harness* nunca apaga reservas: esta é uma limpeza manual de teste, não comportamento do harness.

**Regras:**
- Push no origin real é ação externa: pedir OK ao usuário antes do Step 1 e antes do Step 3.
- Nada de `/ws-commit-push`, `/ws-pr-*` ou push de branch durante a task.

- [ ] **Step 0: Preparar (local, sem tocar o Azure)**

Três clones locais (`e1`, `e2` e `e3`) no scratchpad da sessão, cada um com `git remote set-url origin https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace` e `git fetch -q origin main`. Um stub `ws-stub.sh` com `exit 0`. Anotar `git ls-remote origin 'refs/ws-reserved/*'` antes de começar: são as reservas que já existiam e que não podem ser tocadas.

- [ ] **Step 1: Corrida simultânea entre duas estações, 5 rodadas**

Em cada rodada, `e1` e `e2` disparam juntas, em background, `WS_BIN=<stub> GIT_TRACE_PACKET=<arquivo> bash tools/speckit/ws/scripts/bash/ws-feature.sh --short-name "sp9 teste <rodada> <estação>" "..."`, com slugs diferentes.
Expected: nas 5 rodadas, `BRANCH_NAME` com números diferentes nas duas estações, `ERROR` vazio e uma reserva no origin por número usado. Registrar, por rodada, os dois números e o caminho de rejeição da perdedora (`TF401028`, `fetch first` ou `non-fast-forward`). Se nenhuma rodada cair em `TF401028`, registrar isso. Não é falha, mas a prova do caminho do servidor continua sendo a do `sp9-teste-azure.md`.

- [ ] **Step 2: Três estações**

`e1` e `e2` juntas e, logo depois, `e3`.
Expected: três números diferentes, e `e3` pega o número seguinte aos já reservados.

- [ ] **Step 3: Uma execução com o `ws start` real (opcional, decidir com o usuário)**

Uma execução sem o stub em `e1`. Prova que o JSON e o `ws start` continuam encadeados depois da reserva.
Efeito externo: o `ws start` sincroniza a `ws/sync` e dá push nela, se algum repo tiver mudado desde o último sync. É o mesmo que qualquer dev provoca ao abrir uma feature, mas numa branch do time inteiro. A branch `ws-NNN-*` criada fica só local.
Expected: `ERROR` vazio, branch `ws-NNN-...` criada em `e1`, número diferente de todos os anteriores.

- [ ] **Step 4: Visibilidade**

Expected: `git ls-remote --heads origin` sem nenhuma `ws-reserved`. O usuário confere no Azure, **antes** de qualquer limpeza: Repos → Branches (abas e busca por `ws-reserved`), Tags, o seletor de branch e Pushes.

- [ ] **Step 5: Limpeza**

Com o OK do usuário:
1. Apagar as reservas da validação pelo SHA, como descrito acima.
2. Conferir com `ls-remote` que sobraram só as reservas anotadas no Step 0.
3. Apagar os clones e o stub.
4. Se o Step 3 rodou, apagar a branch `ws-NNN-*` local de `e1`.

- [ ] **Step 6: Registrar**

Em `docs/discovery/sp9-validacao.md`: a tabela das rodadas (números, caminho de rejeição), o Step 3 (se rodou, e o que o `ws start` enviou), a visibilidade conferida pelo usuário e a limpeza feita.

---

### Task 4: PR para o main

Só com os Steps 1, 2 e 4 da Task 3 ok, e com o OK do usuário: push da `harness/sp9-reserva-numero` e PR direto para o `main` do workspace, como o PR 17341 (SP8).
