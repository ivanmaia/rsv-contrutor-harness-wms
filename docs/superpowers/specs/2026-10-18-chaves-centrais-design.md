# SP6.1: Chaves centrais das fatias de desacoplamento (design)

Data: 2026-10-18. Processo: `superpowers:brainstorming`. Decisões tomadas com o usuário na conversa de 2026-10-18, depois do merge do SP6 (PRs 17131 e 17139 do workspace). Este design muda uma decisão do SP6 (`docs/superpowers/specs/2026-10-16-sp6-refactor-design.md`, seção 4.3): a chave de cada fatia deixa de ser um mecanismo escolhido por repo e passa a morar num lugar central.

## 1. Intenção e porquê

No SP6, cada fatia de desacoplamento tem a sua **chave**: o mecanismo que escolhe entre o caminho antigo, o modo de convivência e o caminho novo. A chave fica no app consumidor, e o mecanismo varia por repo (configuração no AWX, `appSettings` ou tabela de parâmetros no legado). O harness só exige que ela exista, comece em "antigo" e tenha o modo de virar escrito no `assessment.md`.

Isso dá duas dores ao **líder do time**, que é quem vira as chaves em produção (ou manda o dev virar):
1. para cada fatia, ele precisa saber em qual app, em qual arquivo e com qual nome está a chave, e isso se repete por fatia e por ambiente;
2. na maioria dos apps, virar a chave depende de deploy. A busca de 2026-10-18 nos 18 repos confirmou: nenhum usa ferramenta de feature flag; o `Web.config` do servidor recicla o app e é sobrescrito pela esteira; os apps no GKE só mudam configuração com sync do ArgoCD e reinício do pod.

Além disso, o harness não responde **o que está rodando agora em produção**. A tabela de fatias e o `ws refactor pendentes` mostram o que foi registrado nos PRs (os marcos), não o estado das chaves. O M2 (convivência) nem é registrado.

O usuário quer **um lugar único** onde o líder vê todas as chaves, o modo de cada uma em produção, e vira qualquer uma sem deploy; e **um documento central** que diga onde cada chave é usada no código.

## 2. Objetivos, não objetivos e antiobjetivos

**Objetivos:**
- uma fonte única das chaves, lida em produção por todos os consumidores;
- virar uma chave sem deploy, por uma tela, com histórico de quem virou, quando e por quê;
- a tela mostra o que está valendo agora;
- um documento central no workspace com todas as chaves e onde cada uma é lida, mantido pelos comandos de refactor;
- o harness passa a exigir a chave central em toda fatia de desacoplamento.

**Não objetivos:**
- chave por armazém ou por empresa: cada chave vale para a operação inteira;
- uma ferramenta pronta de feature flag (Unleash, Flagsmith etc.): considerada e descartada pelo usuário;
- chaves para features comuns ou bugs: o escopo são as fatias de desacoplamento;
- o harness ler o estado das chaves em produção: o harness não tem acesso a produção, e a tela é o lugar disso.

**Antiobjetivos** (o que faria isto falhar mesmo funcionando):
- duas fontes da verdade: alguém vira a chave num lugar e outro lugar desfaz;
- um app rodar num modo diferente do configurado sem que ninguém saiba;
- o líder ainda precisar abrir arquivo de configuração ou pedir deploy para virar uma chave.

## 3. Decisões tomadas com o usuário

