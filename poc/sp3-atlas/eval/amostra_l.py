"""Amostra L: 30 chamadas método→método no servidor.backend, com o nome do chamado único no repo.
Descartável (PoC SP3)."""
import re, os, random, json, collections, sys
ROOT = sys.argv[1]
SIG = re.compile(r'^\s*(?:public|private|protected|internal)(?:\s+(?:static|virtual|override|async|abstract|sealed|new|partial))*\s+[\w<>\[\],\.\?\s]+?\s+(\w+)\s*(?:<[^>]*>)?\s*\(')
files = []
for d, _, fs in os.walk(ROOT):
    if any(x in d for x in ('Testes', 'graphify-out', 'Scripts', 'obj', 'bin', 'packages')): continue
    files += [os.path.join(d, f) for f in fs if f.endswith('.cs')]
defs = collections.defaultdict(list)
text = {}
for f in files:
    lines = open(f, encoding='utf-8', errors='ignore').read().splitlines()
    text[f] = lines
    for i, l in enumerate(lines):
        m = SIG.match(l)
        if m: defs[m.group(1)].append((f, i + 1))
uniq = {k: v[0] for k, v in defs.items() if len(v) == 1 and len(k) > 6}
cands = []
CALL = re.compile(r'\.(\w+)\s*\(')
for f, lines in text.items():
    cur = None
    for i, l in enumerate(lines):
        m = SIG.match(l)
        if m: cur = m.group(1); continue
        if cur is None or l.strip().startswith('//'): continue
        for c in CALL.findall(l):
            if c in uniq and c != cur:
                cands.append({'caller': cur, 'caller_file': os.path.relpath(f, ROOT).replace(os.sep, '/'), 'line': i + 1,
                              'callee': c, 'callee_file': os.path.relpath(uniq[c][0], ROOT).replace(os.sep, '/')})
# só chamadores com nome único também (para casar sem ambiguidade)
cands = [c for c in cands if c['caller'] in uniq]
seen = set(); dedup = []
for c in cands:
    k = (c['caller'], c['callee'])
    if k not in seen: seen.add(k); dedup.append(c)
random.seed(42)
s = random.sample(dedup, 30)
json.dump(s, open(os.path.join(os.path.dirname(__file__), 'amostra_l.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(files), 'arquivos', len(uniq), 'métodos únicos', len(dedup), 'pares candidatos')
for c in s: print(c['caller'], '->', c['callee'], c['caller_file'] + ':' + str(c['line']))
