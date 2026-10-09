# SP4: documentação em camadas do harness (plano de implementação)

> **Para agentes que executam:** SUB-SKILL OBRIGATÓRIA: use `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para implementar este plano task por task. Os passos usam a sintaxe de checkbox (`- [ ]`) para acompanhamento.

**Objetivo:** substituir o `docs/workspace.md` por uma documentação em 4 camadas (começar, quando dá errado, além do básico, manter), com um `README.md` de entrada, o histórico de decisões e um teste que impede a doc de citar o que não existe.

**Arquitetura:**
- **Markdown no workspace:** um arquivo por camada em `docs/harness/` e o histórico em `docs/harness/historico/`.
- **Teste de referências:** um verificador em Python (`tools/ws/tests/docs_referencias.py`) é chamado por um arquivo de teste bash no padrão da suíte (`test_docs_referencias.sh`). O verificador lê do próprio código o que existe (os subcomandos no uso do `ws`, as skills em `.claude/skills/`), em vez de manter listas fixas.

**Stack:** Markdown, bash (suíte `tools/ws/tests/run.sh`) e Python 3 (só biblioteca padrão).

**Spec:** `C:\src\00-harness_big_brown_field\docs\superpowers\specs\2026-10-08-sp4-documentacao-harness-design.md`. Leia a spec antes de cada task de documentação: ela traz o conteúdo esperado de cada camada (seção 4).

**Onde trabalhar:**
- Workspace `C:\src\wms-workspace`, a partir do `main` em `868b5f0a5` ou mais novo;
- branch `harness/docs-camadas`, criada com `git switch -c harness/docs-camadas origin/main` depois de um `git fetch origin`. Não use `ws start`: a mudança é só do harness;
- os comandos rodam no Git Bash, a partir da raiz do workspace.

## Restrições globais

- Português do Brasil em tudo: docs, mensagens do verificador, nomes de teste e commits.
- Commits no padrão do repo: `harness: <descrição>`, terminando com a linha `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- **Camada 1:** no máximo **80 linhas** (é a "tela e meia" da spec), contando o bloco `<details>`.
- **Suporte**, na camada 2: thread no espaço "Equipe WMS", `https://chat.google.com/room/AAAAKpyvLWs?cls=7`.
- **Clone:** `git clone -c core.longpaths=true -c core.autocrlf=false https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace`.
- **Versões das ferramentas do Atlas:** sempre as de `tools/atlas/VERSOES.md` (hoje `graphifyy[sql,mcp]==0.9.77` e `@ast-grep/cli@0.45.3`). Copie do arquivo; não escreva de memória.
- **Segredos:** nenhum valor de credencial, token ou URL com credencial embutida, nem nas camadas nem no `historico/`. Segredo se cita por nome e local.
- **Escopo do repo:** nada muda em `repos/`, então não há `ws push`. O PR do workspace é aberto pelo usuário.
- **Fontes, não memória:** cada afirmação sobre comportamento sai do código ou do `docs/workspace.md` atual. Mensagens de erro são copiadas literalmente do código.

## Foco de revisão

1. **Caminho com placeholder ou argumento** (`repos/<repo>/docs/adr/`, `tools/atlas/importa-mapeamento.sh --banco`, `` `docs/atlas/<repo>/project-readme.md` ``): o verificador ignora os placeholders e os argumentos e não acusa falso positivo. Coberto em `test_docs_ref_ignora_placeholders_e_argumentos` (Task 1).
2. **Comando nativo do Claude Code citado como skill** (`/mcp`): não é acusado como skill inexistente. Coberto em `test_docs_ref_comando_nativo_nao_e_skill` (Task 1).
3. **Mensagem de erro com parte variável** (`ws: erro: subtree add falhou em <prefixo>`): o verificador confere só os trechos fixos, sem o prefixo `ws: erro: `. Coberto em `test_docs_ref_sintoma_com_parte_variavel` (Task 1).
4. **Link com âncora** (`3-alem-do-basico.md#mudar-uma-feature-que-ja-existe`): o arquivo existe, então passa. A âncora não é conferida. Coberto em `test_docs_ref_link_com_ancora` (Task 1).
5. **Conteúdo do `docs/workspace.md` perdido na migração:** toda seção dele tem destino na tabela da Task 7, conferido item por item antes de remover o arquivo. Os testes do `test_harness.sh` que liam o `docs/workspace.md` passam a ler a camada nova.

---

## Estrutura de arquivos

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `tools/ws/tests/docs_referencias.py` | criar | Verificador: lê `README.md` e `docs/harness/*.md` de uma raiz e lista as violações das 5 regras |
| `tools/ws/tests/test_docs_referencias.sh` | criar | Testes do verificador com fixtures e o teste sobre o workspace real |
| `docs/harness/historico/` + `LEIA-ME.md` | criar | Specs, planos e validações do SP1 ao SP3 |
| `README.md` | criar | Porta de entrada e pré-requisitos |
| `docs/harness/1-comecar.md` | criar | Camada 1 |
| `docs/harness/2-quando-da-errado.md` | criar | Camada 2 |
| `docs/harness/3-alem-do-basico.md` | criar | Camada 3 |
| `docs/harness/4-manter.md` | criar | Camada 4 |
| `docs/workspace.md` | remover | Conteúdo redistribuído (Task 7) |
| `AGENTS.md`, `tools/atlas/relevancia.ini`, `tools/ws/tests/test_harness.sh` | modificar | Referências ao `docs/workspace.md` |

---

### Task 1: Verificador de referências da doc

**Arquivos:**
- Criar: `tools/ws/tests/docs_referencias.py`
- Criar: `tools/ws/tests/test_docs_referencias.sh`

**Interfaces:**
- Produz: `python tools/ws/tests/docs_referencias.py <raiz>`.
  - Sem violação: imprime `ok: N arquivo(s)` e sai com 0.
  - Com violação: imprime uma linha por violação, no formato `<arquivo relativo>:<linha>: <regra>: <trecho>`, e sai com 1.
  - As regras são `caminho`, `ws`, `skill`, `sintoma` e `link`.
  - Arquivos lidos: `<raiz>/README.md` e `<raiz>/docs/harness/*.md`, sem subpastas, então o `historico/` fica de fora. Arquivo ausente é ignorado.
