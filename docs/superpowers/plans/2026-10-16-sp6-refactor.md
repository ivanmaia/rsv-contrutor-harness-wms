# SP6: Vertente de refactor — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** atualizar o Spec Kit do workspace WMS para a 1.2.0, trocar as chamadas do preset `bugs` por hooks nativos e dar ao dev um fluxo de refactor (tipo 1, interno, e tipo 3, fatia de desacoplamento) com prova de comportamento igual, marcos em produção e acompanhamento das fatias pendentes.

**Architecture:** são dois PRs no workspace.
- **PR 1 (`harness/speckit-1.2`):** sobe o `tools/speckit/VERSION`, registra na extensão `ws` os hooks `before_bug_assess`, `after_bug_assess` e `after_bug_test` e tira do preset `bugs` as chamadas da `ws`.
- **PR 2 (`harness/refactor`):** cria a extensão própria `refactor` (5 comandos que disparam `before_`/`after_refactor_*` por um procedimento comum em `hooks.md`), três comandos novos da `ws` ligados a esses hooks, três scripts bash testados offline (branch, registro e conferência da caracterização) e o subcomando `ws refactor` (`pendentes`, `estado` e `marco`), que lê e grava a tabela de fatias do documento do desacoplamento. Inclui também o aviso no `ws start`, a constitution 1.3.0, o `AGENTS.md` e as camadas da doc.

**Tech Stack:** bash (Git Bash no Windows), awk, Spec Kit 1.2.0 via `uvx`, Markdown (comandos, templates, doc), Claude Code `claude -p` (PoC e ponta a ponta), .NET 8 e 10 (repos do ponta a ponta).

**Spec:** `C:\src\00-harness_big_brown_field\docs\superpowers\specs\2026-10-16-sp6-refactor-design.md` (aprovada em 2026-10-16).

**Ajustes à spec feitos no plano** (refinamentos de implementação; a spec é atualizada junto com este plano):
1. A extensão `ws` vai para a 1.3.0 no PR 1 (hooks de bug) e para a 1.4.0 no PR 2 (refactor). A spec citava só a 1.3.0.
2. A `ws` ganha um terceiro comando, `speckit.ws.refactor-registro`. Ele cuida do registro sem mudança de código: o `assess` que reclassifica e o `validar` que falha. O `refactor-enviar` fica só para os envios com código: `verify` e `contrair`.
3. A coluna Marco só muda pelo subcomando mecânico `ws refactor marco`, que recusa transição fora de ordem. A recusa do M4 sem M3 é o portão 1 do `contrair`, garantido por código. A linha da fatia nasce no M1 (no `verify`), e não no `assess`. O `ws refactor estado <slug>` devolve o marco.
4. O portão 2 do `contrair` consulta o índice de impacto do Atlas **e** procura o nome do objeto no código do consumidor, fora do caminho que vai sair.
5. A branch da validação de uma fatia que já teve uma validação falha é `refactor/<slug>-contrair-<k>`, porque a `-contrair` anterior ficou no origin com o registro da falha.
6. O Atlas sem o adiamento usa o gatilho `converge` existente da skill `atlas-atualizar`, que mapeia todo repo tocado pela branch, sem a política de adiamento (`tools/atlas/plano.py`, ramo `converge`). Não há opção nova no `ws atlas`.

## Global Constraints

- **Repositório:** `C:\src\wms-workspace`.
  - PR 1: branch `harness/speckit-1.2`, a partir do `main` atualizado (`a996df32c` ou mais novo).
  - PR 2: branch `harness/refactor`, a partir do `main` com o PR 1 mergeado.
- Tudo em português do Brasil: comandos, mensagens de erro, doc, mensagens de commit.
- Commits sem atribuição do Claude (o `.claude/settings.json` do workspace já desliga). Prefixo das mensagens de commit do harness: `harness: `.
- Spec Kit: `tools/speckit/VERSION` = `1.2.0`.
- Fontes do harness ficam em `tools/speckit/`. **Nunca** editar as cópias em `.specify/` ou `.claude/skills/` à mão: rodar `tools/ws/ws speckit`.
- Nenhum arquivo da extensão `bug` nem do workflow `bugfix` é editado.
- Pastas: relatórios em `refactors/<slug>/`; documento do desacoplamento em `refactors/desacoplamentos/<nome>.md`. Nada em `.specify/refactors/`.
- Slug: `^([0-9]+|rf-[0-9]{8})-[a-z0-9]+(-[a-z0-9]+)*$`, ou seja, `<id do work item>-<descrição>` ou `rf-<AAAAMMDD>-<descrição>`.
- Nome do desacoplamento: `^[a-z0-9]+(-[a-z0-9]+)*$` (por exemplo, `linx`).
- Branches: `refactor/<slug>`, `refactor/<slug>-r<k>` (k ≥ 2) e `refactor/<slug>-contrair` (ou `-contrair-<k>`, k ≥ 2, quando uma validação anterior falhou e deixou a `-contrair` no origin), no workspace e nos repos.
- Cabeçalho da tabela de fatias, exato: `| Fatia | Consumidor | Objeto | Marco | Data do marco | Convivência a partir de |`. Linha: `| [<slug>](../<slug>/) | <consumidor> | <objeto> | <marco> | <AAAA-MM-DD> | <AAAA-MM-DD> |`. Marcos válidos: `M1`, `M3`, `M3-falhou`, `M4`.
- Mensagens de commit do fluxo:
  - caracterização: `test(<slug>): caracterização`;
  - M1: `refactor(<slug>): <título>`;
  - reclassificar: `docs(<slug>): diagnóstico, não é refactor`;
  - validação que falhou: `docs(<slug>): validação sem sucesso`;
  - M4: `refactor(<slug>): contração <título>`.
