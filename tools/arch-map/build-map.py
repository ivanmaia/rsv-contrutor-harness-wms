"""Gera o mapa de arquitetura cross-repo a partir de docs/discovery/edges-consolidado.csv
e de docs/discovery/edges-sqlagent.csv (jobs do SQL Agent, gerado por tools/db-extract/jobs-edges.py).

Saídas em docs/discovery/arquitetura/: servico-servico.csv, objetos-compartilhados.csv,
filas.csv, nao-resolvidos.csv e mapa.mmd (Mermaid).
Uso: python tools/arch-map/build-map.py
"""
import collections
import csv
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = [ROOT / 'docs' / 'discovery' / 'edges-consolidado.csv', ROOT / 'docs' / 'discovery' / 'edges-sqlagent.csv']
OUT = ROOT / 'docs' / 'discovery' / 'arquitetura'
OUT.mkdir(parents=True, exist_ok=True)


def short(repo):
    if repo == 'sqlagent':
        return 'sqlagent (jobs do banco)'
    repo = repo.replace('industria-logistica.', '')
    return repo.replace('integracoes.core.plataforma.backoffice.frontend', 'fly.backoffice.frontend')


# alvo HTTP -> nó (repo curto ou ext:<nome>). A primeira regra que casa vence.
HTTP_RULES = [
    (r'picking.?front', 'wms.picking.frontend'),
    (r'full picking|picking\.api|wmspickingapi', 'wms.picking.backend'),
    (r'wms3|wms:endpoint|wms:baseurlwms|wmsapi:url|ip interno>:8087|^wms \(httpclient', 'wms.servidor.backend'),
    (r'ecommerce', 'wms.ecommerce.backend'),
    (r'reservanetlinxapi|reservanet-linx-api', 'wms.conector.backend'),
    (r'linxintegration', 'ext:LINX (APIs de integração)'),
    (r'(^|[^a-z])sso|netsso', 'reserva-net.autenticacao.monolito'),  # evita casar 'acesso'
    (r'printer|impressora', 'print-zebra.utilitario.backend'),
    (r'produtividade|hubapi', 'wms.hubprodutividade.backend'),
    (r'trakta', 'wms.trakta.backend'),
    (r'reservanet-b2b-api', 'reserva-net.b2b.backend'),
    (r'awx|checkout|pedidosb2b|pedidosb2c|faturamento|estoque|impressao|erpconnector|reverseproxy'
     r'|recebimento|integracaolegadowms', 'wms.awx.monorepo'),
    (r'intelipost', 'ext:Intelipost'),
    (r'sentry|new relic', 'ext:Observabilidade (Sentry/New Relic)'),
    (r'sendgrid|smtp', 'ext:E-mail (SendGrid/SMTP)'),
    (r'ldap|active directory', 'ext:Active Directory'),
    (r'logistica\.integrada', 'ext:Logistica.Integrada.BFF (Helix, fora do escopo)'),
    (r'ondemand', 'ext:OnDemand (fora do escopo)'),
    (r'reservanet-(queries|commands|tasks|aviamento)', 'ext:ReservaNet (serviços sem repo no workspace)'),
    (r'sftp', 'ext:SFTP transportadoras'),
    (r'genius|trocafacil|troquecommerce', 'ext:Canais de devolução'),
    (r'vtex', 'ext:VTEX'),
    (r'keycloak', 'ext:Keycloak'),
    (r'revopush|codepush', 'ext:Revopush'),
    (r'wkhtmltopdf|arquivo local|compartilhamento de rede', 'ext:Arquivo/processo local'),
    (r'bff intranet|acessible-api|chat-api|gcm|loyalty|prime|faccylita|api principal',
     'ext:Backends não-WMS do Fly'),
]


def resolve_http(alvo):
    a = alvo.lower()
    for pat, node in HTTP_RULES:
        if re.search(pat, a):
            return node
    return 'ext:?' + alvo.strip()[:40]


def norm_queue(alvo):
    a = alvo.lower().split(' ')[0]
    a = re.sub(r'\{?filaatividaderealizada\}?', 'wms-atividade_realizada', a)
    a = re.sub(r'\{?filasessaooperadorregistrada\}?', 'wms-sessao_operador_cluster', a)
    a = re.sub(r'-(dlq|retry.*)$', '', a)
    return re.sub(r'\.integracao-legado$', '', a)  # binding do consumidor na mesma routing key


def norm_db(alvo):
    return re.sub(r'^RESERVA\.', 'Reserva.', alvo.strip()).lower()


rows = [r for f in SRC if f.exists() for r in csv.DictReader(open(f, encoding='utf-8'))]
# Escopo: ONDEMAND fica fora do mapa, exceto objetos do banco WMS (decisão do usuário, 2026-09-24); o CSV de origem não muda.
rows = [r for r in rows if r['alvo'].startswith('WMS.') or not re.search(r'on[ _-]?demand', r['alvo'], re.I)]
pair = collections.defaultdict(lambda: {'n': 0, 'ex': []})
unresolved = []


def add(o, d, via, ex):
    p = pair[(o, d, via)]
    p['n'] += 1
    if len(p['ex']) < 3 and ex and ex not in p['ex']:
        p['ex'].append(ex)


