# SP7: Abertura dos PRs e revisão de código (design)

Data: 2026-10-21. Processo: `superpowers:brainstorming`. As decisões foram tomadas com o usuário na conversa de 2026-10-21. Este design muda a regra "o PR do workspace é aberto depois que todos os PRs dos repos forem mergeados", que vem do SP1 (ADR 0001 do workspace) e se repete no SP5, no SP6 e no SP6.2 (`docs/superpowers/specs/2026-10-15-ws-sync-design.md`, seção 1; `2026-10-20-fatias-pela-eap-design.md`, seção 3).

## 1. Intenção e porquê

Hoje, depois do `ws commit push` de uma feature, de um bug ou de um refactor, o dev faz tudo à mão:
- abre os PRs no Azure DevOps, um por repo enviado mais o do workspace. No exemplo do usuário, foram 3: o do workspace e os de duas subtrees;
- monta uma mensagem que liga esses PRs;
- posta a mensagem nos espaços de PR do time no Google Chat.

Depois, os outros devs leem o código de cada PR separadamente. Não há uma visão do conjunto: a conformidade com a spec, a consistência dos contratos entre os repos e os scripts de banco ficam por conta de quem revisa.

O usuário quer duas coisas:
1. que o harness abra os PRs e poste a mensagem por ele;
2. um comando de revisão que parta do PR do workspace e revise tudo, workspace e subtrees, deixando os achados como comentários nas linhas dos PRs.

## 2. Objetivos, não objetivos e antiobjetivos

**Objetivos:**
- no fim do `ws commit push` (feature, bug ou refactor), o harness **oferece** abrir os PRs para `homolog`: um por subtree enviada e um do workspace. Com o aceite, abre os PRs e posta a mensagem no espaço de homologação do Google Chat;
- um comando que o dev roda quando a homologação aprova, e que abre os PRs para `main` e posta no espaço de produção;
- um comando de revisão que recebe o link de um PR do workspace e revisa o conjunto. Os achados são mostrados ao revisor, que escolhe quais publicar como comentários nos PRs do Azure DevOps.

**Não objetivos:**
- escolher revisores: ficam as regras de cada repo no Azure DevOps;
- aprovar, reprovar, votar ou completar PRs, e ligar o auto-complete;
- descobrir sozinho que a homologação passou: quem decide é o dev, ao rodar o comando;
- integrar com o Azure Boards (work items) ou com as pipelines;
- revisar PRs que não vieram do harness (sem o PR do workspace).

**Antiobjetivos:**
- PR aberto ou mensagem postada sem o aceite do dev;
- comentário publicado no Azure DevOps sem a escolha do revisor;
- PR do workspace completado antes dos PRs das subtrees sem que isso esteja escrito claramente no PR;
- PRs duplicados para a mesma branch e o mesmo destino, ou comentários repetidos quando o comando roda de novo;
- token do Azure DevOps versionado no git.

## 3. Decisões tomadas com o usuário

| Decisão | Valor |
|---|---|
| Quando abrir | Logo depois do `ws commit push`, em feature, bug e refactor. O harness **oferece**, e o dev aceita ou recusa |
| Quais PRs | O de cada subtree que o `ws push` enviou e o do workspace, da mesma branch |
| Destinos | Dois: **`homolog`** (integra para testar no ambiente de homologação) e **`main`** (sobe para produção). O workspace também vai ter uma branch `homolog`, criada pelo usuário |
| Ramo de teste por repo | Todos os repos têm de ter a `homolog`, **exceto o Fly** (`integracoes.core.plataforma.backoffice.frontend`), cujo ramo de teste é o `develop`. Em 2026-10-21, sete repos ainda não tinham a `homolog` no origin: `print-zebra.utilitario.backend`, `wms.app.frontend`, `wms.hubprodutividade.backend`, `wms.servidor.backend`, `wms.tms-finished.backend`, `wms.tms.backend` e `wms.trakta.backend`. Os times precisam criá-la |
| Fatia sem chave (SP6.2) | Fica a regra do SP6.2, com uma mudança: **cada card** ganha os PRs dele para `homolog`, com o do workspace. A **promoção para `main` sai da branch de subida da fatia**, e não da branch de cada card |
| Branch apagada | O PR para `homolog` pede, em destaque, que a branch de origem **não seja apagada** ao completar. Se ela for apagada mesmo assim, a promoção a **recria** a partir do commit do PR completado |
| Ordem dos destinos | Os PRs para `homolog` nascem no fim do `ws commit push`. Os PRs para `main` só são abertos **depois que a homologação passar**, por um comando que o dev roda quando ela é aprovada |
| PR do workspace | É aberto **junto** com os das subtrees (não mais depois do merge delas). Ele lista os PRs das subtrees do mesmo destino e orienta a só completá-lo **depois** de completar todos eles |
| Aviso no Google Chat | Por webhook. Há dois espaços: o de **homologação** (recebe a mensagem dos PRs para `homolog`) e o de **produção** (recebe a dos PRs para `main`) |
| Revisão: entrada | O link do PR do workspace. O comando revisa o workspace e todas as subtrees listadas nele |
| Revisão: saída | Comentários nas linhas dos PRs no Azure DevOps, cada um no PR do repo onde está o código |
| Revisão: publicação | O revisor vê a lista de achados antes e escolhe quais publicar |
| Revisão: o que procura | (1) conformidade com a spec, o bug ou o refactor; (2) consistência dos contratos entre os repos (endpoint, fila, tabela, proc, view); (3) regras da casa (constitution, `AGENTS.md`, `docs/convencoes.md` de cada repo); (4) defeitos, casos de borda e testes que faltam; (5) scripts de banco: instruções de ordem de execução e um script de rollback para cada script |

