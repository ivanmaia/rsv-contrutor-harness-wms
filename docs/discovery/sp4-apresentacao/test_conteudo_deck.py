"""Fatos do deck conferidos na revisão final contra a doc e o código do workspace."""
import pathlib
import unittest

SLIDES = pathlib.Path(__file__).parent / 'deck/project/slides'


def slide(nome):
    return (SLIDES / f'{nome}.html').read_text(encoding='utf-8')


class Conteudo(unittest.TestCase):
    def test_envio_vai_para_os_repos_alterados_nao_pelo_marcador(self):
        # tools/ws/lib/push.sh decide pelos prefixos alterados; o marcador não é lido.
        self.assertNotIn('permite ao envio saber', slide('passo-4'))
        self.assertIn('cada repo que a branch alterou', slide('passo-4'))

    def test_atlas_do_specify_segue_a_politica(self):
        # camada 3: mudança só interna é adiada; há limite por execução.
        for s in ('passo-1', 'atlas'):
            self.assertIn('mudança relevante', slide(s), s)
            self.assertNotIn('nos repos que mudaram', slide(s), s)

    def test_sem_afirmar_spec_kit_padrao(self):
        # camada 4: o preset multirepo troca comandos e templates.
        self.assertNotIn('como o Spec Kit padrão', slide('ja-conhece'))

    def test_branch_so_nos_repos_alterados(self):
        self.assertIn('em cada repo alterado', slide('passo-8-9'))

    def test_slides_de_comandos_entre_impacto_e_onde(self):
        import json
        order = json.loads((SLIDES.parent / 'deck.json').read_text(encoding='utf-8'))['order']
        i = order.index('impacto')
        self.assertEqual(order[i + 1:i + 5], ['cmd-atlas', 'cmd-ws', 'cmd-skills', 'onde'])
        self.assertEqual(len(order), 24)

    def test_rodape_numera_24_slides(self):
        import json
        order = json.loads((SLIDES.parent / 'deck.json').read_text(encoding='utf-8'))['order']
        for n, sid in enumerate(order[1:], 2):
            self.assertIn(f'Harness WMS · {n}/24', slide(sid), sid)

    def test_comandos_ws_de_diagnostico(self):
        # camada 4: os ws atlas são chamados pelas skills e hooks; à mão, só diagnóstico.
        self.assertIn('diagnóstico', slide('cmd-ws'))


if __name__ == '__main__':
    unittest.main()
