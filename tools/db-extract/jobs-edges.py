"""Deriva arestas de banco dos jobs do SQL Agent a partir dos extratos de produção.

Entrada: extract/db-prod/_jobs/{jobs,steps}.csv e steps/<job>/<n>.txt (extract-jobs.ps1),
         extract/db-prod/<DB>/{objects,synonyms}.csv e modules/ (extract-catalog.ps1).
Saída:   docs/discovery/edges-sqlagent.csv  (mesmo formato do edges-consolidado.csv, repo = sqlagent)
         docs/discovery/arquitetura/jobs-sqlagent.csv  (um job por linha)

Regras:
- Só passos TSQL. SSIS/CmdExec/PowerShell ficam listados em jobs-sqlagent.csv como não analisados.
- Comentários são removidos. SQL dinâmico (EXEC(@sql), sp_executesql) não é seguido.
- Nomes são resolvidos no banco do passo (1 parte = dbo) e validados contra o catálogo de produção;
  o que não existe no catálogo é descartado (aliases, temporárias, variáveis, bancos não extraídos).
- Sinônimos viram o objeto base. EXEC de proc é seguido recursivamente (até 5 níveis), então
  as leituras e escritas feitas dentro das procs contam para o job, com "via" no detalhe.
- Premissa do discovery: todo job conta como usado, inclusive desabilitados (marcados no detalhe).
- Escopo (tools/db-extract/scope.py): jobs e objetos ONDEMAND saem e não são atravessados; só ficam
  arestas para objetos-alvo (família WMS ou citados pelos repos) e EXEC de procs no escopo; procs
  fora do escopo não são atravessadas, então o que elas leem e escrevem não conta para o job.
Uso: python tools/db-extract/jobs-edges.py
"""
import csv
import pathlib
import re

from scope import is_ondemand, key as scope_key, load_scope

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROD = ROOT / 'extract' / 'db-prod'
JOBS = PROD / '_jobs'
OUT_EDGES = ROOT / 'docs' / 'discovery' / 'edges-sqlagent.csv'
OUT_JOBS = ROOT / 'docs' / 'discovery' / 'arquitetura' / 'jobs-sqlagent.csv'
DBS = ['WMS', 'Reserva', 'ReservaNet', 'WMSTASKS', 'WMS_Produtividade', 'Audit', 'Ecommerce',
       'LinxFranquia', 'Reserva_Integracao_Anymarket']
CANON = {d.lower(): d for d in DBS}
MAX_DEPTH = 5
# Jobs com passos SSIS/CmdExec/PowerShell descartados pelo usuário como não relevantes (2026-09-24).
DISCARDED_JOBS = {
    'syspolicy_purge_history', 'DBAONL - Coleta Long Running Queries', 'Manutencao_Estoque_Entradas_Ecommerce',
    'Manutencao_Faturamento', 'Manutencao_Vendas', 'RSV_WFA_INTEGRACAO_SAP', 'RSV_INTEGRACAO_DEPENDENTES',
    'RSV_INTEGRACAO_FRANQUIAS', 'RSV_Update_LDB_Franquias', 'RSV_Update_LDB_LOJAS', 'RSV_INTEGRACAO_VENDEDOR_AUXILIAR',
    'RSV_ENVIO_MAIL_RESERVADO_RUA_ATRASADO_SUPERVISOR_2022',
}

ID = r'(?:\[[^\]]+\]|[A-Za-z_][\w$#@]*)'
QN = rf'({ID}(?:\s*\.\s*(?:{ID})?){{0,3}})'
WRITE_RES = [re.compile(p, re.I) for p in (
    rf'\binsert\s+(?:into\s+)?{QN}', rf'\bupdate\s+(?:top\s*\([^)]*\)\s*)?{QN}',
    rf'\bdelete\s+(?:top\s*\([^)]*\)\s*)?(?:from\s+)?{QN}', rf'\bmerge\s+(?:into\s+)?{QN}',
    rf'\btruncate\s+table\s+{QN}')]
READ_RE = re.compile(rf'\b(?:from|join)\s+{QN}', re.I)
EXEC_RE = re.compile(rf'\bexec(?:ute)?\s+(?:@\w+\s*=\s*)?{QN}', re.I)