- Suíte: `bash tools/ws/tests/run.sh` 100% verde ao fim de cada task. Os testes de instalação rodam com `WS_TEST_REDE=1`.
- Ações externas (push ao origin do workspace, `claude -p`, criação de ambientes em `C:\src\` ou `%TEMP%`, clone do Azure DevOps) só com OK do usuário, marcadas **(OK)**. O push das branches do harness é feito pelo usuário (no SP5, a permissão automática negou o push pelo agente).
- Fora de escopo: corrigir defeitos achados nos repos do WMS.

## Review Focus

1. **Dev roda `/speckit-refactor-contrair` numa fatia ainda em M1**, porque achou que a convivência bastava: `ws refactor estado` devolve `M1`, o comando para, e `ws refactor marco <slug> M4` recusa com "a contração exige o M3 registrado". Teste: `test_refactor_marco_m4_sem_m3_recusa` (Task 5).
2. **Tabela de fatias editada à mão**, com a data em `01/12/2026` ou a linha sem o link: o `pendentes` avisa a linha fora do formato e segue listando as outras, e o `ws start` não quebra. Testes: `test_refactor_pendentes_linha_fora_do_formato_avisa_e_segue` e `test_refactor_aviso_do_start_ignora_linha_fora_do_formato` (Task 5).
3. **`/speckit-refactor-assess` de novo para uma fatia já registrada no `main`**, sem ser nova rodada: o start recusa e diz o caminho (nova rodada ou validar), sem criar branch. Teste: `test_refactor_start_registrado_no_main_falha` (Task 4).
4. **O agente apaga um teste de caracterização** em vez de alterar: a conferência acusa o arquivo apagado. Teste: `test_refactor_confere_teste_apagado_falha` (Task 4).
5. **Documento do desacoplamento salvo com CRLF** por um editor do Windows: as linhas são lidas igual e o `marco` grava sem quebrar o arquivo. Teste: `test_refactor_marco_aceita_documento_com_crlf` (Task 5).

---

## PR 1: Spec Kit 1.2.0 e hooks nativos de bug

### Task 1: PoC do Spec Kit 1.2.0 (itens 1 a 3 da spec 10.1)

Confirma, num ambiente descartável, que a 1.2.0 não quebra os presets, que uma extensão nossa dispara hooks com nome próprio e que os hooks nativos da `bug` funcionam. **Se algum item falhar, pare e volte ao usuário** com as saídas da spec (seção 11): o próprio comando chama a `ws` no texto, como no SP5, ou fica na versão atual. Não contorne.

**Files:**
- Create: `C:\src\00-harness_big_brown_field\docs\discovery\sp6-refactor-validacao.md` (pasta de discovery, não o workspace)

- [ ] **Step 1 (OK): Montar a cópia descartável com a 1.2.0**

```bash
P=$(cygpath -u "$TEMP")/sp6-poc && rm -rf "$P" && mkdir -p "$P"
git clone -q -c core.longpaths=true -c core.autocrlf=false /c/src/wms-workspace "$P/ws"
cd "$P/ws" && git remote remove origin
echo 1.2.0 > tools/speckit/VERSION && git commit -qam "poc: spec kit 1.2.0"
bash tools/ws/ws speckit; echo "rc=$?"
```

Expected: `rc=0` e a linha `ws: Spec Kit 1.2.0 instalado com ...`. Se o `specify` recusar o `workflow add` da URL `v1.2.0`, anote a mensagem.

- [ ] **Step 2: Item 1, presets intactos**

```bash
cd "$P/ws"
grep -c "Regras do workspace multi-repo" .claude/skills/speckit-specify/SKILL.md
bash .specify/scripts/bash/resolve-template.sh spec-template | grep -c "Repos afetados"
grep -c "Regras do workspace para bugs (preset bugs)" .claude/skills/speckit-bug-assess/SKILL.md
grep -c ".specify/bugs/" .specify/extensions/bug/commands/speckit.bug.assess.md
grep -c "before_bug_assess" .specify/extensions/bug/commands/speckit.bug.assess.md
grep -c "after_bug_test" .specify/extensions/bug/commands/speckit.bug.test.md
grep "version:" .specify/extensions/bug/extension.yml
bash tools/ws/tests/run.sh 2>&1 | tail -3
```

Expected: todas as contagens ≥ 1; a extensão `bug` em `1.0.1` ou mais nova; a suíte com `0 falha(s)`. O teste `test_speckit_extensao_bug_ainda_sem_hooks_lembrete_sp5` só roda com rede e é o gatilho esperado: não rode com `WS_TEST_REDE=1` aqui.

- [ ] **Step 3: Bundle `bugfix` na 1.2.0**

```bash
B="$P/bundle" && mkdir -p "$B" && cd "$B" && git init -q
uvx --from "git+https://github.com/github/spec-kit.git@v1.2.0" specify init --here --force --non-interactive --integration claude --script sh >/dev/null
uvx --from "git+https://github.com/github/spec-kit.git@v1.2.0" specify bundle add bugfix; echo "rc=$?"
ls .specify/extensions .specify/workflows
```

Anote o resultado: **bundle ok** (`rc=0`, `bug` e `bugfix` instalados) ou **bundle falha** (a mensagem). A Task 2 usa a variante que corresponder.

- [ ] **Step 4: Item 2, extensão nossa com hook de nome próprio**

Crie duas extensões de brinquedo fora do workspace:

```bash
mkdir -p "$P/ext/poc/commands" "$P/ext/pocws/commands"
cat > "$P/ext/poc/extension.yml" <<'EOF'
schema_version: "1.0"
extension:
  id: poc
  name: "PoC de hook próprio"
  version: "0.0.1"
  description: "Dispara before_poc_ola"
  author: workspace-wms
  repository: https://example.invalid/poc
  license: Proprietary
requires:
  speckit_version: ">=1.2.0"
provides:
  commands:
    - name: speckit.poc.ola
      file: commands/speckit.poc.ola.md
      description: "Comando que dispara before_poc_ola"
EOF
cat > "$P/ext/poc/commands/speckit.poc.ola.md" <<'EOF'
---
description: "Comando de PoC que dispara o evento before_poc_ola"
---

# Olá

1. Leia `.specify/extensions.yml` e procure entradas em `hooks.before_poc_ola`. Ignore as com `enabled: false`. Para cada entrada com `optional: false`, mostre `EXECUTE_COMMAND: {command}` e **rode** a skill correspondente (troque os pontos por hífens: `speckit.pocws.marca` vira `/speckit-pocws-marca`), esperando ela terminar.
2. Depois, responda só: `olá concluído`.
EOF
cat > "$P/ext/pocws/extension.yml" <<'EOF'
schema_version: "1.0"
extension:
  id: pocws
  name: "PoC: hooks em eventos de outras extensões"
  version: "0.0.1"
  description: "Registra hooks em before_poc_ola e before_bug_assess"
  author: workspace-wms
  repository: https://example.invalid/pocws
  license: Proprietary
requires:
  speckit_version: ">=1.2.0"
provides:
  commands:
    - name: speckit.pocws.marca
      file: commands/speckit.pocws.marca.md
      description: "Grava marca.txt"
hooks:
  before_poc_ola:
    command: speckit.pocws.marca
    optional: false
    description: "Marca antes do olá"
  before_bug_assess:
    command: speckit.pocws.marca
    optional: false
    description: "Marca antes do assess do bug"
EOF
cat > "$P/ext/pocws/commands/speckit.pocws.marca.md" <<'EOF'
---
description: "Grava marca.txt na raiz com o evento recebido"
---

# Marca

Rode `echo "marca $(date +%H:%M:%S)" >> marca.txt` na raiz do projeto e responda `marca gravada`.
EOF
cd "$P/ws"
S=(uvx --from "git+https://github.com/github/spec-kit.git@v1.2.0" specify)
"${S[@]}" extension add --dev "$P/ext/poc" && "${S[@]}" extension add --dev "$P/ext/pocws"
grep -A6 "before_poc_ola:" .specify/extensions.yml
grep -A6 "before_bug_assess:" .specify/extensions.yml
```

Expected: as duas extensões instalam sem erro de validação, e o `.specify/extensions.yml` lista `before_poc_ola` e `before_bug_assess` com `command: speckit.pocws.marca`.

- [ ] **Step 5 (OK): Item 2 com o agente**

```bash
cd "$P/ws" && rm -f marca.txt
claude -p --permission-mode acceptEdits --allowedTools "Bash Read Edit Write Grep Glob Skill" --output-format json \
  "/speckit-poc-ola" > "$P/poc-ola.json"
cat marca.txt
```

Expected: `marca.txt` com uma linha; o `result` do JSON termina com `olá concluído`.

- [ ] **Step 6 (OK): Item 3, hook nativo da `bug`**

```bash
cd "$P/ws" && rm -f marca.txt
claude -p --permission-mode acceptEdits --allowedTools "Bash Read Edit Write Grep Glob Skill" --output-format json \
  "/speckit-bug-assess Work item 90100. Teste de PoC: o endpoint de saúde do conector (industria-logistica.wms.conector.backend) devolve 500 quando o banco está fora. Só diagnostique." > "$P/poc-bug.json"
cat marca.txt; git branch --show-current
```

Expected: `marca.txt` com uma linha, gravada pelo hook `before_bug_assess`. Nesta cópia, o preset `bugs` ainda chama o `/speckit-ws-bug-start`, então a branch `hotfix/90100-*` pode ou não ter sido criada, porque a cópia não tem origin. Isso não conta para o item.

- [ ] **Step 7: Registrar e decidir**

Crie `C:\src\00-harness_big_brown_field\docs\discovery\sp6-refactor-validacao.md`:

```markdown
# SP6: validação da vertente de refactor

Spec: `docs/superpowers/specs/2026-10-16-sp6-refactor-design.md`. Plano: `docs/superpowers/plans/2026-10-16-sp6-refactor.md`.

## PoC do Spec Kit 1.2.0 (spec 10.1, itens 1 a 3)

Ambiente: cópia descartável em `%TEMP%\sp6-poc`, sem origin.

| # | Item | Resultado | Evidência e custo |
|---|---|---|---|
| 1 | Atualização sem quebrar `multirepo` e `bugs` | | |
| 2 | Extensão nossa com hook de nome próprio | | |
| 3 | Hook nativo `before_bug_assess` | | |
| — | Bundle `bugfix` na 1.2.0 | | |
```

Preencha com o resultado, a evidência e o custo (US$ do JSON). **Se o item 1, 2 ou 3 falhar, pare e volte ao usuário.** Commit no repo de discovery:

```bash
cd /c/src/00-harness_big_brown_field
git add docs/discovery/sp6-refactor-validacao.md
git commit -m "SP6: PoC do Spec Kit 1.2.0"
```

---

### Task 2: Spec Kit 1.2.0 e hooks nativos de bug

**Files:**
- Modify: `tools/speckit/VERSION`
- Modify: `tools/ws/lib/speckit.sh`
- Modify: `tools/speckit/ws/extension.yml`
- Modify: `tools/speckit/ws/commands/speckit.ws.bug-start.md`
- Modify: `tools/speckit/ws/scripts/bash/ws-bug-start.sh:1-3`
- Modify: `tools/speckit/bugs/preset.yml`, `tools/speckit/bugs/commands/speckit.bug.assess.md`, `tools/speckit/bugs/commands/speckit.bug.test.md`
- Modify: `tools/ws/tests/test_speckit_install.sh`, `tools/ws/tests/test_speckit_bug.sh`, `tools/ws/tests/test_harness.sh`
- Modify: `AGENTS.md` (seção "Bugs com o Spec Kit"), `docs/harness/4-manter.md`
- Regenerate: `.specify/`, `.claude/skills/` (pelo `ws speckit`)

**Interfaces:**
- Consumes: o resultado do bundle (Task 1, Step 3).
- Produces: `.specify/extensions.yml` com `before_bug_assess` → `speckit.ws.bug-start`, `after_bug_assess` → `speckit.ws.bug-sem-correcao` e `after_bug_test` → `speckit.ws.bug-enviar`; a extensão `ws` 1.3.0.

- [ ] **Step 0: Branch de trabalho**

```bash
cd /c/src/wms-workspace
git switch main && git pull -q --ff-only origin main
git switch -c harness/speckit-1.2
```

- [ ] **Step 1: Escrever os testes offline**

Acrescente ao fim de `tools/ws/tests/test_speckit_bug.sh`:

```bash
# SP6 (spec 5.1): a extensão ws registra os hooks nativos da extensão bug, e o preset bugs não chama mais a ws.
test_ws_registra_os_hooks_nativos_de_bug() {
  local y="$WS_DIR/../speckit/ws/extension.yml"
  local ev cmd
  for ev in before_bug_assess:speckit.ws.bug-start after_bug_assess:speckit.ws.bug-sem-correcao after_bug_test:speckit.ws.bug-enviar; do
    cmd=$(awk -v e="  ${ev%%:*}:" '$0 == e { getline; sub(/^ *command: */, ""); print; exit }' "$y")
    assert_eq "$cmd" "${ev#*:}" "hook ${ev%%:*}"
  done
  assert_contains "$(cat "$y")" 'version: "1.3.0"'
}

test_preset_bugs_nao_chama_mais_a_ws() {
  local d="$WS_DIR/../speckit/bugs/commands" f
  for f in "$d"/*.md; do
    ! grep -qE '/speckit-ws-bug-(start|sem-correcao|enviar)' "$f" || fail "$(basename "$f") ainda chama a ws"
  done
  grep -qF 'before_bug_assess' "$d/speckit.bug.assess.md" || fail "o assess do preset não explica o hook da branch"
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_bug.sh`
Expected: FALHA em `test_ws_registra_os_hooks_nativos_de_bug` (esperado `[speckit.ws.bug-start]`, obtido `[]`) e em `test_preset_bugs_nao_chama_mais_a_ws`.

- [ ] **Step 3: Versão e instalação**

`tools/speckit/VERSION`:

```
1.2.0
```

Em `tools/ws/lib/speckit.sh`, troque o cabeçalho (linhas 1 e 2) por:

```bash
# ws speckit: instala ou atualiza o Spec Kit na raiz do workspace, com a extensão ws,
# a extensão agent-context, a extensão bug, o workflow bugfix e os presets multirepo e bugs (specs SP2, 6.3, SP5, 4, e SP6, 5.1).
```

**Variante A, bundle falhou na Task 1 (Step 3):** troque o bloco das linhas 39 a 41 (o comentário) por:

```bash
  # Extensão bug e workflow bugfix oficiais (spec SP5, 4.1), separados: o bundle bugfix falhou na
  # validação da 1.2.0 (docs/discovery/sp6-refactor-validacao.md do discovery). Desde a 1.1.3 a extensão
  # dispara hooks before_/after_bug_*, que a extensão ws usa (spec SP6, 5.1).
  # O preset bugs envolve os comandos da extensão: precisa vir depois dela.
```

**Variante B, bundle funcionou:** troque as linhas 39 a 52 (do comentário até o `workflow add`) por:

```bash
  # Extensão bug e workflow bugfix oficiais pelo bundle (spec SP6, 5.1). Desde a 1.1.3 a extensão
  # dispara hooks before_/after_bug_*, que a extensão ws usa. O preset bugs envolve os comandos da
  # extensão: precisa vir depois dela.
  if [ -d .specify/presets/bugs ]; then
    "${spec[@]}" preset remove bugs >/dev/null || die "não consegui remover o preset bugs"
  fi
  if [ -d .specify/extensions/bug ]; then
    "${spec[@]}" extension remove bug --force >/dev/null || die "não consegui remover a extensão bug"
  fi
  if [ -d .specify/workflows/bugfix ]; then
    "${spec[@]}" workflow remove bugfix >/dev/null || die "não consegui remover o workflow bugfix"
  fi
  "${spec[@]}" bundle add bugfix >/dev/null || die "não consegui instalar o bundle bugfix"
```

- [ ] **Step 4: Hooks na extensão `ws`**

Em `tools/speckit/ws/extension.yml`:
- `version: "1.2.0"` → `version: "1.3.0"`;
- `description` → `"Branch da feature e do bug com ws start, Atlas e envio aos repos com ws push (specs SP2, SP3, SP5 e SP6)"`;
- `requires.speckit_version` → `">=1.2.0"`;
- no bloco `hooks:`, depois de `after_converge`, acrescente:

```yaml
  before_bug_assess:
    command: speckit.ws.bug-start
    optional: false
    description: "Branch hotfix/<slug> do bug com ws start e Atlas atualizado"
  after_bug_assess:
    command: speckit.ws.bug-sem-correcao
    optional: false
    description: "Registra o diagnóstico que não pede correção de código, ou lembra o próximo passo"
  after_bug_test:
    command: speckit.ws.bug-enviar
    optional: false
    description: "Atlas dos repos tocados pelo bug e oferta de commit e envio aos repos"
```

- [ ] **Step 5: Comando `bug-start` como hook**

Em `tools/speckit/ws/commands/speckit.ws.bug-start.md`, troque a linha 15 (`A entrada é o slug do bug, ...`) por:

```markdown
Este comando roda pelo hook `before_bug_assess`, depois que o `/speckit-bug-assess` resolveu o slug. O slug é o `BUG_SLUG` desta sessão, já na convenção do preset `bugs`; se a entrada acima trouxer um slug, use o da entrada. A pasta `bugs/<slug>/` pode já existir vazia: o `ws start` não se importa com pasta vazia.
```

No passo 2, primeiro item, troque `Não crie a pasta do bug nem o `assessment.md`.` por `Não grave o `assessment.md`: o `/speckit-bug-assess` também para.`

No passo 4, troque `devolva o controle ao `/speckit-bug-assess`.` por `devolva o controle ao `/speckit-bug-assess`, que segue para a execução.`

Em `tools/speckit/ws/scripts/bash/ws-bug-start.sh`, troque as linhas 2 e 3 por:

```bash
# Comando speckit.ws.bug-start da extensão ws, chamado pelo hook before_bug_assess no início do
# /speckit-bug-assess: cria a branch hotfix/<slug> com ws start (specs SP5, 4.3, e SP6, 5.1).
```

- [ ] **Step 6: Preset `bugs` sem as chamadas**

`tools/speckit/bugs/preset.yml`: `version: "1.0.0"` → `version: "1.1.0"`; `description` → `"Relatórios de bug em bugs/<slug>/ e slug com o work item; branch e envio pelos hooks da extensão ws (specs SP5 e SP6)"`; `speckit_version: ">=1.0.12"` → `speckit_version: ">=1.2.0"`.

`tools/speckit/bugs/commands/speckit.bug.assess.md`, troque a regra 3 inteira por:

```markdown
3. **Branch:** o hook `before_bug_assess` da extensão `ws` cria a branch `hotfix/<slug>` com o slug. Se ele devolver `ERROR`, pare: não grave o `assessment.md`. Antes de gravar, confirme com `git branch --show-current` que você está em `hotfix/<slug>`.
```

e apague as duas últimas linhas do arquivo (`## Depois do diagnóstico (preset bugs)` e a frase que manda seguir `/speckit-ws-bug-sem-correcao`), com a linha em branco antes delas. O arquivo termina em `{CORE_TEMPLATE}`.

`tools/speckit/bugs/commands/speckit.bug.test.md`: apague as duas últimas linhas (`## Depois da verificação (preset bugs)` e a frase que manda seguir `/speckit-ws-bug-enviar`), com a linha em branco antes delas. O arquivo termina em `{CORE_TEMPLATE}`.

- [ ] **Step 7: Testes de instalação com rede**

Em `tools/ws/tests/test_speckit_install.sh`, troque o corpo de `test_speckit_preset_bugs_envolve_os_comandos_oficiais` por:

```bash
test_speckit_preset_bugs_envolve_os_comandos_oficiais() {
  precisa_rede || return 0
  fx_speckit
  local a f t
  a=$(cat .claude/skills/speckit-bug-assess/SKILL.md)
  f=$(cat .claude/skills/speckit-bug-fix/SKILL.md)
  t=$(cat .claude/skills/speckit-bug-test/SKILL.md)
  assert_contains "$a" "Regras do workspace para bugs (preset bugs)"
  assert_contains "$a" "# Assess Bug"
  assert_contains "$a" "before_bug_assess"
  assert_not_contains "$a" "Depois do diagnóstico (preset bugs)"
  assert_contains "$f" "Regras do workspace para bugs (preset bugs)"
  assert_contains "$f" "# Fix Bug"
  assert_contains "$t" "# Test Bug"
  assert_contains "$t" "after_bug_test"
  assert_not_contains "$t" "Depois da verificação (preset bugs)"
  [ "$(grep -n 'preset bugs' .claude/skills/speckit-bug-assess/SKILL.md | head -1 | cut -d: -f1)" -lt \
    "$(grep -n '^# Assess Bug' .claude/skills/speckit-bug-assess/SKILL.md | cut -d: -f1)" ] || fail "preâmbulo depois do texto oficial"
}
```

e troque `test_speckit_extensao_bug_ainda_sem_hooks_lembrete_sp5` (o comentário e a função) por:

```bash
# SP6 (spec 5.1): os hooks nativos da extensão bug ligados aos comandos da ws.
test_speckit_bug_dispara_os_hooks_da_ws() {
  precisa_rede || return 0
  fx_speckit
  local ext
  ext=$(cat .specify/extensions.yml)
  assert_contains "$ext" "before_bug_assess:"
  assert_contains "$ext" "command: speckit.ws.bug-start"
  assert_contains "$ext" "after_bug_assess:"
  assert_contains "$ext" "command: speckit.ws.bug-sem-correcao"
  assert_contains "$ext" "after_bug_test:"
  assert_contains "$ext" "command: speckit.ws.bug-enviar"
  grep -q 'before_bug_assess' .specify/extensions/bug/commands/speckit.bug.assess.md \
    || fail "a extensão bug instalada não dispara before_bug_assess"
  grep -q '\.specify/bugs/' .specify/extensions/bug/commands/speckit.bug.assess.md \
    || fail "a extensão bug não grava mais em .specify/bugs/: o preset bugs depende desse texto"
}
```

- [ ] **Step 8: `AGENTS.md`, camada 4 e teste da doc**

`AGENTS.md`, seção "Bugs com o Spec Kit", item **Iniciar**: troque `O preset `bugs` define o slug (...) e chama `/speckit-ws-bug-start`, que cria a branch` por `O preset `bugs` define o slug (`<id do work item>-<descrição>` ou `inc-<AAAAMMDD>-<descrição>`), e o hook `before_bug_assess` roda o `/speckit-ws-bug-start`, que cria a branch`. O resto da frase não muda.

`docs/harness/4-manter.md`:
- linhas 14 e 15 do mermaid:

```
  K["/speckit-bug-assess"] --> L["hook before_bug_assess<br/>speckit.ws.bug-start"] --> C
  M["/speckit-bug-test"] --> N["hook after_bug_test<br/>speckit.ws.bug-enviar"] --> J
```

- linhas 25 e 26 viram:

```markdown
- a extensão `bug` e o workflow `bugfix` oficiais, instalados como vêm. Desde o Spec Kit 1.1.3 a extensão dispara os hooks `before_bug_assess`, `after_bug_assess` e `after_bug_test`, que a extensão `ws` liga aos comandos `speckit.ws.bug-start`, `speckit.ws.bug-sem-correcao` e `speckit.ws.bug-enviar`;
- o preset `bugs` (`tools/speckit/bugs/`), que envolve os comandos `speckit.bug.*`: grava em `bugs/<slug>/` em vez de `.specify/bugs/<slug>/` e define o slug.
```

- linha 76 (passo 5 de "Atualizar o Spec Kit") vira:

```markdown
5. Confira se os comandos `speckit.bug.*` ainda gravam em `.specify/bugs/<slug>/` e ainda disparam os hooks `before_bug_assess`, `after_bug_assess` e `after_bug_test`: o preset `bugs` e a extensão `ws` dependem disso. O teste `test_speckit_bug_dispara_os_hooks_da_ws` confere os dois.
```

Em `tools/ws/tests/test_harness.sh`, `test_doc_cobre_a_vertente_de_bugs`, troque a última linha (`grep -qF 'seção 10' ...`) por:

```bash
  grep -qF 'before_bug_assess' "$d/4-manter.md" || fail "camada 4 sem os hooks nativos da extensão bug"
```

- [ ] **Step 9: Reinstalar e rodar tudo**

```bash
cd /c/src/wms-workspace
git add -A && git commit -qm "harness: Spec Kit 1.2.0 e hooks nativos de bug (fontes)"
bash tools/ws/ws speckit
git add -A && git commit -qm "harness: reinstala o Spec Kit 1.2.0"
bash tools/ws/tests/run.sh
WS_TEST_REDE=1 bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_install.sh
```

Expected: as duas suítes com `0 falha(s)`. Se a reinstalação mudar a constitution, o `AGENTS.md` ou o `CLAUDE.md`, pare: o `init --force` não devia mexer neles.

- [ ] **Step 10: Commit da doc**

Se o Step 9 deixou mudanças (a doc e os testes já entraram no primeiro commit), confira com `git status --short` e faça:

```bash
git add -A && git commit -qm "harness: doc e testes dos hooks nativos de bug"
```

---

### Task 3: Regressão do bug e entrega do PR 1

Valida um bug de ponta a ponta com os hooks nativos (o caso "Regressão do bug" da spec 10.3) e entrega o PR 1. O ambiente montado aqui é reaproveitado na Task 8.

**Files:**
- Modify: `C:\src\00-harness_big_brown_field\docs\discovery\sp6-refactor-validacao.md`

- [ ] **Step 1 (OK): Montar o ambiente descartável**

```bash
cd /c/src
git clone -q --bare /c/src/wms-workspace wms-e2e6-origin.git
git -C wms-e2e6-origin.git symbolic-ref HEAD refs/heads/main
git -C wms-e2e6-origin.git update-ref refs/heads/main "$(git -C /c/src/wms-workspace rev-parse harness/speckit-1.2)"
git clone -q -c core.longpaths=true -c core.autocrlf=false wms-e2e6-origin.git wms-workspace-e2e6
cd wms-workspace-e2e6
git config url."C:/bloqueado/".pushInsteadOf https://dev.azure.com/
git clone -q --bare https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.conector.backend /c/src/wms-e2e6-conector.git
git clone -q --bare https://dev.azure.com/ARECO/AReCO/_git/integracoes.wms.servicos-linx-wms.monorepo /c/src/wms-e2e6-linx.git
sed -i "s#^repos/industria-logistica.wms.conector.backend .*#repos/industria-logistica.wms.conector.backend C:/src/wms-e2e6-conector.git main#" workspace.repos
sed -i "s#^repos/integracoes.wms.servicos-linx-wms.monorepo .*#repos/integracoes.wms.servicos-linx-wms.monorepo C:/src/wms-e2e6-linx.git main#" workspace.repos
git commit -qam "e2e: conector e servicos-linx nos espelhos locais" && git push -q origin main
```

Os outros repos continuam apontando para o Azure DevOps, só leitura: o `pushInsteadOf` bloqueia qualquer push para lá.

- [ ] **Step 2: Plantar o bug no espelho do conector, como outro time**

```bash
tmp=/c/src/wms-e2e6-plantio && rm -rf $tmp && git clone -q /c/src/wms-e2e6-conector.git $tmp
sed -i 's/ArgumentOutOfRangeException.ThrowIfLessThanOrEqual(quantidade, 0);/ArgumentOutOfRangeException.ThrowIfLessThan(quantidade, 0);/' \
  $tmp/src/ReservaNet.Linx.Domain/OrdensReserva/FaturamentoCaixa.cs
git -C $tmp diff --stat   # 1 file changed, 1 insertion(+), 1 deletion(-)
git -C $tmp commit -qam "simplifica a validação da caixa" && git -C $tmp push -q origin main
rm -rf $tmp
```

- [ ] **Step 3 (OK): Bug com correção em 1 repo**

**Custo:** o `/speckit-ws-bug-start` roda o `atlas-atualizar --gatilho start`, que mapeia o conector e talvez outros repos que andaram (200 mil a 450 mil tokens por repo, pela calibração do SP3). Mostre ao usuário o plano (`tools/ws/ws atlas plano --gatilho start`) antes de pedir o OK.

```bash
cd /c/src/wms-workspace-e2e6
O="--permission-mode acceptEdits --allowedTools Bash,Read,Edit,Write,Grep,Glob,Skill --output-format json"
claude -p $O "/speckit-bug-assess Work item 90101. Desde ontem, o Linx recebe caixas embaladas com quantidade zero vindas do conector (industria-logistica.wms.conector.backend), e o faturamento quebra. Antes isso era recusado na criação da caixa." > /c/src/wms-e2e6-bug-assess.json
S=$(python -c "import json;print(json.load(open('C:/src/wms-e2e6-bug-assess.json'))['session_id'])")
claude -p --resume "$S" $O "/speckit-bug-fix" > /c/src/wms-e2e6-bug-fix.json
claude -p --resume "$S" $O "/speckit-bug-test" > /c/src/wms-e2e6-bug-test.json
claude -p --resume "$S" $O "Sim, pode fazer o commit e o envio." > /c/src/wms-e2e6-bug-envio.json
```

Critérios:
- a branch `hotfix/90101-<desc>` foi criada **pelo hook** `before_bug_assess` (o `result` do assess mostra `EXECUTE_COMMAND: speckit.ws.bug-start`);
- existem `bugs/90101-<desc>/{assessment,fix,test}.md`, e não existe `.specify/bugs/`;
- o `after_bug_assess` rodou o `/speckit-ws-bug-sem-correcao`, que mandou ler o `assessment.md` e rodar o `/speckit-bug-fix`;
- o `test.md` registra `verified` ou `partial`, com o motivo;
- o `after_bug_test` rodou o `/speckit-ws-bug-enviar`;
- há um commit `fix(90101-<desc>): …`, e `git -C /c/src/wms-e2e6-conector.git branch --list 'hotfix/*'` mostra a branch.

- [ ] **Step 4: Registrar**

Acrescente ao `sp6-refactor-validacao.md`:

```markdown
## Regressão do bug com hooks nativos (spec 10.3)

Ambiente: workspace `C:\src\wms-workspace-e2e6`, origin bare `C:\src\wms-e2e6-origin.git` (main = `harness/speckit-1.2` <sha>), espelhos `C:\src\wms-e2e6-conector.git` e `C:\src\wms-e2e6-linx.git`. Bug plantado: `ThrowIfLessThan(quantidade, 0)` no `FaturamentoCaixa`.

| Caso | Resultado | Evidência e custo |
|---|---|---|
| Bug com correção em 1 repo, hooks nativos | | |
```

Preencha. Se falhar, pare e volte ao usuário. Commit no repo de discovery: `git commit -am "SP6: regressão do bug com hooks nativos"`.

- [ ] **Step 5: Revisão e entrega do PR 1**

- Peça uma revisão da branch (skill `superpowers:requesting-code-review`) e corrija os achados importantes com teste.
- Rode `bash tools/ws/tests/run.sh` e `WS_TEST_REDE=1 bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_install.sh`. Os dois precisam terminar com `0 falha(s)`.
- Peça ao usuário o push: `git push -u origin harness/speckit-1.2`. Ele abre o PR para o `main`.
- **O PR 2 só começa depois do merge do PR 1.**

---

## PR 2: Vertente de refactor

### Task 4: Scripts de branch, registro e caracterização (offline)

**Files:**
- Create: `tools/speckit/ws/scripts/bash/ws-refactor-start.sh`
- Create: `tools/speckit/ws/scripts/bash/ws-refactor-registro.sh`
- Create: `tools/speckit/ws/scripts/bash/ws-refactor-confere.sh`
- Create: `tools/ws/tests/test_speckit_refactor.sh`

**Interfaces:**
- Consumes: `tools/ws/ws start <branch>` (recusa árvore suja, branch local existente e nome inválido; imprime `aviso:` e o link do PR da `ws/sync`).
- Produces:
  - `ws-refactor-start.sh <slug> [--rodada|--contrair]` → uma linha JSON `{"BRANCH_NAME":..,"REFACTOR_DIRECTORY":..,"EXISTING":true|false,"ERROR":..,"AVISOS":..}`. Sai 1 com `ERROR` preenchido. Usado por `speckit.ws.refactor-start` (Task 6).
  - `ws-refactor-registro.sh "<mensagem>"` → commit só de `refactors/` e `git push -u origin <branch>`. Usado por `speckit.ws.refactor-registro` (Task 6).
  - `ws-refactor-confere.sh <commit>` → `ws: caracterização intacta: <n> arquivo(s)` (0) ou `ws: erro: testes de caracterização alterados depois do commit <hash>: <arquivos>` (1). Usado por `speckit.refactor.verify` (Task 6).

- [ ] **Step 0: Branch de trabalho**

```bash
cd /c/src/wms-workspace
git switch main && git pull -q --ff-only origin main
git log --oneline -1 --grep "speckit-1.2" || echo "PR 1 ainda não mergeado: pare"
git switch -c harness/refactor
```

- [ ] **Step 1: Escrever os testes**

`tools/ws/tests/test_speckit_refactor.sh`:

```bash
# Testes dos scripts de refactor da extensão ws (spec SP6, 5.2 e 5.3):
# ws-refactor-start.sh, ws-refactor-registro.sh e ws-refactor-confere.sh.

RF_START_SH="$WS_DIR/../speckit/ws/scripts/bash/ws-refactor-start.sh"
RF_REGISTRO_SH="$WS_DIR/../speckit/ws/scripts/bash/ws-refactor-registro.sh"
RF_CONFERE_SH="$WS_DIR/../speckit/ws/scripts/bash/ws-refactor-confere.sh"

rf_start() { WS_BIN="$WS_BIN" bash "$RF_START_SH" "$@"; }
rf_registro() { bash "$RF_REGISTRO_SH" "$@"; }
rf_confere() { bash "$RF_CONFERE_SH" "$@"; }

# Valor de um campo do JSON de uma linha: json_get <campo> <json>
json_get() { printf '%s' "$2" | sed -E "s/.*\"$1\":(\"([^\"]*)\"|([a-z]+)).*/\2\3/"; }

# slug -> refactor registrado no main do origin (o PR do workspace foi mergeado).
rf_registrado() {
  ws_commit "refactors/$1/assessment.md" "# assessment $1"
  git push -q origin main
}

test_refactor_start_cria_branch() {
  fx_ready
  assert_ok rf_start 90201-extrai-montagem
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "refactor/90201-extrai-montagem"
  assert_eq "$(json_get REFACTOR_DIRECTORY "$OUT")" "refactors/90201-extrai-montagem"
  assert_eq "$(json_get EXISTING "$OUT")" "false"
  assert_eq "$(json_get ERROR "$OUT")" ""
  assert_eq "$(git symbolic-ref --short HEAD)" "refactor/90201-extrai-montagem"
}

test_refactor_start_aceita_slug_sem_work_item() {
  fx_ready
  assert_ok rf_start rf-20261016-renomeia-servico
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "refactor/rf-20261016-renomeia-servico"
}

test_refactor_start_sem_slug_falha() {
  fx_ready
  assert_fails rf_start
  assert_contains "$(json_get ERROR "$OUT")" "uso: ws-refactor-start.sh <slug> [--rodada|--contrair]"
}

test_refactor_start_modo_desconhecido_falha() {
  fx_ready
  assert_fails rf_start 90201-extrai-montagem --outro
  assert_contains "$(json_get ERROR "$OUT")" "uso: ws-refactor-start.sh"
}

test_refactor_start_slug_invalido_falha() {
  fx_ready
  assert_fails rf_start Extrai-Montagem
  assert_contains "$(json_get ERROR "$OUT")" "slug inválido: Extrai-Montagem"
  assert_contains "$(json_get ERROR "$OUT")" "rf-<AAAAMMDD>-<descrição>"
  assert_eq "$(git symbolic-ref --short HEAD)" "main"
}

test_refactor_start_slug_do_bug_falha() {
  fx_ready
  assert_fails rf_start inc-20261016-fila
  assert_contains "$(json_get ERROR "$OUT")" "slug inválido"
}

test_refactor_start_ja_na_branch_continua() {
  fx_ready
  assert_ok rf_start 90201-extrai-montagem
  assert_ok rf_start 90201-extrai-montagem
  assert_eq "$(json_get EXISTING "$OUT")" "true"
  assert_eq "$(git symbolic-ref --short HEAD)" "refactor/90201-extrai-montagem"
}

test_refactor_start_registrado_no_main_falha() {
  fx_ready
  rf_registrado 90301-movimenta-vendas
  assert_fails rf_start 90301-movimenta-vendas
  assert_contains "$(json_get ERROR "$OUT")" "o refactor 90301-movimenta-vendas já está registrado no main"
  assert_contains "$(json_get ERROR "$OUT")" "/speckit-refactor-validar"
  assert_eq "$(git symbolic-ref --short HEAD)" "main"
}

test_refactor_start_contrair_cria_branch() {
  fx_ready
  rf_registrado 90301-movimenta-vendas
  assert_ok rf_start 90301-movimenta-vendas --contrair
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "refactor/90301-movimenta-vendas-contrair"
  assert_eq "$(git symbolic-ref --short HEAD)" "refactor/90301-movimenta-vendas-contrair"
}

test_refactor_start_contrair_sem_registro_falha() {
  fx_ready
  assert_fails rf_start 90301-movimenta-vendas --contrair
  assert_contains "$(json_get ERROR "$OUT")" "o refactor 90301-movimenta-vendas não está registrado no main"
}

test_refactor_start_contrair_ja_na_branch_continua() {
  fx_ready
  rf_registrado 90301-movimenta-vendas
  rf_start 90301-movimenta-vendas --contrair >/dev/null
  assert_ok rf_start 90301-movimenta-vendas --contrair
  assert_eq "$(json_get EXISTING "$OUT")" "true"
}

test_refactor_start_contrair_de_novo_usa_o_proximo_numero() {
  fx_ready
  rf_registrado 90301-movimenta-vendas
  git push -q origin main:refs/heads/refactor/90301-movimenta-vendas-contrair
  assert_ok rf_start 90301-movimenta-vendas --contrair
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "refactor/90301-movimenta-vendas-contrair-2"
  assert_ok rf_start 90301-movimenta-vendas --contrair
  assert_eq "$(json_get EXISTING "$OUT")" "true"
}

test_refactor_start_rodada_usa_o_proximo_numero_livre() {
  fx_ready
  rf_registrado 90301-movimenta-vendas
  assert_ok rf_start 90301-movimenta-vendas --rodada
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "refactor/90301-movimenta-vendas-r2"
  git switch -q main
  assert_ok rf_start 90301-movimenta-vendas --rodada
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "refactor/90301-movimenta-vendas-r3"
}

test_refactor_start_rodada_pula_a_que_esta_no_origin() {
  fx_ready
  rf_registrado 90301-movimenta-vendas
  git push -q origin main:refs/heads/refactor/90301-movimenta-vendas-r2
  assert_ok rf_start 90301-movimenta-vendas --rodada
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "refactor/90301-movimenta-vendas-r3"
}

test_refactor_start_na_rodada_o_modo_padrao_continua() {
  fx_ready
  rf_registrado 90301-movimenta-vendas
  rf_start 90301-movimenta-vendas --rodada >/dev/null
  assert_ok rf_start 90301-movimenta-vendas
  assert_eq "$(json_get EXISTING "$OUT")" "true"
  assert_eq "$(json_get BRANCH_NAME "$OUT")" "refactor/90301-movimenta-vendas-r2"
}

test_refactor_start_branch_no_origin_falha() {
  fx_ready
  git push -q origin main:refs/heads/refactor/90201-extrai-montagem
  assert_fails rf_start 90201-extrai-montagem
  assert_contains "$(json_get ERROR "$OUT")" "a branch refactor/90201-extrai-montagem já existe no origin"
}

test_refactor_start_branch_local_falha() {
  fx_ready
  git branch refactor/90201-extrai-montagem
  assert_fails rf_start 90201-extrai-montagem
  assert_contains "$(json_get ERROR "$OUT")" "a branch refactor/90201-extrai-montagem já existe nesta máquina"
}

test_refactor_start_arvore_suja_para() {
  fx_ready
  echo x > sujo.txt
  assert_fails rf_start 90201-extrai-montagem
  assert_contains "$(json_get ERROR "$OUT")" "mudanças não commitadas"
  [ ! -d refactors ] || fail "não devia criar refactors/"
}

test_refactor_start_repassa_os_avisos_do_ws_start() {
  fx_ready
  upstream_commit r1 src/novo.txt "x"
  assert_ok rf_start 90201-extrai-montagem
  assert_contains "$(json_get AVISOS "$OUT")" "pullrequestcreate?sourceRef=ws/sync&targetRef=main"
}

test_refactor_registro_commita_refactors_e_envia_so_o_workspace() {
  fx_ready
  rf_start 90203-quantidade-zero >/dev/null
  mkdir -p refactors/90203-quantidade-zero
  echo "# reclassificar" > refactors/90203-quantidade-zero/assessment.md
  assert_ok rf_registro "docs(90203-quantidade-zero): diagnóstico, não é refactor"
  assert_contains "$OUT" "abra o PR do workspace para o main"
  assert_eq "$(git log -1 --format=%s)" "docs(90203-quantidade-zero): diagnóstico, não é refactor"
  git -C "$T/origin.git" rev-parse -q --verify refs/heads/refactor/90203-quantidade-zero >/dev/null \
    || fail "a branch devia estar no origin do workspace"
  ! git -C "$T/remotes/r1.git" rev-parse -q --verify refs/heads/refactor/90203-quantidade-zero >/dev/null \
    || fail "nenhum repo devia receber a branch"
}

test_refactor_registro_aceita_o_documento_do_desacoplamento() {
  fx_ready
  rf_registrado 90301-movimenta-vendas
  rf_start 90301-movimenta-vendas --contrair >/dev/null
  mkdir -p refactors/desacoplamentos
  echo "| linha |" > refactors/desacoplamentos/linx.md
  echo "# validação" > refactors/90301-movimenta-vendas/validacao.md
  assert_ok rf_registro "docs(90301-movimenta-vendas): validação sem sucesso"
  assert_eq "$(git show --name-only --format= HEAD | sort | paste -sd' ' -)" \
    "refactors/90301-movimenta-vendas/validacao.md refactors/desacoplamentos/linx.md"
}

test_refactor_registro_recusa_o_main() {
  fx_ready
  ws_commit refactors/x/assessment.md "# a"
  assert_fails rf_registro "docs(x): diagnóstico, não é refactor"
  assert_contains "$OUT" "ws-refactor-registro só roda numa branch refactor/<slug> (atual: main)"
}

test_refactor_registro_recusa_mudanca_fora_de_refactors() {
  fx_ready
  rf_start 90203-quantidade-zero >/dev/null
  mkdir -p refactors/90203-quantidade-zero
  echo "# a" > refactors/90203-quantidade-zero/assessment.md
  echo "v2" > repos/r1/src/app.txt
  assert_fails rf_registro "docs(90203-quantidade-zero): diagnóstico, não é refactor"
  assert_contains "$OUT" "há mudanças fora de refactors/: repos/r1/src/app.txt"
  assert_eq "$(git log -1 --format=%s)" "$(git log -1 --format=%s main)"
}

test_refactor_registro_sem_mensagem_falha() {
  fx_ready
  rf_start 90203-quantidade-zero >/dev/null
  mkdir -p refactors/90203-quantidade-zero
  echo "# a" > refactors/90203-quantidade-zero/assessment.md
  assert_fails rf_registro
  assert_contains "$OUT" "informe a mensagem de commit"
}

test_refactor_registro_nada_a_registrar_falha() {
  fx_ready
  rf_start 90203-quantidade-zero >/dev/null
  assert_fails rf_registro "docs(x): nada"
  assert_contains "$OUT" "nada a registrar em refactors/"
}

test_refactor_registro_aceita_commit_do_atlas() {
  fx_ready
  rf_start 90203-quantidade-zero >/dev/null
  ws_commit docs/atlas/r1/x.md "atlas" "atlas: atualiza mapeamento de r1"
  mkdir -p refactors/90203-quantidade-zero
  echo "# a" > refactors/90203-quantidade-zero/assessment.md
  assert_ok rf_registro "docs(90203-quantidade-zero): diagnóstico, não é refactor"
}

# Branch do refactor com um commit de caracterização em repos/r1/tests/ e o hash em CARAC.
fx_carac() {
  fx_ready
  git switch -q -c refactor/90201-extrai-montagem
  ws_commit repos/r1/tests/caracterizacao.txt "fixa v1" "test(90201-extrai-montagem): caracterização"
  CARAC=$(git rev-parse HEAD)
}

test_refactor_confere_caracterizacao_intacta() {
  fx_carac
  echo "v2" > repos/r1/src/app.txt
  git commit -qam "refactor"
  assert_ok rf_confere "$CARAC"
  assert_contains "$OUT" "ws: caracterização intacta: 1 arquivo(s)"
}

test_refactor_confere_teste_alterado_na_arvore_falha() {
  fx_carac
  echo "fixa v2" > repos/r1/tests/caracterizacao.txt
  assert_fails rf_confere "$CARAC"
  assert_contains "$OUT" "testes de caracterização alterados depois do commit ${CARAC:0:7}"
  assert_contains "$OUT" "repos/r1/tests/caracterizacao.txt"
}

test_refactor_confere_teste_alterado_e_commitado_falha() {
  fx_carac
  echo "fixa v2" > repos/r1/tests/caracterizacao.txt
  git commit -qam "ajusta teste"
  assert_fails rf_confere "$CARAC"
  assert_contains "$OUT" "repos/r1/tests/caracterizacao.txt"
}

test_refactor_confere_teste_apagado_falha() {
  fx_carac
  git rm -q repos/r1/tests/caracterizacao.txt
  git commit -qm "remove teste"
  assert_fails rf_confere "$CARAC"
  assert_contains "$OUT" "repos/r1/tests/caracterizacao.txt"
}

test_refactor_confere_commit_inexistente_falha() {
  fx_carac
  assert_fails rf_confere 0123456789abcdef0123456789abcdef01234567
  assert_contains "$OUT" "commit de caracterização não encontrado"
}

test_refactor_confere_commit_fora_da_branch_falha() {
  fx_carac
  git switch -q main
  ws_commit outro.txt "x" "outro"
  local fora
  fora=$(git rev-parse HEAD)
  git switch -q refactor/90201-extrai-montagem
  assert_fails rf_confere "$fora"
  assert_contains "$OUT" "não está na branch atual"
}

test_refactor_confere_sem_commit_falha() {
  fx_carac
  assert_fails rf_confere
  assert_contains "$OUT" "uso: ws-refactor-confere.sh <commit>"
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_refactor.sh`
Expected: FALHA em todos (os scripts não existem: `No such file or directory`).

- [ ] **Step 3: `ws-refactor-start.sh`**

```bash
#!/usr/bin/env bash
# Comando speckit.ws.refactor-start da extensão ws, chamado pelos hooks before_refactor_assess e
# before_refactor_validar: cria a branch do refactor com ws start (spec SP6, 5.3).
# Modos: (padrão) refactor/<slug>; --rodada refactor/<slug>-r<k>, com o próximo k livre a partir de 2;
# --contrair refactor/<slug>-contrair, ou -contrair-<k> com o próximo k livre a partir de 2 (uma validação
# que falhou deixa a -contrair anterior no origin).
# - Slug: <id do work item>-<descrição> ou rf-<AAAAMMDD>-<descrição>, em minúsculas e com hífens.
# - Já na branch do modo (no padrão, também numa -r<k> do mesmo slug): continua nela, sem ws start.
# - Padrão: refactor já registrado no main é erro. --rodada e --contrair exigem o registro no main.
# Uso: ws-refactor-start.sh <slug> [--rodada|--contrair]
# Saída: uma linha JSON com BRANCH_NAME, REFACTOR_DIRECTORY, EXISTING, ERROR e AVISOS.
set -uo pipefail

WS_DESTINO=${WS_DESTINO:-main}
USO="uso: ws-refactor-start.sh <slug> [--rodada|--contrair]"

json_str() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\r'/}
  s=${s//$'\t'/ }
  s=${s//$'\n'/\\n}
  printf '"%s"' "$s"
}

# branch pasta existente erro [avisos]
emit() {
  printf '{"BRANCH_NAME":%s,"REFACTOR_DIRECTORY":%s,"EXISTING":%s,"ERROR":%s,"AVISOS":%s}\n' \
    "$(json_str "$1")" "$(json_str "$2")" "$3" "$(json_str "$4")" "$(json_str "${5:-}")"
}

# saída do ws start -> os avisos e o link do PR da ws/sync, sem o prefixo "ws: ".
avisos_do_start() {
  printf '%s\n' "$1" | grep -E 'aviso:|pullrequestcreate' | sed 's/^ws: //' || true
}

fail() { emit "" "" false "$1"; exit 1; }

slug=${1:-}
modo=${2:-}
[ -n "$slug" ] || fail "$USO"
case "$modo" in ""|--rodada|--contrair) ;; *) fail "$USO" ;; esac
[[ $slug =~ ^([0-9]+|rf-[0-9]{8})-[a-z0-9]+(-[a-z0-9]+)*$ ]] \
  || fail "slug inválido: $slug. Use <id do work item>-<descrição> ou rf-<AAAAMMDD>-<descrição>, em minúsculas e com hífens"
dir="refactors/$slug"

root=$(git rev-parse --show-toplevel 2>/dev/null) || fail "fora de um repo git"
cd "$root" || exit 1

atual=$(git symbolic-ref --short -q HEAD || true)
case "$modo" in
  "")
    if [ "$atual" = "refactor/$slug" ] || [[ $atual =~ ^refactor/$slug-r[0-9]+$ ]]; then emit "$atual" "$dir" true ""; exit 0; fi ;;
  --rodada)
    if [[ $atual =~ ^refactor/$slug-r[0-9]+$ ]]; then emit "$atual" "$dir" true ""; exit 0; fi ;;
  --contrair)
    if [[ $atual =~ ^refactor/$slug-contrair(-[0-9]+)?$ ]]; then emit "$atual" "$dir" true ""; exit 0; fi ;;