## 4. Abertura dos PRs

### 4.1 Fluxo para `homolog`

Ponto de entrada: o passo 7 do `speckit-ws-commit-push` (e o passo 5 do `speckit-ws-bug-enviar` e do `speckit-ws-refactor-enviar`), que hoje lista os PRs a abrir à mão. Ele passa a fazer isto:

1. Mostra os PRs que vai abrir para `homolog`: um por repo enviado e o do workspace. O título e a descrição saem do que o harness já tem.
2. Pergunta se o dev quer abrir esses PRs e postar no espaço de homologação. Se ele recusar, mostra os links `pullrequestcreate` como hoje e termina.
3. Com o aceite, envia a branch do workspace ao origin, se ela ainda não estiver lá. Hoje o `ws push` envia só os repos. (Decisão minha: o PR do workspace precisa da branch no origin.)
4. Abre primeiro os PRs das subtrees e depois o do workspace, que leva os links deles.
5. Posta uma mensagem no espaço de homologação.
6. Mostra os links e diz o próximo passo: quando a homologação aprovar, rodar o comando de promoção (seção 4.2).

### 4.2 Fluxo para `main` (promoção)

Comando novo que o dev roda na branch da entrega quando a homologação aprova. O nome fica com o builder: algo como `ws pr main` no CLI e uma skill `/speckit-ws-promover` que o chama.

1. Descobre os repos da entrega pelos PRs para `homolog` da mesma branch (ou pelo mesmo cálculo do `ws push`, `ws/sync...HEAD`).
2. Se algum PR para `homolog` ainda está aberto, avisa e pergunta se o dev quer seguir.
3. **Branch apagada:** se a branch de origem não existe mais no origin de algum repo (ou do workspace), recria a branch a partir do commit de origem do PR para `homolog` completado (`lastMergeSourceCommit`) e avisa o que recriou. Se não achar o PR completado, para e diz qual repo ficou sem a branch.
4. Mostra os PRs para `main`, pede confirmação, abre os das subtrees e depois o do workspace, e posta no espaço de produção.
5. **Fatia sem chave do SP6.2:** a promoção roda na **branch de subida da fatia**, que junta os cards, e não na branch de cada card. Ela abre os PRs para `main` dessa branch, um por repo e um do workspace, e a tabela do workspace lista esses PRs. Os PRs continuam esperando a janela: o comando só os abre, e a ordem de completar segue o plano de subida. Os repos da entrega vêm do cálculo do `ws push` na branch de subida, não dos PRs para `homolog` dos cards. (Decisão minha.)

### 4.3 Título e descrição

**Título:** o mesmo padrão das mensagens de commit de hoje, por exemplo `feat(ws-NNN): <título>`, `fix(<slug>): <título>` e `refactor(<slug>): <título>`. Leva ` (r<k>)` nas revisões e o prefixo `[homolog]` nos PRs para `homolog`. (Decisão minha.)

**Descrição dos PRs das subtrees:**
- a origem: `specs/ws-NNN-*`, `bugs/<slug>/` ou `refactors/<slug>/`, com o resumo tirado do `spec.md`, do `assess.md` ou do `assessment.md`;
- o link do PR do workspace do mesmo destino. Por isso, os PRs das subtrees são atualizados depois que o do workspace é aberto;
- a lista dos commits da branch naquele repo.

**Descrição do PR do workspace:**
- a mesma origem e o mesmo resumo;
- uma tabela com os PRs das subtrees do mesmo destino (repo e link);
- o aviso, em destaque: "Complete este PR só depois que todos os PRs acima estiverem completados".

**Todos os PRs para `homolog`** (subtrees e workspace) levam também, em destaque: "Não apague a branch de origem ao completar: o PR para produção sai dela".

