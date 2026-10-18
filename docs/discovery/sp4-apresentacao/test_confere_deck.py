import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from confere_deck import confere

ASIDE = '<aside>Fale do tema. Tempo: 42 min</aside>'


def slide(id_, corpo='<h2 style="font-size:72px">Título</h2>', aside=ASIDE):
    return f'<section id="{id_}" style="background:#f6f4ef;font-size:32px">{corpo}{aside}</section>'


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = pathlib.Path(self.tmp.name)
        self.ws = raiz / 'ws'
        (self.ws / 'tools/ws').mkdir(parents=True)
        (self.ws / 'tools/ws/ws').write_text('echo "uso: ws <add|start|push|atlas>"\n', encoding='utf-8')
        (self.ws / '.claude/skills/speckit-specify').mkdir(parents=True)
        (self.ws / '.claude/skills/speckit-specify/SKILL.md').write_text('x', encoding='utf-8')
        (self.ws / 'docs/harness').mkdir(parents=True)
        (self.ws / 'docs/harness/2-quando-da-errado.md').write_text(
            'ws: erro: há mudanças não commitadas; faça commit ou stash antes\n'
            'ws: aviso: o mapeamento falhou em <repos>; esses repos continuam pendentes\n', encoding='utf-8')
        self.deck = raiz / 'deck'
        (self.deck / 'project/slides').mkdir(parents=True)
        self.slides = {'capa': slide('capa')}

    def tearDown(self):
        self.tmp.cleanup()

    def roda(self):
        for f in (self.deck / 'project/slides').glob('*.html'):
            f.unlink()
        for k, v in self.slides.items():
            (self.deck / f'project/slides/{k}.html').write_text(v, encoding='utf-8')
        (self.deck / 'project/deck.json').write_text(json.dumps({'order': list(self.slides)}), encoding='utf-8')
        return confere(self.deck, self.ws)

    def falha(self, trecho):
        erros, _, _ = self.roda()
        self.assertTrue(any(trecho in e for e in erros), erros)


class Testes(Base):
    def test_deck_valido(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">Rode <span>/speckit-specify</span>, que chama ws start.</p>'
                                    '<p style="font-size:24px">ws: erro: há mudanças não commitadas; faça commit ou stash antes</p>'
                                    '<p style="font-size:24px">ws: aviso: o mapeamento falhou em &lt;repos&gt;; esses repos continuam pendentes</p>'
                                    '<p style="font-size:24px">Índice: docs/harness/2-quando-da-errado.md e https://chat.google.com/room/X</p>')
        erros, n, t = self.roda()
        self.assertEqual(erros, [])
        self.assertEqual((n, t), (1, 42.0))

    def test_sem_nota(self):
        self.slides['capa'] = slide('capa', aside='')
        self.falha('capa: nota')

    def test_nota_sem_tempo(self):
        self.slides['capa'] = slide('capa', aside='<aside>Fale.</aside>')
        self.falha('capa: tempo')

    def test_tempo_fora_da_janela(self):
        self.slides['capa'] = slide('capa', aside='<aside>x Tempo: 20 min</aside>')
        self.falha('deck: tempo total 20')

    def test_tempo_com_virgula(self):
        self.slides['capa'] = slide('capa', aside='<aside>x Tempo: 21,5 min</aside>')
        self.slides['b'] = slide('b', aside='<aside>x Tempo: 20,5 min</aside>')
        erros, n, t = self.roda()
        self.assertEqual((erros, t), ([], 42.0))

    def test_fonte_pequena(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:20px">x</p>')
        self.falha('capa: fonte 20px')

    def test_skill_inexistente(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">Rode /speckit-sumiu agora</p>')
        self.falha('capa: skill /speckit-sumiu')

    def test_ws_inexistente(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">Rode ws sincroniza</p>')
        self.falha('capa: ws sincroniza')

    def test_mensagem_inexistente(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">ws: erro: algo que o código não diz</p>')
        self.falha('capa: mensagem')

    def test_caminho_inexistente(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">Veja docs/harness/9-nada.md</p>')
        self.falha('capa: caminho docs/harness/9-nada.md')

    def test_caminho_generico_passa(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">Em docs/atlas/&lt;repo&gt;/ e tools/ws/ws</p>')
        erros, _, _ = self.roda()
        self.assertEqual(erros, [])

    def test_exemplo_sem_marca(self):
        self.slides['exemplo'] = slide('exemplo', '<p style="font-size:32px">Bloquear endereço</p>', aside='<aside>Tempo: 0 min</aside>')
        self.falha('exemplo: sem a marca de fictício')

    def test_id_diferente_do_arquivo(self):
        self.slides['capa'] = slide('outro')
        self.falha('capa: id')

    def test_duas_secoes(self):
        self.slides['capa'] = slide('capa') + slide('capa')
        self.falha('capa: seções')

    def test_tag_proibida(self):
        self.slides['capa'] = slide('capa', '<style>p{}</style><p style="font-size:32px">x</p>')
        self.falha('capa: tag <style>')

    def test_aside_nao_e_o_ultimo(self):
        self.slides['capa'] = f'<section id="capa" style="font-size:32px">{ASIDE}<p style="font-size:32px">x</p></section>'
        self.falha('capa: nota')

    def test_segredo(self):
        self.slides['capa'] = slide('capa', '<p style="font-size:32px">https://user:abc123@dev.azure.com/x</p>')
        self.falha('capa: segredo')

    def test_data_uri(self):
        self.slides['capa'] = slide('capa', '<img src="data:image/png;base64,AAAA" alt="x" style="width:10px">')
        self.falha('capa: data:')

    def test_arquivo_fora_do_order(self):
        self.roda()
        (self.deck / 'project/slides/solto.html').write_text(slide('solto'), encoding='utf-8')
        erros, _, _ = confere(self.deck, self.ws)
        self.assertTrue(any('solto: fora do order' in e for e in erros), erros)


if __name__ == '__main__':
    unittest.main()
