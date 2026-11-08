# Atlas sob demanda: validação real

Data: 2026-11-07. Branch validada: `harness/atlas-sob-demanda` do workspace (`394b31711`, sobre o `main` `9c47c3fa3`). Design: `docs/superpowers/specs/2026-11-05-atlas-sob-demanda-design.md`. Plano: `docs/superpowers/plans/2026-11-05-atlas-sob-demanda.md` (Task 9).

## Como foi feito

- Tudo rodou na worktree `C:\src\wms-workspace-atlas`, isolado por variáveis do `ws`:
  - `WS_DESTINO=harness/teste-main`, uma cópia da branch validada;
  - `WS_BASE=harness/teste-sync`;
  - `WS_ATLAS_BRANCH=harness/teste-atlas-atualizacao`.

  As três branches de teste foram apagadas no fim. Nada foi enviado aos repos dos times nem à `ws/sync` ou à `atlas/atualizacao` reais.
- Cada fluxo rodou numa sessão nova e não interativa do Claude Code (`claude -p`, Opus 5.5, `--output-format json`). Os números saem do `modelUsage` da sessão, e o gasto de cada subagente sai da transcrição dele.
- "Processados" soma entrada, leitura de cache, criação de cache e saída, como no diagnóstico do 65594.
- O cenário foi um bug de teste no `servidor.backend` (`99999-validar-volume-expedicao`): o `validar-identificador` do volume de expedição recusaria identificadores do armazém 8 no B2B.

## Resultados

| Passo | Tempo | Processados | Custo | Antes (65594) |
|---|---|---|---|---|
| 1. `/speckit-bug-assess`, sessão inteira (start + diagnóstico + `assessment.md`) | 4,9 min | 1,34 M | US$ 1,10 | 65 M só no Atlas do start; 83% da sessão era Atlas |
| 1b. `ws atlas confere` numa página em dia | 3,4 s | 0 | 0 | — |
| 2. Converge com 0 afirmações tocadas (arquivo novo fora de qualquer item) | 70 s | 0,19 M | US$ 0,32 | 6,5 M |
| 3. Converge com 7 afirmações em 4 repos (2 arquivos do servidor alterados) | 5,4 min | 3,43 M (0,70 M Opus + 2,73 M Sonnet) | US$ 1,88 | 6,5 M |
| 4. Execução manual: 38 afirmações em 3 repos + 1 lacuna de 6 arquivos | 14,9 min | 14,3 M (Opus) | US$ 8,55 | 17 a 25 M por repo num incremental |

Detalhes por passo:

1. **Start.** O `ws start` não chamou o Atlas. Os mapas rodaram em segundo plano (`.ws/mapas/*.split`), sem tokens do agente.
2. **`confere` e `registra`.**
   - Com uma suspeita forçada (um comentário no fim de `ValidarIdentificadorDeVolumeDeExpedicaoServico.cs`), o `confere` apontou `C-64: <arquivo>`.
   - O `registra C-64 vale` gravou o `conferidas.csv`. Um id inexistente foi recusado com aviso.
3. **Converge sem afirmações.** Nenhum subagente rodou. O arquivo novo (`Validacao99999/Marcador.cs`) virou lacuna no `lacunas.csv` (Ruling 15), e o commit só levou `docs/atlas/`.
4. **Converge com afirmações.** Um subagente Sonnet por repo:

   | Repo | Afirmações | Gasto |
   |---|---|---|
   | app.frontend | 1 | 0,26 M |
   | ecommerce.frontend | 1 | 0,28 M |
   | awx.monorepo | 1 | 1,02 M |
   | servidor.backend | 4 | 1,18 M |

   - Corrigidas: C-27, C-219, C-64 e C-125. Mantidas: C-37, C-43 e C-56.
   - A lacuna nova virou uma página mínima com a C-152, e a linha continua no `lacunas.csv`, sem duplicar.
   - A estimativa do plano era 7,05 M; o real foi 3,43 M.
