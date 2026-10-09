# SP4b: apresentação do harness — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** um deck de 21 slides no claude.ai (Artifact do tipo Slides) para o usuário apresentar o harness ao time WMS em cerca de 40 min, remoto, só teoria.

**Architecture:** o deck são arquivos locais em `docs/discovery/sp4-apresentacao/deck/project/` (`deck.json` + um HTML por slide), publicados no Artifact do tipo Slides. Um verificador Python (`confere_deck.py`) confere os arquivos locais contra a doc do `main` do workspace antes de cada publicação: comandos, skills, mensagens e caminhos citados existem, todo slide tem nota com tempo, a soma fica entre 35 e 40 min, nada fora do formato do tipo Slides.

**Tech Stack:** HTML no formato do tipo Slides (seção 1920×1080, estilos inline), Python 3 (stdlib: `html.parser`, `unittest`), ferramenta Artifact.

**Spec:** `docs/superpowers/specs/2026-10-08-sp4-apresentacao-harness-design.md`

## Restrições globais

- Fonte da verdade: `C:\src\wms-workspace` no `main` (`0cbac04e5`), `README.md` e `docs/harness/1-4`. O deck não afirma nada que a doc não diga.
- As mensagens de erro citadas vêm literalmente de `docs/harness/2-quando-da-errado.md`; o exemplo de impacto é o de `Audit.DBO.ADT_CAIXA`, já citado na camada 3.
- A feature dos slides 5 a 13 é fictícia, e o slide 5 diz isso ("Exemplo fictício").
- Remoto: título + até 4 linhas ou um diagrama por slide; nenhuma fonte abaixo de 24px; o detalhe vai nas notas (`<aside>`, último filho, até 4.000 caracteres).
- Toda nota termina com `Tempo: N min` (decimal com vírgula); soma entre 35 e 40.
- Sem segredos, credenciais ou dados de produção no deck.
- Português.
- Formato do tipo Slides: um `<section id="<id>">` por arquivo `project/slides/<id>.html`, sem `<html>`, `<head>`, `<style>`, `<script>`, `<link>`, `<body>`, `<title>`; no máximo 200 elementos por slide; sem `data:` URI.
- A regra do tipo Slides "não verificar depois de publicar" vale: a conferência é sempre nos arquivos locais, antes de publicar, com o verificador. Nada de renderizar ou ler o deck de volta.

## Foco de revisão

1. **Texto que estoura o slide:** um card ou lista maior que o espaço (824 px úteis) corta no meio da apresentação. O verificador não mede layout; cada slide segue o orçamento da seção "Layouts" (linhas máximas por bloco), conferido na escrita.
2. **Comando citado que não existe ou mudou de nome** (`/speckit-ws-commit-push`, `ws start`): o verificador confere skills contra `.claude/skills/` e subcomandos contra o uso do `tools/ws/ws`. Coberto em `test_skill_inexistente` e `test_ws_inexistente` (Task 1).
3. **Mensagem de erro parafraseada no slide 17:** o dev procura o texto na camada 2 e não acha. Toda linha que começa com `ws: ` precisa existir literalmente na camada 2. Coberto em `test_mensagem_inexistente` (Task 1).
4. **Exemplo fictício tomado por real:** coberto em `test_exemplo_sem_marca` (Task 1).
5. **Tempo total fora da janela:** coberto em `test_tempo_fora_da_janela` (Task 1).

---

## Estrutura de arquivos

Tudo em `C:\src\00-harness_big_brown_field\docs\discovery\sp4-apresentacao\` (pasta sem git; nada de commit):

- `confere_deck.py`: o verificador. Uso: `python confere_deck.py <pasta do deck> <raiz do workspace>`; sai com 1 se houver violação.
- `test_confere_deck.py`: testes do verificador (`unittest`, fixtures em pasta temporária).
- `deck/project/deck.json`: o índice do deck.
- `deck/project/slides/<id>.html`: um por slide.
- `deck/url.txt`: o link do Artifact, gravado na Task 2.

Ids dos slides, em ordem: `capa`, `hoje`, `antes-depois`, `pecas`, `exemplo`, `passo-1`, `passo-2`, `passo-3`, `passo-4`, `passo-5`, `passo-6`, `passo-7`, `passo-8-9`, `resumo`, `ja-conhece`, `regras`, `erros`, `atlas`, `impacto`, `onde`, `proximos`.

## Direção visual

- **Paleta:** tinta `#1d2433`, papel `#f6f4ef`, papel 2 `#ebe7de`, acento `#b5452f` (texto ≥ 32px sobre papel), azul `#2f5f7f`, cinza `#5a6170`, acento claro `#e8846f` (só sobre tinta), borda `#d9d4c8`.
- **Tipos:** IBM Plex Sans (texto) e IBM Plex Mono (comandos e mensagens).
- **Escala:** 120 (capa), 72 (títulos), 40 (destaques e títulos de card), 32 (corpo), 24 (rótulos e rodapé).
- **Fundos:** conteúdo em papel; capa, `exemplo`, `resumo` e `proximos` em tinta.
- **Rodapé** em todo slide menos a capa: um `<p>` fixo `position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:#5a6170` (sobre tinta: `#c9c4b8`) com `Harness WMS · <n>/21`.

## Layouts

Cada slide usa um destes. Os trechos `{…}` são os valores dados por slide nas Tasks 2 a 4. Todo slide termina com `<aside>{nota}</aside>` antes de `</section>`.

**L-capa** (fundo tinta):
```html
<section id="{id}" data-transition="fade" style="background:#1d2433;color:#f6f4ef;font-family:'IBM Plex Sans', Arial, sans-serif;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">
<p style="font-size:24px;color:#e8846f;font-weight:600;letter-spacing:4px">{rótulo}</p>
<h1 style="font-size:120px;font-weight:700;line-height:1.05">{título}</h1>
<p style="font-size:40px;color:#c9c4b8">{subtítulo}</p>
<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:#c9c4b8">{rodapé}</p>
<aside>{nota}</aside>
</section>
```