| Decisão | Valor |
|---|---|
| Onde as chaves moram | **Opção B:** uma tabela de chaves num contexto do AWX, o `AWX.ERP.Connector` (o ACL do LINX, dono do desacoplamento). Descartadas: tabela no banco do legado WMS (opção A, cria dependência do AWX no legado, ao contrário da migração) e ferramenta pronta de feature flag (opção C) |
| Fonte da verdade | O `ERP.Connector` é a **única fonte** |
| Cópia no legado | A `AWX.IntegracaoLegadoWMS` mantém uma cópia das chaves no banco do WMS legado, **só para leitura do legado**: evita muitas chamadas HTTP e deixa o legado funcionando com o `ERP.Connector` fora do ar. Ninguém escreve na cópia |
| Leitura | O legado lê a cópia local. Os contextos do AWX e o `servicos-linx-wms` consultam o `ERP.Connector` (o `servicos-linx-wms` já só fala com ele) |
| `ERP.Connector` fora do ar | Para quem consulta o `ERP.Connector`: **erro, e a operação trava**, mesmo com a chave em "antigo". O usuário aceitou o custo de o caminho antigo ganhar essa dependência |
| Conteúdo da chave | O **modo** da fatia: "antigo", o modo de convivência ou "novo"; não ligado/desligado |
| Granularidade | Uma chave vale para a **operação inteira** |
| Quem vira | O líder do time, ou o dev a comando dele |
| Como vira | **Normal:** uma **tela no WMS legado** (não no Fly), que lê e grava no `ERP.Connector` pela `IntegracaoLegadoWMS`, com histórico. **Emergência:** UPDATE direto no banco do `ERP.Connector` |
| Criação da chave | **No PR da fatia:** o INSERT da chave em "antigo" vem junto do código, e o diagnóstico tem de prevê-lo |
| Documento central | Um arquivo no workspace com todas as chaves e onde são usadas, **mantido pelos comandos** de refactor |
| Remoção da chave | **Separada e posterior ao desacoplar:** o desacoplar só tira a leitura; a chave sai depois, com o consumidor desacoplado já em produção |
| `wms.conector.backend` | **Fora por enquanto:** não pode ser consumidor de fatia com chave central |
| Como o produto é feito | A tabela, a tela e a leitura nos apps são **uma feature nova do workspace**, feita com o próprio harness: `/speckit-specify` e os 9 passos |
| Corte deste design | Cobre a decisão (ADR) e as mudanças no harness. O produto é descrito no nível do que o ADR exige, e o time o especifica pela feature |

## 4. As três partes e a ordem

1. **ADR 0002** no workspace (`docs/adr/0002-chaves-centrais.md`): a decisão da seção 3, pela regra IV da constitution (cruza repos). Rascunho na seção 5.
2. **Produto:** a feature do workspace que constrói a tabela, a cópia, a tela e a leitura (seção 6).
3. **Harness:** template, comandos, documento central, doc e apresentação (seção 7).

**Ordem:**
- O ADR vem primeiro: as outras duas partes dependem do nome e do formato da chave que ele fixa.
- A parte 3 pode ser construída em paralelo com a 2, mas só entra no `main` do workspace **depois** de a feature do produto estar mergeada nos repos e em produção. Antes disso, nenhuma fatia teria onde criar a chave. Hoje não há fatia real no `main` do workspace (não existe `refactors/`), então nada fica parado.
- O ADR também preenche o "Padrão do caminho novo" do desacoplamento do LINX, junto da arquitetura de transição explicada pelo usuário (`docs/discovery/sources/arquitetura-transicao-linx.md`), que ainda não tem ADR. Juntar as duas no mesmo ADR é decisão do builder (seção 9).

## 5. Rascunho do ADR 0002

O texto final segue o formato do ADR 0001 (status, data, subprojeto, contexto, decisão, consequências) e é aprovado por humano antes do merge.

**Contexto:** a seção 1 deste design, mais o resultado da busca de 2026-10-18: nenhum repo tem feature flag; a tabela `WMS.dbo.Configuracao` do servidor muda sem deploy, mas fica no legado e não tem histórico; o `ERP.Connector` hoje **não tem banco próprio**.

**Decisão:**
1. **Fonte única:** uma tabela de chaves no `AWX.ERP.Connector`, com banco próprio do contexto, no padrão de persistência dos outros contextos do AWX. Uma linha por chave: nome, modo atual, fatia e data da última mudança.
2. **Modos:** `antigo`, `paralelo`, `sombra` e `novo`. A troca direta é a chave ir de `antigo` para `novo`. A chave aceita os quatro; o modo previsto da fatia está no `assessment.md`, e escolher o modo certo na tela é responsabilidade de quem vira.
3. **Histórico:** toda mudança grava valor anterior, valor novo, quem, quando e o motivo. A mudança por UPDATE direto também é registrada, com o usuário do banco no lugar de quem.
4. **API no `ERP.Connector`:** listar as chaves, ler uma chave, mudar o modo (com quem e motivo) e ler o histórico. Os contextos do AWX e o `servicos-linx-wms` leem por ela.
5. **Cópia no legado:** a `IntegracaoLegadoWMS` mantém uma tabela de chaves no banco do WMS legado, só leitura para o legado, com a hora da última sincronização por chave. Ninguém escreve nela fora da sincronização.
6. **Tela no WMS legado:** no `Reserva.WMS3` Web (`repos/industria-logistica.wms.servidor.backend`). Lista as chaves, o modo de origem, o modo da cópia do legado e a hora da última sincronização, e o histórico. Vira o modo chamando a `IntegracaoLegadoWMS`, que grava no `ERP.Connector`; a tela nunca grava na cópia. Pede o motivo a cada mudança.
7. **Falha:** quem consulta o `ERP.Connector` e não tem resposta, ou não acha a chave, devolve erro e a operação para, em qualquer modo. O legado lê a cópia e não depende do `ERP.Connector` no momento da leitura.
8. **Emergência:** UPDATE direto no banco do `ERP.Connector`, nunca na cópia. A sincronização leva a mudança ao legado.
9. **Ciclo de vida:** a chave nasce no PR da fatia, por migração do banco do `ERP.Connector`, em `antigo`. Sai num passo próprio, **depois** do desacoplar (M4) estar em produção: o desacoplar só tira a leitura do consumidor, e a remoção da chave vem depois, em PR separado.

