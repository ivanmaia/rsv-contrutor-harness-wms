"""Escopo do levantamento de banco: quais objetos e procs de produção entram no mapa.

Regras (decididas pelo usuário em 2026-09-24):
- ONDEMAND está fora: todo objeto ou job cujo banco, schema ou nome case com /on[ _-]?demand/i
  sai e não serve de caminho para outros objetos. Exceção: objetos do banco WMS ficam.
- Alvo = objetos da família WMS (bancos WMS, WMSTASKS, WMS_Produtividade) + objetos que os repos
  citam (arestas db-* de docs/discovery/edges-consolidado.csv) + o objeto base desses que são sinônimos.
- Procs (filtro apertado pelo usuário no mesmo dia):
  - do banco WMS (família) ou do ReservaNet: ficam;
  - chamadas diretamente pelos repos: ficam (ponto de integração);
  - chamadas diretamente por uma proc do banco WMS (inclusive via sinônimo): ficam;
  - de qualquer outro banco (Reserva, LinxFranquia...): só ficam se alcançam, direta ou
    indiretamente, um objeto da família WMS ou do ReservaNet. Tocar só tabelas do LINX que os
    repos leem (PRODUTOS, FILIAIS...) não basta.
  "Indiretamente" = grafo de sys.sql_expression_dependencies (procs, views, funções) mais
  sinônimo → objeto base. Triggers disparados por escrita não contam como caminho.
- Tabelas e views continuam no mapa quando são alvo (família WMS ou citadas pelos repos).

Uso: python tools/db-extract/scope.py  → docs/discovery/arquitetura/procs-escopo.csv
Importável: from scope import load_scope
"""
import collections
import csv
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROD = ROOT / 'extract' / 'db-prod'
REPO_EDGES = ROOT / 'docs' / 'discovery' / 'edges-consolidado.csv'
OUT = ROOT / 'docs' / 'discovery' / 'arquitetura' / 'procs-escopo.csv'
DBS = ['WMS', 'Reserva', 'ReservaNet', 'WMSTASKS', 'WMS_Produtividade', 'Audit', 'Ecommerce',
       'LinxFranquia', 'Reserva_Integracao_Anymarket']
WMS_FAMILY = {'WMS', 'WMSTASKS', 'WMS_Produtividade'}
ANCHOR_DBS = WMS_FAMILY | {'ReservaNet'}
CANON = {d.lower(): d for d in DBS}
ONDEMAND = re.compile(r'on[ _-]?demand', re.I)


def read_csv(p):
    with open(p, encoding='utf-8-sig') as h:
        return list(csv.DictReader(h))


def key(db, schema, name):
    return (CANON.get((db or '').lower(), db or ''), (schema or 'dbo').lower(), (name or '').lower())


def is_ondemand(k):
    # No banco WMS, objetos ONDEMAND ficam no escopo (correção do usuário, 2026-09-24).
    return k[0] != 'WMS' and bool(ONDEMAND.search(' '.join(k)))


def load_scope():
    """Retorna (catalog, targets, relevant, reason).
    catalog: key -> (schema, nome, tipo); targets: tabelas/views/procs-alvo do mapa;
    relevant: procs no escopo (e views/funções que levam a WMS/ReservaNet); reason: key -> motivo."""
    catalog, graph = {}, collections.defaultdict(set)
    for db in DBS:
        for r in read_csv(PROD / db / 'objects.csv'):
            catalog[key(db, r['schema'], r['name'])] = (r['schema'], r['name'], r['type'].strip())
        for r in read_csv(PROD / db / 'dependencies.csv'):
            if r['to_server']:
                continue
            graph[key(db, r['from_schema'], r['from_name'])].add(key(r['to_db'] or db, r['to_schema'], r['to_name']))
        for r in read_csv(PROD / db / 'synonyms.csv'):
            if not r['to_server']:
                graph[key(db, r['schema'], r['name'])].add(key(r['to_db'] or db, r['to_schema'], r['to_name']))

    targets, reason = set(), {}
    for k, (_, _, t) in catalog.items():
        if k[0] in WMS_FAMILY and not is_ondemand(k):
            targets.add(k)
            reason[k] = 'objeto da família WMS'
    for r in read_csv(REPO_EDGES):
        if not r['tipo'].startswith('db-'):
            continue
        parts = r['alvo'].split(' ')[0].split('.')
        if len(parts) != 3 or parts[0].lower() not in CANON:
            continue
        k = key(*parts)
        if is_ondemand(k):
            continue
        for kk in [k, *graph.get(k, ())] if catalog.get(k, ('', '', ''))[2] == 'SN' else [k]:
            if kk not in targets:
                targets.add(kk)
                reason[kk] = 'citado pelos repos' if kk == k else f'base do sinônimo {".".join(k)}'

    repo_called = {k for k in targets if catalog.get(k, ('', '', ''))[2] == 'P' and reason.get(k) == 'citado pelos repos'}
    anchors = {k for k in catalog if k[0] in ANCHOR_DBS and not is_ondemand(k)}
    reverse = collections.defaultdict(set)
    for src, dsts in graph.items():
        if is_ondemand(src):
            continue
        for d in dsts:
            if not is_ondemand(d):
                reverse[d].add(src)
    reach = set(anchors)
    via = {}
    queue = collections.deque(anchors)
    while queue:
        cur = queue.popleft()
        for src in reverse[cur]:
            if src not in reach:
                reach.add(src)
                via[src] = cur
                queue.append(src)
    relevant = set()
    for k in reach | repo_called:
        if k[0] in ANCHOR_DBS:
            relevant.add(k)
            reason.setdefault(k, f'proc do banco {k[0]}')
            if catalog.get(k, ('', '', ''))[2] == 'P' and k not in targets:
                reason[k] = f'proc do banco {k[0]}'
        elif k in repo_called:
            relevant.add(k)
        else:
            relevant.add(k)
            hop = via[k]
            reason[k] = (f'alcança {".".join(hop)}' if hop[0] in ANCHOR_DBS else f'via {".".join(hop)}')
    for p in [k for k in catalog if k[0] == 'WMS' and catalog[k][2] == 'P']:
        for d in graph.get(p, ()):
            hops = [d, *graph.get(d, ())] if catalog.get(d, ('', '', ''))[2] == 'SN' else [d]
            for x in hops:
                if catalog.get(x, ('', '', ''))[2] == 'P' and x[0] not in ANCHOR_DBS and not is_ondemand(x)                         and x not in relevant:
                    relevant.add(x)
                    reason[x] = f'chamada pela proc do WMS {".".join(p)}'
    return catalog, targets, relevant, reason


def main():
    catalog, targets, relevant, reason = load_scope()
    rows, stats = [], collections.Counter()
    for k, (sch, nm, t) in sorted(catalog.items()):
        if t != 'P':
            continue
        if is_ondemand(k):
            status, why = 'fora', 'ONDEMAND'
        elif k in relevant:
            status, why = 'dentro', reason[k]
        else:
            status, why = 'fora', 'não alcança WMS nem ReservaNet'
        stats[(k[0], status)] += 1
        rows.append([k[0], sch, nm, status, why])
    with open(OUT, 'w', encoding='utf-8', newline='') as h:
        w = csv.writer(h)
        w.writerow(['db', 'schema', 'proc', 'escopo', 'motivo'])
        w.writerows(rows)
    for db in DBS:
        print(db, 'dentro', stats[(db, 'dentro')], 'fora', stats[(db, 'fora')])


if __name__ == '__main__':
    main()