**L-cartoes** (papel; título + 3 cartões lado a lado; cada cartão: título ≤ 2 linhas de 40px, texto ≤ 4 linhas de 32px, cerca de 26 caracteres por linha):
```html
<section id="{id}" data-transition="fade" style="background:#f6f4ef;color:#1d2433;font-family:'IBM Plex Sans', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:column;gap:64px">
<h2 style="font-size:72px;font-weight:700;line-height:1.1">{título}</h2>
<div style="display:flex;gap:32px">
<div style="flex:1;display:flex;flex-direction:column;gap:16px;background:#ffffff;padding:48px;border:1px solid #d9d4c8;border-radius:16px">
<h3 style="font-size:40px;font-weight:700;color:#b5452f;line-height:1.15">{cartão 1 título}</h3>
<p style="font-size:32px;line-height:1.4">{cartão 1 texto}</p>
</div>
{… cartões 2 e 3 com a mesma marcação}
</div>
<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:#5a6170">{rodapé}</p>
<aside>{nota}</aside>
</section>
```

**L-tabela** (papel; título + tabela de até 4 linhas de dados, células de 32px com até 2 linhas de texto):
```html
<section id="{id}" data-transition="fade" style="background:#f6f4ef;color:#1d2433;font-family:'IBM Plex Sans', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:column;gap:56px">
<h2 style="font-size:72px;font-weight:700;line-height:1.1">{título}</h2>
<table style="width:1664px;font-size:32px;line-height:1.35">
<tr><th style="text-align:left;padding:16px 24px;font-size:24px;color:#5a6170;border-bottom:2px solid #1d2433">{cab 1}</th>{… demais cabeçalhos iguais}</tr>
<tr><td style="padding:24px;border-bottom:1px solid #d9d4c8;font-weight:600">{célula}</td><td style="padding:24px;border-bottom:1px solid #d9d4c8">{célula}</td>{…}</tr>
</table>
<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:#5a6170">{rodapé}</p>
<aside>{nota}</aside>
</section>
```

**L-passo** (papel; o número grande à esquerda, à direita o comando, "O que acontece" com até 3 itens de até 2 linhas e "Você vê" com até 2 linhas):
```html
<section id="{id}" data-transition="push" style="background:#f6f4ef;color:#1d2433;font-family:'IBM Plex Sans', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:row;gap:80px;align-items:flex-start">
<div style="width:320px;display:flex;flex-direction:column;gap:8px">
<p style="font-size:24px;color:#5a6170;font-weight:600;letter-spacing:4px">PASSO</p>
<p style="font-size:200px;font-weight:700;color:#b5452f;line-height:1">{n}</p>
</div>
<div style="flex:1;display:flex;flex-direction:column;gap:40px">
<h2 style="font-family:'IBM Plex Mono', Consolas, monospace;font-size:56px;font-weight:600;line-height:1.15">{comando}</h2>
<div style="display:flex;flex-direction:column;gap:12px">
<h3 style="font-size:24px;color:#5a6170;font-weight:600;letter-spacing:2px">O QUE ACONTECE</h3>
<ul style="font-size:32px;line-height:1.4;display:flex;flex-direction:column;gap:12px">
<li>{item}</li>{…}
</ul>
</div>
<div style="background:#ebe7de;border-radius:16px;padding:32px 40px;display:flex;flex-direction:column;gap:8px">
<h3 style="font-size:24px;color:#2f5f7f;font-weight:600;letter-spacing:2px">VOCÊ VÊ</h3>
<p style="font-size:32px;line-height:1.4">{você vê}</p>
</div>
</div>
<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:#5a6170">{rodapé}</p>
<aside>{nota}</aside>
</section>
```
O `{comando}` cabe em uma linha de 56px na coluna (1264px ≈ 37 caracteres mono); comandos maiores ficam em 2 linhas, e então "O que acontece" tem no máximo 2 itens.

**L-declaracao** (tinta; uma frase forte e um apoio):
```html
<section id="{id}" data-transition="fade" style="background:#1d2433;color:#f6f4ef;font-family:'IBM Plex Sans', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:column;justify-content:center;gap:48px">
<p style="font-size:24px;color:#e8846f;font-weight:600;letter-spacing:4px">{rótulo}</p>
<h2 style="font-size:72px;font-weight:700;line-height:1.15;width:1500px">{frase}</h2>
<p style="font-size:32px;line-height:1.4;color:#c9c4b8;width:1400px">{apoio}</p>
<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:#c9c4b8">{rodapé}</p>
<aside>{nota}</aside>
</section>
```

**L-lista** (papel; título + até 4 itens numerados grandes, cada um com até 2 linhas de 32px):
```html
<section id="{id}" data-transition="fade" style="background:#f6f4ef;color:#1d2433;font-family:'IBM Plex Sans', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:column;gap:56px">
<h2 style="font-size:72px;font-weight:700;line-height:1.1">{título}</h2>
<div style="display:flex;flex-direction:column;gap:32px">
<div style="display:flex;flex-direction:row;gap:40px;align-items:flex-start">
<p style="font-size:40px;font-weight:700;color:#b5452f;width:64px">{n}</p>
<p style="font-size:32px;line-height:1.4;width:1500px">{item}</p>
</div>
{… demais itens com a mesma marcação}
</div>
<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:#5a6170">{rodapé}</p>
<aside>{nota}</aside>
</section>
```

**Comando ou mensagem dentro de texto:** `<span style="font-family:'IBM Plex Mono', Consolas, monospace;color:#2f5f7f">{texto}</span>` (sobre tinta: `color:#e8846f`). Placeholders como `<repo>` são escritos `&lt;repo&gt;`.

---

### Task 1: verificador do deck

**Files:**
- Create: `docs/discovery/sp4-apresentacao/confere_deck.py`
- Test: `docs/discovery/sp4-apresentacao/test_confere_deck.py`

**Interfaces:**
- Produces: `python confere_deck.py <deck> <workspace>`; imprime `<slide>: <regra>: <detalhe>` por violação, ou `ok: <n> slide(s), <t> min`; sai 1 ou 0. `<deck>` é a pasta que contém `project/`. Função `confere(deck: Path, ws: Path) -> tuple[list[str], int, float]` (erros, nº de slides, minutos).

