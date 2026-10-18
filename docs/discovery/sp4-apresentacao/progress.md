# SDD ledger — plan: C:\src\00-harness_big_brown_field\docs\superpowers\plans\2026-10-08-sp4-apresentacao-harness.md
Setup: Ruling: sem git nesta pasta — ledger em docs/discovery/sp4-apresentacao/progress.md, sem worktree, sem commits, task-start/task-done manuais (o plano já previa) — custo se errado: nenhum, os arquivos são o registro.
Pre-flight: Task 2→3→4 consomem o Artifact (deck/url.txt) e o order da Task 2; Task 2-5 consomem confere_deck.py da Task 1. Sem conflito.
Task 1: complete (tests: python -m unittest test_confere_deck → 19 OK; RED antes: ModuleNotFoundError confere_deck)
Task 2: Ruling: o formato do tipo Slides não aceita font-family em <span> (só color) — comandos dentro de texto ficam em <span style="color:#2f5f7f"> (sobre tinta #e8846f), sem mono; comandos em bloco próprio (h2 do passo, cartões de mensagem, trilha) seguem em IBM Plex Mono — custo se errado: comandos inline sem fonte mono, só cor.
Task 2: Ruling: display/gap não valem em <ul> no formato — a lista do L-passo fica sem display:flex/gap — custo: espaçamento entre itens só pelo line-height.
Task 2: Artifact criado: https://claude.ai/artifact/GJjEDbZtoBLRLthKn4KxxC
Task 2: Ruling: fundo dos cartões #fbfaf7 em vez de #ffffff — o tipo Slides pede brancos tonalizados — custo: nenhum.
Task 2: complete (verificador: só ausentes + tempo 7.5 fora da janela, como esperado; publicado v3)
Task 3: Ruling: "8·9" a 200px não cabia na coluna de 320px (≈360px) — 160px com nowrap — custo: número menor que nos outros passos.
Task 3: complete (verificador: só ausentes + tempo 25.5, como esperado; publicado v7)
Task 4: Ruling: rótulo do código do slide impacto ganhou "(resumida)" — a página real é abreviada no slide (servidor.backend, via a trigger) e o deck não deve parecer cópia literal — custo: nenhum.
Task 4: complete (verificador: ok: 21 slide(s), 36 min; publicado v9)
Task 5: conferência de conteúdo feita pela revisão final (subagente opus), "With fixes": 0 Critical, 2 Important, 9 Minor.
Final: re-grade — Minor 1 (Atlas "nos repos que mudaram"), 2 ("como o Spec Kit padrão", contradiz a camada 4) e 3 (branch "em cada repo") promovidos a Important: afirmações que a doc não sustenta, e a spec §4 proíbe.
Final: fixed nota do passo 4 dizia que o marcador direciona o envio — test_envio_vai_para_os_repos_alterados_nao_pelo_marcador RED→GREEN, suite 23/23
Final: fixed Atlas atualizado "nos repos que mudaram" — test_atlas_do_specify_segue_a_politica RED→GREEN, suite 23/23
Final: fixed "o resto funciona como o Spec Kit padrão" — test_sem_afirmar_spec_kit_padrao RED→GREEN, suite 23/23
Final: fixed branch "em cada repo" — test_branch_so_nos_repos_alterados RED→GREEN, suite 23/23
Final: Ruling: ordem piloto × apresentação (o dev do piloto não pode assistir antes) — decisão do usuário; slide 21 mantido, pergunta levada ao usuário — custo: piloto contaminado se o dev assistir.
Final: minor (deferred): frases de orientação fora da doc (ordem de execução, revisar como de um colega, linguagem de negócio)
Final: minor (deferred): comandos do slide 17 sem destaque de cor
Final: minor (deferred): slide 4 em cartões, não diagrama com relação entre as peças
Final: minor (deferred): slide 21 não repete como pedir ajuda (está no 20)
Final: minor (deferred): "17 repos" é número que muda
Final: minor (deferred): passo-1, passo-7, passo-8-9 e erros passam de título + 4 linhas
Task 5: complete (python -m unittest test_conteudo_deck test_confere_deck → 23 OK; confere_deck → ok: 21 slide(s), 36 min; publicado v10)
Pedido do usuário (2026-10-08): slides de comandos entre o Atlas e "Onde está cada coisa".
Ruling: inseridos depois do "impacto" (19) e antes do "onde": cmd-atlas, cmd-ws, cmd-skills, em tabela no estilo do "onde" (28px para caber 3 colunas) — o "impacto" continua colado no "O Atlas" — custo se errado: reordenar 1 slide.
Ruling: deck passa de 21 para 24 slides (spec pedia 18–22) por pedido explícito; para manter a janela de 35–40 min, erros 3→2,5 e antes-depois 2,5→2; novos 1,5+1,5+1 — total 39 min — custo: menos folga para perguntas.
Comandos: test_slides_de_comandos_entre_impacto_e_onde, test_rodape_numera_24_slides, test_comandos_ws_de_diagnostico RED→GREEN; confere_deck ok: 24 slide(s), 39 min; publicado v11.
Merge: o usuário editou o slide erros no deck ("Essa parte da documentação do harness é organizada por etapa"); a versão dele foi mantida, só com rodapé 17/24 e Tempo 2,5. Publicado v14.
Atualização (2026-10-18, pedido do usuário): vertentes de bug e refactor, Spec Kit 1.2.0 e o que mudou desde 8/10. Slides novos: novidades (2), bug, refactor e desacoplamento (18-20, seção s2b, entre regras e erros). Atualizados: capa, hoje (18 repos), pecas, passo-1 (ws/sync, mais de 20 min, sistema de fora), atlas (fim de bug e refactor também atualiza), cmd-ws (ws sync e ws refactor pendentes), cmd-skills, onde (linhas de bug e refactor), proximos, nota do erros.
Ruling: 28 slides e 45 min; janela do confere_deck de 35-40 para 40-45 min e tempos de hoje, antes-depois, pecas, passo-6, passo-7 (2→1,5), atlas, impacto e erros (→2) — custo: menos folga para perguntas.
Atualização: test_conteudo_deck (6 testes novos) e test_confere_deck → 32 OK; confere_deck → ok: 28 slide(s), 45 min; publicado v16.