A tabela segue um formato fixo, que o comando de revisão lê (seção 5.1).

### 4.4 Mensagem no Google Chat

Uma mensagem por destino e por entrega. Ela leva:
- o título e o tipo da entrega;
- o autor;
- o link do PR do workspace;
- os links dos PRs das subtrees.

O formato do card ou do texto do Chat fica com o builder.

### 4.5 Rodar de novo

- Se já existe um PR aberto da mesma branch para o mesmo destino, o harness não abre outro: só atualiza a descrição. Isso cobre um segundo `ws commit push` na mesma branch, por exemplo depois da revisão.
- Se a entrega passou a tocar um repo novo, o harness abre só o PR dele e atualiza a tabela do PR do workspace.
- Num segundo envio, o Chat não recebe mensagem nova, a menos que o dev peça. (Decisão minha.)
- Uma revisão de feature (`-r<k>`) tem branch nova, portanto PRs novos.

### 4.6 Acesso e configuração

- **Azure DevOps:** pelo `az` CLI com a extensão `azure-devops`, que já está instalada na máquina do usuário (`az repos pr`). O que o `az repos pr` não cobre vai pelo `az devops invoke` ou pela REST: comentário de linha (threads) e atualização da descrição. Cada um usa a própria credencial, então o PR sai em nome de quem roda. Se o `az` não estiver autenticado, o harness diz como entrar e não abre nada. (Decisão minha.)
- **Webhooks:** as URLs ficam **versionadas no workspace** (decisão do usuário), num arquivo de configuração do harness com `homolog=` e `producao=`. O lugar exato fica com o builder. Assim, todo dev já as recebe no clone. Se a URL estiver vazia ou a postagem falhar, o harness mantém os PRs abertos, avisa que não postou e mostra o texto da mensagem para o dev colar.
- **Destinos:** `main` para produção, como o `WS_DESTINO` de hoje. O ramo de teste é **por repo**: `homolog` por padrão e `develop` no Fly. Ele fica registrado num lugar versionado no workspace (uma coluna nova no `workspace.repos` ou um arquivo próprio, à escolha do builder), para que o próximo repo fora do padrão não exija mudança de código.
- **Ramo de teste ausente:** antes de abrir qualquer PR, o harness confere se o ramo de teste existe no origin de cada repo da entrega e do workspace. Se faltar em algum, não abre nenhum PR, diz quais repos estão sem o ramo e que o time do repo precisa criá-lo, e mostra os links `pullrequestcreate` para quem quiser abrir à mão. (Decisão minha: nada de PRs pela metade.)

### 4.7 O que muda no que já existe

- A regra "o PR do workspace vem depois que todos os PRs dos repos forem mergeados" passa a ser "o PR do workspace é aberto junto e completado por último". Ela muda nos seguintes lugares:
  - o `speckit-ws-commit-push`, o `speckit-ws-bug-enviar` e o `speckit-ws-refactor-enviar`;
  - o `ws-bug-registro.sh`;
  - a mensagem final do `ws push` (`push.sh`, "abra um PR por repo…");
  - as camadas de documentação em `docs/harness/`;
  - um adendo na ADR 0001.
- **SP6.2:** na fatia sem chave, "a branch integrada na `homolog` do repo para teste (passo do time, fora do harness)" passa a ser o PR do card para `homolog`, aberto pelo harness, com o do workspace. A branch de subida e o PR do workspace dela para `main` depois da janela continuam como no SP6.2, e a promoção (seção 4.2) roda nessa branch. O SP6.2 já está no `main` do workspace (PR 17222, completado em 2026-10-21), então quem implementar este design ajusta o `refactor-enviar` e os textos dele diretamente.
- **`homolog` do workspace:** o usuário cria a branch. O harness não a cria nem a sincroniza. O `ws sync` continua levando o `main` à `ws/sync`, e a `homolog` recebe a sincronização pelos próprios PRs das entregas.

## 5. Revisão de código

### 5.1 Entrada

Um comando de Claude Code, que é uma skill porque precisa do agente. O nome fica com o builder, algo como `/ws-revisar <link do PR do workspace>`. Quem roda é o colega que vai revisar, no workspace dele.

1. Lê o PR do workspace (link, destino, branch de origem) e a tabela dos PRs das subtrees na descrição. Se a tabela não existir, diz que o PR não veio do harness e para.
2. Busca a branch do workspace. Ela já contém o código de todas as subtrees em `repos/<repo>/`, então o código da revisão vem do workspace. O diff de cada subtree é o de `repos/<repo>/` contra o merge-base com a `ws/sync`, a mesma base do `ws push`, e não contra o destino. A `homolog` do workspace não recebe a sincronização da `ws/sync`, então um diff contra ela traria código de outras pessoas. (Decisão minha.)
3. Lê a origem da entrega (`specs/ws-NNN-*`, `bugs/<slug>/`, `refactors/<slug>/`) e, nas fatias, o plano de subida.