- [ ] **Step 1: Escrever os testes**

`test_confere_deck.py`:
```python
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from confere_deck import confere

ASIDE = '<aside>Fale do tema. Tempo: 36 min</aside>'


def slide(id_, corpo='<h2 style="font-size:72px">Título</h2>', aside=ASIDE):
    return f'<section id="{id_}" style="background:#f6f4ef;font-size:32px">{corpo}{aside}</section>'


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = pathlib.Path(self.tmp.name)
        self.ws = raiz / 'ws'
        (self.ws / 'tools/ws').mkdir(parents=True)
        (self.ws / 'tools/ws/ws').write_text('echo "uso: ws <add|start|push|atlas>"\n', encoding='utf-8')
        (self.ws / '.claude/skills/speckit-specify').mkdir(parents=True)
        (self.ws / '.claude/skills/speckit-specify/SKILL.md').write_text('x', encoding='utf-8')
        (self.ws / 'docs/harness').mkdir(parents=True)
        (self.ws / 'docs/harness/2-quando-da-errado.md').write_text(
            'ws: erro: há mudanças não commitadas; faça commit ou stash antes\n'
            'ws: aviso: o mapeamento falhou em <repos>; esses repos continuam pendentes\n', encoding='utf-8')
        self.deck = raiz / 'deck'
        (self.deck / 'project/slides').mkdir(parents=True)
        self.slides = {'capa': slide('capa')}

    def tearDown(self):
        self.tmp.cleanup()

    def roda(self):
        for f in (self.deck / 'project/slides').glob('*.html'):
            f.unlink()
        for k, v in self.slides.items():
            (self.deck / f'project/slides/{k}.html').write_text(v, encoding='utf-8')
        (self.deck / 'project/deck.json').write_text(json.dumps({'order': list(self.slides)}), encoding='utf-8')
        return confere(self.deck, self.ws)

    def falha(self, trecho):
        erros, _, _ = self.roda()
        self.assertTrue(any(trecho in e for e in erros), erros)


class Testes(Base):
    def test_deck_valido(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">Rode <span>/speckit-specify</span>, que chama ws start.</p>'
                                    '<p style="font-size:24px">ws: erro: há mudanças não commitadas; faça commit ou stash antes</p>'
                                    '<p style="font-size:24px">ws: aviso: o mapeamento falhou em &lt;repos&gt;; esses repos continuam pendentes</p>'
                                    '<p style="font-size:24px">Índice: docs/harness/2-quando-da-errado.md e https://chat.google.com/room/X</p>')
        erros, n, t = self.roda()
        self.assertEqual(erros, [])
        self.assertEqual((n, t), (1, 36.0))

    def test_sem_nota(self):
        self.slides['capa'] = slide('capa', aside='')
        self.falha('capa: nota')

    def test_nota_sem_tempo(self):
        self.slides['capa'] = slide('capa', aside='<aside>Fale.</aside>')
        self.falha('capa: tempo')

    def test_tempo_fora_da_janela(self):
        self.slides['capa'] = slide('capa', aside='<aside>x Tempo: 20 min</aside>')
        self.falha('deck: tempo total 20')

    def test_tempo_com_virgula(self):
        self.slides['capa'] = slide('capa', aside='<aside>x Tempo: 18,5 min</aside>')
        self.slides['b'] = slide('b', aside='<aside>x Tempo: 18,5 min</aside>')
        erros, n, t = self.roda()
        self.assertEqual((erros, t), ([], 37.0))

    def test_fonte_pequena(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:20px">x</p>')
        self.falha('capa: fonte 20px')

    def test_skill_inexistente(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">Rode /speckit-sumiu agora</p>')
        self.falha('capa: skill /speckit-sumiu')

    def test_ws_inexistente(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">Rode ws sincroniza</p>')
        self.falha('capa: ws sincroniza')

    def test_mensagem_inexistente(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">ws: erro: algo que o código não diz</p>')
        self.falha('capa: mensagem')

    def test_caminho_inexistente(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">Veja docs/harness/9-nada.md</p>')
        self.falha('capa: caminho docs/harness/9-nada.md')

    def test_caminho_generico_passa(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">Em docs/atlas/&lt;repo&gt;/ e tools/ws/ws</p>')
        erros, _, _ = self.roda()
        self.assertEqual(erros, [])

    def test_exemplo_sem_marca(self):
        self.slides['exemplo'] = slide('exemplo', '<p style="font-size:32px">Bloquear endereço</p>', aside='<aside>Tempo: 0 min</aside>')
        self.falha('exemplo: sem a marca de fictício')

    def test_id_diferente_do_arquivo(self):
        self.slides['capa'] = slide('outro')
        self.falha('capa: id')

    def test_duas_secoes(self):
        self.slides['capa'] = slide('capa') + slide('capa')
        self.falha('capa: seções')

    def test_tag_proibida(self):
        self.slides['capa'] = slide('capa', '<style>p{}</style><p style="font-size:32px">x</p>')
        self.falha('capa: tag <style>')

    def test_aside_nao_e_o_ultimo(self):
        self.slides['capa'] = f'<section id="capa" style="font-size:32px">{ASIDE}<p style="font-size:32px">x</p></section>'
        self.falha('capa: nota')

    def test_segredo(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">https://user:abc123@dev.azure.com/x</p>')
        self.falha('capa: segredo')

    def test_data_uri(self):
        self.slides['capa'] = slide('capa', '<img src="data:image/png;base64,AAAA" alt="x" style="width:10px">')
        self.falha('capa: data:')

    def test_arquivo_fora_do_order(self):
        self.roda()
        (self.deck / 'project/slides/solto.html').write_text(slide('solto'), encoding='utf-8')
        erros, _, _ = confere(self.deck, self.ws)
        self.assertTrue(any('solto: fora do order' in e for e in erros), erros)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd C:/src/00-harness_big_brown_field/docs/discovery/sp4-apresentacao && python -m unittest test_confere_deck -v`
Expected: erro de import, `ModuleNotFoundError: No module named 'confere_deck'`.

- [ ] **Step 3: Escrever o verificador**

