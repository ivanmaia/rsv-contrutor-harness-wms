"""Compara cada cópia editada com o original, byte a byte. Descartável."""
import os, sys, filecmp
CASOS = {'T2s': ('industria-logistica.wms.servidor.backend', b'ObterNomeTipoEndereco', b'ObterNomeDoTipoEndereco'),
         'T2a': ('industria-logistica.wms.awx.monorepo', b'ObterIdTipoPedidoAsync', b'ObterIdDoTipoPedidoAsync'),
         'T3a': ('industria-logistica.wms.awx.monorepo', None, None)}
def arquivos(raiz):
    for d, ds, fs in os.walk(raiz):
        ds[:] = [x for x in ds if x not in ('.serena', 'graphify-out', '.git', 'obj', 'bin')]
        for f in fs: yield os.path.relpath(os.path.join(d, f), raiz)
for caso, (repo, velho, novo) in CASOS.items():
    for cfg in ('padrao', 'serena'):
        orig, run = f'repos/{repo}', f'runs/{caso}-{cfg}/{repo}'
        mud = [f for f in arquivos(run) if not os.path.exists(os.path.join(orig, f)) or open(os.path.join(orig, f), 'rb').read() != open(os.path.join(run, f), 'rb').read()]
        print(f'== {caso}-{cfg}: {len(mud)} arquivo(s) alterado(s)')
        for f in mud:
            a = open(os.path.join(orig, f), 'rb').read() if os.path.exists(os.path.join(orig, f)) else b''
            b = open(os.path.join(run, f), 'rb').read()
            if velho:
                exato = a.replace(velho, novo) == b
                print(f'   {f}: troca exata={exato} bom_antes={a[:3]==b"\xef\xbb\xbf"} bom_depois={b[:3]==b"\xef\xbb\xbf"} crlf_antes={a.count(b"\r\n")} crlf_depois={b.count(b"\r\n")}')
            else:
                print(f'   {f}: bom {a[:3]==b"\xef\xbb\xbf"}->{b[:3]==b"\xef\xbb\xbf"} crlf {a.count(b"\r\n")}->{b.count(b"\r\n")} tamanho {len(a)}->{len(b)}')
        if velho:
            resto = sum(open(os.path.join(run, f), 'rb').read().count(velho) for f in arquivos(run) if f.endswith(('.cs', '.ts')))
            print('   ocorrências restantes do nome antigo:', resto)