### 5.2 O que revisa

| Ponto | O que procura | Onde se apoia |
|---|---|---|
| Conformidade | O código faz o que a spec e as tasks (ou o diagnóstico do bug, ou o do refactor) pedem, nem mais nem menos | `spec.md`, `tasks.md`, `assess.md`, `assessment.md` |
| Contratos entre repos | Se um endpoint, fila, tabela, proc ou view mudou num repo, quem consome o contrato nos outros repos acompanhou, mesmo que esse repo não esteja na entrega | Atlas (`atlas-consultar`) e as arestas de `docs/sistemas/` |
| Regras da casa | Constitution, `AGENTS.md` e o `docs/convencoes.md` do repo | os próprios arquivos |
| Defeitos | Bugs, casos de borda e testes que faltam | o diff e o código em volta |
| Scripts de banco | Todo script de banco da entrega diz a ordem de execução e tem um script de rollback | o diff (o builder define como reconhecer os scripts pelas convenções de cada repo) |

Como dividir a revisão entre agentes, e se reaproveita a skill `code-review`, fica com o builder.

### 5.3 Lista para o revisor

Ao fim, o comando mostra a lista de achados. Cada um traz:
- o ponto (dos cinco);
- a gravidade;
- o repo e o PR;
- o arquivo e a linha;
- o texto do comentário.

O revisor escolhe quais publicar. Se quiser, edita o texto antes. Só os escolhidos vão para o Azure DevOps.

### 5.4 Publicação

- **Comentário de linha:** vai no PR do repo onde está o código. O caminho `repos/<repo>/x` do workspace vira `x` no PR da subtree. O que é do workspace (`specs/`, `bugs/`, `refactors/`, `docs/`) vai no PR do workspace.
- **Achado sem linha** (por exemplo, "falta o rollback" ou "o repo X não acompanhou o contrato"): vira um comentário geral no PR mais próximo. Se o repo não está na entrega, o comentário vai no PR do workspace. (Decisão minha.)
- **Linha fora do diff do PR:** vira um comentário geral no mesmo PR, citando o arquivo e a linha. (Decisão minha.)
- **Autoria:** os comentários saem com a credencial do revisor e levam uma marca discreta de que vieram da revisão do harness.
- **Voto:** o harness não vota, não aprova e não reprova.

### 5.5 Rodar de novo

Se o revisor roda o comando de novo, por exemplo depois de uma correção do autor, os achados iguais aos que já estão publicados no PR (abertos ou resolvidos) não voltam à lista. A identificação é pela marca da seção 5.4. (Decisão minha.)

### 5.6 Qual par revisar

O comando aceita o PR do workspace de qualquer destino. O caminho normal é revisar o par de `homolog`, que é o primeiro a existir. O par de `main` sai da mesma branch, então revisá-lo de novo repete trabalho. (Suposição minha, não confirmada pelo usuário.)

## 6. Testes

Seguem o padrão dos testes do `tools/ws` (origin `bare` local). As chamadas ao Azure DevOps e ao Google Chat são simuladas por um `az` falso no `PATH` e por um servidor ou script falso para o webhook. Os testes cobrem:
- oferta recusada: nada é aberto e os links aparecem como hoje;
- abertura para `homolog`: PRs das subtrees e do workspace, com a tabela e o aviso;
- uma postagem no espaço certo;
- segundo envio na mesma branch: nenhum PR duplicado e a descrição atualizada;
- repo novo na entrega;
- promoção: PRs para `main`, aviso de PR para `homolog` ainda aberto e postagem no espaço de produção;
- promoção com a branch de origem apagada: recriação a partir do commit do PR completado;
- promoção na branch de subida de uma fatia sem chave;
- ramo de teste por repo: o `develop` do Fly; repo sem o ramo, caso em que nenhum PR é aberto;
- webhook vazio ou com falha na postagem, e `az` sem autenticação;
- revisão: leitura da tabela, mapeamento dos caminhos de `repos/<repo>/` para o PR certo e ausência de repetição na segunda passada.

Por fim, uma validação real no Azure DevOps, com uma branch de teste num repo e no workspace, os dois webhooks de teste e uma revisão publicada, como no SP1 e no SP2.

## 7. O que fica com o builder

- os nomes dos comandos e das skills;
- o formato da mensagem do Chat;
- o formato da tabela no PR do workspace;
- como a revisão se divide entre agentes;
- como reconhecer scripts de banco em cada repo;
- a escala de gravidade;
- os detalhes da API do Azure DevOps (threads, iterações) e do webhook do Google Chat.
