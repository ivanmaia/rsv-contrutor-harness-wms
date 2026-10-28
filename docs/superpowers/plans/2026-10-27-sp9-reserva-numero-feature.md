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
    while ! reserve_num "$n"; do n=$(printf '%03d' $((10#$n + 1))); done
  fi
  name="$P$n-$slug"
  branch=$name
  ! branch_taken "$branch" || fail "a branch $branch já existe"
```

As mensagens do `case` foram capturadas no Azure real com Git 2.54.0 para Windows (`docs/discovery/sp9-teste-azure.md`): `(non-fast-forward)` e `(fetch first)` vêm do cliente; `TF401028` vem do servidor, como `[remote rejected]`. Não troque nenhuma delas por um padrão mais genérico.

- [ ] **Step 4: Rodar os testes de novo e ver que passam**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_feature.sh`
Expected: os sete testes novos `ok` e nenhuma regressão nos testes já existentes do arquivo.

- [ ] **Step 5: Rodar a suíte inteira do `ws` para checar que nada mais quebrou**

Run: `bash tools/ws/tests/run.sh`
Expected: todos os testes `ok`, `0 falha(s)`.

- [ ] **Step 6: Commit**

```bash
git add tools/speckit/ws/scripts/bash/ws-feature.sh tools/ws/tests/test_speckit_feature.sh
git commit -m "ws-feature: reserva atomica do numero da feature via refs/ws-reserved"
```

---

### Task 2: Propagar para a extensão instalada e fechar o PR

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

- [ ] **Step 5: Abrir o PR de homologação**

Seguir o fluxo padrão do harness (`/ws-commit-push`, `/ws-pr-homolog`) a partir da branch `harness/sp9-reserva-numero`, como no SP8 (PR 17341). A promoção para o main (`/ws-pr-main`) só depois da Task 3.

---

### Task 3: Validação de ponta a ponta contra o Azure

O caminho `TF401028` (as duas estações enviando ao mesmo tempo) só existe contra o Azure; os testes da Task 1 apenas o simulam. Esta task prova o `ws-feature.sh` real, não só o mecanismo, que já foi provado em `docs/discovery/sp9-teste-azure.md`.

**Files:**
- Create: `docs/discovery/sp9-validacao.md` (repo de discovery), no formato do `sp8-validacao.md`.

**Regras:**
- Push no origin real é ação externa: pedir OK ao usuário antes de começar.
- Usar o repo fixture do SP8 (`industria-logistica.wms.harness-test-dummy`) nas features de teste, nenhum repo de produção.
- Uma worktree separada por "estação", todas com a branch `harness/sp9-reserva-numero`. Nunca compartilhar worktree entre os lados (erro de processo do SP8).

- [ ] **Step 1: Corrida simultânea, várias rodadas**

Nas duas worktrees, rodar o `ws-feature.sh` ao mesmo tempo (dois processos em background disparados juntos), com slugs diferentes. Repetir pelo menos 5 vezes.
Expected: em toda rodada, números diferentes nas duas estações; `git ls-remote origin 'refs/ws-reserved/*'` com uma reserva por número usado. Registrar quantas rodadas caíram em `TF401028` e quantas em `fetch first`.

- [ ] **Step 2: Três estações em sequência**

Uma terceira worktree roda logo depois das duas.
Expected: pega o número seguinte aos já reservados.

- [ ] **Step 3: Visibilidade**

Expected: `git ls-remote --heads origin` sem nenhuma `ws-reserved`; o usuário confere a tela de branches do Azure **antes** de qualquer limpeza.

- [ ] **Step 4: Limpeza**

Com o OK do usuário: apagar as branches e as features de teste. As reservas criadas pela validação ficam (o harness nunca apaga reservas, spec seção 3); listar no `sp9-validacao.md` quais números ficaram reservados.

- [ ] **Step 5: Promover para o main**

Só com os Steps 1 a 3 ok: `/ws-pr-main`.
