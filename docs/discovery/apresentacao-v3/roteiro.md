# Roteiro da v2 do deck "Harness WMS" (para os escritores de slide)

Objetivo (pedido do usuário): deixar claro para os devs TUDO o que eles precisam fazer para (1) se beneficiar do harness e entregar com mais eficiência e qualidade; (2) melhorar a qualidade do harness e dos repos, com ênfase nas convenções e definições que CADA repo precisa ter. Duração alvo: 75 min (até 80). Público: devs do time WMS. Idioma: pt-BR, frases curtas, voz ativa, sem jargão de processo.

Fonte de verdade do conteúdo: `conteudo.md` (nesta pasta). Não invente: tudo que está no slide tem de estar no brief. O que no brief está marcado "proposta (não está na doc)" pode ir para o slide como recomendação ("o que recomendamos"), nunca como regra já existente; diga isso na nota.

Slides da v1 (estilo e textos que podem ser reaproveitados): `v1-slides/<id>.html`. Corrija o que o brief (seção 11) diz estar desatualizado.

## Regras de forma (iguais à v1)

- Um arquivo por slide: `deck/project/slides/<id>.html`, contendo EXATAMENTE UM `<section id="<id>" ...>`, nada antes ou depois. Nada de `<html>`, `<head>`, `<style>`, classes, `margin`, `em`, `var()`. Só estilos inline. Canvas 1920×1080, `padding:128px 128px 160px` nos slides de conteúdo.
- Paleta: fundo claro `#f6f4ef`, cartão `#fbfaf7` com borda `1px solid #d9d4c8` e `border-radius:16px`, faixa de destaque `#ebe7de`; texto `#1d2433`; secundário `#5a6170`; acento `#b5452f` (rótulos, números); comando/caminho `#2f5f7f`; slides escuros (capa, aberturas de parte, exemplo) `background:#1d2433;color:#f6f4ef`, rótulo `#e8846f`, texto secundário `#c9c4b8`.
- Fontes: `font-family:'IBM Plex Sans', Arial, sans-serif` na section; comandos em bloco próprio em `'IBM Plex Mono', Consolas, monospace`. Comando dentro de texto: `<span style="color:#2f5f7f">…</span>` (span só aceita cor).
- Escala: título h2 72px/700; h3 40px (cartões) ou 24px com letter-spacing:2px (rótulo); corpo 32px (28px em tabelas/cartões densos); nada abaixo de 24px. Rodapé: `<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:#5a6170">Harness WMS · N/63</p>` (claro) ou cor `#c9c4b8` (escuro). N = posição na ordem abaixo.
- Uma ideia por slide; no máximo ~6 linhas de tabela ou 4 cartões; se não cabe, simplifique (o detalhe vai para a nota). Espaço útil 1664×824.
- Notas: um `<aside>` como ÚLTIMO filho, texto corrido para o apresentador (o que dizer, detalhes, fontes), terminando com `Tempo: X min` (vírgula decimal). Máximo 4.000 caracteres.
- `&lt;` e `&gt;` para `<` e `>` no texto.
- Títulos introduzem o assunto, mesma gramática (substantivo ou frase curta), sem drama.

## Ordem, seções e tempos (63 slides, 75 min)

### Parte 0 — Abertura (s1) · 6 min
1. `capa` — escuro. "EQUIPE WMS" / "Harness WMS" / subtítulo "Versão 2: entregar melhor e melhorar o harness e os repos" / rodapé "Outubro de 2026". Nota: objetivo da sessão, duas metas, duração. 1 min
2. `metas` — "Duas metas para hoje": dois cartões grandes: "1. Entregar com mais eficiência e qualidade" (o fluxo, o que você revisa, PRs e revisão pelo harness) e "2. Melhorar o harness e os repos" (convenções e definições de cada repo, feedback ao harness). 1 min
3. `hoje` — reaproveitar v1 (18 repos, conhecimento espalhado, agente sem contexto). 1 min
4. `antes-depois` — atualizar: acrescentar linhas "Abrir os PRs e avisar o time" (antes: um PR por repo à mão e mensagem no Chat; com o harness: abre todos e posta no Chat) e "Revisar" (antes: PR por PR; com o harness: `/ws-revisar` revisa o conjunto). Máx 5 linhas. 1,5 min
5. `pecas` — as peças (workspace + subtrees, Spec Kit, Atlas, `ws`, e agora `ws pr` e `/ws-revisar`). Reaproveitar v1 e atualizar. 1 min
6. `novidades` — "O que mudou desde a última apresentação": SP7 (PRs pelo harness, card, homolog/develop, promover, `/ws-revisar`), setup (az + PAT, Python), correções de feedback (ws push com marcador repetido, ws sync volta para a branch), constitution 1.5.0. 1,5 min — (soma 7; ajuste: capa 1, metas 1, hoje 0,5, antes-depois 1,5, pecas 1, novidades 1,5 = 6,5)