**Consequências:**
- O caminho antigo de um consumidor no AWX passa a depender do `ERP.Connector` (aceito pelo usuário).
- O `ERP.Connector` ganha banco e uma responsabilidade que não é de tradução com o LINX. Quando o legado sair, a cópia sai junto, e a fonte já está no AWX.
- Ordem de deploy: a chave tem de existir no `ERP.Connector` antes de o consumidor ir para produção, e só pode sair depois que o consumidor deixar de lê-la (seção 7.4).

## 6. O produto, como feature do workspace

O produto é feito pelo fluxo de feature do harness (camada 1, "Uma feature, do início ao PR"), pelo time, depois do ADR aprovado. Este design não especifica a feature; ele fixa o que ela tem de entregar para o harness funcionar.

**Repos que a feature toca** (a confirmar pelo `/speckit-plan` com o Atlas):
- `repos/industria-logistica.wms.awx.monorepo`: o `AWX.ERP.Connector` (banco, tabela, histórico, API) e a `AWX.IntegracaoLegadoWMS` (endpoints da tela e sincronização da cópia). O AWX tem Spec Kit e constitution próprios: vale a camada 3, "Repo com Spec Kit próprio (AWX)";
- `repos/industria-logistica.wms.servidor.backend`: a cópia no banco do legado, a leitura da chave pelo legado e a tela no `Reserva.WMS3` Web;
- `repos/integracoes.wms.servicos-linx-wms.monorepo`: a leitura da chave pelo `ERP.Connector`, se alguma fatia tiver peça de decisão do lado LINX.

**O que o harness precisa da feature** (contrato com a parte 3):
- o nome da tabela de chaves e o formato da migração que cria uma chave (o template que o `/speckit-refactor-apply` vai seguir);
- o formato da migração que remove uma chave;
- como cada tipo de consumidor lê a chave: uma biblioteca ou um trecho padrão no legado, nos contextos do AWX e no `servicos-linx-wms`. O `apply` chama isso, em vez de escolher um mecanismo por fatia.

Esses três itens vão para a doc do harness (camada 3) quando a feature for mergeada, e são o ponto de encontro com a parte 3.

**Sugestão de entrada para o `/speckit-specify`** (o time ajusta): "Chaves centrais das fatias de desacoplamento do LINX, conforme o ADR 0002: tabela de chaves com histórico no AWX.ERP.Connector, cópia somente leitura no banco do WMS legado mantida pela AWX.IntegracaoLegadoWMS, tela no WMS legado para ver e virar as chaves, e leitura das chaves pelo legado, pelos contextos do AWX e pelo servicos-linx-wms, com erro quando o ERP.Connector não responde."

## 7. Mudanças no harness

Todas no workspace, numa branch `harness/` própria, com testes na suíte de `tools/ws/tests`, como no SP6.

### 7.1 Nome da chave
A chave de uma fatia se chama como a fatia: o **slug** (por exemplo, `90301-movimenta-vendas`). O slug já é único, validado e não termina como as branches de rodada e validação. (Decisão minha; seção 9.)

### 7.2 `/speckit-refactor-assess` e o modelo do `assessment.md`
- O campo **Chave** passa de `<mecanismo e nome>` para: `<slug> na tabela de chaves do ERP.Connector; começa em "antigo"`, mais os pontos do consumidor onde a chave é lida.
- O diagnóstico prevê, no caminho novo, a **migração que cria a chave** no `ERP.Connector` como parte da fatia. Ela entra mesmo quando a fatia não muda mais nada no AWX.
- O "Padrão do caminho novo" do documento do desacoplamento cita o ADR 0002.