esac

# O registro mergeado fica no main do origin; o ws start cria a branch a partir da ws/sync.
base=$WS_DESTINO
has_origin=false
if git remote get-url origin >/dev/null 2>&1; then
  has_origin=true
  git fetch -q origin "$WS_DESTINO" 2>/dev/null && base="origin/$WS_DESTINO"
fi
registrado=false
git cat-file -e "$base:$dir/assessment.md" 2>/dev/null && registrado=true

no_origin() { $has_origin && git ls-remote --exit-code --heads origin "$1" >/dev/null 2>&1; }
local_existe() { git show-ref --verify --quiet "refs/heads/$1"; }

case "$modo" in
  "")
    ! $registrado \
      || fail "o refactor $slug já está registrado no $WS_DESTINO ($dir/). Para uma nova rodada de uma fatia que falhou na validação, rode /speckit-refactor-assess citando o slug; para validar uma fatia em M1, rode /speckit-refactor-validar $slug"
    br="refactor/$slug" ;;
  --contrair)
    $registrado \
      || fail "o refactor $slug não está registrado no $WS_DESTINO; o PR do workspace com $dir/ precisa estar mergeado antes de validar"
    br="refactor/$slug-contrair"
    k=2
    while local_existe "$br" || no_origin "$br"; do br="refactor/$slug-contrair-$k"; k=$((k + 1)); done ;;
  --rodada)
    $registrado \
      || fail "o refactor $slug não está registrado no $WS_DESTINO; a nova rodada parte do registro mergeado"
    k=2
    while local_existe "refactor/$slug-r$k" || no_origin "refactor/$slug-r$k"; do k=$((k + 1)); done
    br="refactor/$slug-r$k" ;;
esac

if no_origin "$br"; then
  fail "a branch $br já existe no origin: faça checkout dela (git switch $br) para continuar o refactor"
fi
if local_existe "$br"; then
  fail "a branch $br já existe nesta máquina: faça checkout dela (git switch $br) para continuar o refactor"
fi

out=$(bash "${WS_BIN:-$root/tools/ws/ws}" start "$br" 2>&1) \
  || fail "$(printf '%s\n' "$out" | grep -v '^[[:space:]]*$' | tail -1 | sed 's/^ws: erro: //')"
emit "$br" "$dir" false "" "$(avisos_do_start "$out")"
```

- [ ] **Step 4: `ws-refactor-registro.sh`**

```bash
#!/usr/bin/env bash
# Comando speckit.ws.refactor-registro da extensão ws: registra no workspace um diagnóstico que não é
# refactor ou uma validação que falhou. Faz commit só de refactors/ e envia a branch refactor/<slug>
# ao origin do workspace, sem ws push, porque nenhum repo mudou (spec SP6, 5.3).
# Uso: ws-refactor-registro.sh "<mensagem de commit>"  — a mensagem é obrigatória quando há mudanças.
set -uo pipefail

WS_BASE=${WS_BASE:-ws/sync}
WS_DESTINO=${WS_DESTINO:-main}

log() { echo "ws: $*"; }
die() { echo "ws: erro: $*" >&2; exit 1; }

