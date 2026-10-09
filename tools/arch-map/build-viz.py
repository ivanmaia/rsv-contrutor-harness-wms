"""Gera a página interativa do grafo de arquitetura a partir dos CSVs de docs/discovery/arquitetura/.

Rodar depois de build-map.py:  python tools/arch-map/build-viz.py
Saída: docs/discovery/arquitetura/grafo.html (HTML único; dados embutidos, d3 via cdnjs).
"""
import collections
import csv
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
ARQ = ROOT / 'docs' / 'discovery' / 'arquitetura'
EDGE_FILES = [ROOT / 'docs' / 'discovery' / 'edges-consolidado.csv', ROOT / 'docs' / 'discovery' / 'edges-sqlagent.csv']
TEMPLATE = pathlib.Path(__file__).with_name('grafo-template.html')
OUT = ARQ / 'grafo.html'

GROUPS = {
    'front': {'wms.app.frontend', 'wms.ecommerce.frontend', 'wms.picking.frontend', 'fly.backoffice.frontend'},
    'nova': {'wms.awx.monorepo', 'wms.hubprodutividade.backend', 'wms.trakta.backend'},
    'jobs': {'sqlagent (jobs do banco)'},
}
DBS = {'wms': 'WMS', 'reserva': 'Reserva', 'reservanet': 'ReservaNet', 'wms_produtividade': 'WMS_Produtividade'}
ONDEMAND = re.compile(r'on[ _-]?demand', re.I)


def read(p):
    with open(p, encoding='utf-8-sig') as h:
        return list(csv.DictReader(h))


def short(repo):
    if repo == 'sqlagent':
        return 'sqlagent (jobs do banco)'
    repo = repo.replace('industria-logistica.', '')
    return repo.replace('integracoes.core.plataforma.backoffice.frontend', 'fly.backoffice.frontend')


def group(n):
    if n.startswith('db:'):
        return 'db'
    if n.startswith('ext:'):
        return 'ext'
    for g, members in GROUPS.items():
        if n in members:
            return g
    return 'legado'


def label(n):
    if n == 'sqlagent (jobs do banco)':
        return 'SQL Agent (jobs)'
    n = re.sub(r'^(db|ext):', '', n)
    return re.sub(r'^(wms|reserva-net)\.', '', n)


nodes, links = {}, []


def node(n):
    if n not in nodes:
        nodes[n] = {'id': n, 'label': label(n), 'group': group(n)}
    return n


for r in read(ARQ / 'servico-servico.csv'):
    via = r['via']
    links.append({'source': node(r['origem']), 'target': node(r['destino']),
                  'via': 'objeto' if via == 'banco' else ('http' if via in ('http', 'outro') else via),
                  'n': int(r['n_arestas']), 'ex': r['exemplos']})

# repo -> banco (leitura/escrita), com o mesmo filtro de escopo do build-map
acc = collections.Counter()
for f in EDGE_FILES:
    for r in read(f):
        if not r['tipo'].startswith('db-'):
            continue
        if not r['alvo'].startswith('WMS.') and ONDEMAND.search(r['alvo']):
            continue
        k = re.sub(r'^RESERVA\.', 'Reserva.', r['alvo'].strip()).lower().split('.')[0]
        db = DBS.get(k) or ('Postgres (um por serviço)' if k.startswith('pg-') or 'postgres' in k else None)
        if db:
            acc[(short(r['repo']), 'db:' + db, 'escrita' if r['tipo'] == 'db-write' else 'leitura')] += 1
for (rp, db, modo), n in acc.items():
    links.append({'source': node(rp), 'target': node(db), 'via': 'banco', 'modo': modo, 'n': n, 'ex': ''})

objetos = [{'o': r['objeto'], 'w': [x for x in r['escritores'].split(';') if x],
            'r': [x for x in r['leitores'].split(';') if x], 'x': [x for x in r['executores'].split(';') if x]}
           for r in read(ARQ / 'objetos-compartilhados.csv')]
filas = [{'f': r['fila'], 'p': r['publicadores'], 'c': r['consumidores']} for r in read(ARQ / 'filas.csv')]

# jobs do SQL Agent que escrevem objetos usados pelos repos
users = collections.defaultdict(set)
for r in read(EDGE_FILES[0]):
    if r['tipo'].startswith('db-') and (r['alvo'].startswith('WMS.') or not ONDEMAND.search(r['alvo'])):
        users[r['alvo'].strip().lower()].add(short(r['repo']))
agenda = {j['job']: (j['habilitado'], j['agenda']) for j in read(ARQ / 'jobs-sqlagent.csv')}
jobs = collections.defaultdict(lambda: {'objs': set(), 'repos': set()})
for r in read(EDGE_FILES[1]):
    if r['tipo'] != 'db-write' or not users[r['alvo'].lower()]:
        continue
    j = re.match(r'job "(.*)" passo', r['detalhe']).group(1)
    jobs[j]['objs'].add(r['alvo'])
    jobs[j]['repos'] |= users[r['alvo'].lower()]
job_list = sorted(({'job': j, 'on': agenda.get(j, ('?', ''))[0] == '1', 'agenda': agenda.get(j, ('', ''))[1],
                    'objs': sorted(v['objs']), 'wms': any(o.startswith('WMS.') for o in v['objs']),
                    'repos': sorted(label(x) for x in v['repos'])} for j, v in jobs.items()),
                  key=lambda x: (not x['wms'], x['job'].lower()))

data = {'nodes': list(nodes.values()), 'links': links, 'objetos': objetos, 'filas': filas, 'jobs': job_list}
html = TEMPLATE.read_text(encoding='utf-8').replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False))
OUT.write_text(html, encoding='utf-8')
print('nós', len(nodes), '| ligações', len(links), '| objetos', len(objetos), '| jobs', len(job_list), '->', OUT)