- Usado por: Tasks 3 a 8, que rodam o teste sobre o workspace real.

- [ ] **Passo 1: escrever os testes, que devem falhar**

Crie `tools/ws/tests/test_docs_referencias.sh`:

```bash
# Testes do verificador de referências da doc do harness (spec SP4, seção 6).

VERIFICA="$WS_DIR/tests/docs_referencias.py"
WS_RAIZ="$(cd "$WS_DIR/../.." && pwd)"

# Raiz falsa em $T/d: ws com uso de add|start|atlas e de atlas plano|mapas, skill speckit-plan,
# tools/atlas/VERSOES.md, um die com parte variável e docs/harness/ vazio.
fx_docs() {
  local d="$T/d"
  mkdir -p "$d/tools/ws/lib" "$d/tools/atlas" "$d/.claude/skills/speckit-plan" "$d/docs/harness"
  printf '%s\n' '#!/usr/bin/env bash' '  *) die "uso: ws <add|start|atlas> [args]" ;;' > "$d/tools/ws/ws"
  printf '%s\n' '    *) die "uso: ws atlas <plano|mapas> [args]" ;;' \
    '  git subtree add "$p" || die "subtree add falhou em $prefix"' > "$d/tools/ws/lib/atlas.sh"
  echo '# skill' > "$d/.claude/skills/speckit-plan/SKILL.md"
  echo 'versões' > "$d/tools/atlas/VERSOES.md"
}

verifica() { python "$VERIFICA" "$T/d"; }
doc() { printf '%s\n' "$@" > "$T/d/docs/harness/$DOC"; }
DOC=1-comecar.md

test_docs_ref_tudo_certo_passa() {
  fx_docs
  doc '# Começar' 'Rode `tools/ws/ws start minha-branch` e `ws atlas mapas --todos`.' \
    'Depois `/speckit-plan`. Versões em `tools/atlas/VERSOES.md`. Veja [a camada 2](2-quando-da-errado.md).'
  echo '# 2' > "$T/d/docs/harness/2-quando-da-errado.md"
  assert_ok verifica
}

test_docs_ref_caminho_inexistente_falha() {
  fx_docs
  doc 'Veja `tools/atlas/NAOEXISTE.md`.'
  local out
  out=$(verifica 2>&1) && fail "devia falhar"
  assert_contains "$out" "docs/harness/1-comecar.md:1: caminho: tools/atlas/NAOEXISTE.md"
}

test_docs_ref_ignora_placeholders_e_argumentos() {
  fx_docs
  doc 'Em `repos/<repo>/docs/adr/`, `specs/ws-NNN-*` e `tools/atlas/VERSOES.md --algo`.' \
    '```bash' 'bash tools/atlas/VERSOES.md --banco' '```'
  assert_ok verifica
}

test_docs_ref_subcomando_inexistente_falha() {
  fx_docs
  doc 'Rode `tools/ws/ws sincroniza`.' 'E `ws atlas regenera`.'
  local out
  out=$(verifica 2>&1) && fail "devia falhar"
  assert_contains "$out" "1-comecar.md:1: ws: ws sincroniza"
  assert_contains "$out" "1-comecar.md:2: ws: ws atlas regenera"
}

test_docs_ref_skill_inexistente_falha() {
  fx_docs
  doc 'Rode `/speckit-voar`.'
  local out
  out=$(verifica 2>&1) && fail "devia falhar"
  assert_contains "$out" "1-comecar.md:1: skill: /speckit-voar"
}

test_docs_ref_comando_nativo_nao_e_skill() {
  fx_docs
  doc 'Confira em `/mcp`.'
  assert_ok verifica
}

test_docs_ref_sintoma_inexistente_falha() {
  DOC=2-quando-da-errado.md
  fx_docs
  doc '**Sintoma:**' '```' 'ws: erro: mensagem que ninguém escreveu' '```'
  local out
  out=$(verifica 2>&1) && fail "devia falhar"
  assert_contains "$out" "2-quando-da-errado.md:3: sintoma: mensagem que ninguém escreveu"
}

test_docs_ref_sintoma_com_parte_variavel() {
  DOC=2-quando-da-errado.md
  fx_docs
  doc '**Sintoma:**' '```' 'ws: erro: subtree add falhou em <prefixo>' '```'
  assert_ok verifica
}

test_docs_ref_link_quebrado_falha() {
  fx_docs
  doc 'Veja [a camada 9](9-nao-existe.md).'
  local out
  out=$(verifica 2>&1) && fail "devia falhar"
  assert_contains "$out" "1-comecar.md:1: link: 9-nao-existe.md"
}

test_docs_ref_link_com_ancora() {
  fx_docs
  echo '# 3' > "$T/d/docs/harness/3-alem-do-basico.md"
  doc 'Veja [mudar](3-alem-do-basico.md#mudar-uma-feature) e [site](https://exemplo.com/x.md).'
  assert_ok verifica
}

test_docs_ref_historico_fica_de_fora() {
  fx_docs
  mkdir -p "$T/d/docs/harness/historico"
  echo 'Veja `tools/nao/existe.sh`.' > "$T/d/docs/harness/historico/velho.md"
  doc '# ok'
  assert_ok verifica
}

test_docs_ref_readme_da_raiz_e_verificado() {
  fx_docs
  echo 'Veja `docs/harness/sumiu.md`.' > "$T/d/README.md"
  local out
  out=$(verifica 2>&1) && fail "devia falhar"
  assert_contains "$out" "README.md:1: caminho: docs/harness/sumiu.md"
}

# A doc real do workspace não cita nada que não exista.
test_docs_ref_workspace_real() {
  assert_ok python "$VERIFICA" "$WS_RAIZ"
}
```

