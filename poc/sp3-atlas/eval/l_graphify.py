"""L para o Graphify: a amostra aparece como aresta chamador→chamado? Descartável."""
import json, re, sys, collections
g = json.load(open(sys.argv[1], encoding='utf-8'))
s = json.load(open('eval/amostra_l.json', encoding='utf-8'))
norm = lambda x: re.sub(r'[^A-Za-z0-9_]', '', (x or '').split('(')[0].split('.')[-1])
byname = collections.defaultdict(set)
for n in g['nodes']: byname[norm(n.get('label'))].add(n['id'])
CALLREL = {'calls', 'indirect_call', 'dispatches_to'}
out = collections.defaultdict(set)
for e in g['links']:
    if e.get('relation') in CALLREL: out[e['source']].add(e['target'])
hit = 0
for c in s:
    srcs, dsts = byname.get(c['caller'], set()), byname.get(c['callee'], set())
    ok = any(out[a] & dsts for a in srcs)
    hit += ok
    print('OK ' if ok else '-- ', c['caller'], '->', c['callee'], f'(nós: {len(srcs)}/{len(dsts)})')
print(f'L = {hit}/{len(s)}')