5. **Execução manual.**
   - Preparação na `harness/teste-sync`:
     - uma mudança externa simulada (`TAMANHO_MAXIMO_DO_CAMPO` de 7 para 8 em `GerarCodigoCaixaExpedicaoCheckoutServico.cs`);
     - uma lacuna pequena (`Reserva.WMS3.Infraestrutura/Respositorios/InventarioRotativo`, 6 arquivos).
   - Revisão por lote, com subagentes Opus:

     | Repo | Afirmações | Gasto |
     |---|---|---|
     | servidor.backend | 3 | 1,20 M |
     | ecommerce.frontend | 18 | 2,51 M |
     | awx.monorepo | 17 | 3,47 M |

   - O mapeamento da lacuna gastou 5,73 M e o orquestrador, 1,4 M.
   - Publicou na `harness/teste-atlas-atualizacao` sobre a `harness/teste-sync`.
   - Numa branch nova com a publicação incorporada, o `confere` de `areas/checkout/rules-checkout.md` (revista) e de `areas/inventario-rotativo/rules-inventario-rotativo.md` (nova) disse `em dia`.

## Calibração (`tools/atlas/relevancia.ini`)

| Chave | Antes | Depois | Base |
|---|---|---|---|
| `tokens_revisao_base` | 1.500.000 | 400.000 | Com 0,15 M por afirmação, estima 2,65 M para o passo 3 (real: 2,74 M nos subagentes) e 6,9 M para o passo 4 (real: 7,18 M) |
| `tokens_por_afirmacao` | 150.000 | 150.000 | Mantido |
| `tokens_area` | 20.000.000 | 20.000.000 | Mantido por cautela: a área de 6 arquivos custou 5,7 M, mas as `src/app` abertas (592 e 713 arquivos) devem ficar perto de um do-zero |
| `tokens_do_zero` | 25.000.000 | 25.000.000 | Sem medição nova |
| `teto_chamadas_revisao` | 40 | 60 | Revisões completas usaram 46, 53 e 56 chamadas |

## Achados para o time do harness

1. **O teto de chamadas não segura os subagentes.** Três subagentes passaram do teto e relataram trabalho completo, e nada no fluxo detecta isso. Subir para 60 cobre o uso medido; a detecção continua manual.
2. **Afirmações que citam arquivos de outros repos multiplicam subagentes.** Mudar 2 arquivos do servidor acionou 4 repos, porque app.frontend, AWX e ecommerce.frontend citam esses arquivos. Isso é correto, mas custa uma base por repo.
3. **Itens de pasta largos marcam afirmações de arquitetura.** Um arquivo novo em `Reserva.WMS3.Aplicacao/Servicos/` deixou suspeitas a C-43 e a C-125, pelo item `Servicos/`. É o comportamento do Ruling 4: ruído, não omissão.
4. **Muitas pastas do servidor não são cobertas por nenhuma afirmação.** Há centenas delas, com 3 a 8 arquivos cada. Com o Ruling 15, cada mudança nelas vira uma lacuna, o que é barato no dia a dia, mas a lista de lacunas vai crescer.
5. **A estimativa da área não depende do tamanho.** A área de 6 arquivos custou 5,7 M, e uma `src/app` com centenas de arquivos deve custar 20 M ou mais. Fica como próxima melhoria estimar por número de arquivos.
6. **Os itens `?` do ecommerce.frontend viraram `[outdated]` (C-50 a C-57).**
   - O remapeamento do fluxo antigo, de 06/11, citava arquivos de checkout (ws-003) que não estão no código sincronizado.
   - A execução manual tratou isso como deveria. Confirmar com o time do ecommerce se a ws-003 ainda vai entrar.
7. **Subagentes sem Bash.**
   - Na sessão não interativa, o Bash e o Serena dos subagentes foram negados; eles terminaram só com Read, Grep e Edit.
   - Numa sessão de dev isso vira pedido de permissão.
   - O `prompt-revisao.md` poderia dizer para usar Read e Grep em vez de shell.
8. **O `ws start` ainda sugere o PR da base para o destino** (`harness/teste-sync` → `harness/teste-main`), embora o PR da `atlas/atualizacao` o substitua. É o minor M5 da revisão final.
9. **Achados de produto vistos pelos subagentes ficam fora do escopo.** São só registro, sem proposta de correção:
   - o validador da ACL no AWX aceita 7 dígitos, e a mudança simulada gerou 8;
   - `ExistePlanoEmAberto` sempre responde sim.

## Comparação com o 65594

No 65594, o Atlas levou cerca de 83% dos tokens da sessão: 65 M no start e 6,5 M no converge. Neste bug de teste:

- **Start:** o Atlas custa zero. A sessão inteira do diagnóstico ficou em 1,34 M.
- **Converge:** custa 0,19 M sem afirmações tocadas e 3,43 M com 7 afirmações em 4 repos.
- **Revisão completa:** o custo foi para a execução manual do time do harness, com 14,3 M para 38 afirmações e uma área pequena, e é escolhido e confirmado por quem roda.
