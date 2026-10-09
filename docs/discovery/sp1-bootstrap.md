# SP1: bootstrap do workspace (Task 8 do plano)

- **Data:** 2026-09-25
- **Ambiente:** Windows 11, Git 2.54.0.windows.1, credencial via GCM
- **Plano:** `docs/superpowers/plans/2026-09-24-sp1-workspace-multi-repo.md`
- **ADR:** `docs/adr/0001-workspace-git-subtree.md`, com os adendos 1 e 2
- **Repo:** `https://dev.azure.com/ARECO/AReCO/_git/industria-logistica.wms.workspace`
- **Clone local:** `C:\src\wms-workspace`, `main` em `6f7005b04`

## Resultados

| Medida | Valor |
|---|---|
| `ws add` dos 17 repos (com rede) | 189 s no total, de 3 a 33 s por repo (log: `sp1-bootstrap-add.log`) |
| Repos mais lentos | awx.monorepo (33 s), servidor.backend (27 s), ecommerce.backend e print-zebra (17 s) |
| Arquivos versionados no workspace | 18.386 |
| `ws maintain` (17 fetches) | 29 s, `sem deriva` |
| `git push -u origin main` | 22 s |
| `git clone` do workspace | 39 s; `.git` de 65 MB |
| `ws start` no clone novo (17 `subtree pull`) | 171 s, sem erro, branch criada |
| `.git` depois do primeiro `ws start` ou do `ws add` | 253 MB |
| Step 7: smoke test de `ws push` no picking.backend, a partir do clone novo | 13 s; a branch `chore/ws-smoke` descende do `main` do repo, com 1 commit à frente e só o `README.md` alterado; apagada em seguida |

## Achados

1. **O `.git` local passa de 65 MB para 253 MB no primeiro `ws start`.** O `subtree pull`/`add` baixa o histórico completo do `main` de cada repo para o object store local. O `--squash` deixa esse histórico fora dos commits do workspace: o remoto do workspace e um clone novo ficam em 65 MB. Mas cada clone que roda `ws start` acumula os históricos, e o total fica perto da soma dos `.git` dos 17 repos. A ADR previa isso só no remoto ("subtree com histórico completo" pesaria a soma). Não bloqueia; uma mitigação possível, como fetch raso no pull, fica para decisão futura.
2. **O `ws start` leva cerca de 3 min com 17 repos**, mesmo sem novidade nos repos. É o custo de 17 fetches sequenciais pela rede. A PoC local media de 1,4 a 4,4 s por repo; com rede e Azure DevOps ficou em cerca de 10 s por repo.
3. **O `ws add` sem conflito com `core.longpaths=true`**, inclusive nos 3 repos que exigem caminhos longos (ecommerce.frontend, servidor.backend e Fly).

## Pendências menores do `tools/ws` (revisão final, adiadas)

- M1 mensagem de erro do ws start sempre fala em conflito, mesmo em falha de rede/credencial
- M2 nome de branch inválido só é detectado depois do sync e do push do main
- M3 push do main rejeitado (outro dev enviou antes) deixa o main divergente sem orientação
- M4 stderr do rejoin escondido (sem efeito agora que não há rejoin real)
- M5 git log -1 escolhe por data; relógios defasados podem pegar squash antigo (agora só adia o marcador)
- M6 manifesto aceita repos/.., repos/. e prefixos duplicados; manifesto vazio gera erro confuso
- M7 cd "$(ws_root)" não para fora de um repo git; erro sai depois e ruidoso
- M8 ws maintain com prefixo do manifesto ainda não adicionado morre com fatal do git em vez de "rode ws add"
- M9 guarda ignora type change (arquivo de harness trocado por symlink)
- M10 teste de clone novo não exercita commit citado ausente do object store (o pull busca antes)

## Decisões tomadas na execução (ledger)