def safe(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def strip_comments(t):
    t = re.sub(r'/\*.*?\*/', ' ', t, flags=re.S)
    t = re.sub(r'--[^\n]*', ' ', t)
    return re.sub(r"'(?:[^']|'')*'", "''", t)  # literais (inclui SQL dinâmico) não são analisados


def read_csv(p):
    with open(p, encoding='utf-8-sig') as h:
        return list(csv.DictReader(h))


catalog, synonyms, module_files = {}, {}, {}
for db in DBS:
    for r in read_csv(PROD / db / 'objects.csv'):
        catalog[(db, r['schema'].lower(), r['name'].lower())] = (r['schema'], r['name'], r['type'].strip())
    for r in read_csv(PROD / db / 'synonyms.csv'):
        synonyms[(db, r['schema'].lower(), r['name'].lower())] = r
    for f in (PROD / db / 'modules').glob('*/*.sql'):
        module_files[(db, f.stem.lower())] = f


def resolve(qn, ctx_db, hops=0):
    parts = [p.strip().strip('[]') for p in re.split(r'\s*\.\s*', qn)]
    if len(parts) > 3:
        return None  # servidor vinculado
    name = parts[-1]
    schema = (parts[-2] if len(parts) >= 2 else '') or 'dbo'
    db = CANON.get(parts[-3].lower()) if len(parts) == 3 else ctx_db
    if not db or name.startswith(('#', '@')):
        return None
    key = (db, schema.lower(), name.lower())
    if key in synonyms and hops < 3:
        s = synonyms[key]
        if s['to_server']:
            return None
        base = '.'.join(p for p in (s['to_db'] or db, s['to_schema'] or 'dbo', s['to_name']))
        return resolve(base, db, hops + 1)
    if key not in catalog:
        return None
    sch, nm, typ = catalog[key]
    return db, sch, nm, typ


def scan(text, ctx_db):
    """Retorna conjuntos de (db, schema, nome, tipo) escritos, lidos e executados."""
    t = strip_comments(text)
    writes, reads, execs = set(), set(), set()
    for rx in WRITE_RES:
        for m in rx.finditer(t):
            o = resolve(m.group(1), ctx_db)
            if o and o[3] == 'U':
                writes.add(o)
        t = rx.sub(' ', t)  # evita contar "DELETE FROM x" também como leitura
    for m in READ_RE.finditer(t):
        o = resolve(m.group(1), ctx_db)
        if o and o[3] in ('U', 'V', 'IF', 'TF'):
            reads.add(o)
    for m in EXEC_RE.finditer(t):
        o = resolve(m.group(1), ctx_db)
        if o and o[3] == 'P':
            execs.add(o)
    return writes, reads, execs


_, TARGETS, RELEVANT, _ = load_scope()


def in_scope(tipo, o):
    k = scope_key(o[0], o[1], o[2])
    return k in TARGETS or (tipo == 'db-exec' and k in RELEVANT)


_proc_cache = {}


def proc_effects(proc, depth, stack):
    """Leituras/escritas transitivas de uma proc: {(tipo, obj): via}."""
    if proc in _proc_cache:
        return _proc_cache[proc]
    db, sch, nm, _ = proc
    f = module_files.get((db, f'{sch}.{nm}'.lower()))
    eff = {}
    if f and depth < MAX_DEPTH and proc not in stack and scope_key(*proc[:3]) in RELEVANT:
        w, r, x = scan(f.read_text(encoding='utf-8', errors='replace'), db)
        via = f'{db}.{sch}.{nm}'
        for o in w:
            eff.setdefault(('db-write', o), via)
        for o in r:
            eff.setdefault(('db-read', o), via)
        for p in x:
            eff.setdefault(('db-exec', p), via)
            for k, v in proc_effects(p, depth + 1, stack | {proc}).items():
                eff.setdefault(k, v)
    _proc_cache[proc] = eff
    return eff


jobs = {j['job']: j for j in read_csv(JOBS / 'jobs.csv')}
steps = read_csv(JOBS / 'steps.csv')
edges, per_job = {}, {}
for s in steps:
    job = s['job']
    if is_ondemand((job,)) or job in DISCARDED_JOBS:
        continue
    info = per_job.setdefault(job, {'dbs': set(), 'w': set(), 'r': set(), 'x': set(), 'nao_analisados': set()})
    if s['subsystem'] != 'TSQL':
        info['nao_analisados'].add(f"{s['step_id']}:{s['subsystem']}")
        continue
    ctx = CANON.get((s['database_name'] or '').lower())
    path = JOBS / 'steps' / safe(job) / f"{s['step_id']}.txt"
    text = path.read_text(encoding='utf-8')
    if 'fn_hadr_group_is_primary' in text and len(text) < 1500:
        continue  # passo 1 padrão: para o job fora da primária do AG
    w, r, x = scan(text, ctx or 'master')
    found = {('db-write', o): '' for o in w}
    found.update({('db-read', o): '' for o in r if ('db-read', o) not in found})
    for p in x:
        found.setdefault(('db-exec', p), '')
        for k, via in proc_effects(p, 1, frozenset()).items():
            found.setdefault(k, via)
    disabled = '' if jobs[job]['enabled'] == '1' else ' (job desabilitado)'
    rel = path.relative_to(ROOT).as_posix()
    for (tipo, o), via in found.items():
        if not in_scope(tipo, o):
            continue
        alvo = f'{o[0]}.{o[1]}.{o[2]}'
        info['dbs'].add(o[0])
        info[{'db-write': 'w', 'db-read': 'r', 'db-exec': 'x'}[tipo]].add(alvo)
        k = (tipo, alvo, job)
        if k not in edges:
            det = f'job "{job}" passo {s["step_id"]}' + (f' via {via}' if via else '') + disabled
            edges[k] = ['sqlagent', 'SQL Agent (jobs do RSV_AG)', tipo, alvo, det, rel]

OUT_EDGES.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_EDGES, 'w', encoding='utf-8', newline='') as h:
    c = csv.writer(h)
    c.writerow(['repo', 'app', 'tipo', 'alvo', 'detalhe', 'evidencia'])
    c.writerows(sorted(edges.values(), key=lambda e: (e[4], e[2], e[3])))

with open(OUT_JOBS, 'w', encoding='utf-8', newline='') as h:
    c = csv.writer(h)
    c.writerow(['job', 'habilitado', 'agenda', 'bancos', 'escritas', 'leituras', 'procs', 'passos_nao_analisados'])
    for job in sorted(per_job, key=str.lower):
        i = per_job[job]
        if not (i['w'] or i['r'] or i['x'] or i['nao_analisados']):
            continue
        c.writerow([job, jobs[job]['enabled'], jobs[job]['schedules'], ';'.join(sorted(i['dbs'])),
                    len(i['w']), len(i['r']), len(i['x']), ';'.join(sorted(i['nao_analisados']))])

print('arestas', len(edges), '| jobs com arestas', sum(1 for i in per_job.values() if i['w'] or i['r'] or i['x']),
      '| tipos', {t: sum(1 for k in edges if k[0] == t) for t in ('db-read', 'db-write', 'db-exec')})