### 7.3 `/speckit-refactor-apply`
- Antes do consumidor, cria a migração da chave em `antigo` no `ERP.Connector`, no formato que a feature do produto definir.
- No consumidor, a leitura da chave usa o padrão do produto para aquele tipo de app. O texto atual ("a chamada à primeira peça do caminho novo, atrás da chave") fica, com a chave central.
- Acrescenta a linha da chave no documento central (7.5).
- O `apply.md` registra a migração criada e onde a chave é lida.

### 7.4 `/speckit-refactor-desacoplar`
- Remove a leitura da chave do consumidor, como hoje. **Não** remove a chave do `ERP.Connector` (decisão do usuário: remoção separada e posterior).
- Marca a linha da chave no documento central como **para remover**, com a data do M4.
- O `desacoplar.md` diz que a chave só sai depois que o consumidor desacoplado estiver em produção.

### 7.4b Remoção da chave, depois do M4
- Um comando novo da extensão `refactor`, `/speckit-refactor-remover-chave <slug>`, roda quando o PR do desacoplar já estiver em produção. Ele cria a branch `refactor/<slug>-chave` (pelo `ws-refactor-start.sh`, com um modo novo), a migração que remove a chave do `ERP.Connector` e tira a linha do documento central; o envio segue pelo `speckit.ws.refactor-enviar`, num evento `after_refactor_remover-chave`.
- Portão: o comando pergunta ao dev se o consumidor desacoplado já está em produção e só segue com a confirmação; se a chave ainda tiver leitura no código do consumidor (busca pelo nome), para.
- O `ws refactor pendentes` lista as chaves "para remover" do documento central, com o passo `/speckit-refactor-remover-chave <slug>`.
- O sufixo `-chave` entra no fim de slug reservado (como `-r<n>` e `-desacoplar`).
- A forma exata (comando próprio, nome do evento, modo do start) é decisão minha e pode mudar no plano; a decisão do usuário é a remoção separada e posterior.

### 7.4a `/speckit-refactor-verify` e `/speckit-refactor-validar`
- O "como virar a chave em cada modo" do `apply.md` e da seção "Para retomar" passa a ser: pela tela no WMS legado, com o nome da chave.
- O `validar` com falha manda voltar a chave para `antigo` pela tela.
- Uma rodada nova reaproveita a chave da fatia: nada muda no `ERP.Connector`.

### 7.5 Documento central: `refactors/chaves.md`
- Uma tabela com uma linha por chave: **Chave** (o slug), **Fatia** (link para `refactors/<slug>/`), **Desacoplamento** (link para o documento), **Consumidor** (o repo), **Onde é lida** (os arquivos do consumidor) e **Situação** (`em uso` ou `para remover desde <data do M4>`).
- Mantido pelos comandos: o `apply` acrescenta ou atualiza a linha, o `desacoplar` marca `para remover` e o `remover-chave` tira a linha. Ninguém edita à mão.
- Sem coluna de marco nem de modo: o marco está na tabela de fatias e o modo em produção está na tela. (Decisão minha; seção 9.)
- Uma rodada nova (`-r<k>`) atualiza a linha em vez de duplicar.

### 7.5a Consumidores aceitos
- **Aceitos:** o legado (`servidor.backend`, pela cópia), os contextos do AWX e o `servicos-linx-wms` (pelo `ERP.Connector`). O `servicos-linx-wms` entra como consumidor quando a decisão do caminho for do lado LINX. (Decisão minha, seguindo a proposta inicial do usuário de o lado LINX ler as chaves pelo `ERP.Connector`.)
- **Fora por enquanto (decisão do usuário):** o `wms.conector.backend`. O `/speckit-refactor-assess` recusa a fatia cujo consumidor é ele, com o motivo, e diz que ela espera um jeito de o conector ler a chave.

### 7.6 O que não muda
- Os marcos M1, M3, M3-falhou e M4, o `ws refactor marco` e a tabela de fatias continuam iguais. O M2 continua sem registro no harness: a tela no legado é o lugar de saber se a chave foi virada.
- `ws refactor pendentes` e o aviso do `ws start` continuam com o mesmo texto.
- Os modos de convivência da camada 3 continuam os mesmos.