`confere_deck.py`:
```python
"""Confere o deck da apresentação do harness contra a doc do workspace (spec SP4b, seção 5).

Uso: python confere_deck.py <pasta do deck> <raiz do workspace>   (sai com 1 se houver violação)
"""
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

PROIBIDAS = {'html', 'head', 'body', 'style', 'script', 'link', 'title', 'meta'}
FONTE = re.compile(r'font-size:\s*(\d+(?:\.\d+)?)px')
TEMPO = re.compile(r'Tempo:\s*(\d+(?:,\d+)?)\s*min')
SKILL = re.compile(r'(?<![\w/.:-])/([a-z][a-z0-9-]+)')
WS = re.compile(r'(?<![\w/-])ws ([a-z]+)')
CAMINHO = re.compile(r'(?<![\w/.-])((?:docs|tools)/[^\s"\'`),;]+)')
GENERICO = re.compile(r'<|>|NNN|\*|\.\.\.')
SEGREDO = re.compile(r'(?i)(senha|password|pwd=|token=|://[^/\s:@]+:[^@\s]+@)')
JANELA = (35, 40)
FICTICIO = 'exemplo'


class Leitor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags, self.secoes, self.blocos, self.nota = [], [], [], None
        self.em_nota, self.depois_da_nota, self.atual = False, False, []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag == 'section':
            self.secoes.append(dict(attrs).get('id'))
        elif tag == 'aside':
            self.em_nota, self.nota = True, ''
        elif self.nota is not None and not self.em_nota:
            self.depois_da_nota = True
        if tag in ('p', 'h1', 'h2', 'h3', 'li', 'td', 'th', 'div'):
            self._fecha()

    def handle_endtag(self, tag):
        if tag == 'aside':
            self.em_nota = False
        if tag in ('p', 'h1', 'h2', 'h3', 'li', 'td', 'th', 'div'):
            self._fecha()

    def handle_data(self, data):
        if self.em_nota:
            self.nota += data
        else:
            if self.nota is not None and data.strip():
                self.depois_da_nota = True
            self.atual.append(data)

    def _fecha(self):
        t = ' '.join(''.join(self.atual).split())
        if t:
            self.blocos.append(t)
        self.atual = []


def confere(deck, ws):
    deck, ws = pathlib.Path(deck), pathlib.Path(ws)
    erros, total = [], 0.0
    ws_txt = (ws / 'tools/ws/ws').read_text(encoding='utf-8')
    m = re.search(r'uso: ws <([a-z|]+)>', ws_txt)
    cmds = set(m.group(1).split('|')) if m else set()
    camada2 = (ws / 'docs/harness/2-quando-da-errado.md').read_text(encoding='utf-8')
    order = json.loads((deck / 'project/deck.json').read_text(encoding='utf-8')).get('order', [])
    for f in sorted((deck / 'project/slides').glob('*.html')):
        if f.stem not in order:
            erros.append(f'{f.stem}: fora do order')
    for sid in order:
        f = deck / f'project/slides/{sid}.html'
        if not f.exists():
            erros.append(f'{sid}: arquivo ausente')
            continue
        bruto = f.read_text(encoding='utf-8')
        lr = Leitor()
        lr.feed(bruto)
        lr._fecha()
        if len(lr.secoes) != 1:
            erros.append(f'{sid}: seções: {len(lr.secoes)}')
        elif lr.secoes[0] != sid:
            erros.append(f'{sid}: id da seção é {lr.secoes[0]}')
        for tag, _ in lr.tags:
            if tag in PROIBIDAS:
                erros.append(f'{sid}: tag <{tag}>')
        if len(lr.tags) > 200:
            erros.append(f'{sid}: {len(lr.tags)} elementos')
        for tam in FONTE.findall(bruto):
            if float(tam) < 24:
                erros.append(f'{sid}: fonte {tam}px')
        if 'data:' in bruto:
            erros.append(f'{sid}: data: URI')
        if lr.nota is None or lr.depois_da_nota or not re.search(r'</aside>\s*</section>\s*$', bruto):
            erros.append(f'{sid}: nota ausente ou não é o último filho')
        else:
            if len(lr.nota) > 4000:
                erros.append(f'{sid}: nota com {len(lr.nota)} caracteres')
            t = TEMPO.search(lr.nota)
            if t:
                total += float(t.group(1).replace(',', '.'))
            else:
                erros.append(f'{sid}: tempo ausente na nota')
        texto = '\n'.join(lr.blocos)
        tudo = texto + '\n' + (lr.nota or '')
        for nome in SKILL.findall(texto):
            if not (ws / '.claude/skills' / nome / 'SKILL.md').exists():
                erros.append(f'{sid}: skill /{nome}')
        for sub in WS.findall(tudo):
            if sub not in cmds:
                erros.append(f'{sid}: ws {sub}')
        for c in CAMINHO.findall(texto):
            c = c.rstrip('.')
            if not GENERICO.search(c) and not (ws / c.rstrip('/')).exists():
                erros.append(f'{sid}: caminho {c}')
        for b in lr.blocos:
            if b.startswith('ws: ') and b not in camada2:
                erros.append(f'{sid}: mensagem fora da camada 2: {b}')
        if SEGREDO.search(tudo):
            erros.append(f'{sid}: segredo ou credencial')
        if sid == FICTICIO and 'fictíci' not in texto.lower():
            erros.append(f'{sid}: sem a marca de fictício')
    if not JANELA[0] <= total <= JANELA[1]:
        erros.append(f'deck: tempo total {total:g} min fora de {JANELA[0]}-{JANELA[1]}')
    return erros, len(order), total


def main(argv):
    sys.stdout.reconfigure(encoding='utf-8')
    erros, n, t = confere(argv[1], argv[2])
    for e in erros:
        print(e)
    if not erros:
        print(f'ok: {n} slide(s), {t:g} min')
    return 1 if erros else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Rodar e ver passar**

Run: `cd C:/src/00-harness_big_brown_field/docs/discovery/sp4-apresentacao && python -m unittest test_confere_deck -v`
Expected: `Ran 19 tests` … `OK`.

Sem commit: a pasta não é repo git.

---

### Task 2: deck criado, índice e abertura (slides 1 a 4)