msg=${1:-}
root=$(git rev-parse --show-toplevel 2>/dev/null) || die "fora de um repo git"
cd "$root" || exit 1
branch=$(git symbolic-ref --short -q HEAD) || die "HEAD destacado; faça checkout da branch refactor/<slug>"
case "$branch" in
  refactor/*) ;;
  *) die "ws-refactor-registro só roda numa branch refactor/<slug> (atual: $branch)" ;;
esac

# Ponto em que a branch saiu da base: a ws/sync local, a do origin ou o main (adendo 6 do ADR 0001).
base=$WS_DESTINO
for r in "refs/heads/$WS_BASE" "refs/remotes/origin/$WS_BASE"; do
  if git show-ref --verify -q "$r"; then base=$r; break; fi
done
mb=$(git merge-base "$base" HEAD 2>/dev/null) || die "não achei o ponto em que a branch $branch saiu da base"

# Mudanças fora de refactors/ na árvore, no índice e nos commits da branch. Os commits em docs/atlas/
# são do Atlas do refactor-start.
lista() { git -c core.quotepath=off "$@"; }
fora=$( {
  lista diff --name-only --no-renames HEAD
  lista diff --name-only --no-renames --cached HEAD
  lista ls-files -o --exclude-standard
  lista diff --name-only --no-renames "$mb" HEAD | grep -v '^docs/atlas/'
} | grep -v '^refactors/' | sort -u | paste -sd' ' -)
[ -z "$fora" ] \
  || die "há mudanças fora de refactors/: $fora. O registro só leva relatórios; se houve mudança de código, siga /speckit-refactor-apply e /speckit-refactor-verify"

if [ -n "$(git status --porcelain --untracked-files=all -- refactors/)" ]; then
  [ -n "$msg" ] || die "informe a mensagem de commit"
  git add -A -- refactors/ || die "git add falhou"
  git commit -q -m "$msg" -- refactors/ || die "git commit falhou"
  log "commit: $(git log -1 --format='%h %s')"
fi

git diff --quiet "$mb" HEAD -- refactors/ && die "nada a registrar em refactors/"

if git remote get-url origin >/dev/null 2>&1; then
  git push -q -u origin "$branch" || die "push da branch $branch recusado"
  log "branch $branch enviada ao origin; abra o PR do workspace para o $WS_DESTINO"
else
  log "sem origin: o commit ficou só local"
fi
```

- [ ] **Step 5: `ws-refactor-confere.sh`**

```bash
#!/usr/bin/env bash
# Usado pelo /speckit-refactor-verify: confere que os testes de caracterização (os arquivos do commit
# de caracterização) não mudaram desde ele, contando o que ainda não foi commitado (spec SP6, 5.2 e
# regra VII da constitution).
# Uso: ws-refactor-confere.sh <commit>
set -uo pipefail

log() { echo "ws: $*"; }
die() { echo "ws: erro: $*" >&2; exit 1; }

c=${1:-}
[ -n "$c" ] || die "uso: ws-refactor-confere.sh <commit>"
root=$(git rev-parse --show-toplevel 2>/dev/null) || die "fora de um repo git"
cd "$root" || exit 1
git rev-parse -q --verify "$c^{commit}" >/dev/null || die "commit de caracterização não encontrado: $c"
git merge-base --is-ancestor "$c" HEAD || die "o commit $c não está na branch atual"

mapfile -t arqs < <(git -c core.quotepath=off diff-tree --no-commit-id --name-only -r --no-renames "$c")
[ ${#arqs[@]} -gt 0 ] || die "o commit $c não tem arquivos"

# Commit contra a árvore de trabalho: pega mudança commitada, em stage, na árvore e arquivo apagado.
alterados=$(git -c core.quotepath=off diff --name-only --no-renames "$c" -- "${arqs[@]}" | paste -sd' ' -)
[ -z "$alterados" ] \
  || die "testes de caracterização alterados depois do commit ${c:0:7}: $alterados. O refactor não pode mudar esses testes; desfaça a mudança neles ou registre uma nova exceção no assessment.md"
log "caracterização intacta: ${#arqs[@]} arquivo(s)"
```

- [ ] **Step 6: Rodar e ver passar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_refactor.sh`
Expected: todos `ok`. No `test_refactor_confere_teste_alterado_na_arvore_falha`, o hash curto do `git rev-parse` tem 7 caracteres, como o `${c:0:7}`.

- [ ] **Step 7: Suíte e commit**

```bash
bash tools/ws/tests/run.sh
git add tools/speckit/ws/scripts/bash/ws-refactor-*.sh tools/ws/tests/test_speckit_refactor.sh
git commit -m "harness: scripts de branch, registro e caracterização do refactor"
```

Expected: suíte com `0 falha(s)`.

---

### Task 5: `ws refactor` (pendentes, estado e marco) e aviso no `ws start`

**Files:**
- Create: `tools/ws/lib/refactor.sh`
- Modify: `tools/ws/ws:3,10-19`
- Modify: `tools/ws/lib/start.sh:171` (dentro de `ws_start`)
- Create: `tools/ws/tests/test_refactor.sh`

**Interfaces:**
- Consumes: `log`, `die`, `ws_root` (`common.sh`).
- Produces:
  - `ws refactor pendentes`: uma linha por fatia em `M1`, `M3` ou `M3-falhou`: `<nome>  <slug>  <marco> desde <data> (<n> dia(s)): <próximo passo>`; ou `ws: nenhuma fatia pendente`.
  - `ws refactor estado <slug>`: o marco (`M1`, `M3`, `M3-falhou` ou `M4`) na saída padrão; erro se a fatia não estiver em nenhuma tabela.
  - `ws refactor marco <slug> <M1|M3|M3-falhou|M4> [--desacoplamento <nome> --consumidor <repo> --objeto <objeto> --convivencia <AAAA-MM-DD>]`: grava a coluna Marco e a Data do marco (hoje); no M1 de fatia nova, acrescenta a linha. Usado pelos comandos da extensão `refactor` (Task 6).
  - `ws_refactor_aviso`: chamado pelo `ws_start`.
  - `WS_HOJE=<AAAA-MM-DD>` sobrepõe a data de hoje (testes).

- [ ] **Step 1: Escrever os testes**

`tools/ws/tests/test_refactor.sh`:

```bash
# Testes do ws refactor e do aviso do ws start (spec SP6, 4.4, 5.3 e 7).

CAB='| Fatia | Consumidor | Objeto | Marco | Data do marco | Convivência a partir de |'

# slug consumidor objeto marco data convivencia -> linha da tabela
linha() { echo "| [$1](../$1/) | $2 | $3 | $4 | $5 | $6 |"; }

# [linhas...] -> refactors/desacoplamentos/linx.md com a tabela e texto depois dela, commitado no main.
fx_linx() {
  fx_ready
  mkdir -p refactors/desacoplamentos
  printf '%s\n' '# Desacoplamento linx' '' '## Fatias' '' "$CAB" '|---|---|---|---|---|---|' "$@" \
    '' '## Dívidas de repo fora do escopo' '' '- nenhuma' > refactors/desacoplamentos/linx.md
  git add -A && git commit -qm "linx" && git push -q origin main
}

test_refactor_sem_subcomando_mostra_uso() {
  fx_ready
  assert_fails ws refactor
  assert_contains "$OUT" "uso: ws refactor <pendentes|estado|marco> [args]"
}

test_refactor_pendentes_sem_documentos() {
  fx_ready
  assert_ok ws refactor pendentes
  assert_contains "$OUT" "ws: nenhuma fatia pendente"
}

test_refactor_pendentes_m1_antes_da_data_aguarda() {
  fx_linx "$(linha 90301-movimenta-vendas wms.conector.backend Reserva.dbo.LX_MOVIMENTA_VENDAS_PA M1 2026-11-10 2026-12-01)"
  export WS_HOJE=2026-11-20
  assert_ok ws refactor pendentes
  assert_contains "$OUT" "linx  90301-movimenta-vendas  M1 desde 2026-11-10 (10 dia(s)): aguardando a convivência a partir de 2026-12-01"
}

test_refactor_pendentes_m1_depois_da_data_manda_validar() {
  fx_linx "$(linha 90301-movimenta-vendas wms.conector.backend Reserva.dbo.LX_MOVIMENTA_VENDAS_PA M1 2026-11-10 2026-12-01)"
  export WS_HOJE=2026-12-01
  assert_ok ws refactor pendentes
  assert_contains "$OUT" "M1 desde 2026-11-10 (21 dia(s)): virar a chave e rodar /speckit-refactor-validar 90301-movimenta-vendas (convivência desde 2026-12-01)"
}

test_refactor_pendentes_m3_m3falhou_e_ignora_m4() {
  fx_linx "$(linha 90301-a c o M3 2026-12-05 2026-12-01)" "$(linha 90302-b c o M3-falhou 2026-12-06 2026-12-01)" \
    "$(linha 90303-c c o M4 2026-12-07 2026-12-01)"
  export WS_HOJE=2026-12-10
  assert_ok ws refactor pendentes
  assert_contains "$OUT" "linx  90301-a  M3 desde 2026-12-05 (5 dia(s)): rodar /speckit-refactor-contrair 90301-a"
  assert_contains "$OUT" "linx  90302-b  M3-falhou desde 2026-12-06 (4 dia(s)): nova rodada com /speckit-refactor-assess 90302-b"
  assert_not_contains "$OUT" "90303-c"
}

test_refactor_pendentes_linha_fora_do_formato_avisa_e_segue() {
  fx_linx '| 90309-sem-link | c | o | M1 | 01/12/2026 | 2026-12-01 |' \
    "$(linha 90301-a c o M3 2026-12-05 2026-12-01)"
  export WS_HOJE=2026-12-10
  assert_ok ws refactor pendentes
  assert_contains "$OUT" "ws: aviso: linha fora do formato em refactors/desacoplamentos/linx.md:7"
  assert_contains "$OUT" "90301-a  M3 desde"
}

test_refactor_estado_devolve_o_marco() {
  fx_linx "$(linha 90301-a c o M3 2026-12-05 2026-12-01)"
  assert_ok ws refactor estado 90301-a
  assert_eq "$OUT" "M3"
}

test_refactor_estado_fatia_inexistente_falha() {
  fx_linx "$(linha 90301-a c o M3 2026-12-05 2026-12-01)"
  assert_fails ws refactor estado 90399-x
  assert_contains "$OUT" "a fatia 90399-x não está em nenhuma tabela de refactors/desacoplamentos/"
}

test_refactor_estado_fatia_duplicada_falha() {
  fx_linx "$(linha 90301-a c o M1 2026-12-05 2026-12-01)" "$(linha 90301-a c o M3 2026-12-06 2026-12-01)"
  assert_fails ws refactor estado 90301-a
  assert_contains "$OUT" "a fatia 90301-a aparece em mais de uma linha"
}

test_refactor_marco_m1_acrescenta_a_linha_no_fim_da_tabela() {
  fx_linx "$(linha 90301-a c o M4 2026-12-05 2026-12-01)"
  export WS_HOJE=2026-11-10
  assert_ok ws refactor marco 90302-movimenta-vendas M1 --desacoplamento linx --consumidor wms.conector.backend \
    --objeto Reserva.dbo.LX_MOVIMENTA_VENDAS_PA --convivencia 2026-12-01
  assert_contains "$OUT" "ws: fatia 90302-movimenta-vendas marcada em M1 em refactors/desacoplamentos/linx.md"
  assert_eq "$(sed -n 8p refactors/desacoplamentos/linx.md)" \
    "$(linha 90302-movimenta-vendas wms.conector.backend Reserva.dbo.LX_MOVIMENTA_VENDAS_PA M1 2026-11-10 2026-12-01)"
  assert_eq "$(sed -n 9p refactors/desacoplamentos/linx.md)" ""
  assert_eq "$(tail -1 refactors/desacoplamentos/linx.md)" "- nenhuma"
}

test_refactor_marco_m1_de_fatia_nova_exige_as_opcoes() {
  fx_linx
  assert_fails ws refactor marco 90302-x M1 --desacoplamento linx
  assert_contains "$OUT" "fatia nova: informe --desacoplamento, --consumidor, --objeto e --convivencia"
}

test_refactor_marco_m1_documento_inexistente_falha() {
  fx_ready
  assert_fails ws refactor marco 90302-x M1 --desacoplamento linx --consumidor c --objeto o --convivencia 2026-12-01
  assert_contains "$OUT" "não encontrei refactors/desacoplamentos/linx.md"
}

test_refactor_marco_m1_sem_tabela_falha() {
  fx_ready
  mkdir -p refactors/desacoplamentos && echo "# linx" > refactors/desacoplamentos/linx.md
  assert_fails ws refactor marco 90302-x M1 --desacoplamento linx --consumidor c --objeto o --convivencia 2026-12-01
  assert_contains "$OUT" "não tem a tabela de fatias"
}

test_refactor_marco_m1_convivencia_invalida_falha() {
  fx_linx
  assert_fails ws refactor marco 90302-x M1 --desacoplamento linx --consumidor c --objeto o --convivencia 01/12/2026
  assert_contains "$OUT" "data de convivência inválida: 01/12/2026"
}

test_refactor_marco_m3_depois_do_m1() {
  fx_linx "$(linha 90301-a c o M1 2026-11-10 2026-12-01)"
  export WS_HOJE=2026-12-15
  assert_ok ws refactor marco 90301-a M3
  assert_eq "$(sed -n 7p refactors/desacoplamentos/linx.md)" "$(linha 90301-a c o M3 2026-12-15 2026-12-01)"
}

test_refactor_marco_m3_sem_m1_recusa() {
  fx_linx "$(linha 90301-a c o M3-falhou 2026-12-05 2026-12-01)"
  assert_fails ws refactor marco 90301-a M3
  assert_contains "$OUT" "a fatia 90301-a está em M3-falhou; a validação exige o M1"
}

test_refactor_marco_m4_sem_m3_recusa() {
  fx_linx "$(linha 90301-a c o M1 2026-11-10 2026-12-01)"
  assert_fails ws refactor marco 90301-a M4
  assert_contains "$OUT" "a fatia 90301-a está em M1; a contração exige o M3 registrado (rode /speckit-refactor-validar)"
  assert_eq "$(sed -n 7p refactors/desacoplamentos/linx.md)" "$(linha 90301-a c o M1 2026-11-10 2026-12-01)"
}

test_refactor_marco_m4_depois_do_m3() {
  fx_linx "$(linha 90301-a c o M3 2026-12-15 2026-12-01)"
  export WS_HOJE=2026-12-20
  assert_ok ws refactor marco 90301-a M4
  assert_eq "$(sed -n 7p refactors/desacoplamentos/linx.md)" "$(linha 90301-a c o M4 2026-12-20 2026-12-01)"
}

test_refactor_marco_m1_de_novo_so_depois_de_m3_falhou() {
  fx_linx "$(linha 90301-a c o M3-falhou 2026-12-05 2026-12-01)" "$(linha 90302-b c o M1 2026-12-05 2026-12-01)"
  export WS_HOJE=2026-12-20
  assert_ok ws refactor marco 90301-a M1
  assert_eq "$(sed -n 7p refactors/desacoplamentos/linx.md)" "$(linha 90301-a c o M1 2026-12-20 2026-12-01)"
  assert_fails ws refactor marco 90302-b M1
  assert_contains "$OUT" "a fatia 90302-b está em M1; o M1 só vale para fatia nova ou depois de M3-falhou"
}

test_refactor_marco_preserva_a_convivencia_editada_a_mao() {
  fx_linx "$(linha 90301-a c o M1 2026-11-10 2027-01-15)"
  export WS_HOJE=2027-01-20
  assert_ok ws refactor marco 90301-a M3
  assert_contains "$(sed -n 7p refactors/desacoplamentos/linx.md)" "| 2027-01-15 |"
}

test_refactor_marco_aceita_documento_com_crlf() {
  fx_linx "$(linha 90301-a c o M1 2026-11-10 2026-12-01)"
  sed -i 's/$/\r/' refactors/desacoplamentos/linx.md
  export WS_HOJE=2026-12-15
  assert_ok ws refactor estado 90301-a
  assert_eq "$OUT" "M1"
  assert_ok ws refactor marco 90301-a M3
  assert_eq "$(sed -n 7p refactors/desacoplamentos/linx.md | tr -d '\r')" "$(linha 90301-a c o M3 2026-12-15 2026-12-01)"
  assert_eq "$(tr -cd '\r' < refactors/desacoplamentos/linx.md | wc -c | tr -d ' ')" "0"
}

test_refactor_marco_slug_invalido_falha() {
  fx_linx
  assert_fails ws refactor marco Fatia-X M3
  assert_contains "$OUT" "slug inválido: Fatia-X"
}

test_refactor_marco_marco_invalido_falha() {
  fx_linx "$(linha 90301-a c o M1 2026-11-10 2026-12-01)"
  assert_fails ws refactor marco 90301-a M2
  assert_contains "$OUT" "uso: ws refactor marco <slug> <M1|M3|M3-falhou|M4>"
}

test_refactor_aviso_do_start_depois_da_data() {
  fx_linx "$(linha 90301-a c o M1 2026-11-10 2026-12-01)" "$(linha 90302-b c o M1 2026-11-12 2026-11-25)" \
    "$(linha 90303-c c o M3 2026-11-12 2026-11-20)"
  export WS_HOJE=2026-12-02
  assert_ok ws start feat-x
  assert_contains "$OUT" "ws: aviso: 2 fatia(s) do desacoplamento linx aguardando validação desde 2026-11-25 (ws refactor pendentes)"
}

test_refactor_aviso_do_start_nao_aparece_antes_da_data() {
  fx_linx "$(linha 90301-a c o M1 2026-11-10 2026-12-01)"
  export WS_HOJE=2026-11-20
  assert_ok ws start feat-x
  assert_not_contains "$OUT" "aguardando validação"
}

test_refactor_aviso_do_start_sem_documentos_fica_quieto() {
  fx_ready
  assert_ok ws start feat-x
  assert_not_contains "$OUT" "desacoplamento"
}

test_refactor_aviso_do_start_ignora_linha_fora_do_formato() {
  fx_linx '| quebrada | sem | colunas |' "$(linha 90301-a c o M1 2026-11-10 2026-12-01)"
  export WS_HOJE=2026-12-02
  assert_ok ws start feat-x
  assert_contains "$OUT" "1 fatia(s) do desacoplamento linx aguardando validação desde 2026-12-01"
  assert_contains "$OUT" "ws: branch feat-x criada"
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_refactor.sh`
Expected: FALHA em todos (`uso: ws <add|start|...>`, porque o `ws` não conhece `refactor`). Exceção: `test_refactor_aviso_do_start_sem_documentos_fica_quieto` e `test_refactor_aviso_do_start_nao_aparece_antes_da_data`, que já passam.

- [ ] **Step 3: `tools/ws/lib/refactor.sh`**

```bash
# ws refactor: estado das fatias dos desacoplamentos, lido e gravado na tabela de fatias de
# refactors/desacoplamentos/<nome>.md (spec SP6, 4.4, 5.3 e 7). A coluna Marco só muda por aqui;
# a Convivência a partir de pode ser editada à mão. WS_HOJE=AAAA-MM-DD sobrepõe a data de hoje.

WS_REFACTOR_DIR=refactors/desacoplamentos
WS_REFACTOR_CAB='| Fatia | Consumidor | Objeto | Marco | Data do marco | Convivência a partir de |'
WS_REFACTOR_SLUG='^([0-9]+|rf-[0-9]{8})-[a-z0-9]+(-[a-z0-9]+)*$'

ws_refactor() {
  local sub=${1:-}
  [ $# -gt 0 ] && shift
  cd "$(ws_root)"
  case "$sub" in
    pendentes) ws_refactor_pendentes ;;
    estado)    ws_refactor_estado "$@" ;;
    marco)     ws_refactor_marco "$@" ;;
    *)         die "uso: ws refactor <pendentes|estado|marco> [args]" ;;
  esac
}

ws_refactor_hoje() { echo "${WS_HOJE:-$(date +%F)}"; }

# Uma linha por linha da tabela de fatias, separada por TAB:
# arquivo nº nome slug consumidor objeto marco data convivencia ok
# ok = 1 quando a linha segue o formato; 0 quando não (campo vazio vem como "-"). Tolera CRLF.
ws_refactor_linhas() {
  local f
  for f in "$WS_REFACTOR_DIR"/*.md; do
    [ -f "$f" ] || continue
    tr -d '\r' < "$f" | awk -v arq="$f" -v cab="$WS_REFACTOR_CAB" '
      function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
      function data(s) { return s ~ /^[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]$/ }
      function v(s) { s = trim(s); return s == "" ? "-" : s }
      BEGIN { nome = arq; sub(/^.*\//, "", nome); sub(/\.md$/, "", nome); OFS = "\t" }
      $0 == cab { dentro = 1; next }
      dentro && /^\|( *:?-+:? *\|)+ *$/ { next }
      dentro && /^\|/ {
        n = split($0, c, "|")
        f1 = trim(c[2]); slug = ""
        if (match(f1, /^\[[a-z0-9-]+\]/)) slug = substr(f1, 2, RLENGTH - 2)
        ok = (n == 8 && slug != "" && f1 == "[" slug "](../" slug "/)" && trim(c[3]) != "" && trim(c[4]) != "" \
              && trim(c[5]) ~ /^(M1|M3|M3-falhou|M4)$/ && data(trim(c[6])) && data(trim(c[7])))
        # Campo vazio vira "-": o read com IFS de TAB juntaria TABs seguidos.
        print arq, NR, nome, v(slug), v(c[3]), v(c[4]), v(c[5]), v(c[6]), v(c[7]), ok
        next
      }
      dentro { dentro = 0 }
    '
  done
}

# AAAA-MM-DD AAAA-MM-DD -> dias entre as duas datas
ws_refactor_dias() { echo $(( ( $(date -u -d "$2" +%s) - $(date -u -d "$1" +%s) ) / 86400 )); }

ws_refactor_pendentes() {
  local hoje arq n nome slug cons obj marco data conv ok passo achou=0
  hoje=$(ws_refactor_hoje)
  while IFS=$'\t' read -r arq n nome slug cons obj marco data conv ok; do
    if [ "$ok" != 1 ]; then
      log "aviso: linha fora do formato em $arq:$n; confira as colunas da tabela de fatias (camada 2 da doc)"
      continue
    fi
    case "$marco" in
      M1)
        if [[ "$conv" > "$hoje" ]]; then
          passo="aguardando a convivência a partir de $conv"
        else
          passo="virar a chave e rodar /speckit-refactor-validar $slug (convivência desde $conv)"
        fi ;;
      M3) passo="rodar /speckit-refactor-contrair $slug" ;;
      M3-falhou) passo="nova rodada com /speckit-refactor-assess $slug" ;;
      *) continue ;;
    esac
    echo "$nome  $slug  $marco desde $data ($(ws_refactor_dias "$data" "$hoje") dia(s)): $passo"
    achou=1
  done < <(ws_refactor_linhas)
  [ $achou -eq 1 ] || log "nenhuma fatia pendente"
}

# slug -> grava em RF_MARCO, RF_ARQ e RF_LINHA a linha da fatia (vazios se não houver). Falha se houver duas.
ws_refactor_acha() {
  local alvo=$1 arq n nome slug cons obj marco data conv ok
  RF_MARCO="" RF_ARQ="" RF_LINHA=""
  while IFS=$'\t' read -r arq n nome slug cons obj marco data conv ok; do
    [ "$ok" = 1 ] && [ "$slug" = "$alvo" ] || continue
    [ -z "$RF_MARCO" ] || die "a fatia $alvo aparece em mais de uma linha; corrija a tabela"
    RF_MARCO=$marco RF_ARQ=$arq RF_LINHA=$n
  done < <(ws_refactor_linhas)
}

ws_refactor_estado() {
  local alvo=${1:-}
  [ -n "$alvo" ] || die "uso: ws refactor estado <slug>"
  ws_refactor_acha "$alvo"
  [ -n "$RF_MARCO" ] || die "a fatia $alvo não está em nenhuma tabela de $WS_REFACTOR_DIR/"
  echo "$RF_MARCO"
}

ws_refactor_marco() {
  local uso="uso: ws refactor marco <slug> <M1|M3|M3-falhou|M4> [--desacoplamento <nome> --consumidor <repo> --objeto <objeto> --convivencia <AAAA-MM-DD>]"
  [ $# -ge 2 ] || die "$uso"
  local alvo=$1 novo=$2 des="" cons="" obj="" conv="" hoje tmp arq
  shift 2
  while [ $# -gt 0 ]; do
    case "$1" in
      --desacoplamento) des=${2:-}; shift 2 ;;
      --consumidor) cons=${2:-}; shift 2 ;;
      --objeto) obj=${2:-}; shift 2 ;;
      --convivencia) conv=${2:-}; shift 2 ;;
      *) die "$uso" ;;
    esac
  done
  [[ $alvo =~ $WS_REFACTOR_SLUG ]] || die "slug inválido: $alvo"
  case "$novo" in M1|M3|M3-falhou|M4) ;; *) die "$uso" ;; esac
  hoje=$(ws_refactor_hoje)
  ws_refactor_acha "$alvo"
  case "$novo" in
    M1) [ -z "$RF_MARCO" ] || [ "$RF_MARCO" = M3-falhou ] \
          || die "a fatia $alvo está em $RF_MARCO; o M1 só vale para fatia nova ou depois de M3-falhou" ;;
    M3|M3-falhou) [ "$RF_MARCO" = M1 ] \
          || die "a fatia $alvo está em ${RF_MARCO:-nenhuma tabela}; a validação exige o M1" ;;
    M4) [ "$RF_MARCO" = M3 ] \
          || die "a fatia $alvo está em ${RF_MARCO:-nenhuma tabela}; a contração exige o M3 registrado (rode /speckit-refactor-validar)" ;;
  esac
  tmp=$(mktemp)
  if [ -n "$RF_MARCO" ]; then
    arq=$RF_ARQ
    tr -d '\r' < "$arq" | awk -F'|' -v n="$RF_LINHA" -v m="$novo" -v d="$hoje" \
      'BEGIN { OFS = "|" } NR == n { $5 = " " m " "; $6 = " " d " " } { print }' > "$tmp"
  else
    [ -n "$des" ] && [ -n "$cons" ] && [ -n "$obj" ] && [ -n "$conv" ] \
      || die "fatia nova: informe --desacoplamento, --consumidor, --objeto e --convivencia"
    [[ $des =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || die "nome de desacoplamento inválido: $des"
    [[ $conv =~ ^[0-9]{4}-[0-1][0-9]-[0-3][0-9]$ ]] || die "data de convivência inválida: $conv (use AAAA-MM-DD)"
    arq="$WS_REFACTOR_DIR/$des.md"
    [ -f "$arq" ] || die "não encontrei $arq; o /speckit-refactor-assess cria o documento do desacoplamento"
    tr -d '\r' < "$arq" > "$tmp"
    grep -qxF "$WS_REFACTOR_CAB" "$tmp" || die "$arq não tem a tabela de fatias (cabeçalho: $WS_REFACTOR_CAB)"
    awk -v cab="$WS_REFACTOR_CAB" -v row="| [$alvo](../$alvo/) | $cons | $obj | M1 | $hoje | $conv |" '
      NR == FNR {
        if (!fim && $0 == cab) dentro = 1
        if (dentro && /^\|/) { ult = FNR; next }
        if (dentro) { dentro = 0; fim = 1 }
        next
      }
      { print }
      FNR == ult { print row }
    ' "$tmp" "$tmp" > "$tmp.novo"
    mv "$tmp.novo" "$tmp"
  fi
  mv "$tmp" "$arq"
  log "fatia $alvo marcada em $novo em $arq"
}

# Aviso do ws start: fatias em M1 com a convivência vencida, por desacoplamento. Nunca falha.
ws_refactor_aviso() {
  [ -d "$WS_REFACTOR_DIR" ] || return 0
  local hoje
  hoje=$(ws_refactor_hoje)
  ws_refactor_linhas 2>/dev/null | awk -F'\t' -v h="$hoje" '
    $10 == 1 && $7 == "M1" && $9 <= h { n[$3]++; if (!($3 in d) || $9 < d[$3]) d[$3] = $9 }
    END { for (k in n) printf "ws: aviso: %d fatia(s) do desacoplamento %s aguardando validação desde %s (ws refactor pendentes)\n", n[k], k, d[k] }
  ' || true
}
```

- [ ] **Step 4: Ligar no `ws` e no `ws start`**

`tools/ws/ws`, linha 3: `# Uso: tools/ws/ws <add|start|sync|push|maintain|speckit|atlas|refactor> [args]`. No `case`, depois de `atlas)`:

```bash
  refactor) ws_refactor "$@" ;;
```

e a linha do `*)`:

```bash
  *)        die "uso: ws <add|start|sync|push|maintain|speckit|atlas|refactor> [args]" ;;
```

`tools/ws/lib/start.sh`, em `ws_start`, depois de `log "branch $br criada"`:

```bash
  ws_refactor_aviso
```

- [ ] **Step 5: Rodar e ver passar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_refactor.sh`
Expected: todos `ok`.

Em `test_refactor_marco_m1_acrescenta_a_linha_no_fim_da_tabela`, a tabela do fixture ocupa as linhas 5 (cabeçalho), 6 (separador) e 7 (linha M4). A linha nova entra na 8, antes da linha em branco que separa a tabela de "## Dívidas de repo fora do escopo".

- [ ] **Step 6: Suíte e commit**

```bash
bash tools/ws/tests/run.sh
git add tools/ws/lib/refactor.sh tools/ws/ws tools/ws/lib/start.sh tools/ws/tests/test_refactor.sh
git commit -m "harness: ws refactor (pendentes, estado e marco) e aviso no ws start"
```

Expected: suíte com `0 falha(s)`. Os testes do `ws start` existentes continuam verdes: sem `refactors/`, o aviso não imprime nada.

---

### Task 6: Extensão `refactor` e comandos da `ws`

**Files:**
- Create: `tools/speckit/refactor/extension.yml`
- Create: `tools/speckit/refactor/hooks.md`
- Create: `tools/speckit/refactor/commands/speckit.refactor.assess.md`
- Create: `tools/speckit/refactor/commands/speckit.refactor.apply.md`
- Create: `tools/speckit/refactor/commands/speckit.refactor.verify.md`
- Create: `tools/speckit/refactor/commands/speckit.refactor.validar.md`
- Create: `tools/speckit/refactor/commands/speckit.refactor.contrair.md`
- Create: `tools/speckit/refactor/templates/assessment-template.md`
- Create: `tools/speckit/refactor/templates/desacoplamento-template.md`
- Create: `tools/speckit/ws/commands/speckit.ws.refactor-start.md`
- Create: `tools/speckit/ws/commands/speckit.ws.refactor-registro.md`
- Create: `tools/speckit/ws/commands/speckit.ws.refactor-enviar.md`
- Modify: `tools/speckit/ws/extension.yml`
- Modify: `tools/ws/lib/speckit.sh`
- Modify: `tools/ws/tests/test_speckit_refactor.sh`, `tools/ws/tests/test_speckit_install.sh`
- Regenerate: `.specify/`, `.claude/skills/`

**Interfaces:**
- Consumes: `ws-refactor-start.sh`, `ws-refactor-registro.sh`, `ws-refactor-confere.sh` (Task 4); `ws refactor estado|marco|pendentes` (Task 5); `ws-commit-push.sh` (existente); skills `atlas-consultar` e `atlas-atualizar` (existentes).
- Produces: as skills `/speckit-refactor-assess`, `/speckit-refactor-apply`, `/speckit-refactor-verify`, `/speckit-refactor-validar`, `/speckit-refactor-contrair`, `/speckit-ws-refactor-start`, `/speckit-ws-refactor-registro` e `/speckit-ws-refactor-enviar`; os eventos `before_`/`after_refactor_<assess|apply|verify|validar|contrair>`.

- [ ] **Step 1: Escrever os testes offline da fonte**

Acrescente ao fim de `tools/ws/tests/test_speckit_refactor.sh`:

```bash
RF_SRC="$WS_DIR/../speckit/refactor"

test_extensao_refactor_lista_os_cinco_comandos_com_arquivo() {
  local y="$RF_SRC/extension.yml" c f
  assert_contains "$(cat "$y")" "id: refactor"
  for c in assess apply verify validar contrair; do
    grep -qF "name: speckit.refactor.$c" "$y" || fail "extension.yml sem speckit.refactor.$c"
    f="$RF_SRC/commands/speckit.refactor.$c.md"
    [ -f "$f" ] || fail "falta $f"
    grep -qF "before_refactor_$c" "$f" || fail "speckit.refactor.$c não dispara before_refactor_$c"
    grep -qF "after_refactor_$c" "$f" || fail "speckit.refactor.$c não dispara after_refactor_$c"
    grep -qF '.specify/extensions/refactor/hooks.md' "$f" || fail "speckit.refactor.$c não segue o hooks.md"
  done
  [ -f "$RF_SRC/hooks.md" ] || fail "falta hooks.md"
  [ -f "$RF_SRC/templates/assessment-template.md" ] || fail "falta o modelo do assessment"
  [ -f "$RF_SRC/templates/desacoplamento-template.md" ] || fail "falta o modelo do documento do desacoplamento"
}

test_modelo_do_desacoplamento_tem_o_cabecalho_da_tabela() {
  grep -qxF '| Fatia | Consumidor | Objeto | Marco | Data do marco | Convivência a partir de |' \
    "$RF_SRC/templates/desacoplamento-template.md" || fail "modelo sem o cabeçalho exato da tabela de fatias"
}

test_ws_registra_os_hooks_de_refactor() {
  local y="$WS_DIR/../speckit/ws/extension.yml" ev cmd
  for ev in before_refactor_assess:speckit.ws.refactor-start after_refactor_assess:speckit.ws.refactor-registro \
            after_refactor_verify:speckit.ws.refactor-enviar before_refactor_validar:speckit.ws.refactor-start \
            after_refactor_validar:speckit.ws.refactor-registro after_refactor_contrair:speckit.ws.refactor-enviar; do
    cmd=$(awk -v e="  ${ev%%:*}:" '$0 == e { getline; sub(/^ *command: */, ""); print; exit }' "$y")
    assert_eq "$cmd" "${ev#*:}" "hook ${ev%%:*}"
  done
  assert_contains "$(cat "$y")" 'version: "1.4.0"'
  for cmd in refactor-start refactor-registro refactor-enviar; do
    [ -f "$WS_DIR/../speckit/ws/commands/speckit.ws.$cmd.md" ] || fail "falta speckit.ws.$cmd.md"
  done
}

