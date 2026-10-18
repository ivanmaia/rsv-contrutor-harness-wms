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
        self.assertEqual(len(order), 29)

    def test_rodape_numera_29_slides(self):
        import json
        order = json.loads((SLIDES.parent / 'deck.json').read_text(encoding='utf-8'))['order']
        for n, sid in enumerate(order[1:], 2):
            self.assertIn(f'Harness WMS · {n}/29', slide(sid), sid)

    def test_comandos_ws_de_diagnostico(self):
        # camada 4: os ws atlas são chamados pelas skills e hooks; à mão, só diagnóstico.
        self.assertIn('diagnóstico', slide('cmd-ws'))

    # Atualização de 2026-10-18: vertentes de bug e refactor, Spec Kit 1.2.0 e o que mudou desde a primeira versão.
    def test_bug_refactor_e_fatia_entre_regras_e_erros(self):
        import json
        order = json.loads((SLIDES.parent / 'deck.json').read_text(encoding='utf-8'))['order']
        i = order.index('regras')
        self.assertEqual(order[i + 1:i + 6], ['bug', 'refactor', 'marcos', 'desacoplamento', 'erros'])
        self.assertEqual(order[1], 'novidades')

    def test_novidades_traz_a_versao_do_spec_kit(self):
        self.assertIn('Spec Kit 1.2.0', slide('novidades'))
        self.assertIn('ws/sync', slide('novidades'))

    def test_bug_sem_correcao_vai_so_ao_workspace(self):
        # camada 1, passo 3 do bug.
        self.assertIn('só o PR do workspace', slide('bug'))

    def test_refactor_faz_a_caracterizacao_antes(self):
        # camada 1, passo 3 do refactor; regra VII.
        self.assertIn('Primeiro os testes que fixam o comportamento atual', slide('refactor'))
        self.assertIn('regra VII', slide('refactor'))

    def test_fatia_com_os_marcos_e_o_pendentes(self):
        s = slide('desacoplamento')
        for m in ('ENTREGUE (M1)', '>CONVIVÊNCIA<', 'VALIDADO (M3)', 'DESACOPLADO (M4)', 'refactor pendentes'):
            self.assertIn(m, s)

    def test_comandos_ws_com_sync_e_refactor(self):
        s = slide('cmd-ws')
        self.assertIn('>ws sync<', s)
        self.assertIn('>ws refactor pendentes<', s)

    def test_marcos_explica_os_codigos_antes_da_fatia(self):
        s = slide('marcos')
        for c in ('>M1<', '>M2<', '>M3<', '>M3-falhou<', '>M4<', 'ws refactor pendentes'):
            self.assertIn(c, s)


if __name__ == '__main__':
    unittest.main()