**Files:**
- Create: `deck/project/deck.json`, `deck/project/slides/{capa,hoje,antes-depois,pecas}.html`, `deck/url.txt`

**Interfaces:**
- Consumes: `confere_deck.py` (Task 1); layouts e direção visual deste plano.
- Produces: o Artifact (link em `deck/url.txt`); o `order` completo com os 21 ids.

- [ ] **Step 1: Criar o Artifact**

Artifact `publish` com `type_url` `https://claude.ai/artifact/8jTsAFQMFDb2oA8MsPJ2eL`, `title` `Harness WMS`, `auto_open` `after_first_write`, sem arquivos. Gravar o `url` da resposta em `deck/url.txt`. Ler o `SKILL.md` que a resposta traz e seguir o que divergir deste plano (ledger: Ruling).

- [ ] **Step 2: Escrever o `deck.json`**

```json
{"v":4,"createdOnFiles":{"v":1,"at":"<agora, ISO 8601 UTC>"},"lists":"css","title":"Harness WMS",
 "order":["capa","hoje","antes-depois","pecas","exemplo","passo-1","passo-2","passo-3","passo-4","passo-5","passo-6","passo-7","passo-8-9","resumo","ja-conhece","regras","erros","atlas","impacto","onde","proximos"],
 "sections":{"s1":{"description":"Por que o harness existe e o que ele é","start":"capa"},
             "s2":{"description":"Uma feature fictícia passando pelos 9 passos do fluxo básico","start":"exemplo"},
             "s3":{"description":"Quando dá errado e o Atlas","start":"erros"},
             "s4":{"description":"Onde está cada coisa e próximos passos","start":"onde"}},
 "cover":"capa",
 "faces":{"ibm-plex-sans":{"family":"IBM Plex Sans","href":"https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&display=swap"},
          "ibm-plex-mono":{"family":"IBM Plex Mono","href":"https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap"}},
 "designSystems":[]}
```

- [ ] **Step 3: Escrever os slides 1 a 4**

- **`capa`**, L-capa. Rótulo: `EQUIPE WMS`. Título: `Harness WMS`. Subtítulo: `Como fazer uma feature com o agente`. Rodapé: `Outubro de 2026`.
  Nota: `Abertura. O objetivo de hoje é entender por que o harness existe, como é o fluxo de uma feature e onde procurar ajuda. Não é uma aula prática: o uso vem com a documentação, começando pelo README do workspace. Tempo: 1 min`
- **`hoje`**, L-cartoes. Título: `Hoje`. Cartões:
  1. `17 repos` / `Cada um no seu clone, com a sua branch e o seu PR.`
  2. `Conhecimento espalhado` / `Quem toca esta tabela? A resposta está em vários repos ou na cabeça de alguém.`
  3. `Agente sem contexto` / `Cada conversa começa do zero, sem saber como os sistemas se ligam.`
  Rodapé `Harness WMS · 2/21`. Nota: `Contexto de hoje: uma feature do WMS costuma tocar mais de um repo. Descobrir o impacto e coordenar branches e PRs dá trabalho, e o agente, sem contexto, repete as mesmas perguntas. Tempo: 2 min`
- **`antes-depois`**, L-tabela. Título: `Antes e depois`. Cabeçalhos: `Tarefa`, `Antes`, `Com o harness`. Linhas:
  1. `Entender o impacto` / `Procurar em vários repos e perguntar` / `O Atlas mostra quem é afetado`
  2. `Abrir a branch` / `Clonar e criar a branch em cada repo` / `<span mono>/speckit-specify</span> cria uma branch no workspace`
  3. `Enviar e abrir PRs` / `Push repo a repo` / `<span mono>/speckit-ws-commit-push</span> envia para cada repo alterado`
  Rodapé `Harness WMS · 3/21`. Nota: `Três cenas do dia a dia. Impacto: o Atlas responde quem lê ou grava uma tabela, uma proc, um endpoint ou uma fila. Branch: o /speckit-specify cria a branch no workspace, que reúne todos os repos. Envio: o /speckit-ws-commit-push faz o commit e envia a branch para cada repo que mudou; os PRs seguem o fluxo normal de cada time. Tempo: 2,5 min`
- **`pecas`**, L-cartoes. Título: `Três peças`. Cartões:
  1. `Workspace` / `Os repos juntos, cada um em <span mono>repos/&lt;repo&gt;/</span>, com o harness na raiz.`
  2. `Spec Kit` / `A feature começa e termina por ele: branch, spec, plano, tarefas e envio.`
  3. `Atlas` / `A memória dos sistemas: o mapa entre os repos, os docs e o impacto.`
  Rodapé `Harness WMS · 4/21`. Nota: `As três peças, nas palavras do README. Workspace: os repos do Azure DevOps num só lugar; a raiz é o harness, o ferramental para desenvolver com IA. Spec Kit: o fluxo da feature. Atlas: o mapa entre os repos, os docs de cada um e o impacto de mudar uma tabela, uma proc, um endpoint ou uma fila. Tempo: 2 min`

- [ ] **Step 4: Rodar o verificador**

Run: `cd C:/src/00-harness_big_brown_field/docs/discovery/sp4-apresentacao && python confere_deck.py deck C:/src/wms-workspace`
Expected: só linhas `<id>: arquivo ausente` dos 17 slides ainda não escritos e `deck: tempo total 7.5 min fora de 35-40`. Nenhuma outra violação nos 4 slides escritos.

- [ ] **Step 5: Publicar**

Artifact `publish` com `url` de `deck/url.txt`, `root` `C:/src/00-harness_big_brown_field/docs/discovery/sp4-apresentacao/deck`, `file_path` `…/deck/project/deck.json`, `files` com as 4 slides (`"project/slides/<id>.html":"project/slides/<id>.html"`). Os slides ausentes do `order` não aparecem até existirem.

---

### Task 3: a jornada (slides 5 a 16)

**Files:**
- Create: `deck/project/slides/{exemplo,passo-1,passo-2,passo-3,passo-4,passo-5,passo-6,passo-7,passo-8-9,resumo,ja-conhece,regras}.html`

