# SP4: piloto da documentação do harness

Spec: `docs/superpowers/specs/2026-10-08-sp4-documentacao-harness-design.md`, seção 7.
Documentação no `main` do workspace desde o PR 16940 (`0cbac04e5`, 2026-10-08).

## Como conduzir

- **Quem:** um dev do time, escolhido durante a apresentação do harness (2026-10-08). Ele roda o fluxo completo numa demanda real e depois dá o feedback.
- **O que ele recebe:** o link do `README.md` do workspace. Ele já viu a apresentação (só teoria), então não parte do zero: o piloto testa se a doc basta para operar, não se ela explica o porquê.
- **Quem observa:** não ajuda enquanto o dev não travar de fato. Anota cada travada, dúvida ou desvio no registro abaixo, com a etapa e as palavras do dev.
- **Ao travar:** primeiro o dev procura na camada 2. Só depois o observador ajuda, e registra se a resposta estava na doc.
- **Depois:** cada linha com ação vira correção num PR de acompanhamento no workspace, na camada 1 ou como entrada nova na camada 2. O teste `tools/ws/tests/test_docs_referencias.sh` precisa continuar passando.

## Dados da sessão

- Data:
- Dev (papel, não nome):
- Demanda real (id ou título):
- Já conhecia o Spec Kit? (s/n):
- Feature:
- Repos tocados:
- Instalou as ferramentas do Atlas? (s/n):

## Registro

| # | Etapa (camada 1, passo) | O que aconteceu (palavras do dev ou mensagem) | Estava na doc? | Ação | PR |
|---|---|---|---|---|---|

## Pontos para conferir no piloto

- As âncoras `<a id>` e o bloco `<details>` funcionam no preview do Azure DevOps (decisão da execução: se o ADO tirar os ids, o link cai no topo do arquivo).
- O Claude Code pede aprovação dos servidores MCP do `.mcp.json` na primeira abertura; a camada 3 não menciona isso.

## Pendências adiadas da revisão final (candidatas a PR de acompanhamento)

- Camada 2, "Nada a enviar": cita causa impossível (mudanças não commitadas).
- Camada 2, "A branch já existe": prefixo `ws: erro:` errado e erro praticamente inalcançável.
- Perdas pequenas do antigo `docs/workspace.md`: `atlas.estado`, PAT como credencial, `git push` só vai para o workspace, PR do workspace leva o harness; camada 3 diz "proibidos" sem dizer que remover é permitido.
- Verificador: prefixo `./`, skills em bloco, `NATIVOS` fixo, sintoma pega o primeiro bloco depois de `**Sintoma:**`, exclusão de `docs/atlas/` sem comentário.
- Camada 1, regra 3: não lista `CLAUDE.md` e `docs/adr/` como harness.

## Resultado

(preencher ao fim: travadas por camada, correções feitas, se a camada 1 bastou sozinha, e o feedback do dev depois da entrega)
