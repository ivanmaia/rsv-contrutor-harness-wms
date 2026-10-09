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