test_contrair_confere_os_dois_portoes() {
  local f="$RF_SRC/commands/speckit.refactor.contrair.md"
  grep -qF 'tools/ws/ws refactor estado' "$f" || fail "contrair sem o portão do M3"
  grep -qF 'docs/atlas/impacto/' "$f" || fail "contrair sem o portão do Atlas"
  grep -qF 'tools/ws/ws refactor marco' "$f" || fail "contrair não grava o M4"
}

test_verify_confere_a_caracterizacao() {
  grep -qF 'ws-refactor-confere.sh' "$RF_SRC/commands/speckit.refactor.verify.md" \
    || fail "verify não confere os testes de caracterização"
}
```

Em `tools/ws/tests/test_speckit_install.sh`, acrescente:

```bash
test_speckit_instala_a_extensao_refactor_e_os_hooks() {
  precisa_rede || return 0
  fx_speckit
  local s ext
  for s in speckit-refactor-assess speckit-refactor-apply speckit-refactor-verify speckit-refactor-validar \
           speckit-refactor-contrair speckit-ws-refactor-start speckit-ws-refactor-registro speckit-ws-refactor-enviar; do
    [ -f ".claude/skills/$s/SKILL.md" ] || fail "falta a skill $s"
  done
  [ -f .specify/extensions/refactor/hooks.md ] || fail "falta o hooks.md instalado"
  [ -f .specify/extensions/refactor/templates/assessment-template.md ] || fail "falta o modelo instalado"
  ext=$(cat .specify/extensions.yml)
  assert_contains "$ext" "before_refactor_assess:"
  assert_contains "$ext" "command: speckit.ws.refactor-start"
  assert_contains "$ext" "after_refactor_contrair:"
  assert_contains "$ext" "command: speckit.ws.refactor-enviar"
  assert_contains "$ext" "command: speckit.ws.refactor-registro"
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_refactor.sh`
Expected: FALHA nos cinco testes novos; os da Task 4 continuam `ok`.

- [ ] **Step 3: `extension.yml` e `hooks.md` da `refactor`**

`tools/speckit/refactor/extension.yml`:

```yaml
schema_version: "1.0"

extension:
  id: refactor
  name: "Refactor do workspace WMS"
  version: "1.0.0"
  description: "Refactor interno e fatia de desacoplamento: diagnóstico, caracterização, refactor, verificação, validação e contração (spec SP6)"
  author: workspace-wms
  repository: https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace
  license: Proprietary

requires:
  speckit_version: ">=1.2.0"

provides:
  commands:
    - name: speckit.refactor.assess
      file: commands/speckit.refactor.assess.md
      description: "Diagnóstico do refactor ou da fatia de desacoplamento, só leitura"
    - name: speckit.refactor.apply
      file: commands/speckit.refactor.apply.md
      description: "Testes de caracterização e o refactor proposto no diagnóstico"
    - name: speckit.refactor.verify
      file: commands/speckit.refactor.verify.md
      description: "Build, testes e caracterização intacta; marca o M1"
    - name: speckit.refactor.validar
      file: commands/speckit.refactor.validar.md
      description: "Confere a evidência da convivência contra os critérios; marca M3 ou M3-falhou"
    - name: speckit.refactor.contrair
      file: commands/speckit.refactor.contrair.md
      description: "Remove o caminho acoplado e a chave depois do M3; marca o M4"

tags:
  - "workspace"
  - "refactor"
```

`tools/speckit/refactor/hooks.md`:

````markdown
# Hooks da extensão refactor

Cada comando `speckit.refactor.<comando>` dispara o evento `before_refactor_<comando>` antes de começar e o `after_refactor_<comando>` no fim, como os comandos do core e da extensão `bug`. A extensão `ws` registra neles a branch e o envio. Para disparar um evento:

1. Leia `.specify/extensions.yml`. Se ele não existir, ou se não houver entradas em `hooks.<evento>`, siga sem dizer nada.
2. Se o YAML não puder ser lido, não pule em silêncio: diga ao usuário que `.specify/extensions.yml` não pôde ser lido (com o erro) e que nenhum hook foi conferido, inclusive os obrigatórios, e **pare**. Sem os hooks não há branch nem envio.
3. Ignore as entradas com `enabled: false`. Uma entrada sem `enabled` vale.
4. Não avalie `condition`: uma entrada com `condition` não vazia fica para o HookExecutor; pule-a.
5. O nome do comando vira skill trocando os pontos por hífens: `speckit.ws.refactor-start` vira `/speckit-ws-refactor-start`.
6. Para cada entrada que vale, na ordem do arquivo:
   - **obrigatória (`optional: false`):** mostre

     ```
     ## Extension Hooks

     **Automatic Hook**: {extension}
     Executing: `/{command}`
     EXECUTE_COMMAND: {command}
     ```

     e **rode** a skill nesta sessão, esperando ela terminar antes de seguir. Mostrar o bloco não roda o hook. Se o hook terminar dizendo para parar (por exemplo, `ERROR` na branch), **pare** também o comando que disparou o evento;
   - **opcional (`optional: true`):** mostre o comando e a descrição e pergunte se o usuário quer rodar.
````

- [ ] **Step 4: Modelos**

`tools/speckit/refactor/templates/assessment-template.md`:

```markdown
# Refactor: <título curto>

- **Slug:** <slug>
- **Work item:** <id, ou "nenhum">
- **Tipo:** interno | desacoplamento
- **Desacoplamento:** <nome> (só no tipo desacoplamento)
- **Veredito:** refactor | reclassificar
- **Data:** <AAAA-MM-DD>

## Estado atual e alvo

<como o código está hoje e como fica; arquivos e classes>

## O que não pode mudar no comportamento

<entradas, saídas, efeitos no banco, mensagens e erros que ficam iguais>

## Afetados

<consumidores, pelo índice de impacto do Atlas (`docs/atlas/impacto/`), citando a página consultada; "nenhum" se o refactor não toca contrato>

## Caracterização

**Plano:** <testes que fixam o comportamento atual, com o framework de testes do repo, e onde ficam>

<ou, quando o trecho não é testável sem um refactor anterior:>

**Exceção:** <motivo>
**Verificação que substitui:** <passo manual, com o resultado esperado>
**Aprovada pelo usuário:** pendente

## Dívidas de repo fora do escopo

<dívidas que o código tocado tem (por exemplo, as Dívidas de Conformidade do AWX) e que ficam fora, pela regra VII; "nenhuma">

## Desacoplamento

(só no tipo desacoplamento)

- **Consumidor:** repos/<repo>
- **Provedor:** repos/<repo>
- **Objeto do banco:** <Reserva.dbo.<objeto>>
- **Contrato novo:** <endpoint ou evento>
- **Chave:** <mecanismo e nome>; começa em "antigo"
- **Modo de convivência:** paralelo | sombra | troca direta
- **Critérios do M3:** <cada critério com a consulta ou o log que o dev vai rodar>
- **Convivência a partir de:** <AAAA-MM-DD>

## Para retomar

(preenchida pelo `/speckit-refactor-verify`)
```

`tools/speckit/refactor/templates/desacoplamento-template.md`:

```markdown
# Desacoplamento <nome>

## Objetivo e critério de fim

<o que sai do caminho. No LINX: o WMS não depende do banco Reserva para funcionar; a dependência passa para os serviços de integração (regra II da constitution)>

O desacoplamento termina quando o inventário não tiver mais acesso de sistema do WMS ao banco de origem.

## Padrão do caminho novo

<definido pelo time, com o link do ADR. Até ser preenchido, nenhuma fatia segue>

## Inventário

| Objeto | Consumidores | Leitura ou escrita | Página do índice de impacto |
|---|---|---|---|

## Fatias

O marco só muda pelos comandos de refactor (`tools/ws/ws refactor marco`). A coluna "Convivência a partir de" pode ser editada à mão.

| Fatia | Consumidor | Objeto | Marco | Data do marco | Convivência a partir de |
|---|---|---|---|---|---|

## Dívidas de repo fora do escopo

- nenhuma
```

- [ ] **Step 5: `speckit.refactor.assess.md`**

```markdown
---
description: "Diagnóstico de um refactor ou de uma fatia de desacoplamento, só leitura, com as regras do workspace WMS"
---

# Diagnóstico do refactor

**Idioma:** responda ao usuário sempre em português do Brasil, inclusive em erros e perguntas. Não proponha mudanças no harness (`tools/`, `.specify/`, `.claude/`, `AGENTS.md`) como próximo passo: descreva o problema e sugira registrá-lo para o time do harness.

## Entrada

```text
$ARGUMENTS
```

O relato: work item, motivo e o que mudar na estrutura. Pode citar o slug de uma fatia que já existe.

## 1. Slug e tipo

- **Slug:** `<id do work item>-<descrição>`; sem work item, `rf-<AAAAMMDD>-<descrição>`, com a data de hoje. A descrição tem de 2 a 4 palavras, em minúsculas, sem acento, separadas por hífen.
- **Tipo:**
  - **interno:** muda a estrutura dentro de um repo, sem contrato novo nem mudado;
  - **desacoplamento:** um consumidor deixa de acessar um objeto do banco `Reserva` (tabela, view, proc ou outro mecanismo do banco) e passa por um contrato novo (endpoint ou evento) num provedor.
- **Fora deste comando:** mover código entre projetos ou repos, ou migrar do legado para o AWX. Diga que esses tipos ficam para um subprojeto futuro e que, por enquanto, seguem como feature (`/speckit-specify`) ou pelo fluxo manual do `AGENTS.md`, e **pare** sem criar branch.
- **Nova rodada:** se o relato cita um slug em que `tools/ws/ws refactor estado <slug>` devolve `M3-falhou`, é uma nova rodada da mesma fatia: use o mesmo slug.

## 2. Antes

Dispare o evento `before_refactor_assess` seguindo `.specify/extensions/refactor/hooks.md`. O `/speckit-ws-refactor-start` cria a branch (`--rodada` numa nova rodada). Se ele devolver `ERROR`, **pare**: não crie a pasta nem o relatório. Antes de gravar qualquer arquivo, confirme com `git branch --show-current` que você está na `BRANCH_NAME` dele.

## 3. Diagnóstico, só leitura

- Não altere nada em `repos/`.
- Leia as instruções de cada repo tocado (regra 1 do `AGENTS.md`).
- Use o Atlas pela skill `atlas-consultar` para achar repos e objetos, e o índice de impacto (`docs/atlas/impacto/`) para os afetados (regra II da constitution).
- **Banco (opcional):** só `SELECT`, só com um acesso que o usuário já tenha, mostrando a consulta e esperando a confirmação. Sem acesso, escreva a consulta para o usuário rodar e colar o resultado. Valores sensíveis não vão para o relatório.
- **Desacoplamento:**
  - ache o documento em `refactors/desacoplamentos/<nome>.md`. Se houver mais de um e o relato não disser qual, pergunte;
  - se não existir, ofereça criá-lo a partir de `.specify/extensions/refactor/templates/desacoplamento-template.md`, com o inventário tirado do Atlas (objetos do banco de origem que o WMS acessa, consumidores, leitura ou escrita). A seção "Padrão do caminho novo" é do time: pergunte se o usuário quer ditá-la agora;
  - se o "Padrão do caminho novo" estiver vazio, grave o documento, diga que a fatia espera o padrão e o ADR, e **pare** sem gravar o `assessment.md`. Rodar este comando de novo, na mesma branch, continua de onde parou;
  - rode `tools/ws/ws refactor pendentes` e mostre as fatias que tocam o mesmo objeto ou o mesmo consumidor;
  - siga o padrão do caminho novo registrado no documento;
  - o objeto do banco de onde o consumidor sai **não muda** enquanto outro sistema ainda o acessar (regra II).
- **Dívidas de repo** (como as Dívidas de Conformidade do AWX) ficam fora do escopo (regra VII): liste as que o código tocado tem.
- **Não é refactor:** se a mudança altera o comportamento observável ou um contrato existente, o veredito é `reclassificar`, com o motivo e a recomendação (feature, bug ou subprojeto futuro).

## 4. Relatório

- Grave `refactors/<slug>/assessment.md` a partir de `.specify/extensions/refactor/templates/assessment-template.md`, preenchendo todas as seções que valem para o tipo. A seção "Para retomar" fica como está no modelo.
- Se o arquivo já existir e não for uma nova rodada, pergunte antes de sobrescrever.
- **Nova rodada:** não sobrescreva. Acrescente antes de "Para retomar" uma seção `## Rodada <k>` (o k da branch `-r<k>`) com as divergências do `refactors/<slug>/validacao.md` e o que muda no caminho novo.
- **Caracterização:** prefira o plano. Use a exceção só quando o trecho não for testável sem um refactor anterior (tela WebForms, acesso ao banco dentro da tela, `static` acoplado), e deixe `Aprovada pelo usuário: pendente`.

## 5. Depois

Dispare o evento `after_refactor_assess` seguindo `.specify/extensions/refactor/hooks.md`.

## 6. Conclusão

Mostre o slug, o tipo, o veredito, a branch e o caminho do relatório. Com o veredito `refactor`, o próximo passo é: "leia o `assessment.md`, corrija o que precisar, aprove a exceção de caracterização se houver, e rode `/speckit-refactor-apply`".
```

- [ ] **Step 6: `speckit.refactor.apply.md`**

```markdown
---
description: "Testes de caracterização e o refactor proposto no diagnóstico, com as regras do workspace WMS"
---

# Refactor: caracterização e mudança

**Idioma:** responda ao usuário sempre em português do Brasil, inclusive em erros e perguntas. Não proponha mudanças no harness (`tools/`, `.specify/`, `.claude/`, `AGENTS.md`) como próximo passo: descreva o problema e sugira registrá-lo para o time do harness.

## Entrada

```text
$ARGUMENTS
```

## 1. Qual refactor

- Sem slug na entrada nem na conversa, use o da branch atual quando ela for `refactor/<slug>` ou `refactor/<slug>-r<k>` e existir `refactors/<slug>/assessment.md`. Diga que o slug veio da branch.
- Fora dessas branches, procure `refactors/*/assessment.md`. Com mais de um candidato, pergunte qual.
- Confirme com `git branch --show-current` que você está na branch do refactor. Se não estiver, pare e peça ao usuário para fazer `git switch refactor/<slug>`.
- Leia o `assessment.md`. Se o veredito for `reclassificar`, pare: não há o que aplicar.
- Se a caracterização for uma exceção com `Aprovada pelo usuário: pendente`, mostre a exceção e pergunte se o usuário aprova. Com o sim, troque por `sim, <AAAA-MM-DD>`. Com o não, pare e sugira rodar `/speckit-refactor-assess` de novo.

## 2. Antes

Dispare o evento `before_refactor_apply` seguindo `.specify/extensions/refactor/hooks.md`.

## 3. Caracterização

- **Com plano:** escreva os testes de caracterização do plano, com o framework de testes do repo. Eles fixam o comportamento **atual**: rode-os e confirme que passam antes de mexer no código. Faça um commit só com esses arquivos de teste:

  ```bash
  git add <arquivos de teste>
  git commit -m "test(<slug>): caracterização"
  ```

  Guarde o hash (`git rev-parse HEAD`).
- **Com exceção aprovada:** não há commit de caracterização. Siga.

## 4. Refactor

- Cada mudança em `repos/<repo>/` segue as instruções daquele repo (regra 1 do `AGENTS.md`).
- Faça só o que o `assessment.md` propõe. Nada de refatoração fora do escopo (regra VI).
- **Nunca** altere nem apague os testes de caracterização: o `/speckit-refactor-verify` confere.
- **Desacoplamento, nesta ordem:**
  1. **provedor:** o contrato novo, com os testes dele. Build e testes do provedor;
  2. **consumidor:** o caminho novo atrás da chave, que começa em "antigo", com o comportamento atual intacto nesse modo. Build e testes do consumidor;
  3. o objeto do banco de onde o consumidor sai não muda (regra II).

## 5. Relatório

Grave `refactors/<slug>/apply.md` com:
- **Caracterização:** o hash do commit e a lista dos arquivos de teste, ou `exceção aprovada em <data>`;
- **Mudanças por repo:** os arquivos e o que mudou;
- **Desacoplamento:** o contrato novo e como a chave é virada em cada modo.

## 6. Depois

Dispare o evento `after_refactor_apply` seguindo `.specify/extensions/refactor/hooks.md`.

## 7. Conclusão

Mostre o resumo e o próximo passo: `/speckit-refactor-verify`.
```

- [ ] **Step 7: `speckit.refactor.verify.md`**

```markdown
---
description: "Build, testes e caracterização intacta do refactor; marca o M1"
---

# Refactor: verificação (M1)

**Idioma:** responda ao usuário sempre em português do Brasil, inclusive em erros e perguntas. Não proponha mudanças no harness (`tools/`, `.specify/`, `.claude/`, `AGENTS.md`) como próximo passo: descreva o problema e sugira registrá-lo para o time do harness.

## Entrada

```text
$ARGUMENTS
```

## 1. Qual refactor

Resolva o slug como no `/speckit-refactor-apply`: entrada, conversa, branch `refactor/<slug>` ou `refactor/<slug>-r<k>`, ou o único `refactors/*/apply.md`. Confirme a branch com `git branch --show-current`. Leia o `assessment.md` e o `apply.md`.

## 2. Antes

Dispare o evento `before_refactor_verify` seguindo `.specify/extensions/refactor/hooks.md`.

## 3. Verificação

1. **Build e testes** de cada repo tocado, com as ferramentas dele (regra III da constitution e regra 6 do `AGENTS.md`). Rode de verdade; não registre `ok` sem ter rodado.
2. **Caracterização intacta:** com o hash do `apply.md`, rode na raiz do workspace:

   ```bash
   bash .specify/extensions/ws/scripts/bash/ws-refactor-confere.sh <hash>
   ```

   Se falhar, o resultado é `falhou`: mostre os arquivos. Nunca ajuste o teste para passar.
3. **Exceção aprovada:** faça, ou peça ao usuário para fazer, a verificação que substitui o teste, e registre o resultado.

## 4. Relatório

Grave `refactors/<slug>/verify.md` com `**Resultado:** ok` ou `**Resultado:** falhou`, o motivo e a saída resumida de cada build, teste e conferência.

## 5. M1 (só com `ok`)

- Preencha a seção "Para retomar" do `assessment.md`, trocando o texto do modelo:
  - **interno:** a data do M1 e "nada a retomar";
  - **desacoplamento:** a data do M1; a chave e como virá-la em cada modo (paralelo, sombra, troca direta e de volta para "antigo"); os critérios do M3 com as consultas prontas; o que o `/speckit-refactor-contrair` vai remover (arquivos, a chave e o caminho antigo); a data de convivência.
- **Desacoplamento:** registre o marco na raiz do workspace:

  ```bash
  bash tools/ws/ws refactor marco <slug> M1 --desacoplamento <nome> --consumidor <repo sem repos/> --objeto <objeto> --convivencia <AAAA-MM-DD>
  ```

  Numa nova rodada, a linha já existe em `M3-falhou`, e só o `<slug> M1` basta. Se o `ws` recusar, mostre a mensagem e pare.

## 6. Depois

Dispare o evento `after_refactor_verify` seguindo `.specify/extensions/refactor/hooks.md`. O `/speckit-ws-refactor-enviar` lê o resultado do `verify.md`.
```

- [ ] **Step 8: `speckit.refactor.validar.md`**

```markdown
---
description: "Confere a evidência da convivência em produção contra os critérios da fatia; marca M3 ou M3-falhou"
---

# Fatia de desacoplamento: validação (M3)

**Idioma:** responda ao usuário sempre em português do Brasil, inclusive em erros e perguntas. Não proponha mudanças no harness (`tools/`, `.specify/`, `.claude/`, `AGENTS.md`) como próximo passo: descreva o problema e sugira registrá-lo para o time do harness.

## Entrada

```text
$ARGUMENTS
```

O slug da fatia e a evidência que o usuário colou: consultas e resultados, logs, prints, contagens de divergência.

## 1. Qual fatia

- O slug vem da entrada. Sem ele, rode `tools/ws/ws refactor pendentes` e pergunte qual fatia.
- Rode `tools/ws/ws refactor estado <slug>`. Se não for `M1`, mostre o marco e **pare**: só uma fatia em M1 pode ser validada.
- Leia `refactors/<slug>/assessment.md`, inclusive a seção "Para retomar".

## 2. Antes

Dispare o evento `before_refactor_validar` seguindo `.specify/extensions/refactor/hooks.md`. O `/speckit-ws-refactor-start` cria a branch `refactor/<slug>-contrair` (ou `-contrair-<k>`, se uma validação anterior falhou). Se ele devolver `ERROR`, pare.

## 3. Conferência

- Pergunte o modo e o período da convivência em produção, se a entrada não disser.
- Para cada critério do M3 no `assessment.md`, confira a evidência colada. Se faltar evidência de um critério, mostre a consulta de "Para retomar" e peça o resultado.
- **Banco (opcional):** só `SELECT`, só com um acesso que o usuário já tenha, mostrando a consulta e esperando a confirmação. Valores sensíveis não vão para o relatório.
- Um critério sem evidência não passa.

## 4. Relatório e marco

- Grave `refactors/<slug>/validacao.md` com o modo, o período, cada critério com a evidência e `ok` ou `falhou`, as divergências achadas e `**Resultado:** validado` ou `**Resultado:** falhou`.
- Registre o marco:

  ```bash
  bash tools/ws/ws refactor marco <slug> M3          # validado
  bash tools/ws/ws refactor marco <slug> M3-falhou   # falhou
  ```

- **Falhou:** diga ao usuário para voltar a chave para "antigo" em produção. A correção é uma nova rodada: `/speckit-refactor-assess <slug>` depois que o registro desta validação estiver no `main`.

## 5. Depois

Dispare o evento `after_refactor_validar` seguindo `.specify/extensions/refactor/hooks.md`.
```

- [ ] **Step 9: `speckit.refactor.contrair.md`**

```markdown
---
description: "Remove o caminho acoplado e a chave do consumidor depois do M3; marca o M4"
---

# Fatia de desacoplamento: contração (M4)

**Idioma:** responda ao usuário sempre em português do Brasil, inclusive em erros e perguntas. Não proponha mudanças no harness (`tools/`, `.specify/`, `.claude/`, `AGENTS.md`) como próximo passo: descreva o problema e sugira registrá-lo para o time do harness.

## Entrada

```text
$ARGUMENTS
```

## 1. Qual fatia

- Sem slug na entrada nem na conversa, use o da branch atual quando ela for `refactor/<slug>-contrair` ou `refactor/<slug>-contrair-<k>`. Diga que o slug veio da branch.
- Confirme com `git branch --show-current` que você está numa dessas branches, criada pelo `/speckit-refactor-validar`. Se não estiver, pare: a contração roda na branch da validação.
- Leia o `assessment.md`, o `apply.md` e o `validacao.md`.

## 2. Antes

Dispare o evento `before_refactor_contrair` seguindo `.specify/extensions/refactor/hooks.md`.

## 3. Portões (nunca contorne)

1. **M3 registrado:** rode `tools/ws/ws refactor estado <slug>`. Se não for `M3`, **pare** e diga: "a contração exige o M3 registrado; rode `/speckit-refactor-validar <slug>`".
2. **O consumidor não acessa o objeto por outro caminho:**
   - consulte a página do objeto no índice de impacto do Atlas (`docs/atlas/impacto/`) e veja os acessos do repo consumidor;
   - procure o nome do objeto no código do consumidor (`repos/<consumidor>/`, por exemplo com `grep -rn "<nome do objeto>"`);
   - todo acesso achado precisa estar no caminho antigo que esta fatia remove (listado em "Para retomar"). Se houver acesso fora dele, **pare** e liste cada um com arquivo e linha: ele precisa de uma fatia própria antes da contração.

## 4. Contração

- No consumidor, remova o caminho acoplado e a chave, deixando só o caminho novo. Siga as instruções do repo (regra 1 do `AGENTS.md`).
- **Não** mexa no objeto do banco (regra II) nem no provedor.
- Os testes de caracterização que exercitavam o caminho antigo continuam, agora contra o caminho novo. Se um teste dependia da chave em "antigo", ajuste-o para o caminho novo e registre o porquê no relatório.
- Build e testes do consumidor, de verdade.

## 5. Relatório e marco

- Grave `refactors/<slug>/contracao.md` com os portões (a evidência de cada um), o que foi removido, o build e os testes, e `**Resultado:** ok` ou `**Resultado:** falhou`.
- Com `ok`, registre o marco:

  ```bash
  bash tools/ws/ws refactor marco <slug> M4
  ```

  Se o `ws` recusar, mostre a mensagem e pare.

## 6. Depois

Dispare o evento `after_refactor_contrair` seguindo `.specify/extensions/refactor/hooks.md`. O `/speckit-ws-refactor-enviar` lê o resultado do `contracao.md`.
```

- [ ] **Step 10: Comandos da `ws`**

`tools/speckit/ws/commands/speckit.ws.refactor-start.md`:

```markdown
---
description: "Cria a branch do refactor com ws start e atualiza o Atlas"
---

# Branch do refactor no workspace

**Idioma:** responda ao usuário sempre em português do Brasil, inclusive em erros e perguntas. Não proponha mudanças no harness (`tools/`, `.specify/`, `.claude/`, `AGENTS.md`) como próximo passo: descreva o problema e sugira registrá-lo para o time do harness.

## User Input

```text
$ARGUMENTS
```

Este comando roda pelos hooks `before_refactor_assess` e `before_refactor_validar`. O slug é o que o comando de refactor desta sessão definiu; se a entrada acima trouxer um slug, use o da entrada.

1. **Modo:**
   - chamado pelo `/speckit-refactor-validar`: `--contrair`;
   - chamado pelo `/speckit-refactor-assess` numa nova rodada (fatia em `M3-falhou`): `--rodada`;
   - nos outros casos: sem modo.
2. Rode, na raiz do workspace:

   ```bash
   bash .specify/extensions/ws/scripts/bash/ws-refactor-start.sh "<slug>" [--rodada|--contrair]
   ```

3. Leia a única linha JSON da saída:
   - **`ERROR` preenchido:** mostre o erro e **pare**. O comando de refactor também para. Se o erro for de slug inválido, proponha um slug corrigido na convenção e pergunte se pode usá-lo.
   - **`EXISTING` = `true`:** você já está na branch; siga sem atualizar o Atlas.
   - **`EXISTING` = `false`:** a branch foi criada agora.
   - **`AVISOS` preenchido:** mostre os avisos, sem parar. Eles trazem o link do PR da `ws/sync`, o aviso de `main` local à frente do origin e as fatias que aguardam validação.
4. **Atlas (só com `EXISTING` = `false`):** com a skill `atlas-consultar`, ache até 5 repos que o relato envolve. Siga a skill `atlas-atualizar` com `--gatilho start --repos <repos separados por vírgula>`. Um problema no Atlas não para o refactor: mostre o aviso e siga.
5. Informe `BRANCH_NAME` e `REFACTOR_DIRECTORY` e devolva o controle ao comando de refactor.
```

`tools/speckit/ws/commands/speckit.ws.refactor-registro.md`:

```markdown
---
description: "Registra no workspace um diagnóstico que não é refactor ou uma validação que falhou"
---

# Registro do refactor sem mudança de código

**Idioma:** responda ao usuário sempre em português do Brasil, inclusive em erros e perguntas. Não proponha mudanças no harness (`tools/`, `.specify/`, `.claude/`, `AGENTS.md`) como próximo passo: descreva o problema e sugira registrá-lo para o time do harness.

## User Input

```text
$ARGUMENTS
```

Este comando roda pelos hooks `after_refactor_assess` e `after_refactor_validar`. O slug é o do comando de refactor desta sessão.

1. **Depois do `/speckit-refactor-assess`:** leia o veredito do `refactors/<slug>/assessment.md`.
   - **`refactor`:** diga "Próximo passo: leia o `assessment.md`, ajuste o que precisar e rode `/speckit-refactor-apply`." e **pare**.
   - **`reclassificar`:** proponha a mensagem `docs(<slug>): diagnóstico, não é refactor` e siga para o passo 3.
2. **Depois do `/speckit-refactor-validar`:** leia o resultado do `refactors/<slug>/validacao.md`.
   - **`validado`:** diga "Validado. Próximo passo, nesta mesma branch: `/speckit-refactor-contrair`." e **pare**.
   - **`falhou`:** proponha a mensagem `docs(<slug>): validação sem sucesso` e siga para o passo 3.
3. Rode `git status --short` e mostre os arquivos. Explique que o commit fica na branch atual e que só a branch do workspace vai para o origin (se o workspace tiver origin); nenhum repo recebe nada. Peça confirmação.
4. Com a confirmação, rode na raiz do workspace:

   ```bash
   bash .specify/extensions/ws/scripts/bash/ws-refactor-registro.sh "<mensagem>"
   ```

   Mostre a saída. Se falhar, mostre a mensagem e pare. Não tente contornar com `git push` ou `git add` à mão.
5. Se der certo:
   - com a branch enviada ao origin, lembre de abrir o PR do workspace para o `main`;
   - com `sem origin`, explique que o commit ficou só nesta máquina;
   - depois de uma validação que falhou, lembre que a chave volta para "antigo" e que a nova rodada (`/speckit-refactor-assess <slug>`) começa depois do merge desse PR.
```

`tools/speckit/ws/commands/speckit.ws.refactor-enviar.md`:

```markdown
---
description: "Fim do refactor (M1) ou da contração (M4): atualiza o Atlas dos repos tocados e oferece o commit e o envio aos repos"
---

# Fim do refactor: Atlas e envio

**Idioma:** responda ao usuário sempre em português do Brasil, inclusive em erros e perguntas. Não proponha mudanças no harness (`tools/`, `.specify/`, `.claude/`, `AGENTS.md`) como próximo passo: descreva o problema e sugira registrá-lo para o time do harness.

## User Input

```text
$ARGUMENTS
```

Este comando roda pelos hooks `after_refactor_verify` e `after_refactor_contrair`. O slug é o do comando de refactor desta sessão.

1. **Resultado:** leia o `refactors/<slug>/verify.md` (depois do `verify`) ou o `refactors/<slug>/contracao.md` (depois do `contrair`).
   - **`falhou`:** diga que o envio fica para depois, mostre o motivo e recomende corrigir e rodar o comando de novo. **Pare.**
   - **`ok`:** siga.
2. **Atlas:** siga a skill `atlas-atualizar` com `--gatilho converge`. Ela mapeia de novo todos os repos que a branch tocou, contando o que ainda não foi commitado, sem o adiamento de mudança interna, e faz um commit só com `docs/atlas/`.
3. **Envio:** rode `git status --short` e mostre a lista. Proponha a mensagem:
   - depois do `verify`: `refactor(<slug>): <título do assessment.md>`;
   - depois do `contrair`: `refactor(<slug>): contração <título do assessment.md>`.

   Explique que o commit fica na branch atual e que o push cria a mesma branch em cada repo alterado. Peça confirmação.
4. Com a confirmação, rode na raiz do workspace:

   ```bash
   bash .specify/extensions/ws/scripts/bash/ws-commit-push.sh "<mensagem>"
   ```

   Mostre a saída. Se falhar, mostre a mensagem do `ws` e pare. Não tente contornar a guarda nem rodar `git push` ou `git subtree` à mão.
5. Se der certo:
   - liste os PRs a abrir no Azure DevOps, um por repo enviado, citando `refactors/<slug>/`;
   - lembre que o PR do workspace (com `refactors/` e o Atlas) vem depois que todos os PRs dos repos forem mergeados;
   - **desacoplamento, depois do `verify`:** o deploy pode ir mesmo no congelamento, porque a chave fica em "antigo". A convivência começa na data registrada, e o `ws start` avisa quando ela vencer;
   - **depois do `contrair`:** a fatia fica em `M4` no documento do desacoplamento.
```

- [ ] **Step 11: Hooks e versão na `extension.yml` da `ws`**

Em `tools/speckit/ws/extension.yml`:
- `version: "1.3.0"` → `version: "1.4.0"`;
- `description` → `"Branch da feature, do bug e do refactor com ws start, Atlas e envio aos repos com ws push (specs SP2, SP3, SP5 e SP6)"`;
- em `provides.commands`, depois de `speckit.ws.bug-enviar`:

```yaml
    - name: speckit.ws.refactor-start
      file: commands/speckit.ws.refactor-start.md
      description: "Cria a branch do refactor com ws start"
    - name: speckit.ws.refactor-registro
      file: commands/speckit.ws.refactor-registro.md
      description: "Registra no workspace um diagnóstico que não é refactor ou uma validação que falhou"
    - name: speckit.ws.refactor-enviar
      file: commands/speckit.ws.refactor-enviar.md
      description: "Fim do refactor ou da contração: Atlas dos repos tocados e oferta de commit e envio"
```

- no fim de `hooks:`:

```yaml
  before_refactor_assess:
    command: speckit.ws.refactor-start
    optional: false
    description: "Branch refactor/<slug> com ws start e Atlas atualizado"
  after_refactor_assess:
    command: speckit.ws.refactor-registro
    optional: false
    description: "Registra o diagnóstico que não é refactor, ou lembra o próximo passo"
  after_refactor_verify:
    command: speckit.ws.refactor-enviar
    optional: false
    description: "Atlas dos repos tocados pelo refactor e oferta de commit e envio aos repos"
  before_refactor_validar:
    command: speckit.ws.refactor-start
    optional: false
    description: "Branch refactor/<slug>-contrair com ws start"
  after_refactor_validar:
    command: speckit.ws.refactor-registro
    optional: false
    description: "Registra a validação que falhou, ou lembra a contração"
  after_refactor_contrair:
    command: speckit.ws.refactor-enviar
    optional: false
    description: "Atlas dos repos tocados pela contração e oferta de commit e envio aos repos"
```

- [ ] **Step 12: Instalação no `ws speckit`**

Em `tools/ws/lib/speckit.sh`, cabeçalho linha 2: `# a extensão agent-context, a extensão bug, o workflow bugfix, a extensão refactor e os presets multirepo e bugs (specs SP2, 6.3, SP5, 4, e SP6, 5).`

Antes do bloco do preset `multirepo` (`if [ -d .specify/presets/multirepo ]`):

```bash
  # Extensão refactor, nossa (spec SP6, 5.2): os comandos disparam before_/after_refactor_*, que a ws usa.
  if [ -d .specify/extensions/refactor ]; then
    "${spec[@]}" extension remove refactor --force >/dev/null || die "não consegui remover a extensão refactor"
  fi
  "${spec[@]}" extension add --dev "$WS_SPECKIT_SRC/refactor" >/dev/null || die "não consegui instalar a extensão refactor"
```

e a mensagem final:

```bash
  log "Spec Kit $ver instalado com as extensões ws, agent-context, bug e refactor, o workflow bugfix e os presets multirepo e bugs"
```

- [ ] **Step 13: Rodar os testes offline**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_refactor.sh`
Expected: todos `ok`.

- [ ] **Step 14: Reinstalar, suíte completa e commit**

```bash
git add tools/speckit/refactor tools/speckit/ws tools/ws/lib/speckit.sh tools/ws/tests
git commit -m "harness: extensão refactor e comandos de refactor da ws (fontes)"
bash tools/ws/ws speckit
git add -A && git commit -qm "harness: reinstala o Spec Kit com a extensão refactor"
bash tools/ws/tests/run.sh
WS_TEST_REDE=1 bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_install.sh
```

Expected: as duas suítes com `0 falha(s)`. Se o `extension add --dev` recusar o `hooks.md` ou a pasta `templates/` (arquivo fora de `provides`), pare e volte ao usuário com a mensagem.

---

### Task 7: Regras e documentação

**Files:**
- Modify: `.specify/memory/constitution.md`
- Modify: `AGENTS.md`
- Modify: `README.md`, `docs/harness/1-comecar.md`, `docs/harness/2-quando-da-errado.md`, `docs/harness/3-alem-do-basico.md`, `docs/harness/4-manter.md`
- Create: `docs/harness/historico/2026-10-16-sp6-refactor-design.md`, `docs/harness/historico/2026-10-16-sp6-refactor.md` (cópias da spec e deste plano)
- Modify: `docs/harness/historico/LEIA-ME.md`
- Modify: `tools/ws/tests/test_harness.sh`

**Interfaces:**
- Consumes: os nomes das skills, dos comandos `ws` e das mensagens de erro das Tasks 4 a 6. Na camada 2, as mensagens (**Sintoma**) são conferidas pelo `docs_referencias.py` contra a fonte.

- [ ] **Step 1: Escrever os testes**

Em `tools/ws/tests/test_harness.sh`, em `test_regras_de_bug_no_agents_e_na_constitution`, troque `grep -qF 'Versão 1.2.0'` por `grep -qF 'Versão 1.3.0'` e a mensagem por `"constitution não está na 1.3.0"`. Acrescente:

```bash
test_regras_de_refactor_no_agents_e_na_constitution() {
  local a="$WS_RAIZ/AGENTS.md" c="$WS_RAIZ/.specify/memory/constitution.md"
  grep -qF '## Refactor com o Spec Kit' "$a" || fail "AGENTS.md sem a seção de refactor"
  grep -qF '**refactor ou desacoplamento:**' "$a" || fail "AGENTS.md sem o refactor na regra 5"
  grep -qF 'refactor/<slug>' "$a" || fail "AGENTS.md sem a branch refactor/<slug>"
  grep -qF '`refactors/` **não é harness**' "$a" || fail "AGENTS.md não diz que refactors/ não é harness"
  grep -qF 'O importante é que o WMS não dependa do banco Reserva para funcionar.' "$c" || fail "constitution sem a regra II do desacoplamento"
  grep -qF '### VII. Refactor não muda comportamento' "$c" || fail "constitution sem a regra VII"
  grep -qF 'Refatoração é escopo só quando é a própria demanda' "$c" || fail "constitution sem a regra VI revista"
  grep -qF 'Uma feature, um bug ou um refactor só termina' "$c" || fail "constitution sem a regra III revista"
}

test_doc_cobre_a_vertente_de_refactor() {
  local d="$WS_RAIZ/docs/harness"
  grep -qF 'fazer um refactor ou uma fatia de desacoplamento' "$WS_RAIZ/README.md" || fail "README sem a linha de refactor no Quero…"
  grep -qF '## Um refactor, do relato ao PR' "$d/1-comecar.md" || fail "camada 1 sem o refactor"
  grep -qF '## Uma fatia de desacoplamento, do relato à contração' "$d/1-comecar.md" || fail "camada 1 sem a fatia"
  grep -qF '## Comandos de refactor e `refactor/`' "$d/2-quando-da-errado.md" || fail "camada 2 sem o grupo de refactor"
  grep -qF '## Testes de caracterização' "$d/3-alem-do-basico.md" || fail "camada 3 sem caracterização"
  grep -qF '## Convivência e a chave' "$d/3-alem-do-basico.md" || fail "camada 3 sem convivência"
  grep -qF '## O documento do desacoplamento' "$d/3-alem-do-basico.md" || fail "camada 3 sem o documento do desacoplamento"
  grep -qF 'tools/speckit/refactor/' "$d/4-manter.md" || fail "camada 4 sem a extensão refactor"
  grep -qF 'tools/ws/lib/refactor.sh' "$d/4-manter.md" || fail "camada 4 sem o ws refactor"
}
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `bash tools/ws/tests/run.sh tools/ws/tests/test_harness.sh`
Expected: FALHA nos três testes (`constitution não está na 1.3.0`, `AGENTS.md sem a seção de refactor`, `README sem a linha de refactor`).

- [ ] **Step 3: Constitution 1.3.0**

Em `.specify/memory/constitution.md`:

- **II**, acrescente ao fim do parágrafo:

```markdown
 Num refactor, a lista vai no `assessment.md`. Num desacoplamento, o contrato novo (endpoint ou evento) segue esta regra. A tabela, view, proc ou outro mecanismo do banco de dados de onde o consumidor sai não muda enquanto outro sistema ainda a acessar: a fatia muda só o caminho daquele consumidor, e o dado gravado pelo caminho novo tem de ser igual ao do antigo. O importante é que o WMS não dependa do banco Reserva para funcionar. Essa dependência será migrada para serviços de integração.
```

- **III**, segunda frase: `Uma feature só termina quando todos os repos afetados passam.` → `Uma feature, um bug ou um refactor só termina quando todos os repos afetados passam.`
- **VI**: `A menor mudança que atende a spec, sem refatoração fora do escopo.` → `A menor mudança que atende a spec, sem refatoração fora do escopo. Refatoração é escopo só quando é a própria demanda, pelos comandos de refactor.`
- Depois da VI, acrescente:

```markdown
### VII. Refactor não muda comportamento
- O comportamento observável não muda. A prova são testes de caracterização que passam antes e depois sem alteração, ou uma exceção aprovada pelo humano, com a verificação que a substitui.
- Num desacoplamento, o caminho acoplado só é removido depois de a convivência em produção ser validada e registrada.
- Num refactor, obrigações de repo de corrigir dívidas ao tocar o código (como as Dívidas de Conformidade do AWX) não se aplicam; o `assessment.md` as lista como fora do escopo.
```

- **Governança**, última linha: `- Versão 1.3.0, ratificada em 2026-09-29 e emendada em 2026-10-07 (constitution dos repos), em 2026-10-11 (regra II para bugs) e em 2026-10-16 (refactor).`

- [ ] **Step 4: `AGENTS.md`**

Regra 5, depois da linha de **bug ou incidente**:

```markdown
   - **refactor ou desacoplamento:** os comandos de refactor do Spec Kit (seção "Refactor com o Spec Kit");
```

Seção nova, depois de "Bugs com o Spec Kit":

```markdown
## Refactor com o Spec Kit

- **Iniciar:** `/speckit-refactor-assess <relato>`, com o work item e o motivo. O slug é `<id do work item>-<descrição>` ou `rf-<AAAAMMDD>-<descrição>`. O hook `before_refactor_assess` roda o `/speckit-ws-refactor-start`, que cria a branch `refactor/<slug>` com `ws start`. Nunca crie essa branch à mão.
- **Tipos:** interno (um repo, sem contrato novo nem mudado) e desacoplamento (um consumidor deixa de acessar um objeto do banco `Reserva` e passa por um contrato novo num provedor). Mover código entre repos e migrar para o AWX ficam fora destes comandos.
- **Diagnóstico:** só leitura, com o Atlas pela skill `atlas-consultar`. Se o comportamento observável ou um contrato existente mudar, não é refactor: recomende reclassificar.
- **Caracterização:** obrigatória. Os testes fixam o comportamento atual e entram num commit `test(<slug>): caracterização` antes do refactor; o refactor nunca os altera. Quando o trecho não é testável, a exceção fica no `assessment.md` e o usuário aprova antes do `apply`.
- **Desacoplamento:** antes do `assess`, leia `refactors/desacoplamentos/<nome>.md`, mostre as fatias pendentes no mesmo objeto ou consumidor (`tools/ws/ws refactor pendentes`) e siga o padrão do caminho novo registrado nele. Nunca mude o objeto do banco de onde o consumidor sai (regra II da constitution).
- **Seguir:** o usuário lê o `assessment.md` antes do `/speckit-refactor-apply`; depois vem o `/speckit-refactor-verify`, que marca o M1 e oferece o envio.
- **Marcos e portões:** a fatia de desacoplamento segue com `/speckit-refactor-validar` (M3) e `/speckit-refactor-contrair` (M4). O marco só muda por `tools/ws/ws refactor marco`; nunca edite a coluna Marco à mão nem contorne um portão.
- **Banco (opcional):** como nos bugs, só `SELECT` e só com um acesso que o usuário já tenha.
- **Onde ficam:** os relatórios em `refactors/<slug>/` e os documentos dos desacoplamentos em `refactors/desacoplamentos/`, só no workspace. `refactors/` **não é harness**: crie e altere durante o trabalho.
- **PRs:** um por repo enviado, abertos e mergeados à mão. Depois vem o PR do workspace.
```

- [ ] **Step 5: `README.md` e camada 1**

`README.md`, depois da linha `Um bug ou um incidente segue ...`:

```markdown
Um refactor, ou uma fatia de desacoplamento do banco do LINX, segue os comandos de refactor, com os relatórios em `refactors/<slug>/`.
```

Na tabela "Quero…", depois da linha de bug:

```markdown
| fazer um refactor ou uma fatia de desacoplamento | [1. Começar](docs/harness/1-comecar.md#um-refactor-do-relato-ao-pr) |
```

`docs/harness/1-comecar.md`, depois da seção "Um bug, do relato ao PR" (antes de "Já conhece o Spec Kit?"):

```markdown
## Um refactor, do relato ao PR

Para mudar a estrutura do código sem mudar o que ele faz. Mover código entre repos e migrar para o AWX ainda não entram aqui.

1. `/speckit-refactor-assess <relato>`: o work item, o motivo e o que mudar. O agente cria a branch `refactor/<slug>` e grava o diagnóstico em `refactors/<slug>/assessment.md`, com o que não pode mudar e o plano dos testes de caracterização. Ele não muda código.
2. **Leia o `assessment.md`.** Se o agente propôs uma exceção aos testes de caracterização, só aprove se concordar com o motivo e com a verificação que a substitui.
3. `/speckit-refactor-apply`: primeiro os testes que fixam o comportamento atual, num commit próprio; depois o refactor.
4. `/speckit-refactor-verify`: build, testes e a conferência de que os testes de caracterização não mudaram. No fim, o agente atualiza o Atlas e pergunta se você quer fazer o commit e enviar.
5. Abra um PR por repo e, com **todos** mergeados, o PR do workspace.

## Uma fatia de desacoplamento, do relato à contração

Para tirar o acesso direto de um sistema a um objeto do banco `Reserva` (tabela, view, proc) e passar por um serviço de integração. As fatias de um desacoplamento ficam em `refactors/desacoplamentos/<nome>.md`.

1. Os passos 1 a 5 do refactor. O diagnóstico traz também o consumidor, o provedor, o contrato novo, a chave que escolhe entre o caminho antigo e o novo, o modo de convivência, os critérios de validação e a data em que a convivência pode começar. O código vai para produção com a chave em "antigo": nada muda, e o deploy pode ir mesmo no congelamento.
2. **Na data:** o time vira a chave em produção. O `ws start` avisa quando há fatia esperando.
3. `/speckit-refactor-validar <slug> <evidência>`: cole o resultado das consultas e os logs. O agente confere contra os critérios. Se não passar, a chave volta para "antigo" e a fatia ganha uma nova rodada.
4. `/speckit-refactor-contrair`: só roda com a validação registrada e com o Atlas mostrando que o sistema não acessa o objeto por outro caminho. Remove o caminho antigo e a chave.
5. PRs como no passo 5 do refactor. Para ver o que está pendente: `tools/ws/ws refactor pendentes`.
```

- [ ] **Step 6: Camada 2**

Em `docs/harness/2-quando-da-errado.md`, antes de `## PRs e merge`:

````markdown
## Comandos de refactor e `refactor/`

### O slug do refactor é recusado

**Sintoma:**
```
slug inválido: <slug>. Use <id do work item>-<descrição> ou rf-<AAAAMMDD>-<descrição>, em minúsculas e com hífens
```
**Causa:** o nome saiu fora da convenção, em geral com maiúscula ou acento vindos do título do work item.

**O que fazer:** aceite o slug corrigido que o agente propõe, ou diga qual usar.

### O refactor já está registrado

**Sintoma:**
```
o refactor <slug> já está registrado no <main> (<pasta>/). Para uma nova rodada de uma fatia que falhou na validação, rode /speckit-refactor-assess citando o slug; para validar uma fatia em M1, rode /speckit-refactor-validar <slug>
```
**Causa:** já existe `refactors/<slug>/` no `main`.

**O que fazer:** veja o marco com `tools/ws/ws refactor estado <slug>` e siga a mensagem. Se for um refactor novo do mesmo work item, use outra descrição no slug.

### A branch `refactor/<slug>` já existe

**Sintoma:**
```
a branch <branch> já existe no origin: faça checkout dela (git switch <branch>) para continuar o refactor
```
ou
```
a branch <branch> já existe nesta máquina: faça checkout dela (git switch <branch>) para continuar o refactor
```
**Causa:** alguém, talvez você, já começou esse refactor.

**O que fazer:** rode `git switch <branch>` e continue: `/speckit-refactor-apply` se o `assessment.md` já existe, ou `/speckit-refactor-verify` se o `apply.md` já existe.

### A exceção de caracterização está pendente

**Sintoma:** o `/speckit-refactor-apply` mostra a exceção e pergunta se você aprova.

**Causa:** o diagnóstico concluiu que o trecho não é testável sem um refactor anterior e propôs uma verificação manual no lugar dos testes.

**O que fazer:** aprove se concordar com o motivo e se a verificação proposta for suficiente. Se não, responda que não e rode o `/speckit-refactor-assess` de novo pedindo outro plano.

### Os testes de caracterização mudaram

**Sintoma:**
```
ws: erro: testes de caracterização alterados depois do commit <hash>: <arquivos>. O refactor não pode mudar esses testes; desfaça a mudança neles ou registre uma nova exceção no assessment.md
```
**Causa:** o refactor alterou ou apagou um teste que fixava o comportamento atual. Isso esconde uma mudança de comportamento.

**O que fazer:** desfaça a mudança no teste (`git restore --source <hash> <arquivo>`), ajuste o código e rode `/speckit-refactor-verify` de novo.

### A contração foi recusada

**Sintoma:**
```
ws: erro: a fatia <slug> está em <marco>; a contração exige o M3 registrado (rode /speckit-refactor-validar)
```
ou o `/speckit-refactor-contrair` para listando acessos do sistema ao objeto fora do caminho que sai.

**Causa:** a validação ainda não foi registrada, ou o sistema acessa o mesmo objeto por outro caminho.

**O que fazer:** no primeiro caso, rode `/speckit-refactor-validar <slug>` com a evidência. No segundo, cada acesso listado precisa de uma fatia própria antes da contração.

### A validação falhou

**Sintoma:** o `/speckit-refactor-validar` registra `falhou` e marca a fatia em `M3-falhou`.

**Causa:** a evidência mostrou divergência entre o caminho antigo e o novo, ou faltou evidência de um critério.

**O que fazer:** volte a chave para "antigo" em produção, aceite o registro e, com o PR do workspace mergeado, rode `/speckit-refactor-assess <slug>`: ele abre uma nova rodada na branch `refactor/<slug>-r<k>`.

### O `ws start` avisa de fatias aguardando validação

**Sintoma:**
```
ws: aviso: <n> fatia(s) do desacoplamento <nome> aguardando validação desde <data> (ws refactor pendentes)
```
**Causa:** há fatias em M1 cuja data de convivência já passou.

**O que fazer:** rode `tools/ws/ws refactor pendentes` para ver quais. Para adiar a convivência, edite a coluna "Convivência a partir de" da fatia no documento do desacoplamento e faça um PR do workspace.

### Uma linha da tabela de fatias não foi lida

**Sintoma:**
```
ws: aviso: linha fora do formato em <arquivo>:<n>; confira as colunas da tabela de fatias (camada 2 da doc)
```
**Causa:** a linha foi editada à mão fora do formato: a Fatia sem o link `[<slug>](../<slug>/)`, um marco que não é `M1`, `M3`, `M3-falhou` ou `M4`, ou uma data fora de `AAAA-MM-DD`.

**O que fazer:** corrija a linha no formato das outras e faça um PR do workspace.

### O registro do refactor é recusado

**Sintoma:**
```
ws: erro: há mudanças fora de refactors/: <arquivos>. O registro só leva relatórios; se houve mudança de código, siga /speckit-refactor-apply e /speckit-refactor-verify
```
**Causa:** há arquivos alterados fora de `refactors/`, em geral em `repos/`.

**O que fazer:** se a mudança foi por engano, desfaça com `git restore <arquivo>` e registre de novo.
````

- [ ] **Step 7: Camada 3**

Em `docs/harness/3-alem-do-basico.md`, depois da seção "Bug que muda contrato" (antes de `<a id="pr-de-um-repo-abandonado"></a>`):

```markdown
<a id="testes-de-caracterizacao"></a>
## Testes de caracterização

**Quando usar:** em todo refactor. Eles provam que o comportamento não mudou.

**Passos:**
1. O teste chama o código como ele está e afirma o que ele devolve **hoje**, mesmo que pareça estranho: o objetivo é fixar, não corrigir.
2. Use o framework de testes que o repo já tem. Para código que depende de banco ou de serviço, use as abstrações que o repo já tem (interfaces, repositórios) com dublês.
3. O commit dos testes vem antes do refactor. O `/speckit-refactor-verify` confere que eles não mudaram.

**Cuidado:** a exceção é para trecho que não dá para testar sem um refactor anterior. Não é para pular a caracterização por falta de tempo.

<a id="convivencia-e-a-chave"></a>
## Convivência e a chave

**Quando usar:** numa fatia de desacoplamento, entre o M1 e a validação.

**Passos:**
1. A chave escolhe o caminho: "antigo", o modo de convivência ou "novo". Ela é configuração do repo (por exemplo, `appsettings` ou tabela de parâmetros), e a seção "Para retomar" do `assessment.md` diz como virá-la.
2. Os modos:
   - **paralelo:** os dois caminhos rodam, o antigo vale, e as divergências são registradas;
   - **sombra:** o novo calcula e compara sem gravar. Serve para escrita;
   - **troca direta:** a chave vai para "novo", e a volta é pela própria chave.
3. Rode as consultas dos critérios e cole o resultado no `/speckit-refactor-validar`.

**Cuidado:** a convivência só começa na data registrada. No congelamento de fim de ano, a chave fica em "antigo".

<a id="o-documento-do-desacoplamento"></a>
## O documento do desacoplamento

**Quando usar:** para ver o que falta desacoplar e em que marco está cada fatia.

**Passos:**
1. O documento fica em `refactors/desacoplamentos/<nome>.md`. Ele é criado pela primeira fatia, com o inventário tirado do Atlas.
2. A seção "Padrão do caminho novo" é preenchida pelo time, com o ADR. Sem ela, nenhuma fatia segue.
3. A tabela de fatias mostra o marco de cada uma. `tools/ws/ws refactor pendentes` lista o que falta e o próximo passo.

**Cuidado:** o marco só muda pelos comandos. A coluna "Convivência a partir de" pode ser editada à mão para adiar a convivência.
```

- [ ] **Step 8: Camada 4**

Em `docs/harness/4-manter.md`:

- no mermaid, depois da linha `M[...]`:

```
  P["/speckit-refactor-assess"] --> Q["hook before_refactor_assess<br/>speckit.ws.refactor-start"] --> C
  R["/speckit-refactor-verify<br/>/speckit-refactor-contrair"] --> S["hook after_refactor_*<br/>speckit.ws.refactor-enviar"] --> J
```

- em "**`tools/ws`.**", troque `(`add`, `start`, `push`, `maintain`, `speckit`, `atlas`)` por `(`add`, `start`, `push`, `maintain`, `speckit`, `atlas`, `refactor`)`;
- na lista do Spec Kit, depois do preset `bugs`:

```markdown
- a extensão `refactor` (`tools/speckit/refactor/`), nossa: os cinco comandos `speckit.refactor.*`, o `hooks.md` que eles seguem para disparar `before_`/`after_refactor_*`, e os modelos do `assessment.md` e do documento do desacoplamento. A extensão `ws` liga os eventos aos comandos `speckit.ws.refactor-start`, `speckit.ws.refactor-registro` e `speckit.ws.refactor-enviar`. O `ws refactor` (`tools/ws/lib/refactor.sh`) lê e grava a tabela de fatias.
```

- na tabela "Onde fica cada coisa", depois de `bugs/`:

```markdown
| `tools/speckit/refactor/` | Fonte da extensão `refactor`: comandos, `hooks.md` e modelos |
| `tools/ws/lib/refactor.sh` | `ws refactor pendentes`, `estado` e `marco`, e o aviso do `ws start` |
| `refactors/` | Relatórios de refactor (`refactors/<slug>/`) e documentos dos desacoplamentos (`refactors/desacoplamentos/`). Não é harness |
```

- em "Atualizar o Spec Kit", passo 4: `Valide um `/speckit-specify` e um `/speckit-bug-assess` de ponta a ponta.` → `Valide um `/speckit-specify`, um `/speckit-bug-assess` e um `/speckit-refactor-assess` de ponta a ponta.`

- [ ] **Step 9: Histórico**

```bash
cp /c/src/00-harness_big_brown_field/docs/superpowers/specs/2026-10-16-sp6-refactor-design.md docs/harness/historico/
cp /c/src/00-harness_big_brown_field/docs/superpowers/plans/2026-10-16-sp6-refactor.md docs/harness/historico/
```

Em `docs/harness/historico/LEIA-ME.md`: na primeira frase, `(SP1 a SP3, com os adendos, e SP5)` → `(SP1 a SP3, com os adendos, SP5 e SP6)`. Na tabela, depois da linha do plano do SP5:

```markdown
| `2026-10-16-sp6-refactor-design.md` | Spec do SP6: vertente de refactor e Spec Kit 1.2.0 |
| `2026-10-16-sp6-refactor.md` | Plano do SP6 |
```

- [ ] **Step 10: Rodar e ver passar**

```bash
bash tools/ws/tests/run.sh tools/ws/tests/test_harness.sh tools/ws/tests/test_docs_referencias.sh
bash tools/ws/tests/run.sh
```

Expected: `0 falha(s)`. Se o `test_docs_ref_workspace_real` acusar um sintoma da camada 2, compare a mensagem com a do script (Tasks 4 e 5) e corrija a **doc**.

- [ ] **Step 11: Commit**

```bash
git add -A
git commit -m "harness: constitution 1.3.0, AGENTS.md e doc da vertente de refactor"
```

---

### Task 8: PoC do item 4 e ponta a ponta (spec 10.1 e 10.3)

Roda LLM e mexe nos ambientes da Task 3. **Peça OK antes de cada passo marcado com (OK)**, mostrando o custo estimado. **Antes do Step 1, pergunte ao usuário o padrão do caminho novo do LINX** (ele disse que explicaria na hora certa). O documento do desacoplamento do ponta a ponta usa o padrão real; sem ele, use o padrão de teste do Step 2 e registre isso.

**Files:**
- Modify: `C:\src\00-harness_big_brown_field\docs\discovery\sp6-refactor-validacao.md`

- [ ] **Step 1 (OK): Atualizar o ambiente com a `harness/refactor`**

```bash
cd /c/src/wms-workspace-e2e6
git -C /c/src/wms-e2e6-origin.git fetch -q /c/src/wms-workspace harness/refactor:refs/heads/harness-refactor
git fetch -q origin && git switch -q main && git merge -q --no-edit origin/harness-refactor && git push -q origin main
for b in $(git branch --list 'hotfix/*' 'refactor/*' --format='%(refname:short)'); do git branch -q -D "$b"; done
git status --short | wc -l   # 0
```

Expected: `main` do e2e6 com os commits da `harness/refactor` e as linhas dos espelhos; árvore limpa.

- [ ] **Step 2: Documento do desacoplamento do ponta a ponta**

Crie `refactors/desacoplamentos/linx.md` a partir de `.specify/extensions/refactor/templates/desacoplamento-template.md`:
- "Padrão do caminho novo": o padrão real que o usuário explicou, ou, sem ele: `PADRÃO DE TESTE do ponta a ponta: o consumidor chama um endpoint HTTP novo no servicos-linx-wms (WebApi, rota /servico/...), que executa o objeto no Reserva. Sem ADR.`;
- inventário com uma linha: `Reserva.dbo.LX_MOVIMENTA_VENDAS_PA | wms.conector.backend | escrita (EXEC) | <página do índice>`.

```bash
git add refactors && git commit -qm "e2e: documento do desacoplamento linx" && git push -q origin main
```

- [ ] **Step 3 (OK): Tipo 1 com caracterização (work item 90201)**

```bash
cd /c/src/wms-workspace-e2e6
O="--permission-mode acceptEdits --allowedTools Bash,Read,Edit,Write,Grep,Glob,Skill --output-format json"
claude -p $O "/speckit-refactor-assess Work item 90201. Refactor interno no conector (industria-logistica.wms.conector.backend): o EmbalarPedidoECommerceCommandHandler faz tudo num método só. Extrair a montagem do FaturamentoCaixa e dos itens da reserva para métodos privados, sem mudar o comportamento." > /c/src/wms-e2e6-t1-assess.json
S=$(python -c "import json;print(json.load(open('C:/src/wms-e2e6-t1-assess.json'))['session_id'])")
claude -p --resume "$S" $O "Li o assessment.md e aprovo. /speckit-refactor-apply" > /c/src/wms-e2e6-t1-apply.json
claude -p --resume "$S" $O "/speckit-refactor-verify" > /c/src/wms-e2e6-t1-verify.json
claude -p --resume "$S" $O "Sim, pode fazer o commit e o envio." > /c/src/wms-e2e6-t1-envio.json
```

Critérios:
- branch `refactor/90201-<desc>` criada pelo hook;
- `refactors/90201-<desc>/{assessment,apply,verify}.md`;
- `git log --format=%s` com `test(90201-<desc>): caracterização` **antes** dos commits do refactor;
- `verify.md` com `ok` e a linha `caracterização intacta`;
- um commit do Atlas (`atlas: ...`) e o commit `refactor(90201-<desc>): …`;
- `git -C /c/src/wms-e2e6-conector.git branch --list 'refactor/*'` mostra a branch.

- [ ] **Step 4 (OK): Tipo 1 com teste de caracterização alterado**

Na branch do Step 3, antes de qualquer merge:

```bash
cd /c/src/wms-workspace-e2e6
f=$(git show --name-only --format= "$(git log --format=%H --grep '^test(90201' -1)" | head -1)
echo "// alterado à mão" >> "$f"
claude -p $O "/speckit-refactor-verify" > /c/src/wms-e2e6-t1b-verify.json
git checkout -- "$f" refactors/
```

Critérios: o `verify.md` registra `falhou`, com o arquivo; o `/speckit-ws-refactor-enviar` não oferece envio; a linha do `verify.md` volta a `ok` só se rodar o `verify` de novo (opcional).

- [ ] **Step 5 (OK): Tipo 1 com exceção (work item 90202)**

```bash
git switch -q main
claude -p $O "/speckit-refactor-assess Work item 90202. Refactor interno no conector: a consulta SQL do VendaRepository.ObterAsync está escrita inline; mover o texto para uma constante privada da classe, sem mudar o comportamento. Não há banco de teste no repo." > /c/src/wms-e2e6-t1c-assess.json
S=$(python -c "import json;print(json.load(open('C:/src/wms-e2e6-t1c-assess.json'))['session_id'])")
claude -p --resume "$S" $O "/speckit-refactor-apply" > /c/src/wms-e2e6-t1c-apply.json
```

Critérios: o `assessment.md` traz `**Exceção:**` com `Aprovada pelo usuário: pendente`; o `apply`, **antes de mudar código**, mostra a exceção e pergunta. Responda `claude -p --resume "$S" $O "Aprovo a exceção."` e confira que o `assessment.md` passa a `sim, <data>` e que não há commit `test(...)`.

Descarte o caso, que não vai ser enviado:

```bash
git reset -q --hard && git clean -fdq && git switch -q main
git branch -q -D "$(git branch --list 'refactor/90202-*' --format='%(refname:short)')"
```

- [ ] **Step 6 (OK): Não é refactor (work item 90203)**

```bash
claude -p $O "/speckit-refactor-assess Work item 90203. Refatorar o FaturamentoCaixa do conector para aceitar caixa com quantidade zero." > /c/src/wms-e2e6-t1d-assess.json
S=$(python -c "import json;print(json.load(open('C:/src/wms-e2e6-t1d-assess.json'))['session_id'])")
claude -p --resume "$S" $O "Sim, pode registrar." > /c/src/wms-e2e6-t1d-registro.json
```

Critérios: veredito `reclassificar` (muda comportamento); commit `docs(90203-<desc>): diagnóstico, não é refactor`; a branch foi para o origin do workspace e não para o espelho do conector.

- [ ] **Step 7 (OK): Tipo 3, M1 (work item 90301)**

```bash
git switch -q main
claude -p $O "/speckit-refactor-assess Work item 90301. Desacoplamento linx: o conector (industria-logistica.wms.conector.backend) deixa de executar a proc LX_MOVIMENTA_VENDAS_PA direto no Reserva (VendaRepository.MovimentarAsync) e passa pelo servicos-linx-wms. Convivência a partir de hoje." > /c/src/wms-e2e6-t3-assess.json
S=$(python -c "import json;print(json.load(open('C:/src/wms-e2e6-t3-assess.json'))['session_id'])")
claude -p --resume "$S" $O "Li e aprovo. /speckit-refactor-apply" > /c/src/wms-e2e6-t3-apply.json
claude -p --resume "$S" $O "/speckit-refactor-verify" > /c/src/wms-e2e6-t3-verify.json
claude -p --resume "$S" $O "Sim, pode fazer o commit e o envio." > /c/src/wms-e2e6-t3-envio.json
```

Critérios:
- o `assessment.md` traz consumidor, provedor, objeto, contrato novo, chave, modo, critérios do M3 e a data de hoje;
- o `apply` mexe primeiro no servicos-linx-wms e depois no conector;
- a chave começa em "antigo";
- `tools/ws/ws refactor estado 90301-<desc>` = `M1`;
- "Para retomar" preenchida;
- branches `refactor/90301-<desc>` nos dois espelhos.

Simule os PRs mergeados, primeiro nos espelhos e depois no workspace. A função `pr_mergeado` é usada de novo nos Steps 10 e 12; redefina-a se o shell for outro:

```bash
pr_mergeado() {  # branch -> merge nos dois espelhos (se ela estiver lá) e no main do workspace
  local br=$1 m tmp=/c/src/wms-e2e6-merge
  for m in /c/src/wms-e2e6-conector.git /c/src/wms-e2e6-linx.git; do
    git -C "$m" rev-parse -q --verify "refs/heads/$br" >/dev/null || continue
    rm -rf $tmp && git clone -q "$m" $tmp
    git -C $tmp merge -q --no-ff "origin/$br" -m "PR $br" && git -C $tmp push -q origin main
    rm -rf $tmp
  done
  git switch -q main && git merge -q --no-edit "$br" && git push -q origin main
}
SLUG=$(ls refactors | grep '^90301-')
pr_mergeado "refactor/$SLUG"
```

- [ ] **Step 8: Aviso e pendentes**

```bash
bash tools/ws/ws refactor pendentes
bash tools/ws/ws start e2e-aviso 2>&1 | grep "aguardando validação"; git switch -q main; git branch -q -D e2e-aviso
```

Expected: a fatia 90301 com "virar a chave e rodar /speckit-refactor-validar", e o aviso do `ws start`.

- [ ] **Step 9 (OK): Portão do `contrair` sem M3**

Crie à mão a branch da validação, sem validar, para o `contrair` chegar ao portão 1:

```bash
bash .specify/extensions/ws/scripts/bash/ws-refactor-start.sh "$SLUG" --contrair
claude -p $O "/speckit-refactor-contrair" > /c/src/wms-e2e6-t3-contrair-sem-m3.json
git status --short   # nada em repos/
git switch -q main && git branch -q -D "refactor/$SLUG-contrair"
```

Critérios: o comando para no portão 1 (`M1`, "a contração exige o M3 registrado"), sem mudar nada em `repos/`.

- [ ] **Step 10 (OK): `validar` que falha, numa sessão nova, e a nova rodada**

```bash
git switch -q main
claude -p $O "/speckit-refactor-validar 90301 Convivência em modo paralelo de hoje até hoje. Divergência: a consulta do critério 1 mostrou 3 pedidos com movimentação só no caminho antigo (E1001, E1002, E1003)." > /c/src/wms-e2e6-t3-validar1.json
S=$(python -c "import json;print(json.load(open('C:/src/wms-e2e6-t3-validar1.json'))['session_id'])")
claude -p --resume "$S" $O "Sim, pode registrar." > /c/src/wms-e2e6-t3-validar1-registro.json
```

Critérios:
- a sessão é nova (sem `--resume` no primeiro comando) e retomou pela seção "Para retomar";
- branch `refactor/90301-<desc>-contrair`;
- `validacao.md` com `falhou`;
- `estado` = `M3-falhou`;
- commit `docs(90301-<desc>): validação sem sucesso` e push só do workspace.

Simule o merge com `pr_mergeado "refactor/$SLUG-contrair"` e rode a nova rodada:

```bash
claude -p $O "/speckit-refactor-assess 90301 nova rodada: os 3 pedidos divergentes não passaram pelo caminho novo." > /c/src/wms-e2e6-t3-r2-assess.json
S=$(python -c "import json;print(json.load(open('C:/src/wms-e2e6-t3-r2-assess.json'))['session_id'])")
claude -p --resume "$S" $O "Aprovo. /speckit-refactor-apply" > /c/src/wms-e2e6-t3-r2-apply.json
claude -p --resume "$S" $O "/speckit-refactor-verify" > /c/src/wms-e2e6-t3-r2-verify.json
claude -p --resume "$S" $O "Sim, pode fazer o commit e o envio." > /c/src/wms-e2e6-t3-r2-envio.json
```

Critérios: a branch `refactor/90301-<desc>-r2`; a seção `## Rodada 2` no `assessment.md`; `estado` = `M1`. Simule o merge: `pr_mergeado "refactor/$SLUG-r2"`.

- [ ] **Step 11 (OK): `validar` ok e portão do Atlas**

```bash
claude -p $O "/speckit-refactor-validar 90301 Convivência em modo paralelo por 7 dias; nenhuma divergência em 1.240 pedidos (consulta do critério 1 sem linhas)." > /c/src/wms-e2e6-t3-validar2.json
S=$(python -c "import json;print(json.load(open('C:/src/wms-e2e6-t3-validar2.json'))['session_id'])")
```

Critérios: a branch é `refactor/$SLUG-contrair-2`, porque a `-contrair` da validação que falhou está no origin; `estado` = `M3`; o `/speckit-ws-refactor-registro` manda rodar o `contrair` na mesma branch, sem commit.

Plante um segundo acesso no consumidor, na branch `-contrair`:

```bash
d=repos/industria-logistica.wms.conector.backend/src/ReservaNet.Linx.Infra.Repositories/Repositories/Reserva
printf '%s\n' 'namespace ReservaNet.Linx.Infra.Repositories.Repositories.Reserva' '{' '    internal static class RelatorioVendas' '    {' '        internal const string Proc = "LX_MOVIMENTA_VENDAS_PA";' '    }' '}' > "$d/RelatorioVendas.cs"
git add "$d/RelatorioVendas.cs" && git commit -qm "e2e: segundo acesso plantado"
claude -p --resume "$S" $O "/speckit-refactor-contrair" > /c/src/wms-e2e6-t3-contrair-plantado.json
```

Critério: o comando para no portão 2 listando `RelatorioVendas.cs`, sem remover nada.

- [ ] **Step 12 (OK): `contrair` ok**

```bash
git reset -q --hard HEAD~1
claude -p --resume "$S" $O "Removi o acesso plantado. /speckit-refactor-contrair" > /c/src/wms-e2e6-t3-contrair.json
claude -p --resume "$S" $O "Sim, pode fazer o commit e o envio." > /c/src/wms-e2e6-t3-contrair-envio.json
```

Critérios:
- `contracao.md` com os dois portões e `ok`;
- o caminho antigo e a chave sumiram do conector;
- o servicos-linx-wms não mudou nesta branch;
- `estado` = `M4`;
- commit `refactor(90301-<desc>): contração …`;
- branch `refactor/90301-<desc>-contrair-2` no espelho do conector.

- [ ] **Step 13: Registrar**

Acrescente ao `sp6-refactor-validacao.md`:

```markdown
## Ponta a ponta da vertente de refactor (spec 10.1, item 4, e 10.3)

Padrão do caminho novo usado: <real, como o usuário explicou | de teste>.

| Caso | Resultado | Evidência e custo |
|---|---|---|
| Tipo 1 com caracterização (90201) | | |
| Tipo 1 com teste de caracterização alterado | | |
| Tipo 1 com exceção (90202) | | |
| Não é refactor (90203) | | |
| Tipo 3, M1 (90301) | | |
| Aviso e pendentes | | |
| Portão 1 do `contrair` (sem M3) | | |
| Sessão nova no `validar` e validação que falha | | |
| Nova rodada `-r2` | | |
| Portão 2 do `contrair` (acesso plantado) | | |
| `contrair` ok e M4 | | |

Custo total com LLM: US$ <soma>.
```

Preencha com o resultado, a evidência (trecho do `result` ou do arquivo) e o custo de cada caso. **Se um caso falhar por comportamento do agente** (pulou hook, contornou portão, mexeu em teste de caracterização), pare e volte ao usuário com a evidência antes de mudar os comandos. Commit no repo de discovery: `git commit -am "SP6: ponta a ponta da vertente de refactor"`.

---

### Task 9: Revisão final e entrega do PR 2

- [ ] **Step 1: Revisão da branch**

Peça a revisão da `harness/refactor` inteira (skill `superpowers:requesting-code-review`, revisor no modelo mais capaz) contra a spec e este plano. Corrija os achados importantes com teste. Registre os menores adiados no `sp6-refactor-validacao.md`.

- [ ] **Step 2: Suítes**

```bash
cd /c/src/wms-workspace
bash tools/ws/tests/run.sh
WS_TEST_REDE=1 bash tools/ws/tests/run.sh tools/ws/tests/test_speckit_install.sh
```

Expected: as duas com `0 falha(s)`.

- [ ] **Step 3: Entrega**

- Peça ao usuário o push: `git push -u origin harness/refactor`. Ele abre o PR para o `main`. O PR leva a constitution 1.3.0 e exige aprovação humana.
- Liste para o usuário os ambientes descartáveis a apagar:
  - `%TEMP%\sp6-poc`;
  - `C:\src\wms-workspace-e2e6`, `C:\src\wms-e2e6-origin.git`, `C:\src\wms-e2e6-conector.git` e `C:\src\wms-e2e6-linx.git`;
  - os `C:\src\wms-e2e6-*.json`.

- [ ] **Step 4: Estado da sessão**

Em `C:\src\00-harness_big_brown_field\docs\discovery\estado-da-sessao.md`, no item 8 (SP6), troque a última linha por o resumo da execução: as branches, os commits finais, as suítes, o resultado do PoC e do ponta a ponta (com o custo), os PRs e os ambientes descartáveis. Commit no repo de discovery: `git commit -am "SP6: execução concluída"`.