### Parte 1 — Preparar a máquina (s2) · 6 min
7. `parte-1` — escuro, abertura de parte: "PARTE 1" / "Entregar com o harness" / "Setup, o fluxo da feature, o que revisar, bug, refactor, fatias, PRs e revisão". 0,5 min
8. `setup-base` — "Uma vez por máquina": Claude Code, Git for Windows (Git Bash), caminhos longos (admin), clone com `core.longpaths`/`autocrlf=false`, `claude` na raiz. Comandos exatos do brief §1 (os longos ficam na nota). 2 min
9. `setup-az` — "Para o harness abrir e revisar PRs": Azure CLI + `az extension add --name azure-devops`; `az devops login` com PAT (NÃO `az login`); escopos Code (Read & write) e Work Items (Read); Python no PATH. Faixa de destaque: rode o `az devops login` num terminal seu (pelo `!` do Claude Code ele trava no prompt) — isso está na memória da sessão, deixe como dica na nota. 1,5 min
10. `setup-atlas` — "Recomendado: mapas de código": WSL+Ubuntu, `instala-cbm.sh`, uv + graphify, ast-grep, `ws atlas mapas --todos`, conferir `/mcp`. Sem eles funciona, mas o agente navega pior. 1 min
11. `primeira-vez` — "Na primeira feature": o primeiro `/speckit-specify` pode passar de 20 min (Atlas); idioma pt-BR; um comando por vez e leia a resposta. 1 min

### Parte 1 — A feature, ponta a ponta (s3) · 17 min
12. `exemplo` — reaproveitar v1 (feature fictícia de picking/inventário, dois repos), agora "pelos 11 passos". 1 min
13. `passo-1` … 20. `passo-8` — reaproveitar v1 passo-1..passo-7 e a parte de commit-push do passo-8-9, atualizando com o brief §2 (cada slide: número grande, comando, o que o agente faz, O QUE VOCÊ CONFERE). passo-1 2 min, passo-2 1 min, passo-3 1,5 min, passo-4 1 min, passo-5 1 min, passo-6 1 min, passo-7 1,5 min, passo-8 1 min.
21. `passo-9` — "9. Os PRs para homologação": a oferta no fim do commit-push, `ws pr plano homolog`, o número do card (ou "sem card"; o agente não inventa), `ws pr abrir homolog --card <n>`; um PR por repo + o do workspace (com a tabela das subtrees); destino `homolog` (`develop` no Fly); recusou → links `pullrequestcreate`. 2 min
22. `mensagem-chat` — "O aviso no Google Chat": bloco mono com o formato exato (Pull Request <id>: <card>: <título do card> / título do PR / Autor / Workspace / Subtrees / Complete o PR do workspace por último), e as variações sem card e sem título. 1 min
23. `passo-10` — "10. Depois da homologação: promover": `/speckit-ws-promover` na branch da entrega; você decide que a homologação passou; avisa PR de teste aberto; card de novo; abre os PRs para `main`; recria a branch apagada; posta no espaço de produção (enquanto a URL de produção estiver vazia, o texto aparece para colar). 1,5 min
24. `passo-11` — "11. Completar os PRs": complete os dos repos e, POR ÚLTIMO, o do workspace (nos dois destinos); não apague a branch de origem ao completar para `homolog`; a política de PR é de cada repo. Destaque visual forte (statement). 1 min
25. `resumo` — "Os 11 passos" em tabela compacta (passo, comando, o que você confere). 1,5 min
26. `ja-conhece` — reaproveitar v1 (diferenças para quem já usa Spec Kit) + linha "os PRs saem pelo harness". 1 min
27. `branch-parada` — "Feature que muda ou branch parada": mudar uma feature existente (`/speckit-specify` citando o número → `-r<k>`, living spec); branch parada: `tools/ws/ws sync && git merge --no-edit ws/sync` (nunca rebase nem merge do origin/main); se o sync falhar, volta para a sua branch. 1 min