- Setup: Ruling: repo novo com commit inicial vazio no main e execução das Tasks 1–7 na branch feat/sp1-ws-tools — a skill proíbe implementar no main sem consentimento; o merge local no main fica para antes da Task 8, que já exige OK — custo se errado: um merge a mais no histórico.
- Setup: Ruling: Task 1 Step 1 (git init/config/mkdir) executado no setup — necessário para o ledger existir — custo: nenhum.
- Task 3: Ruling: test_maintain_marca_prefixo_intocado_sem_rodar_split usa ws start e ws push (Tasks 4 e 5) na segunda metade; falha na Task 3 só por ws_start ausente — mantido como está no plano; a Task 3 fecha com os outros 6 testes, e esse teste é reexecutado e tem de passar no fim da Task 5 — custo se errado: o marcador ficaria sem prova de push correto até a Task 5.
- Task 6: Ruling: os testes do ciclo passaram na primeira execução — esperado pelo plano (cobrem comportamento das Tasks 2–5, não há código novo); o RED deles foi observado na validação prévia do plano — custo se errado: um teste que não detecta regressão no ciclo.
- Task 7: Ruling: task só de docs, sem teste automatizado; o fechamento usa as verificações do Step 5 (comandos citados ⊆ add/maintain/push/start; os 4 arquivos existem) — custo se errado: doc com comando inexistente.
- Task 8: Ruling: revisão final do branch (Tasks 1–7) feita antes da Task 8 — a Task 8 é operacional, exige OK do usuário e deve rodar sobre código já revisado — custo se errado: nenhum além da ordem.
- Final: Ruling: C1 corrigido pela opção (b) do revisor (sem rejoin real) em vez de (a) (refs privadas no origin) — mais simples, e após cada ws start o prefixo volta a igualar o squash e é marcado — custo se errado: um prefixo que fique divergente do repo por muito tempo tem push lento até o próximo sync.
- Task 8: Ruling: Step 7 (smoke test com branch num repo de time) não executado — o plano exige OK específico e a resposta do usuário ("pode seguir com a Task 8") não respondeu a essa pergunta — custo se errado: o push real ao Azure fica sem validação até o primeiro uso. Resolvido em seguida: o usuário autorizou e o Step 7 foi executado.

## Teste exploratório: fetch raso e ls-remote (2026-09-25, código descartado)

Pergunta: o `ws start` pode pular os repos sem novidade e buscar só o necessário dos que mudaram, sem quebrar o `subtree pull`/`push` nem o clone novo?

| Medida (Azure DevOps real, clone novo, sem push) | Hoje | Variante |
|---|---|---|
| Descobrir quais repos mudaram (17 `ls-remote` em paralelo) | — | 2,5 a 6 s |
| `ws start` com 1 repo alterado (Fly) | 171 s (17 fetches completos) | 21 s |
| `ws start` sem novidade | cerca de 171 s | 13 s |
| `.git` depois do `ws start` | 253 MB | 67 MB |

- **Como a variante funciona:**
  1. `git ls-remote` em paralelo compara o `main` de cada repo com o `git-subtree-split` do último squash do prefixo.
  2. Só os repos que mudaram recebem `git fetch --depth=1 <url> <novo> <atual>`, em sequência. Dois fetches ao mesmo tempo disputam o `.git/shallow.lock`, e a primeira versão falhou por isso.
  3. Por fim, `git subtree merge --squash <novo>`.
- **Fetch por SHA:** o Azure DevOps aceitou `git fetch --depth=1 <url> <sha>`.
- **`ws push` num clone novo:** antes do push, busca raso os commits citados nos squashes que faltam no clone, para o `git subtree` não baixar o histórico completo.
- **Testes:** a suíte local (48 testes, com `uploadpack.allowAnySHA1InWant` nos remotos bare) passou toda com a variante.
- **Não testado:** `ws push` real para o Azure a partir de um clone raso. Os testes locais cobrem esse caminho.

## Implementado (2026-09-25): fetch raso e os 10 minors

- **Código:** workspace `main` em `c3c32305c4ce`, publicado. Nova lib `tools/ws/lib/remote.sh`; `start`, `add`, `maintain` e `push` passam a usar fetch raso. Os minors M1 a M10 foram corrigidos.
- **Testes:** 64 no total (16 novos). Todos passam; o de `--topo-order` também foi conferido falhando sem a correção.
- **M7:** já funcionava (o `cd ""` falha e o `set -e` para o script). Ficou um teste de regressão.
- **Medido no Azure DevOps:**
  - `ws start` no clone existente, com o Fly alterado e o push do `main`: 33 s (antes: 171 s).
  - `ws maintain`: 20 s, `sem deriva`, sem baixar nada.
  - Clone novo mais `ws start` até o push do `main`: 18 s, `.git` de 65 MB. O push foi bloqueado de propósito no teste.
- **Docs:** seções "Clone raso" e "Erros no `ws start`" em `docs/workspace.md`. Adendo 3 na ADR 0001.