### 7.7 Constitution e doc
- **Regra VII ou regra II:** acrescentar que a chave de uma fatia mora na tabela central do ADR 0002 e nasce e sai pelos PRs da fatia. A redação e a versão (1.3.0 → 1.4.0) ficam com o builder; a emenda pede PR aprovado por humano, como toda mudança da constitution.
- **Camada 1** ("Uma fatia de desacoplamento"): o passo 2 passa a dizer que o time vira a chave pela tela no WMS legado.
- **Camada 2:** entradas para a operação que trava porque o `ERP.Connector` não responde ou porque a chave não existe (ordem de deploy errada), apontando para a camada 3.
- **Camada 3** ("Convivência e a chave"): a tela, a emergência por UPDATE, o documento central e o formato das migrações.
- **Camada 4:** o `refactors/chaves.md` na tabela "Onde fica cada coisa".
- **Apresentação** (`docs/discovery/sp4-apresentacao/`): o slide da fatia e o dos marcos citam a tela e o documento central.

### 7.7a Como os comandos citam o formato do produto
Os comandos não copiam o nome da tabela nem o texto das migrações: apontam para uma seção da camada 3 ("Chaves centrais"), que a feature do produto preenche quando for mergeada. Assim a parte 3 pode ser construída e testada antes do produto; os testes conferem que os comandos apontam para essa seção e que ela existe. (Decisão minha.)

### 7.8 Testes do harness
No padrão do SP6: testes de texto para o template e os comandos (a chave central no `assessment-template.md`, a migração no `apply`, a remoção e a ordem de deploy no `desacoplar`, o `refactors/chaves.md` nos dois), referências da doc e a extensão instalada igual à fonte. Um ponta a ponta com agente fica para depois do produto em produção, na primeira fatia real.

## 8. Restrições

- **Regra II:** o objeto do banco `Reserva` não muda enquanto outro sistema o acessar. A tabela de chaves não é objeto do Reserva: fica no banco do `ERP.Connector` e na cópia do legado.
- **Regra IV:** o ADR é aprovado por humano antes do merge.
- **AWX:** a feature segue a constitution e o Spec Kit do AWX quando tocar o monorepo (camada 3). Dívidas de conformidade do AWX valem para a feature, porque ela não é refactor.
- **Harness:** mudanças em `tools/`, `.specify/`, `.claude/` e `AGENTS.md` vão numa branch `harness/` própria, nunca dentro de uma feature (regra 3 da camada 1).
- **Processo:** o workspace é mexido pelo `ws`; os repos recebem as mudanças pelo `ws push`, com PR por repo e depois o do workspace.

## 9. Decisões minhas (para o usuário conferir) e o que fica com o builder

**Decisões minhas:**
- O nome da chave é o slug da fatia (7.1).
- O documento central fica em `refactors/chaves.md` e não tem coluna de marco nem de modo (7.5).
- A remoção é um comando próprio, `/speckit-refactor-remover-chave`, com branch `refactor/<slug>-chave` e lembrete no `ws refactor pendentes` (7.4b).
- O `servicos-linx-wms` é aceito como consumidor (7.5a).
- Os comandos apontam para uma seção da camada 3 em vez de copiar o formato do produto (7.7a).
- A chave não guarda o modo de convivência previsto e aceita os quatro modos (5, item 2). Assim, uma rodada nova (`-r<k>`) que troca o modo reaproveita a chave sem migração.
- A tela mostra, além do modo de origem, o modo da cópia do legado e a hora da última sincronização: é o "o que está rodando" do legado (5, item 6).
- O UPDATE de emergência fica registrado com o usuário do banco (5, item 3).
- A chave que não existe no `ERP.Connector` é tratada como falha: erro e a operação para (5, item 7).
- A parte 3 só entra no `main` depois do produto em produção (4).

**Com o builder:**
- o banco e a tecnologia de persistência do `ERP.Connector`, no padrão dos outros contextos do AWX;
- como a `IntegracaoLegadoWMS` sabe que uma chave mudou (aviso do `ERP.Connector`, evento ou leitura periódica) e o intervalo máximo até a cópia ficar igual à origem;
- se os contextos do AWX guardam a chave em cache e por quanto tempo, respeitando "sem resposta, erro";
- quem pode usar a tela (perfil no `Reserva.WMS3`);
- juntar ou não o "Padrão do caminho novo" do LINX no ADR 0002;
- a redação da emenda na constitution.

## 10. Em aberto

- Nada que mude o que se constrói. O jeito de o `wms.conector.backend` ler a chave fica para quando ele tiver fatias.