Os testes rodam com a fixture `fx_setup` do `run.sh`, que cria `$T`. Eles usam só `$T/d`, sem a parte git da fixture. `assert_ok`, `assert_contains` e `fail` vêm de `lib.sh`.

- [ ] **Passo 2: rodar e ver falhar**

Rode `bash tools/ws/tests/run.sh tools/ws/tests/test_docs_referencias.sh`.
Esperado: todos os `test_docs_ref_*` falham, porque `docs_referencias.py` não existe (`can't open file`). O `test_docs_ref_workspace_real` também falha.

- [ ] **Passo 3: implementar o verificador**

Crie `tools/ws/tests/docs_referencias.py`:

```python
"""Verifica as referências da doc do harness (spec SP4, seção 6).

Lê <raiz>/README.md e <raiz>/docs/harness/*.md (sem subpastas: o historico/ fica de fora) e lista
o que a doc cita e não existe: caminho, subcomando do ws, skill, mensagem de erro (Sintoma) e link relativo.
Uso: python docs_referencias.py <raiz>   (sai com 1 se houver violação)
"""
import pathlib
import re
import sys

PREFIXOS = ('tools/', 'docs/', '.specify/', '.claude/')  # specs/ só existe depois da primeira feature
GENERICO = re.compile(r'<|>|NNN|\*|\{')
NATIVOS = {'mcp', 'help', 'clear', 'login', 'logout', 'config', 'init', 'model', 'status', 'compact', 'resume'}
CODIGO_INLINE = re.compile(r'`([^`\n]+)`')
LINK = re.compile(r'\]\(([^)\s]+)\)')
WS = re.compile(r'(?<![\w/-])(?:tools/ws/)?ws ([a-z]+)(?: ([a-z]+))?')
SKILL = re.compile(r'^/([a-z][a-z0-9-]+)')
PLACEHOLDER = re.compile(r'<[^>]*>')
FONTES = ('tools', '.specify', '.claude')


def uso(texto, padrao):
    m = re.search(padrao, texto)
    return set(m.group(1).split('|')) if m else set()


def trechos(linhas):
    """(nº da linha, texto de código): spans inline e linhas de blocos cercados."""
    em_bloco = False
    for n, linha in enumerate(linhas, 1):
        if linha.lstrip().startswith('```'):
            em_bloco = not em_bloco
            continue
        if em_bloco:
            yield n, linha.strip(), True
        else:
            for m in CODIGO_INLINE.finditer(linha):
                yield n, m.group(1).strip(), False


def caminhos(texto):
    for tok in texto.split():
        tok = tok.strip('.,;:()"\'')
        if tok.startswith(PREFIXOS) and not GENERICO.search(tok):
            yield re.sub(r':\d+$', '', tok)


def sintomas(linhas):
    """(nº da linha, mensagem) das linhas do primeiro bloco cercado depois de cada **Sintoma:**."""
    i = 0
    while i < len(linhas):
        if linhas[i].strip().startswith('**Sintoma:**'):
            j = i + 1
            while j < len(linhas) and not linhas[j].lstrip().startswith('```'):
                j += 1
            j += 1
            while j < len(linhas) and not linhas[j].lstrip().startswith('```'):
                if linhas[j].strip():
                    yield j + 1, linhas[j].strip()
                j += 1
            i = j
        i += 1


def main(raiz):
    sys.stdout.reconfigure(encoding='utf-8')  # no Windows o padrão é cp1252
    raiz = pathlib.Path(raiz)
    ws_txt = (raiz / 'tools/ws/ws').read_text(encoding='utf-8') if (raiz / 'tools/ws/ws').exists() else ''
    lib_txt = '\n'.join(f.read_text(encoding='utf-8') for f in sorted((raiz / 'tools/ws/lib').glob('*.sh')))
    cmds = uso(ws_txt, r'uso: ws <([a-z|]+)>')
    cmds_atlas = uso(lib_txt, r'uso: ws atlas <([a-z|]+)>')
    fonte = '\n'.join(f.read_text(encoding='utf-8', errors='replace')
                      for d in FONTES if (raiz / d).exists()
                      for f in (raiz / d).rglob('*')
                      if f.is_file() and f.suffix in ('.sh', '.md', '.py', '.yml', '') and 'tests' not in f.parts)
    docs = [raiz / 'README.md'] + sorted((raiz / 'docs/harness').glob('*.md'))
    erros, lidos = [], 0
    for doc in docs:
        if not doc.exists():
            continue
        lidos += 1
        rel = doc.relative_to(raiz).as_posix()
        linhas = doc.read_text(encoding='utf-8').splitlines()
        for n, texto, em_bloco in trechos(linhas):
            for c in caminhos(texto):
                if not (raiz / c.rstrip('/')).exists():
                    erros.append(f'{rel}:{n}: caminho: {c}')
            for m in WS.finditer(texto):
                sub, sub2 = m.group(1), m.group(2)
                if sub not in cmds:
                    erros.append(f'{rel}:{n}: ws: ws {sub}')
                elif sub == 'atlas' and sub2 and sub2 not in cmds_atlas:
                    erros.append(f'{rel}:{n}: ws: ws atlas {sub2}')
            m = SKILL.match(texto)
            if not em_bloco and m and m.group(1) not in NATIVOS and \
                    not (raiz / '.claude/skills' / m.group(1) / 'SKILL.md').exists():
                erros.append(f'{rel}:{n}: skill: /{m.group(1)}')
        if doc.name == '2-quando-da-errado.md':
            for n, msg in sintomas(linhas):
                msg = re.sub(r'^ws: erro: ', '', msg)
                fixos = [p.strip() for p in PLACEHOLDER.split(msg) if len(p.strip()) >= 8]
                if not fixos or any(p not in fonte for p in fixos):
                    erros.append(f'{rel}:{n}: sintoma: {msg}')
        for n, linha in enumerate(linhas, 1):
            for m in LINK.finditer(linha):
                alvo = m.group(1).split('#')[0]
                if not alvo or re.match(r'^[a-z]+:', alvo):
                    continue
                if not (doc.parent / alvo).exists():
                    erros.append(f'{rel}:{n}: link: {alvo}')
    for e in erros:
        print(e)
    if not erros:
        print(f'ok: {lidos} arquivo(s)')
    return 1 if erros else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
```

Observações para quem implementa:
- `fonte` lê arquivos sem extensão porque `tools/ws/ws` não tem extensão. Ela ignora as pastas `tests/`: os testes contêm mensagens inventadas, que não podem contar como código.
- A skill só é conferida quando o span inline **começa** com `/`. Caminhos como `docs/x` nunca começam com `/`.
- Uma mensagem de **Sintoma** sem nenhum trecho fixo de 8 caracteres ou mais é acusada. Uma mensagem curta demais não prova nada contra o código.

- [ ] **Passo 4: rodar e ver passar**

Rode `bash tools/ws/tests/run.sh tools/ws/tests/test_docs_referencias.sh`.
Esperado: `13 ok, 0 falha(s)`. O `test_docs_ref_workspace_real` passa porque ainda não há `README.md` nem `docs/harness/`.

- [ ] **Passo 5: commit**

```bash
git add tools/ws/tests/docs_referencias.py tools/ws/tests/test_docs_referencias.sh
git commit -F - <<'EOF'
harness: teste de referências da documentação

Verifica caminhos, subcomandos do ws, skills, mensagens de Sintoma e links citados no README.md e em docs/harness/ (spec SP4, seção 6).

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
EOF
```

---

### Task 2: Histórico das decisões

**Arquivos:**
- Criar: `docs/harness/historico/` com as cópias listadas abaixo
- Criar: `docs/harness/historico/LEIA-ME.md`

**Interfaces:**
- Produz: `docs/harness/historico/LEIA-ME.md`, que a camada 4 (Task 6) cita.

- [ ] **Passo 1: copiar os arquivos**

```bash
D=/c/src/00-harness_big_brown_field/docs
H=docs/harness/historico
mkdir -p "$H"
cp "$D/superpowers/specs/2026-09-28-sp2-speckit-multirepo-design.md" \
   "$D/superpowers/specs/2026-10-05-sp3-grafo-e-navegacao-design.md" \
   "$D/superpowers/specs/2026-10-07-sp2-adendo-harness-awx-subordinado-design.md" \
   "$D/superpowers/plans/2026-09-24-sp1-workspace-multi-repo.md" \
   "$D/superpowers/plans/2026-09-29-sp2-speckit-multirepo.md" \
   "$D/superpowers/plans/2026-10-05-sp3-atlas.md" \
   "$D/superpowers/plans/2026-10-07-sp2-adendo-awx-subordinado.md" \
   "$D/discovery/sp1-bootstrap.md" "$D/discovery/sp2-validacao.md" "$D/discovery/sp3-validacao.md" \
   "$D/discovery/sp3-ledger-execucao.md" "$D/discovery/sp2-adendo-awx-ledger.md" "$H/"
ls "$H" | wc -l
```

Esperado: `12`.

- [ ] **Passo 2: conferir que não vai segredo junto**

```bash
grep -niE 'password|senha|pwd=|secret|token|apikey|api_key|bearer|://[^/ ]+:[^@ ]+@|[A-Za-z0-9]{40,}' docs/harness/historico/*.md
```

Leia cada ocorrência.
- **Aceitável:** citação por nome ou local (por exemplo, "o PAT fica guardado no `az devops login`"), hash de commit e nome de arquivo.
- **Inaceitável:** qualquer valor de credencial, token, string de conexão com senha ou URL com usuário e senha. Remova da cópia, troque por `<redacted>` e anote no relatório da task.
- **Arquivos inteiros:** confira também que nenhum arquivo copiado é de `docs/credentials/`.

- [ ] **Passo 3: escrever o `LEIA-ME.md`**

```markdown
# Histórico das decisões do harness

Registro de como o harness foi desenhado e validado (SP1 a SP3, com os adendos). **Não é atualizado**: o estado atual está nas camadas (`docs/harness/1-comecar.md` a `4-manter.md`), e as decisões vigentes, em `docs/adr/`.

| Arquivo | O que é |
|---|---|
| `2026-09-24-sp1-workspace-multi-repo.md` | Plano do SP1: workspace com git subtree |
| `sp1-bootstrap.md` | Medidas e achados do bootstrap do SP1 |
| `2026-09-28-sp2-speckit-multirepo-design.md` | Spec do SP2: Spec Kit multi-repo |
| `2026-09-29-sp2-speckit-multirepo.md` | Plano do SP2 |
| `sp2-validacao.md` | Validação de ponta a ponta do SP2 e do adendo |
| `2026-10-07-sp2-adendo-harness-awx-subordinado-design.md` | Spec do adendo: AWX mantém o Spec Kit dele, subordinado |
| `2026-10-07-sp2-adendo-awx-subordinado.md` | Plano do adendo |
| `sp2-adendo-awx-ledger.md` | Ledger da execução do adendo |
| `2026-10-05-sp3-grafo-e-navegacao-design.md` | Spec do SP3: Atlas e navegação de código |
| `2026-10-05-sp3-atlas.md` | Plano do SP3 |
| `sp3-validacao.md` | Validação do Atlas (incremental, features reais, ponta a ponta) |
| `sp3-ledger-execucao.md` | Ledger da execução do SP3 |

Os links e caminhos dentro desses arquivos apontam para a pasta de discovery onde eles foram escritos (`docs/discovery/`, `docs/superpowers/`, `poc/`) e podem não abrir aqui.
```

- [ ] **Passo 4: rodar o teste de referências**

Rode `bash tools/ws/tests/run.sh tools/ws/tests/test_docs_referencias.sh`.
Esperado: `13 ok`. O `historico/` fica fora da verificação, e o `LEIA-ME.md` também, por estar numa subpasta.

- [ ] **Passo 5: commit**

```bash
git add docs/harness/historico
git commit -F - <<'EOF'
harness: histórico das specs, planos e validações do SP1 ao SP3

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
EOF
```

---

### Task 3: `README.md` e camada 1

**Arquivos:**
- Criar: `README.md`
- Criar: `docs/harness/1-comecar.md`

**Interfaces:**
- Consome: o verificador (Task 1).
- Produz: os links `docs/harness/1-comecar.md` a `4-manter.md`. Os arquivos das camadas 2 a 4 só nascem nas Tasks 4 a 6, então nesta task eles são criados vazios, com um título, para os links valerem: `# Quando dá errado`, `# Além do básico` e `# Manter o harness`. As tasks seguintes os preenchem.
- Produz: na camada 3, a âncora da receita 1, `#mapas-de-codigo-para-o-agente`. O título da receita na Task 5 tem de ser exatamente `## Mapas de código para o agente`.

- [ ] **Passo 1: criar os arquivos-semente das camadas 2 a 4**

```bash
printf '# Quando dá errado\n' > docs/harness/2-quando-da-errado.md
printf '# Além do básico\n' > docs/harness/3-alem-do-basico.md
printf '# Manter o harness\n' > docs/harness/4-manter.md
```

- [ ] **Passo 2: escrever o `README.md`**

```markdown
# Workspace WMS

Os repos do WMS juntos num só lugar: cada repo do Azure DevOps fica em `repos/<repo>/`, e a raiz é o harness, o ferramental para desenvolver com IA.
Uma feature começa e termina pelo Spec Kit, que cria a branch, a spec, o plano e as tarefas, e envia as mudanças para cada repo.
O Atlas é a memória dos sistemas: o mapa entre os repos, os docs de cada um e o impacto de mudar uma tabela, uma proc, um endpoint ou uma fila.

## Pré-requisitos

- Git for Windows (os scripts rodam no Git Bash).
- Credencial do Azure DevOps com push de branch nos repos de `workspace.repos`.
- Claude Code.
- Ferramentas do Atlas (WSL, codebase-memory-mcp, Graphify e ast-grep): veja [Mapas de código para o agente](docs/harness/3-alem-do-basico.md#mapas-de-codigo-para-o-agente). Sem elas o fluxo funciona, mas o agente navega o código com menos eficiência.

## Quero…

| Quero… | Leia |
|---|---|
| começar e fazer minha primeira feature | [1. Começar](docs/harness/1-comecar.md) |
| resolver um erro | [2. Quando dá errado](docs/harness/2-quando-da-errado.md) |
| fazer algo além do básico | [3. Além do básico](docs/harness/3-alem-do-basico.md) |
| mudar ou manter o harness | [4. Manter o harness](docs/harness/4-manter.md) |
```

- [ ] **Passo 3: escrever a camada 1**

Escreva `docs/harness/1-comecar.md` seguindo a seção 4.2 da spec, nesta ordem e com estes títulos:
1. `# Começar` e uma frase do que a página entrega: preparar a máquina e fazer uma feature até o PR.
2. `## Antes de tudo (só uma vez)`
   - um bloco `<details><summary>Nunca usou Claude Code?</summary>` com no máximo 8 linhas: instalar (link para a doc oficial `https://docs.claude.com/claude-code`), entrar (`claude` e login), conversar em linguagem natural, e que comandos com `/` são skills;
   - o comando de clone das restrições globais e a credencial do Azure DevOps;
   - `cd industria-logistica.wms.workspace` e `claude`;
   - uma linha: "Recomendado: instale as ferramentas do Atlas", com link para `3-alem-do-basico.md#mapas-de-codigo-para-o-agente`.
3. `## Uma feature, do início ao PR`: uma lista numerada, uma linha por passo, no formato "`/comando` — o que acontece". Use o texto atual do `docs/workspace.md` (seção "Features com o Spec Kit") e do `AGENTS.md` como fonte:
   1. `/speckit-specify <descrição>`: cria a branch (com `ws start`) e a spec em `specs/ws-NNN-<nome>/`.
   2. `/speckit-clarify`: só se o agente pedir.
   3. `/speckit-plan`.
   4. `/speckit-tasks`.
   5. `/speckit-analyze`.
   6. `/speckit-implement`.
   7. `/speckit-converge`: no fim, o Atlas dos repos tocados é atualizado.
   8. `/speckit-ws-commit-push`: commit e `ws push` para cada repo alterado, sempre com a sua confirmação.
   9. Abra um PR por repo no Azure DevOps. Com **todos** mergeados, abra o PR do workspace para o `main`.
4. `## Já conhece o Spec Kit? O que muda aqui`: os 4 itens da seção 4.2, item 3, da spec, em lista.
5. `## Três regras que não se quebram`: os 3 itens da seção 4.2, item 4, da spec.
6. `## Travou?` com link para `2-quando-da-errado.md` e para a thread de suporte (seção "Não resolveu?" da camada 2).

- [ ] **Passo 4: conferir o tamanho e as referências**

```bash
wc -l docs/harness/1-comecar.md
bash tools/ws/tests/run.sh tools/ws/tests/test_docs_referencias.sh
```

Esperado: no máximo 80 linhas e `13 ok, 0 falha(s)`.
- O `test_docs_ref_workspace_real` agora verifica o `README.md` e a camada 1 de verdade.
- Se ele acusar algo, corrija a doc, não o verificador. Só mexa no verificador se for um falso positivo comprovado, e nesse caso com um teste novo de fixture na Task 1.

- [ ] **Passo 5: commit**

```bash
git add README.md docs/harness
git commit -F - <<'EOF'
harness: README de entrada e camada 1 (começar)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
EOF
```

---

### Task 4: Camada 2 (quando dá errado)

**Arquivos:**
- Modificar: `docs/harness/2-quando-da-errado.md`

**Interfaces:**
- Consome: o verificador, que confere cada **Sintoma** contra o código.
- Produz: as âncoras das seções por etapa, que a camada 1 e a camada 3 podem citar.

- [ ] **Passo 1: levantar as mensagens reais**

```bash
grep -rn 'die "' tools/ws/ws tools/ws/lib
grep -rnE 'echo .*(erro|pare|parou|recus)' -i .specify/extensions/ws/scripts tools/speckit/ws/scripts
grep -n -A6 'Erros no `ws start`' docs/workspace.md
```

Esperado: cerca de 38 `die` no `tools/ws`, mais as paradas dos scripts `ws-feature.sh` e `ws-commit-push.sh`.
- Classifique cada mensagem numa das 6 etapas da spec (seção 4.3).
- Descarte as mensagens de uso interno que um dev nunca vê no fluxo da camada 1. Por exemplo, `uso: ws atlas concluir --gatilho …` é chamado só pela skill.
- Anote, para cada mensagem, a função e a condição que a disparam, lendo o código ao redor. Isso é a **Causa**.

- [ ] **Passo 2: levantar os problemas já vistos**

Leia `docs/harness/historico/sp2-validacao.md` e `docs/harness/historico/sp3-validacao.md`. Liste os problemas que um dev pode encontrar **hoje**, ou seja, cujo comportamento ainda existe no código. Correções que já mudaram o comportamento não entram.

- [ ] **Passo 3: escrever a camada 2**

A estrutura segue a seção 4.3 da spec:
- `# Quando dá errado`, com uma frase: "Ache a etapa em que você travou; cada entrada traz o sintoma, a causa e o que fazer."
- Seis seções `##`:
  1. `Preparação e clone`
  2. `/speckit-specify e a criação da branch`
  3. `Do plan ao converge`
  4. `/speckit-ws-commit-push e ws push`
  5. `PRs e merge`
  6. `Atlas`

Cada entrada é um `###` com título curto e, dentro dele, exatamente:

````markdown
**Sintoma:**
```
ws: erro: <mensagem copiada do código, com as partes variáveis como <nome>>
```
**Causa:** uma frase.

**O que fazer:**
1. passo
2. passo
````

Regras de escrita:
- Para comportamento sem mensagem de erro (por exemplo, "o hook parou e pediu checkout da branch"), escreva o sintoma como texto **fora** de bloco de código, na mesma linha de `**Sintoma:**`. O verificador só confere blocos.
- Leve para a camada 2, com o texto revisado, as três entradas atuais de "Erros no `ws start`": conflito, "não consegui ler/baixar" e "push do main recusado".
- As situações "PR de um repo abandonado" e "feature não mergeada e quero mudá-la" ganham uma entrada curta cada, com link para a receita da camada 3.

Termine com:

```markdown
## Não resolveu?

Abra uma thread no espaço **Equipe WMS** do Google Chat: https://chat.google.com/room/AAAAKpyvLWs?cls=7

Mande junto:
1. o comando ou a skill que você rodou;
2. a mensagem completa;
3. a saída de `git status` e de `git log --oneline -3`.
```

- [ ] **Passo 4: rodar o teste de referências**

Rode `bash tools/ws/tests/run.sh tools/ws/tests/test_docs_referencias.sh`.
Esperado: `13 ok, 0 falha(s)`. Um `sintoma:` acusado quer dizer que a mensagem não foi copiada literalmente: copie do código de novo.

- [ ] **Passo 5: commit**

```bash
git add docs/harness/2-quando-da-errado.md
git commit -F - <<'EOF'
harness: camada 2 da documentação (quando dá errado)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
EOF
```

---

### Task 5: Camada 3 (além do básico)

**Arquivos:**
- Modificar: `docs/harness/3-alem-do-basico.md`

**Interfaces:**
- Produz: a âncora `#mapas-de-codigo-para-o-agente`, usada pelo `README.md` e pela camada 1. O título tem de ser exatamente `## Mapas de código para o agente`.
- Produz: o texto `graphifyy[sql,mcp]==0.9.77` e a citação `` `.specify/memory/constitution.md` ``, que o `test_harness.sh` passa a conferir nesta camada (Task 7).

- [ ] **Passo 1: escrever as 9 receitas**

Use a ordem e os títulos `##` abaixo. Cada receita tem **Quando usar** (uma frase), **Passos** (numerados) e, se preciso, **Cuidado** (no máximo 2 linhas). As fontes são as seções do `docs/workspace.md` indicadas e a seção 4.4 da spec:

| Receita (`##`) | Fonte |
|---|---|
| Mapas de código para o agente | `docs/workspace.md`, "Preparar uma máquina": os 5 passos com as versões de `tools/atlas/VERSOES.md`, incluindo o `uv tool install "graphifyy[sql,mcp]==0.9.77"` |
| Consultar o Atlas | `AGENTS.md`, regra 7; `.claude/skills/atlas-consultar/SKILL.md`; uma página real de `docs/atlas/impacto/` como exemplo de leitura (distância, via, grupo "fora do escopo", resumo por repo acima de 50, regra de só objetos tocados pelo WMS, trigger em tabela gravada) |
| Mudar uma feature que já existe | `docs/workspace.md`, "Features com o Spec Kit", item 1 |
| Trabalhar fora do Spec Kit | `docs/workspace.md`, "Fluxo", itens 1 a 6. **Começa** com o aviso da spec (seção 4.4, receita 4), em citação (`>`) |
| PR de um repo abandonado | `docs/workspace.md`, "Fluxo", item 5 (o `git restore --source=main …`) |
| Repo com Spec Kit próprio (AWX) | `docs/workspace.md`, "Features com o Spec Kit", subitem do AWX; `AGENTS.md`, regra 2 |
| Atualizar o Atlas à mão | `docs/workspace.md`, "Atlas" inteira: como se mantém, quando roda, onde fica e "O que acontece com cada repo no `ws start`" com o exemplo dos dias 1 a 8, e os nomes `intervalo_dias`, `limiar_arquivos` e `limite_minimo` de `tools/atlas/relevancia.ini` |
| Onde gravar uma regra ou decisão | `docs/workspace.md`, "Regras", 2º e 3º itens, citando `` `.specify/memory/constitution.md` `` como constitution do repo. Arquivos de dentro de um repo vão com o caminho completo (`repos/<repo>/docs/constitution.md`, não `docs/constitution.md`), senão o verificador os procura na raiz |
| Histórico de um repo | `docs/workspace.md`, "Clone raso" |

- [ ] **Passo 2: rodar os testes**

```bash
bash tools/ws/tests/run.sh tools/ws/tests/test_docs_referencias.sh
grep -c 'graphifyy\[sql,mcp\]==0.9.77' docs/harness/3-alem-do-basico.md
grep -c '`.specify/memory/constitution.md`' docs/harness/3-alem-do-basico.md
```

Esperado: `13 ok`, e as duas contagens ≥ 1.

- [ ] **Passo 3: commit**

```bash
git add docs/harness/3-alem-do-basico.md
git commit -F - <<'EOF'
harness: camada 3 da documentação (além do básico)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
EOF
```

---

### Task 6: Camada 4 (manter o harness)

**Arquivos:**
- Modificar: `docs/harness/4-manter.md`

- [ ] **Passo 1: conferir os nomes das peças no código**

```bash
cat .specify/extensions.yml
ls tools/ws/lib tools/atlas tools/speckit tools/speckit/ws tools/speckit/multirepo .claude/skills docs/adr
```

Use os nomes dos hooks como estão no `extensions.yml` (`before_specify`, `after_converge` e os comandos `speckit.ws.feature` e `speckit.ws.converge`), não os da spec, se divergirem.

- [ ] **Passo 2: escrever a camada 4**

Siga as 4 seções da spec (4.5), com estes títulos `##`:
1. **`Como as peças se ligam`**
   - Um diagrama:

     ````markdown
     ```mermaid
     flowchart LR
       A[/speckit-specify/] --> B[hook before_specify<br/>speckit.ws.feature]
       B --> C[ws start] --> D[ws atlas plano] --> E[mapeamento<br/>codebase-discovery]
       F[/speckit-converge/] --> G[hook after_converge<br/>speckit.ws.converge] --> H[Atlas dos repos tocados]
       H --> I[/speckit-ws-commit-push/] --> J[ws push]
     ```
     ````

     Ajuste os nomes ao que o Passo 1 mostrou.
   - Depois, um parágrafo por peça (workspace e subtree com a ADR 0001; `tools/ws`; Spec Kit; Atlas).
2. **`Onde fica cada coisa`**: a tabela da spec (4.5, item 2), uma linha por caminho, com o papel em uma frase. Todo caminho entre crases precisa existir, e o verificador confere.
3. **`Tarefas de manutenção`**: uma receita por tarefa, com o texto vindo destas fontes:
   - **Atualizar o Spec Kit:** `docs/workspace.md`, "Spec Kit: instalar e atualizar";
   - **`ws maintain`:** "Manutenção";
   - **Adicionar um repo:** "Adicionar um repo";
   - **Atualizar as versões das ferramentas do Atlas:** `tools/atlas/VERSOES.md` e o `test_graphify_instalado_com_o_extra_do_mcp`;
   - **Reimportar o catálogo do banco:** cabeçalho de `tools/atlas/importa-mapeamento.sh`;
   - **Regenerar os derivados do Atlas:** `python tools/atlas/build-map.py --raiz .`, conforme a docstring do arquivo;
   - **Rodar os testes:** "Testes do `tools/ws`", com os 4 comandos.
4. **`Evoluir o harness`**: os 5 itens da spec (4.5, item 4), com um checklist de PR copiável:
   ```markdown
   - [ ] Branch própria, fora de uma feature
   - [ ] `bash tools/ws/tests/run.sh` passou
   - [ ] A camada da doc correspondente foi atualizada (comportamento novo não é pego pelo teste)
   - [ ] Decisão relevante registrada em `docs/adr/`
   ```
   Termine com o link para `historico/LEIA-ME.md`.

- [ ] **Passo 3: rodar o teste de referências**

Rode `bash tools/ws/tests/run.sh tools/ws/tests/test_docs_referencias.sh`.
Esperado: `13 ok, 0 falha(s)`.

- [ ] **Passo 4: commit**

```bash
git add docs/harness/4-manter.md
git commit -F - <<'EOF'
harness: camada 4 da documentação (manter o harness)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
EOF
```

---

### Task 7: Migração do `docs/workspace.md`

**Arquivos:**
- Remover: `docs/workspace.md`
- Modificar: `AGENTS.md:4`, `tools/atlas/relevancia.ini:2`, `tools/ws/tests/test_harness.sh:48` e `:80-83`

- [ ] **Passo 1: atualizar os testes que leem o `docs/workspace.md`; eles devem falhar ou continuar passando pelo motivo errado**

Em `tools/ws/tests/test_harness.sh`:
- Linha 48: troque `docs/workspace.md` por `docs/harness/3-alem-do-basico.md`. O laço passa a ser `for f in tools/atlas/VERSOES.md docs/harness/3-alem-do-basico.md; do`.
- Linhas 80 a 83: troque por

  ```bash
    grep -qF '`.specify/memory/constitution.md`' "$WS_RAIZ/docs/harness/3-alem-do-basico.md" \
      || fail "docs/harness/3-alem-do-basico.md não cita a constitution do repo em .specify/memory/"
    ! grep -rqF 'colidiriam com o Spec Kit da raiz' "$WS_RAIZ/README.md" "$WS_RAIZ/docs/harness/"[1-4]-*.md \
      || fail "a documentação ainda dá o motivo antigo da guarda do ws push"
  ```

- Adicione ao fim do arquivo:

  ```bash
  # SP4: o docs/workspace.md foi dissolvido nas camadas; nada fora de repos/ e do histórico aponta para ele.
  test_ninguem_cita_o_docs_workspace_md() {
    local achados
    achados=$(cd "$WS_RAIZ" && grep -rlF 'docs/workspace.md' --exclude-dir=repos --exclude-dir=.git \
      --exclude-dir=.superpowers --exclude-dir=historico . \
      | grep -v -e '^\./docs/atlas/' -e '^\./tools/ws/tests/test_harness\.sh$' || true)
    [ -z "$achados" ] || fail "ainda citam docs/workspace.md: $achados"
    [ ! -e "$WS_RAIZ/docs/workspace.md" ] || fail "docs/workspace.md devia ter sido removido"
  }
  ```

Rode `bash tools/ws/tests/run.sh tools/ws/tests/test_harness.sh`.
Esperado: `test_ninguem_cita_o_docs_workspace_md` **falha**, porque o arquivo existe e é citado. Os outros passam, porque as Tasks 5 e 3 já puseram os textos nas camadas.

O `test_ninguem_cita_o_docs_workspace_md` exclui o próprio `test_harness.sh` (que cita o nome na busca) e `docs/atlas/`, mas não `tools/atlas/`. Exclui `docs/atlas/` porque os docs gerados em `docs/atlas/` são do mapeamento e podem citar o arquivo histórico. Antes de seguir, confira com `grep -rlF 'docs/workspace.md' docs/atlas | head`. Se houver ocorrências, anote no relatório. Não edite `docs/atlas/` à mão.

- [ ] **Passo 2: conferir que nenhum conteúdo se perde**

Para cada seção do `docs/workspace.md`, confira que o conteúdo está no destino abaixo. Marque cada linha:

| Seção do `docs/workspace.md` | Destino |
|---|---|
| Introdução (subtree, ADR 0001) | `README.md` e camada 4, "Como as peças se ligam" |
| Clonar (comando, requisitos) | camada 1, "Antes de tudo"; `README.md`, "Pré-requisitos" |
| Fluxo, itens 1 a 6 | camada 3, "Trabalhar fora do Spec Kit"; PRs na camada 1 |
| Fluxo, PR abandonado | camada 3, "PR de um repo abandonado"; camada 2, entrada curta |
| Features com o Spec Kit | camada 1, "Uma feature"; camada 3, "Mudar uma feature" e "Repo com Spec Kit próprio" |
| Atlas, níveis 1 e 2, como se mantém | camada 3, "Atualizar o Atlas à mão"; camada 4, "Como as peças se ligam" |
| Atlas, o que acontece no `ws start` e exemplo | camada 3, "Atualizar o Atlas à mão" |
| Atlas, preparar uma máquina | camada 3, "Mapas de código para o agente" |
| Spec Kit: instalar e atualizar | camada 4, "Tarefas de manutenção" |
| Regras | camada 1, "Três regras"; camada 3, "Onde gravar uma regra ou decisão" |
| Clone raso | camada 3, "Histórico de um repo" |
| Erros no `ws start` | camada 2 |
| Manutenção (`ws maintain`) | camada 4 |
| Adicionar um repo | camada 4 |
| Testes do `tools/ws` | camada 4 |

Se algo estiver faltando, complete a camada de destino antes do Passo 3.

- [ ] **Passo 3: remover e atualizar as referências**

```bash
git rm -q docs/workspace.md
sed -i 's|^- \*\*Uso humano:\*\* `docs/workspace.md`\.|- **Uso humano:** `README.md` (entrada) e `docs/harness/` (documentação em camadas).|' AGENTS.md
sed -i 's|^# Explicação com exemplo: docs/workspace.md, seção "Atlas"\.|# Explicação com exemplo: docs/harness/3-alem-do-basico.md, receita "Atualizar o Atlas à mão".|' tools/atlas/relevancia.ini
grep -n 'Uso humano' AGENTS.md
sed -n 2p tools/atlas/relevancia.ini
```

Esperado: as duas linhas com o texto novo.

- [ ] **Passo 4: rodar os testes**

```bash
bash tools/ws/tests/run.sh tools/ws/tests/test_harness.sh tools/ws/tests/test_docs_referencias.sh
```

Esperado: 0 falhas. O `test_ninguem_cita_o_docs_workspace_md` agora passa.

- [ ] **Passo 5: commit**

```bash
git add -A AGENTS.md tools/atlas/relevancia.ini tools/ws/tests/test_harness.sh docs/workspace.md
git commit -F - <<'EOF'
harness: dissolve o docs/workspace.md nas camadas da documentação

AGENTS.md e relevancia.ini apontam para as camadas; os testes do harness leem a camada 3.

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
EOF
```

---

### Task 8: Validação final e publicação da branch

- [ ] **Passo 1: suíte completa**

Rode `bash tools/ws/tests/run.sh` (cerca de 15 min).
Esperado: `N ok, 0 falha(s)`, com N = suíte anterior (191) + 13 de `test_docs_referencias.sh` + 1 de `test_harness.sh`, ou seja, 205.

- [ ] **Passo 2: leitura das camadas contra o código**

Para cada comando, skill e mensagem citados nas camadas 1 e 3, confira no código que ele faz o que a doc diz:
- **comandos `ws`:** leia a função em `tools/ws/lib/<cmd>.sh`;
- **skills:** leia o `SKILL.md` delas.

Registre as divergências e corrija a doc, não o código. Esse é o item "leio as camadas contra o código" da seção 7 da spec.

- [ ] **Passo 3: limites de forma**

```bash
wc -l docs/harness/1-comecar.md
grep -nE 'TODO|TBD|a definir|XXX' README.md docs/harness/[1-4]-*.md
```

Esperado: no máximo 80 linhas na camada 1 e nenhuma ocorrência no `grep`.

- [ ] **Passo 4: publicar a branch**

```bash
git push -u origin harness/docs-camadas
```

O PR para o `main` é aberto pelo usuário. Depois do merge vem o piloto (seção 7 da spec): um dev que nunca usou o harness segue a camada 1, e as travadas viram um PR de acompanhamento. O registro fica em `C:\src\00-harness_big_brown_field\docs\discovery\sp4-piloto.md`.