**Interfaces:**
- Consumes: o Artifact e o `order` da Task 2.

- [ ] **Step 1: Escrever os slides**

- **`exemplo`**, L-declaracao. Rótulo: `EXEMPLO FICTÍCIO`. Frase: `“Não deixar reservar um endereço de picking enquanto houver inventário aberto nele.”` Apoio: `Toca dois repos: o backend do servidor e o app. Vamos acompanhar essa feature pelos 9 passos.` Rodapé `Harness WMS · 5/21`.
  Nota: `A feature é inventada para ilustrar o fluxo; não é uma demanda real e os nomes não correspondem a tabelas ou endpoints de verdade. O importante é que ela toca mais de um repo, que é onde o harness mais ajuda. Tempo: 1,5 min`
- **`passo-1`**, L-passo, n `1`, comando `/speckit-specify &lt;descrição&gt;`. Itens:
  1. `O hook cria a branch com <span mono>ws start</span>, depois de sincronizar o <span mono>main</span> de cada repo.`
  2. `O Atlas é atualizado nos repos que mudaram.`
  3. `A spec nasce em <span mono>specs/ws-NNN-&lt;nome&gt;/</span>.`
  Você vê: `A spec em linguagem de negócio, para revisar.` Rodapé `Harness WMS · 6/21`.
  Nota: `Você descreve a feature como pediria a um colega. O hook do Spec Kit faz o resto: sincroniza o workspace, cria a branch e atualiza o Atlas. Não crie a branch nem a pasta da spec à mão. Se o hook parar, nenhuma spec é criada: a camada 2 explica cada erro desta etapa. Tempo: 2 min`
- **`passo-2`**, L-passo, n `2`, comando `/speckit-clarify`. Itens:
  1. `Só quando o agente disser que a spec tem dúvidas.`
  2. `Suas respostas entram na spec.`
  Você vê: `As perguntas do agente sobre o que ficou ambíguo.` Rodapé `Harness WMS · 7/21`.
  Nota: `Passo opcional. No exemplo, uma dúvida possível: o bloqueio vale para qualquer inventário ou só para o inventário daquele endereço? Responder agora evita retrabalho no código. Tempo: 1 min`
- **`passo-3`**, L-passo, n `3`, comando `/speckit-plan`. Itens:
  1. `O plano técnico, com os repos que a feature toca.`
  2. `O agente consulta o Atlas para medir o impacto.`
  3. `O plano é conferido contra a constitution.`
  Você vê: `Quais repos mudam e por quê.` Rodapé `Harness WMS · 8/21`.
  Nota: `Aqui o agente usa o Atlas sozinho para saber quem lê ou grava o que a feature mexe. No exemplo, o plano diria que mudam o backend do servidor e o app. Revise o plano: é mais barato corrigir aqui do que no código. Tempo: 1,5 min`
- **`passo-4`**, L-passo, n `4`, comando `/speckit-tasks`. Itens:
  1. `A lista de tarefas, cada uma marcada com o repo.`
  2. `O marcador é <span mono>[repos/&lt;repo&gt;]</span> ou <span mono>[workspace]</span>.`
  Você vê: `O trabalho quebrado por repo, na ordem de execução.` Rodapé `Harness WMS · 9/21`.
  Nota: `O marcador por repo é o que permite ao envio saber para onde vai cada mudança. Tempo: 1 min`
- **`passo-5`**, L-passo, n `5`, comando `/speckit-analyze`. Itens:
  1. `Confere a consistência entre a spec, o plano e as tarefas.`
  Você vê: `O que está faltando ou contraditório, antes de escrever código.` Rodapé `Harness WMS · 10/21`.
  Nota: `Um conferente antes do código: requisito sem tarefa, tarefa sem requisito, termos diferentes para a mesma coisa. Tempo: 1 min`
- **`passo-6`**, L-passo, n `6`, comando `/speckit-implement`. Itens:
  1. `O agente implementa as tarefas.`
  2. `Você acompanha e revisa como revisaria o código de um colega.`
  Você vê: `As tarefas sendo concluídas, repo por repo.` Rodapé `Harness WMS · 11/21`.
  Nota: `Durante a feature, não altere o harness: tools, .specify, .claude e AGENTS.md. Achou um problema nele? Registre para o time do harness. Tempo: 2 min`
- **`passo-7`**, L-passo, n `7`, comando `/speckit-converge`. Itens:
  1. `Confere o código contra a spec.`
  2. `Faltou algo? Acrescenta tarefas, e você volta ao passo 6.`
  3. `Nada falta: atualiza o Atlas dos repos tocados e oferece o commit e o envio.`
  Você vê: `O que falta, ou a pergunta se pode fazer o commit e enviar.` Rodapé `Harness WMS · 12/21`.
  Nota: `O converge fecha o ciclo: ele não deixa a spec e o código divergirem, e mantém o Atlas em dia com o que a feature mudou. Tempo: 2 min`
- **`passo-8-9`**, L-passo, n `8·9`, comando `/speckit-ws-commit-push` (2 linhas no layout; por isso 2 itens). Itens:
  1. `Mostra os arquivos e a mensagem, pede confirmação, faz o commit e envia a branch para cada repo alterado.`
  2. `Abra um PR por repo; com todos mergeados, o PR do workspace para o <span mono>main</span>.`
  Você vê: `A branch da feature em cada repo do Azure DevOps.` Rodapé `Harness WMS · 13/21`.
  Nota: `Passo 8: responda que sim no fim do converge, ou rode o /speckit-ws-commit-push depois. Passo 9: os PRs dos repos seguem o fluxo normal de cada time. O PR do workspace só entra depois de todos os PRs dos repos mergeados. Tempo: 2 min`