# HTTP e outros destinos de saída
for r in rows:
    if r['tipo'] not in ('http-out', 'other-out'):
        continue
    o, d = short(r['repo']), resolve_http(r['alvo'])
    if d.startswith('ext:?'):
        unresolved.append([o, r['tipo'], r['alvo'], d])
    if d == o:
        continue  # chamada interna (ex.: jobs do WMS3 chamando a própria API)
    add(o, d, 'http' if r['tipo'] == 'http-out' else 'outro', r['detalhe'][:60])

# Filas
pubs, subs = collections.defaultdict(set), collections.defaultdict(set)
for r in rows:
    if r['tipo'] in ('mq-pub', 'mq-sub'):
        if r['tipo'] == 'mq-pub' and re.search(r'-(dlq|retry)', r['alvo'].lower()):
            continue  # republicação do próprio consumidor em DLQ/retry
        q = norm_queue(r['alvo'])
        if 'qualquer' in q or q.startswith('rabbitmq'):
            continue
        (pubs if r['tipo'] == 'mq-pub' else subs)[q].add(short(r['repo']))
queues = []
for q in sorted(set(pubs) | set(subs)):
    queues.append([q, ';'.join(sorted(pubs[q])) or '(sem publicador no workspace)',
                   ';'.join(sorted(subs[q])) or '(sem consumidor no workspace)'])
    for p in pubs[q]:
        for s in subs[q]:
            if p != s:
                add(p, s, 'fila', q)

# Banco: objetos tocados por mais de um repo
obj = collections.defaultdict(lambda: {'r': set(), 'w': set(), 'x': set(), 'nome': ''})
for r in rows:
    if not r['tipo'].startswith('db-'):
        continue
    k = norm_db(r['alvo'])
    if not re.match(r'^(wms|reserva|reservanet|wms_produtividade)\.', k):
        continue  # bancos privados (pg-*, chaves de config) não são compartilhados
    obj[k]['nome'] = obj[k]['nome'] or r['alvo'].strip()
    obj[k][{'db-read': 'r', 'db-write': 'w', 'db-exec': 'x'}[r['tipo']]].add(short(r['repo']))
shared = []
for v in obj.values():
    repos = v['r'] | v['w'] | v['x']
    if len(repos) < 2:
        continue
    shared.append([v['nome'], len(repos), ';'.join(sorted(v['w'])), ';'.join(sorted(v['r'])),
                   ';'.join(sorted(v['x']))])
    for wr in v['w']:
        for rd in (v['r'] | v['x']) - {wr}:
            add(wr, rd, 'banco', v['nome'])
shared.sort(key=lambda s: (-s[1], s[0].lower()))

# Repo -> banco (para o diagrama)
DBS = {'wms': 'WMS', 'reserva': 'Reserva', 'reservanet': 'ReservaNet', 'wms_produtividade': 'WMS_Produtividade'}
repo_db = collections.Counter()
for r in rows:
    if r['tipo'].startswith('db-'):
        k = norm_db(r['alvo']).split('.')[0]
        db = DBS.get(k) or ('Postgres privado' if k.startswith('pg-') or 'postgres' in k else None)
        if db:
            repo_db[(short(r['repo']), 'db:' + db, 'R' if r['tipo'] == 'db-read' else 'W')] += 1


def write(name, header, data):
    with open(OUT / name, 'w', encoding='utf-8', newline='') as h:
        c = csv.writer(h)
        c.writerow(header)
        c.writerows(data)


write('servico-servico.csv', ['origem', 'destino', 'via', 'n_arestas', 'exemplos'],
      sorted([[o, d, t, p['n'], ' | '.join(p['ex'])] for (o, d, t), p in pair.items()],
             key=lambda x: (x[0], x[2], -x[3])))
write('objetos-compartilhados.csv', ['objeto', 'n_repos', 'escritores', 'leitores', 'executores'], shared)
write('filas.csv', ['fila', 'publicadores', 'consumidores'], queues)
write('nao-resolvidos.csv', ['repo', 'tipo', 'alvo', 'no_atribuido'], unresolved)

# Mermaid: repos do workspace + bancos compartilhados; externos ficam nas tabelas
ids = {}


def nid(n):
    return ids.setdefault(n, 'n%d' % len(ids))


edges = collections.Counter()
for (o, d, t), p in pair.items():
    if t in ('http', 'fila') and not d.startswith('ext:'):
        edges[(o, d, t)] += p['n']
for (rp, db, m), n in repo_db.items():
    edges[(rp, db, 'db-' + m)] += n
lines = ['flowchart LR']
for n in sorted({x for e in edges for x in e[:2]}):
    label = n.replace('db:', '')
    lines.append('  %s%s' % (nid(n), ('[(%s)]' if n.startswith('db:') else '[%s]') % label))
ARROW = {'http': '-->', 'fila': '-.->', 'db-R': '-->', 'db-W': '==>'}
for (o, d, t), n in sorted(edges.items()):
    lines.append('  %s %s|%s %d| %s' % (nid(o), ARROW[t], t, n, nid(d)))
(OUT / 'mapa.mmd').write_text('\n'.join(lines) + '\n', encoding='utf-8')

print('pares', len(pair), '| objetos compartilhados', len(shared), '| filas', len(queues),
      '| nao resolvidos', len(unresolved))