### Parte 1 — Qualidade: o que você revisa (s4) · 7 min
28. `voce-revisa` — statement escuro ou faixa: "O agente escreve; você decide." Três frases: corrigir na spec e no plano é mais barato; nada segue sem você ler; o build e os testes de cada repo são a régua. 1 min
29. `qualidade-spec` — Spec e clarify: "Repos afetados" obrigatória; contratos → consumidores pelo índice de impacto; sistema externo (`- externo: …`, não indique a pasta); living spec; responda as dúvidas antes do plano. 1,5 min
30. `qualidade-plan` — Plano: por repo, "Instruções do repo lidas", constitution do repo, stack, COMANDOS EXATOS de build e testes, contratos e afetados; menor mudança (constitution VI); decisão relevante vira ADR aprovado por humano (no repo, se só dele; no harness, se cruza repos). Ponte: "quando o repo não documenta stack e comandos, o agente deduz a cada plano → Parte 2". 1,5 min
31. `qualidade-tarefas` — Tasks, analyze, implement e converge: cada grupo termina na verificação de build e testes; analyze (requisito sem tarefa…); implement: revise como código de colega, recuse mudança no harness, nada de segredo novo; converge até não surgir tarefa nova. 1,5 min
32. `qualidade-envio` — "A entrega só termina quando cada repo passa no próprio build e nos próprios testes" (constitution III), e no bug: `verified`/`partial`/`failed`; partial é decisão sua, e o PR do repo é onde o time confere. 1,5 min

### Parte 1 — Bug, refactor e fatias (s5) · 9 min
33. `bug` — reaproveitar v1 e corrigir (sem correção → PR do workspace direto para `main` pelo harness; com correção → mesma oferta dos PRs da feature). 2 min
34. `refactor` — reaproveitar v1, conferir com brief §3. 2 min
35. `marcos` — reaproveitar v1 ("As etapas de uma fatia"). 1,5 min
36. `desacoplamento` — reaproveitar v1 e corrigir a parte de PRs da fatia sem chave (cada card tem PRs para o ramo de teste; promoção na branch de subida) e `ws refactor fatia pendentes`. 2 min
37. `fatia-bloqueio` — faixa curta: enquanto a seção "Chaves centrais" da camada 3 tiver "a definir pela feature", nenhuma fatia com chave começa; fatia sem chave e refactor interno seguem. Pode ser um slide pequeno de aviso. 1 min — (se preferir, funda no `desacoplamento` e use 62 slides; mantenha 63 e o id).

### Parte 1 — Revisão de código (s6) · 6 min
38. `revisar` — "Revisar um PR com o harness": quem (o colega revisor), onde (no workspace dele, Claude Code), como (`/ws-revisar <link do PR do workspace>`; link do navegador com `?_a=overview` serve); revisa o workspace e todas as subtrees juntos; diff contra a base da `ws/sync`. 1,5 min
39. `revisar-pontos` — os cinco pontos em cartões/tabela (conformidade, contratos, regras, defeitos e testes, banco), um subagente por ponto. 2 min
40. `revisar-escolha` — lista numerada → você escolhe os números e pode editar → publica com a sua credencial (código de repo no PR do repo, o resto no do workspace; sem linha vira comentário geral) → rodar de novo não repete → não aprova, não reprova, não vota. Sem escolha, nada é publicado. 1,5 min
41. `regras` — "Três regras que não se quebram" (v1, corrigindo a regra 3 para incluir `CLAUDE.md` e `docs/adr/`) + linha da regra dos PRs. 1 min