- **`resumo`**, fundo tinta, título + trilha. Marcação:
  ```html
  <section id="resumo" data-transition="fade" style="background:#1d2433;color:#f6f4ef;font-family:'IBM Plex Sans', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:column;justify-content:center;gap:64px">
  <h2 style="font-size:72px;font-weight:700;line-height:1.1">Os 9 passos</h2>
  <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:24px">
  <div style="background:#2a3346;border-radius:16px;padding:28px 32px;display:flex;flex-direction:column;gap:8px"><p style="font-size:24px;color:#e8846f;font-weight:700">1</p><p style="font-family:'IBM Plex Mono', Consolas, monospace;font-size:32px">/speckit-specify</p></div>
  {… mesma marcação para: 2 /speckit-clarify (com <p style="font-size:24px;color:#c9c4b8">se houver dúvidas</p>), 3 /speckit-plan, 4 /speckit-tasks, 5 /speckit-analyze, 6 /speckit-implement, 7 /speckit-converge, 8 /speckit-ws-commit-push, 9 PRs (texto "PRs nos repos e no workspace", sem fonte mono)}
  </div>
  <p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:#c9c4b8">Harness WMS · 14/21</p>
  <aside>…</aside>
  </section>
  ```
  `/speckit-ws-commit-push` tem 23 caracteres mono a 32px ≈ 442px, cabe na coluna (≈ 539px úteis). Nota: `O fluxo inteiro numa tela. Rode um comando de cada vez e leia o que ele devolve antes de seguir. Tempo: 1 min`
- **`ja-conhece`**, L-lista. Título: `Já conhece o Spec Kit?` Itens:
  1. `A branch é criada pelo hook, com <span mono>ws start</span>. Não crie a branch nem a pasta da spec à mão.`
  2. `As specs ficam em <span mono>specs/ws-NNN-&lt;nome&gt;/</span>, na raiz do workspace, nunca dentro de <span mono>repos/</span>.`
  3. `As tarefas levam o marcador <span mono>[repos/&lt;repo&gt;]</span> ou <span mono>[workspace]</span>.`
  4. `O <span mono>converge</span> atualiza o Atlas e oferece o commit e o envio aos repos.`
  Rodapé `Harness WMS · 15/21`. Nota: `Para quem já usou o Spec Kit em outro projeto, estas são as quatro diferenças daqui. O resto funciona como o Spec Kit padrão. Tempo: 1,5 min`
- **`regras`**, L-lista. Título: `Três regras que não se quebram` Itens:
  1. `Nunca rode <span mono>git push</span> para os repos nem <span mono>git subtree</span> à mão: quem envia é o <span mono>ws push</span>.`
  2. `Dentro de <span mono>repos/&lt;repo&gt;/</span>, não crie nem altere <span mono>.specify/</span>, <span mono>specs/</span> e <span mono>.claude/skills/speckit-*</span>.`
  3. `Durante uma feature, não altere o harness. Achou um problema nele? Registre para o time do harness.`
  Rodapé `Harness WMS · 16/21`. Nota: `As regras vêm da camada 1. A primeira: o envio passa pelo ws push, que sabe separar as mudanças de cada repo. A segunda: esses arquivos são do time dono do repo, e o ws push recusa a branch se eles mudarem. A terceira: o harness é tools, .specify, .claude e AGENTS.md; mudanças nele vão numa branch própria. Tempo: 1,5 min`

- [ ] **Step 2: Rodar o verificador**

Run: `cd C:/src/00-harness_big_brown_field/docs/discovery/sp4-apresentacao && python confere_deck.py deck C:/src/wms-workspace`
Expected: só `arquivo ausente` dos 5 slides da Task 4 e `deck: tempo total 25.5 min fora de 35-40`.

- [ ] **Step 3: Publicar**, em 4 chamadas de 3 slides, na ordem do `order`, com `url`, `root` e `files` como na Task 2 (`file_path` = o primeiro dos três, `files` = os outros dois).

---

### Task 4: quando dá errado, Atlas e fechamento (slides 17 a 21)

**Files:**
- Create: `deck/project/slides/{erros,atlas,impacto,onde,proximos}.html`

- [ ] **Step 1: Escrever os slides**

- **`erros`**, papel, título + legenda + 3 linhas mensagem/ação. Marcação:
  ```html
  <section id="erros" data-transition="fade" style="background:#f6f4ef;color:#1d2433;font-family:'IBM Plex Sans', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:column;gap:40px">
  <h2 style="font-size:72px;font-weight:700;line-height:1.1">Quando dá errado</h2>
  <p style="font-size:32px;line-height:1.4">A camada 2 é organizada por etapa. Procure pela mensagem: <span mono>ws: erro:</span> o comando parou; <span mono>ws: aviso:</span> ele seguiu, mas avisa.</p>
  <div style="display:flex;flex-direction:column;gap:20px">
  <div style="background:#ffffff;border:1px solid #d9d4c8;border-radius:16px;padding:24px 32px;display:flex;flex-direction:column;gap:8px">
  <p style="font-family:'IBM Plex Mono', Consolas, monospace;font-size:24px;color:#b5452f">{mensagem}</p>
  <p style="font-size:28px">{o que fazer}</p>
  </div>
  {… mais dois cartões iguais}
  </div>
  <p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:#5a6170">Harness WMS · 17/21</p>
  <aside>…</aside>
  </section>
  ```
  Os `<span mono>` da legenda ficam dentro do `<p>`, então o bloco não começa com `ws: ` e não é conferido como mensagem; as mensagens dos cartões são `<p>` próprios e são conferidas. Cartões (mensagem literal da camada 2, ação resumida da mesma entrada):
  1. `ws: erro: há mudanças não commitadas; faça commit ou stash antes` / `Faça commit, guarde (git stash) ou descarte, e rode o mesmo /speckit-specify de novo.`
  2. `ws: erro: ws-commit-push não roda no &lt;main&gt;; use a branch da feature` / `Volte para a branch da feature (git switch &lt;branch&gt;) e rode de novo.`
  3. `ws: aviso: o mapeamento falhou em &lt;repos&gt;; esses repos continuam pendentes` / `Siga com a feature: ele é tentado de novo no próximo /speckit-specify.`
  Orçamento: título 79 + legenda 2×45 + 3 cartões (24×1,4 + 28×1,4×1 + 8 + 48 ≈ 128) + gaps 40×2 + 20×2 ≈ 674 ≤ 792. A mensagem mais longa (77 caracteres mono a 24px ≈ 1109px) cabe numa linha do cartão (1600px úteis).
  Nota: `Três exemplos reais, copiados da camada 2. Cada entrada de lá traz sintoma, causa e o que fazer. Quando o erro vem por um hook do Spec Kit, o agente mostra a mesma mensagem dentro da resposta dele. Se nada resolver, a última seção da camada 2 diz o que mandar na thread do time. Tempo: 3 min`
