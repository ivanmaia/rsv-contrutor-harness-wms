"""PoC SP3, item 3 (descartável): profundidade da propagação forte e ciclos no grafo SQL + código.
Arestas de impacto: objeto alterado -> quem depende dele."""
import csv, collections, pathlib, statistics
R = pathlib.Path('.')
imp = collections.defaultdict(set)   # x -> dependentes de x
kind = {}
def key(db, sch, name): return f'{db}.{sch or "dbo"}.{name}'.lower()
for dep in R.glob('extract/db-prod/*/dependencies.csv'):
    db = dep.parent.name
    for r in csv.DictReader(open(dep, encoding='utf-8-sig')):
        if not r['to_name']: continue
        a = key(db, r['from_schema'], r['from_name']); b = key(r['to_db'] or db, r['to_schema'] or r['from_schema'], r['to_name'])
        if a != b: imp[b].add(a); kind[a] = 'sql'; kind.setdefault(b, 'sql')
apps = set()
for f in ['docs/discovery/edges-consolidado.csv', 'docs/discovery/edges-sqlagent.csv']:
    for r in csv.DictReader(open(f, encoding='utf-8')):
        if r['tipo'].startswith('db-') or r['tipo'] == 'job':
            app = 'app:' + r['repo']; apps.add(app)
            imp[r['alvo'].lower()].add(app)   # app é terminal (propagação fraca a partir dele)
# BFS forte: não expande a partir de app
depth_max, sizes, maxobj = [], [], ('', 0, 0)
sql_nodes = [n for n in set(imp) | set(kind) if not n.startswith('app:')]
for s in sql_nodes:
    seen = {s: 0}; q = collections.deque([s])
    while q:
        x = q.popleft()
        if x.startswith('app:'): continue
        for y in imp.get(x, ()):
            if y not in seen: seen[y] = seen[x] + 1; q.append(y)
    d = max(seen.values()); n = len(seen) - 1
    if n: depth_max.append(d); sizes.append(n)
    if n > maxobj[1]: maxobj = (s, n, d)
print('objetos SQL com dependentes:', len(sizes), 'de', len(sql_nodes))
print('profundidade: mediana', statistics.median(depth_max), 'p90', sorted(depth_max)[int(.9*len(depth_max))], 'max', max(depth_max))
print('afetados por objeto: mediana', statistics.median(sizes), 'p90', sorted(sizes)[int(.9*len(sizes))], 'p99', sorted(sizes)[int(.99*len(sizes))], 'max', maxobj)
print('objetos com > 50 afetados:', sum(1 for x in sizes if x > 50))
# ciclos (Tarjan iterativo) só entre nós SQL
idx, low, on, st, sccs, c = {}, {}, set(), [], [], [0]
def tarjan(v0):
    stack = [(v0, iter(sorted(imp.get(v0, ()))))]; idx[v0] = low[v0] = c[0]; c[0] += 1; st.append(v0); on.add(v0)
    while stack:
        v, it = stack[-1]
        for w in it:
            if w.startswith('app:'): continue
            if w not in idx:
                idx[w] = low[w] = c[0]; c[0] += 1; st.append(w); on.add(w); stack.append((w, iter(sorted(imp.get(w, ()))))); break
            elif w in on: low[v] = min(low[v], idx[w])
        else:
            stack.pop()
            if stack: low[stack[-1][0]] = min(low[stack[-1][0]], low[v])
            if low[v] == idx[v]:
                comp = []
                while True:
                    w = st.pop(); on.discard(w); comp.append(w)
                    if w == v: break
                if len(comp) > 1 or v in imp.get(v, ()): sccs.append(comp)
for v in sql_nodes:
    if v not in idx: tarjan(v)
print('ciclos (SCC > 1):', len(sccs), 'tamanhos', sorted((len(x) for x in sccs), reverse=True)[:10])
for comp in sorted(sccs, key=len, reverse=True)[:5]: print('  ', ' -> '.join(sorted(comp)[:6]), '...' if len(comp) > 6 else '')