### Parte 2 — Repos e harness melhores (s7) · 19 min
42. `parte-2` — escuro: "PARTE 2" / "Melhorar os repos e o harness" / "O agente só é tão bom quanto o que o repo diz sobre si". 0,5 min
43. `conv-por-que` — "Por que cada repo precisa se descrever": o agente LÊ os arquivos de instrução do repo antes de mexer (AGENTS.md regra 1); o plano registra stack e comandos exatos; o `/ws-revisar` confere contra as convenções. Sem isso, o agente deduz a cada vez e cada entrega sai num estilo. 1,5 min
44. `conv-arquivos` — "O que o harness reconhece num repo": `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `docs/convencoes.md`, `docs/adr/`, constitution do repo; subordinados ao harness (conflito → o agente para e pergunta). 1,5 min
45. `conv-hoje` — "Como estão os 18 repos hoje": números grandes: 0 com `docs/convencoes.md`; 0 com `docs/adr/`; 14 sem nenhum arquivo de instrução; 2 com build e testes bem documentados (AWX e Fly); 5 sem testes encontrados; 9 com SQL, 3 com algum rollback. 1,5 min
46. `conv-tabela` — tabela compacta dos 18 repos (nome curto, instrução de agente, testes, lint, build documentado) — use nomes curtos (ex.: `servidor.backend`); fonte 24px se precisar; se não couber em um slide, faça `conv-tabela` com os 9 primeiros e mantenha o resto na nota? NÃO: mostre os 18 em duas colunas de tabela lado a lado, só as colunas essenciais (repo · instrução · testes · build doc). 2 min
47. `conv-onde` — "Onde gravar uma regra ou decisão": árvore de decisão: vale só para um repo → no arquivo de instrução que ele já tem; não tem nenhum → `repos/<repo>/docs/convencoes.md`; decisão de arquitetura do repo → `repos/<repo>/docs/adr/NNNN-<titulo>.md` (aprovado por humano); vale para mais de um repo ou para o jeito de trabalhar → harness, registrado para o time do harness. 1,5 min
48. `conv-conteudo-1` — "O que todo repo precisa ter descrito (1/2)": stack e versões; comandos exatos de build, teste e lint (teste isolado, o que a pipeline exige); estrutura de pastas e camadas; nomenclatura; tratamento de erro e logging; acesso a dados. Cada item com "por quê" curto (o que o harness faz com ele). Nota: proposta do time do harness, ainda não há modelo no workspace. 2 min
49. `conv-conteudo-2` — "(2/2)": testes (framework, onde, mínimo num PR, caracterização); scripts de banco; contratos expostos; checklist de PR do repo (build, testes, lint, prints, scripts com rollback, ramo de teste); gotchas; ADRs (índice e quando abrir). 2 min
50. `conv-banco` — "Scripts de banco: ordem e rollback": o ponto 5 do `/ws-revisar` cobra; hoje nenhum repo declara a convenção; proponha: pasta, nome com a ordem de execução, script de rollback correspondente, seguro repetir, quem roda em homolog e produção. 1,5 min
51. `conv-exemplos` — "Modelos que já existem": AWX `AGENTS.md` (comandos, mapa, coding standards, antes de commitar), Fly `CLAUDE.md` (comandos obrigatórios antes do commit, `.claude/rules/`, `docs/TESTING.md`), Linx `AGENTS.md` (repositórios, nomenclatura, logging). Comece copiando a estrutura do mais parecido com o seu repo. 1,5 min
52. `conv-acoes` — "O que cada time faz no seu repo": checklist: (1) criar o ramo `homolog` se falta (7 repos listados na nota); (2) descrever o repo (`docs/convencoes.md` ou o arquivo que já tem); (3) comandos de build e teste que funcionam; (4) convenção de scripts de banco; (5) abrir `docs/adr/` na primeira decisão; (6) corrigir o que está errado (ex.: servidor.backend cita scripts que não existem). Nota: é mudança no repo, sai por PR do repo; o modelo comum é mudança de harness. 2 min
53. `harness-feedback` — "Como melhorar o harness": durante uma feature, recuse mudança no harness e registre; onde registrar (thread Equipe WMS) e o que mandar (comando, mensagem completa, `git status`, `git log --oneline -3`); padrão de segredo: só o nome do repo. 1,5 min
54. `harness-ciclo` — "O feedback vira correção": exemplos reais (sistema fora do workspace → regra 7; caminhos longos; ws push no HTTP/2; Atlas apagado; avisos do ws start; e os de 21–22/10: marcador de split repetido, ws sync voltando para a branch). 1,5 min
55. `harness-quem` — "Quem faz o quê": tabela de duas colunas: time do harness (incluir repo no workspace, conflito no sync, política na ws/sync, ramo de teste no `workspace.pr.ini`, modelo de convenções, evoluir com suíte + doc + ADR) × time de cada repo (criar `homolog`, convenções e ADRs do repo, política de PR e revisores). 1 min

### Referência (s8) · 7 min
56. `erros` — reaproveitar v1 (como ler `ws: erro:` × `ws: aviso:` + 3 exemplos). 1,5 min
57. `erros-prs` — "Erros dos PRs": az não autenticado; az não instalado; sem ramo de teste; não consegui postar no Chat; não consegui ler o título do card; PR sem a tabela das subtrees. Mensagem exata (mono, 24px) + o que fazer. 1,5 min
58. `atlas` — reaproveitar v1. 1 min
59. `impacto` — reaproveitar v1. 1 min
60. `cmd-ws` — atualizar (inclui `ws pr plano|abrir|revisao|comentar`, `ws refactor fatia pendentes|status`, `ws sync`). 1 min
61. `cmd-skills` — atualizar (inclui `/speckit-ws-promover`, `/ws-revisar`; manter `/atlas-consultar` e `/atlas-atualizar` aqui, pois o `cmd-atlas` da v1 sai). 1 min

### Fechamento (s9) · 3 min
62. `onde` — reaproveitar v1 e acrescentar "revisar um PR" (camada 1) e "PRs e merge" (camada 2). 1 min
63. `amanha` — escuro: "O que fazer a partir de amanhã": dev: setup do az + PAT; próxima entrega pelos 11 passos; revise pelo `/ws-revisar`. Time de cada repo: `homolog`, convenções, build e testes, scripts com rollback. Todos: travou → thread. 2 min (perguntas depois)

Soma dos tempos ≈ 75 min.