- **`atlas`**, L-cartoes. Título: `O Atlas`. Cartões:
  1. `O que sabe` / `O que cada repo faz, as regras, as integrações e quem toca cada objeto.`
  2. `Quem atualiza` / `O <span mono>/speckit-specify</span>, nos repos que mudaram, e o <span mono>/speckit-converge</span>, nos repos da feature.`
  3. `E você?` / `Quase nunca mexe. Pergunte ao agente ou use <span mono>/atlas-consultar</span>.`
  Rodapé `Harness WMS · 18/21`. Nota: `O Atlas fica em docs/atlas, no workspace. Ele se atualiza sozinho dentro do fluxo. Atualizar à mão é raro e está na camada 3; os comandos ws atlas são só para diagnóstico. Com as ferramentas do Atlas instaladas (camada 3, mapas de código), o agente navega o código com mais eficiência. Tempo: 2,5 min`
- **`impacto`**, papel, título + bloco de código + explicação:
  ```html
  <section id="impacto" data-transition="fade" style="background:#f6f4ef;color:#1d2433;font-family:'IBM Plex Sans', Arial, sans-serif;padding:128px 128px 160px;display:flex;flex-direction:column;gap:40px">
  <h2 style="font-size:72px;font-weight:700;line-height:1.1">Quem toca esta tabela?</h2>
  <div style="background:#1d2433;color:#f6f4ef;border-radius:16px;padding:40px 48px;display:flex;flex-direction:column;gap:12px;font-family:'IBM Plex Mono', Consolas, monospace">
  <p style="font-size:24px;color:#e8846f">docs/atlas/impacto · Audit.DBO.ADT_CAIXA</p>
  <p style="font-size:28px">### banco WMS</p>
  <p style="font-size:28px">- WMS.dbo.tr_CAIXA_Insert (trigger) — distância 1</p>
  <p style="font-size:28px">### industria-logistica.wms.servidor.backend</p>
  <p style="font-size:28px">- servidor.backend (código) — distância 2, via a trigger; db-write em WMS.dbo.Caixa</p>
  </div>
  <p style="font-size:32px;line-height:1.4">O código grava em <span mono>WMS.dbo.Caixa</span>; a trigger dessa tabela grava no Audit. Mudar a tabela do Audit afeta quem grava em <span mono>Caixa</span>.</p>
  <p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:#5a6170">Harness WMS · 19/21</p>
  <aside>…</aside>
  </section>
  ```
  O rótulo `docs/atlas/impacto` é conferido como caminho (existe). A última linha do código tem 84 caracteres mono a 28px ≈ 1411px, cabe em 1568px úteis. Nota: `Exemplo real, o mesmo da camada 3. Cada página de impacto diz quem é afetado, a distância e por onde o impacto chega. Código e jobs são as pontas. Só ganha página o objeto que algum repo ou job do WMS alcança. Para achar a página, procure o objeto em docs/atlas/impacto/indice.csv, ou pergunte ao agente: quem é afetado se eu mudar a tabela WMS.dbo.Caixa? Tempo: 2,5 min`
- **`onde`**, L-tabela. Título: `Onde está cada coisa`. Cabeçalhos: `Quero…`, `Leia`. Linhas (do README):
  1. `começar e fazer minha primeira feature` / `1. Começar`
  2. `resolver um erro` / `2. Quando dá errado`
  3. `fazer algo além do básico` / `3. Além do básico`
  4. `mudar ou manter o harness` / `4. Manter o harness`
  Abaixo da tabela: `<p style="font-size:32px">Tudo parte do <span mono>README.md</span> do workspace. Dúvidas: thread no espaço <b>Equipe WMS</b> do Google Chat.</p>` (o orçamento: título 79 + tabela 5 linhas × 2,1 × 32 ≈ 336 + 45 + gaps 112 ≈ 572). Rodapé `Harness WMS · 20/21`.
  Nota: `A documentação fica em docs/harness no workspace, em quatro camadas. Quem só quer usar o fluxo lê a 1; a 2 é para quando algo trava; a 3 e a 4 são para quem vai além. O link da thread está na última seção da camada 2. Tempo: 1,5 min`
- **`proximos`**, L-declaracao. Rótulo: `PRÓXIMOS PASSOS`. Frase: `Comece pelo README do workspace.` Apoio: `Um piloto: o primeiro dev segue a camada 1 na feature real dele, e cada travada vira correção na doc. Perguntas?` Rodapé `Harness WMS · 21/21`.
  Nota: `Encerramento. O piloto valida a doc com alguém que nunca usou o harness. Depois, abra para perguntas no tempo que sobrar. Tempo: 1 min`

- [ ] **Step 2: Rodar o verificador**

Run: `cd C:/src/00-harness_big_brown_field/docs/discovery/sp4-apresentacao && python confere_deck.py deck C:/src/wms-workspace`
Expected: `ok: 21 slide(s), 36 min`.

- [ ] **Step 3: Publicar** os 5 slides (2 chamadas: 3 + 2), como na Task 3.

---

### Task 5: conferência final e entrega

- [ ] **Step 1: Conferência de conteúdo contra a doc**, slide a slide, lendo `README.md` e `docs/harness/1-comecar.md`, `2-quando-da-errado.md` e `3-alem-do-basico.md` do `main`: cada frase do deck está dita na doc (ou é a feature fictícia). Divergência encontrada: corrigir o slide, rodar o verificador e republicar só ele.
- [ ] **Step 2: Verificador e testes**

Run: `cd C:/src/00-harness_big_brown_field/docs/discovery/sp4-apresentacao && python -m unittest test_confere_deck && python confere_deck.py deck C:/src/wms-workspace`
Expected: `OK` e `ok: 21 slide(s), 36 min`.
- [ ] **Step 3: Registrar** o link em `docs/discovery/estado-da-sessao.md` (item SP4) e passar o link ao usuário.
