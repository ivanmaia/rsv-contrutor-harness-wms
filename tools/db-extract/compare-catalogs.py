"""Compara dois extratos de catálogo (ex.: homologação x produção) gerados por extract-catalog.ps1.

Saída por banco em <out>/<DB>/:
  objetos-so-em-<a>.csv, objetos-so-em-<b>.csv   objetos de usuário presentes em um só lado
  modulos-diferentes.csv                         módulos com definição diferente (ignorando espaços e caixa)
E um resumo em <out>/resumo.csv.

Uso: python tools/db-extract/compare-catalogs.py extract/db-hml extract/db-prod extract/diff-hml-prod WMS Reserva ReservaNet
"""
import csv
import pathlib
import re
import sys


def load_objects(d):
    rows = csv.DictReader(open(d / 'objects.csv', encoding='utf-8-sig'))
    return {(r['schema'].lower(), r['name'].lower(), r['type'].strip()): r for r in rows}


def load_modules(d):
    out = {}
    for f in (d / 'modules').glob('*/*.sql'):
        text = f.read_text(encoding='utf-8', errors='replace')
        out[(f.parent.name, f.stem.lower())] = re.sub(r'\s+', ' ', text).strip().lower()
    return out


def write(path, header, rows):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def main():
    a_root, b_root, out_root = (pathlib.Path(p) for p in sys.argv[1:4])
    a_name, b_name = a_root.name, b_root.name
    summary = []
    for db in sys.argv[4:]:
        a, b = a_root / db, b_root / db
        out = out_root / db
        out.mkdir(parents=True, exist_ok=True)
        oa, ob = load_objects(a), load_objects(b)
        only_a = sorted(set(oa) - set(ob))
        only_b = sorted(set(ob) - set(oa))
        hdr = ['schema', 'name', 'type', 'modify_date']
        write(out / f'objetos-so-em-{a_name}.csv', hdr, [(*k, oa[k]['modify_date']) for k in only_a])
        write(out / f'objetos-so-em-{b_name}.csv', hdr, [(*k, ob[k]['modify_date']) for k in only_b])
        ma, mb = load_modules(a), load_modules(b)
        diff = sorted(k for k in set(ma) & set(mb) if ma[k] != mb[k])
        write(out / 'modulos-diferentes.csv', ['type', 'schema.name'], diff)
        summary.append((db, len(oa), len(ob), len(only_a), len(only_b), len(set(ma) & set(mb)), len(diff)))
    write(out_root / 'resumo.csv',
          ['db', f'objetos_{a_name}', f'objetos_{b_name}', f'so_{a_name}', f'so_{b_name}', 'modulos_comuns', 'modulos_diferentes'],
          summary)
    for row in summary:
        print(*row, sep='\t')


if __name__ == '__main__':
    main()
