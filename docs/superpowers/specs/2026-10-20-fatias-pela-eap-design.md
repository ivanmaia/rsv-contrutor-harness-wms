# SP6.2: Fatias de desacoplamento pela EAP (design)

Data: 2026-10-20. Processo: `superpowers:brainstorming`. Decisões tomadas com o usuário na conversa de 2026-10-20, depois de uma reunião dele com o time (Hugo, Gabriel e Diego) sobre a subida das fatias para produção. Este design muda a unidade de fatia do SP6 (`docs/superpowers/specs/2026-10-16-sp6-refactor-design.md`, seção 4.1) e parte do SP6.1 (`docs/superpowers/specs/2026-10-18-chaves-centrais-design.md`, ADR 0002 do workspace).

## 1. Intenção e porquê

No SP6, uma fatia é **um consumidor saindo de um objeto** do banco `Reserva`, com uma entrega de código e, desde o SP6.1, uma chave central. O time já fez o planejamento do desacoplamento do LINX numa **EAP** (planilha "EAP Desacoplamento", item 1 e subitens), e lá o recorte é outro: a unidade é um **processo de negócio**, como 1.1.3 Registro de Notas Fiscais de Recebimento, 1.1.4 Contagem, 1.2 Auditoria, 1.3.4.2 Faturamento Automático B2C. Um processo toca vários objetos do `Reserva` e vários sistemas (apps, jobs, AWX, LINX), e precisa virar **de uma vez**, por consistência de dados e para a operação mudar o processo inteiro junto.

O time também concluiu que **nem toda fatia precisa de chave**: se o caminho novo mantém os contratos e a subida é fácil de gerenciar e de reverter, a troca é direta, numa janela combinada com a operação. E pediu um **plano de subida** por fatia (cenários operacionais, janela, scripts de banco, ordem de deploy, reversão) e um lugar para acompanhar cada fatia até o código acoplado sair.

O usuário quer que o harness siga a EAP: a fatia é definida no planejamento (o card do item da EAP, refinado pelo time), e cada refactor declara a qual fatia pertence.

## 2. Objetivos, não objetivos e antiobjetivos

**Objetivos:**
- a fatia é um item da EAP, identificado pelo código dele, e reúne um ou mais refactors (cards), em vários repos e sistemas;
- dois tipos de fatia: **com chave** (uma chave central por fatia, lida por todos os sistemas da fatia) e **sem chave** (troca direta, com o código antigo saindo na própria entrega);
- um **plano de subida** por fatia, montado pelo agente e revisado e completado pelo time;
- um **documento das fatias** no workspace, mantido pelos comandos, com o estado de cada fatia e o que falta para o código antigo sair;
- o `ws refactor pendentes` mostra as fatias e o próximo passo de cada uma.

**Não objetivos:**
- o painel para o líder (página publicada lendo o documento das fatias e o estado dos PRs no Azure DevOps): fica para depois, quando houver fatias reais em andamento;
- integração com o Azure Boards (atualizar cards): o cruzamento é pelo número do card e pelo código da EAP;
- ler a planilha da EAP: o dev informa o código e o título;
- mudar a feature das chaves centrais já implementada (`ws-002-chaves-centrais`): tabela, cópia, tela, leitores, cache e regra de falha ficam como estão;
- refactors que não são desacoplamento (tipo 1, interno): continuam como hoje.

**Antiobjetivos:**
- um processo meio no caminho novo e meio no antigo em produção;
- uma fatia sem chave sem a aprovação do líder registrada;
- o código antigo de uma fatia com chave ficar esquecido no repo depois da validação, sem aparecer em lugar nenhum.

## 3. Decisões tomadas com o usuário

| Decisão | Valor |
|---|---|
| Unidade da fatia | Um **item da EAP** (normalmente um subprocesso, como 1.1.3 ou 1.1.4; pode ser mais fundo, como 1.1.4.3). Reúne vários objetos do `Reserva` e vários sistemas |
| Identificação | O **código do item da EAP** (`1.1.4`, `1.1.4.3`…), de tamanho variável. O dev **deve** informá-lo no refactor |
| Quem define a fatia | O time, no planejamento: um card com o item da EAP é criado e refinado até estar pronto; um dev o puxa e começa |
| Cards de uma fatia | Ou um card faz a fatia inteira numa entrega, ou o time quebra o card em **vários cards irmãos** (não subtarefas). Cada card vira **um refactor** (`/speckit-refactor-assess`…), nunca um `/speckit-specify` (que é para feature) |
| Padrão | **Preferencialmente com chave.** "Sem chave" é a exceção, com motivo e aprovação do líder |
| Fatia com chave | O padrão; obrigatória quando a mudança altera o fluxo. Uma chave por fatia, na tabela central do ADR 0002, lida por todos os sistemas da fatia. Voltar atrás é virar a chave |
| Fatia sem chave | Quando o caminho novo **mantém os contratos existentes e o risco para a operação é baixo** (subida fácil de gerenciar e reversão fácil). O diagnóstico ou o plano propõe; o **líder aprova**, e o dev confirma no fluxo que o líder aprovou. O código antigo sai na própria entrega. Vai para produção na janela combinada com a operação e é validada no monitoramento do dia. Voltar atrás é reimplantar a versão anterior |
| Subida | Na fatia **com chave**, cada card vai para produção sozinho, assim que fica pronto (a chave está em "antigo"); o plano de subida é o da **virada da chave**. Na fatia **sem chave**, todos os cards sobem **juntos**, na mesma janela; o plano de subida é o do **deploy** |
| Plano de subida | O agente monta a partir das entregas dos cards; o time revisa e completa |
| Acompanhamento | Agora: um documento no workspace mantido pelos comandos. Depois: um painel lendo esse documento |
| Chaves centrais | Ficam como implementadas na feature `ws-002-chaves-centrais` (o "cache de 5 minutos" citado na reunião era o da tabela de configuração do WMS, não uma regra nova) |
| Virada | Para o sistema inteiro, sem separar por perfil de usuário ou armazém (confirmado na reunião) |
| Sistema que não lê a chave | Numa fatia **com chave**, todo sistema da fatia precisa ler a chave. Se algum não consegue (hoje, o `wms.conector.backend`), o **diagnóstico recusa** a fatia. Por isso, o `wms.conector.backend` precisa passar a ler a chave (seção 6.1) |
| PRs da fatia sem chave | Ficam **abertos até a janela**. Até lá, as branches dos cards são integradas na branch `homolog` de cada repo só para teste, e esperam a hora de subir. Na janela, os PRs são completados na ordem do plano de subida |

## 4. O modelo

### 4.1 Fatia, cards e refactors
- **Fatia:** um item da EAP. Nome = o código (`1.1.4`) e o título (`Contagem`). Tem um tipo (com ou sem chave), uma etapa e, se tiver chave, a chave `eap-<código com hífens>` (`eap-1-1-4`).
- **Card:** um item de trabalho do Azure Boards que entrega parte da fatia (ou ela toda). Cada card é um **refactor** do harness, com o slug de hoje (`<id do card>-<descrição>`), a sua branch `refactor/<slug>`, os seus relatórios em `refactors/<slug>/` e os seus PRs por repo.
- O refactor declara a fatia no diagnóstico (`/speckit-refactor-assess`): o código da EAP é obrigatório num desacoplamento.
- **O card vem do slug:** o slug do refactor já começa pelo id do work item (`<id do card>-<descrição>`). Num desacoplamento, o slug sem card (`rf-<AAAAMMDD>-…`) é recusado: o card passa a ser obrigatório, junto com o código da EAP. (Decisão minha.)

### 4.2 Etapas da fatia

**Com chave:**

| Etapa | Quando | Como |
|---|---|---|
| em andamento | o primeiro refactor da fatia cita o código | o `assess` cria a linha da fatia |
| entregue | todos os cards em produção com a chave em "antigo" | o comando do plano de subida, depois que o time confirma que a lista de cards está completa |
| convivência | o time vira a chave na tela (é o antigo M2) | o dev registra com `ws refactor fatia atualiza <código> convivencia [--desde <data>]`; a tela de chaves continua sendo a referência do modo real |
| validada | a evidência do processo atende os critérios | `/speckit-refactor-validar` da fatia |
| validação falhou | a evidência não atende | o mesmo comando; a chave volta para "antigo" e a fatia volta para **em andamento** (correção por refactor, ver 4.5) |
| desacoplada | o caminho antigo e a leitura da chave saem de todos os sistemas | `/speckit-refactor-desacoplar` da fatia |
| chave removida | a chave sai do `AWX.ERP.Connector` | `/speckit-refactor-remover` da fatia |

**Sem chave:**

| Etapa | Quando | Como |
|---|---|---|
| em andamento | o primeiro refactor cita o código | o `assess` cria a linha |
| entregue | todos os cards prontos e o plano de subida revisado; a subida acontece na janela | o comando do plano de subida |
| validada | o monitoramento do dia confirma | `/speckit-refactor-validar` da fatia, com a evidência do monitoramento |
| validação falhou | o monitoramento mostrou problema | o mesmo comando; a reversão é reimplantar a versão anterior (e reverter scripts), e a fatia volta para **em andamento** |

### 4.3 Chave da fatia
- Uma por fatia com chave: `eap-1-1-4`. O formato cabe na regra de nome da tabela de chaves (`^[a-z0-9]+(-[a-z0-9]+)*$`).
- **Quem cria:** o `apply` do primeiro card da fatia com chave cria a migração da chave em "antigo" no `AWX.ERP.Connector` (formato da camada 3), **mesmo que o card não mexa em mais nada no AWX** (como já previa o SP6.1, 7.2). Sem isso, a tela não mostraria a chave e o time não conseguiria virá-la. Os cards seguintes só leem a chave. (Decisão minha.) A migração é idempotente (`ON CONFLICT DO NOTHING`), então dois cards em paralelo não quebram nada; o documento das fatias registra qual card criou a chave.
- **Leitura:** todo sistema da fatia lê a mesma chave, pelo leitor padrão do seu tipo de app.
- **Remoção:** pelo `/speckit-refactor-remover` da fatia, depois do desacoplar em produção (como no SP6.1).

### 4.4 Plano de subida
- Um documento por fatia, `refactors/fatias/<código>/plano-subida.md`, montado pelo agente.
- **O plano não trava outras fatias:** os estados do plano valem só para a própria fatia. A única coisa que eles seguram é a validação dela: o `validar` da fatia pede o plano `revisado`. (Decisão minha, a partir do pedido do usuário de não travar as demais fatias.)
- **Estado do plano:** `rascunho` quando o comando monta; `revisado` quando o dev roda o comando de novo e confirma que o time revisou e completou (janela, cenários, plantão, monitoramento); `executado` quando o `validar` da fatia registra que a subida (sem chave) ou a virada (com chave) aconteceu na janela. (Decisão minha.)
- **Em produção:** o harness não enxerga produção. Ao montar o plano, o comando lista os cards e pede ao dev que confirme, card a card, o estado de cada um (na fatia com chave, que já está em produção com a chave em "antigo"). (Decisão minha.)
- **O que o agente preenche**, a partir dos relatórios e dos envios dos cards: os cards e os PRs por repo; os sistemas e apps tocados; os scripts de banco (de qual repo, em que banco, em que ordem); a ordem de deploy; a reversão (com chave: virar a chave e o que mais for preciso; sem chave: a versão anterior de cada app e a reversão de cada script); os critérios de validação do processo.
- **O que o time completa e revisa:** a janela combinada com a operação, os cenários operacionais a acompanhar, quem está de plantão e o checklist de monitoramento do dia.
- **Com chave:** o plano é o da virada (os cards já estão em produção). **Sem chave:** o plano é o do deploy conjunto.

### 4.5 Correção depois de uma validação que falhou
- A fatia volta para **em andamento**. A correção é feita por refactor: uma nova rodada do card que tem o problema (`refactor/<slug>-r<k>`, como hoje) ou um card novo citando o mesmo código da EAP.
- Depois, o plano de subida é montado de novo (a lista de cards e a reversão podem ter mudado).

### 4.6 Documento das fatias
- `refactors/fatias.md`, mantido só pelos comandos (por um subcomando mecânico do `ws refactor`, no padrão do `marco` e do `chave`).
- **Duas tabelas:**
  - **Fatias**, uma linha por fatia: código, título, tipo (com chave `eap-…` ou sem chave com a data da aprovação do líder), etapa, data da etapa, depende de (códigos da EAP), plano de subida (rascunho, revisado ou executado, e a data da janela), o que falta para o código antigo sair;
  - **Cards**, uma linha por refactor: código da fatia, card e slug, sistemas (repos) tocados, objetos do `Reserva`, onde a chave é lida (fatia com chave), estado do card (diagnóstico, aplicado, entregue, rodada).
- **Substitui** a tabela de fatias dos documentos de desacoplamento (`refactors/desacoplamentos/<nome>.md`, que fica com o objetivo, o padrão do caminho novo e o inventário) e o `refactors/chaves.md` do SP6.1 (a chave agora é da fatia).
- **Ligação com o desacoplamento:** cada fatia aponta para um documento de desacoplamento (coluna Desacoplamento; o do LINX corresponde ao item 1 da EAP). O `assess` continua exigindo o documento, por causa do padrão do caminho novo e do ADR. (Decisão minha.)
- O `ws refactor pendentes` passa a ler este documento e mostra, por fatia, a etapa, há quantos dias e o próximo passo; e o aviso do `ws start` (fatias com chave entregues e esperando validação há mais de N dias, ou com o plano de subida executado sem validação) passa a vir dele.

## 5. Regras

- **Código da EAP:** `^[0-9]+(\.[0-9]+)*$`. Obrigatório no `assess` de um desacoplamento.
- **Fatias são independentes, mesmo aninhadas na EAP** (decisão do usuário): `1.1.4` e `1.1.4.3` podem ser fatias ao mesmo tempo, cada uma com a sua chave, as suas etapas e o seu plano. Um card pertence a uma fatia só: a do código que o dev informou.
- **Padrão com chave:** o `assess` propõe "com chave" sempre que não houver motivo claro para o contrário; "sem chave" só com o motivo registrado (contratos mantidos, risco baixo, reversão fácil) e a aprovação do líder.
- **Tipo da fatia:** definido pelo primeiro card; um card seguinte que discorda (por exemplo, propõe chave numa fatia sem chave) para e pede a decisão do líder. Mudar o tipo de uma fatia em andamento é possível enquanto nenhum card dela estiver em produção. (Decisão minha.)
- **Aprovação do "sem chave":** o diagnóstico registra o motivo (contratos mantidos, risco baixo, reversão fácil) e `Aprovada pelo líder: pendente`. O dev troca por `sim, <data>` no `apply`, confirmando que o líder aprovou, como hoje na exceção de caracterização. Sem isso, o `apply` não segue.
- **Dependências:** o dev informa os códigos da EAP de que a fatia depende ao criar a fatia. O plano de subida avisa se alguma dependência ainda não está validada; não bloqueia (a ordem é decisão do time). (Decisão minha.)
- **Todo sistema da fatia com chave lê a chave:** o `assess` confere cada sistema que o card toca contra os tipos de app que têm leitor padrão (seção "Chaves centrais" da camada 3). Se algum não tiver, recusa a fatia com chave e diz qual sistema falta. Enquanto o `wms.conector.backend` não tiver leitor, ele só pode estar em fatia sem chave.
- **Gate das chaves:** a espera pela feature das chaves centrais (seção "Chaves centrais" da camada 3 com `<a definir pela feature>`) vale **só para fatia com chave**. Fatia sem chave pode começar já.
- **Desacoplar e validar por fatia:** o `validar`, o `desacoplar` e o `remover` passam a receber o código da EAP e a valer para a fatia inteira (todos os sistemas e objetos dela). O portão do desacoplar confere cada par sistema e objeto da tabela de cards.

## 6. O que muda no harness

### 6.1 Dependência de produto: o `wms.conector.backend` lê a chave
Fora deste design, mas necessária para fatias com chave que envolvam o conector: uma feature do workspace (pelo `/speckit-specify`, como a `ws-002-chaves-centrais`) que dá ao `wms.conector.backend` um leitor padrão de chave. Ele hoje só se conecta ao banco `Reserva`, então a feature escolhe entre ler a cópia no banco do WMS (nova conexão) ou consultar o `AWX.ERP.Connector` (com a regra de falha do ADR 0002). Quando ela estiver em produção, o ADR 0002 (item 12) deixa de excluir o conector e a camada 3 ganha o leitor dele. Na EAP, o conector está previsto para ser descomissionado (1.3.4.2.5); a feature só vale a pena se alguma fatia com chave precisar dele antes disso.

### 6.2 Mudanças no harness

Sem detalhar a implementação (fica para o plano):
- **ADR 0003** no workspace (`docs/adr/0003-fatias-pela-eap.md`): a fatia pela EAP, os dois tipos, o critério do "sem chave" e o plano de subida. O ADR 0002 ganha uma nota de que a chave passou a ser da fatia da EAP (nome `eap-…`), sem mudar o resto.
- **Constitution:** a regra VII passa a dizer que a fatia é um item da EAP, que a chave é opcional pelo critério do "sem chave" (com aprovação do líder) e que, sem chave, o código antigo sai na própria entrega.
- **Comandos de refactor:**
  - `assess`: pede o código da EAP num desacoplamento; cria ou lê a linha da fatia; define ou confere o tipo; registra o card; para fatia sem chave, registra o motivo e a aprovação pendente; o gate das chaves só para fatia com chave;
  - `apply`: cria a chave só no primeiro card da fatia com chave que tocar o AWX; confere a aprovação do líder na fatia sem chave; numa fatia sem chave, o card já remove o caminho antigo;
  - `verify`: marca o card como entregue (o card, não a fatia);
  - **comando novo do plano de subida** (por exemplo, `/speckit-refactor-subida <código>`): lista os cards da fatia e o estado de cada um, pede ao dev que confirme que a lista está completa, monta o `plano-subida.md` e marca a fatia como entregue;
  - **envio dos cards:** na fatia com chave, como hoje (o PR de cada repo é mergeado quando o card fica pronto). Na fatia sem chave, o `refactor-enviar` envia a branch e diz que o PR fica aberto até a janela, com a branch integrada na `homolog` do repo para teste (passo do time, fora do harness); o PR do workspace do card vem depois da janela;
  - `validar`, `desacoplar` e `remover`: pelo código da EAP, valendo para a fatia inteira;
  - branches das etapas da fatia (validação, desacoplar, remover) passam a ser por fatia, por exemplo `refactor/eap-1-1-4-validar`.
- **`ws refactor fatia`** (decisão do usuário, nomes ajustados com ele): o grupo de subcomandos das fatias.
  - `ws refactor fatia pendentes`: lista as fatias pendentes, com a etapa, há quantos dias e o próximo passo, inclusive as em convivência; avisa a fatia em convivência há mais tempo que o prazo sem validação. Substitui o `ws refactor pendentes`.
  - `ws refactor fatia atualiza <código> convivencia [--desde <data>]`: registra que o time virou a chave.
  - `ws refactor fatia atualiza <código> antigo [--motivo <texto>]`: registra que a chave voltou para "antigo" numa emergência, fora de uma validação; a fatia sai da convivência e o motivo fica registrado.
  - O `atualiza` só registra o que acontece fora do harness. As etapas com portão (entregue, validada, desacoplada, chave removida) só mudam pelos comandos de refactor, por subcomandos internos do `ws refactor fatia` que o `atualiza` não expõe.
  - O aviso do `ws start` lê o mesmo documento. O `marco` e o `chave` atuais saem ou viram internos.
- **Doc:** camadas 1 a 4 e `AGENTS.md`; o slide da fatia e o dos marcos na apresentação.
- **Migração:** não há fatias reais no `main` do workspace (nem `refactors/`), então não há dado para migrar.

## 7. Restrições

- **Regra II:** o objeto do `Reserva` não muda enquanto outro sistema o acessar; numa fatia com vários objetos, isso vale para cada um.
- **Regra III e VII:** cada card continua com a sua caracterização e os seus testes; a fatia não substitui a prova por card.
- **Regra IV:** o ADR 0003 é aprovado por humano.
- **Harness:** mudanças em `tools/`, `.specify/`, `.claude/` e `AGENTS.md` numa branch `harness/` própria, com testes na suíte do `tools/ws/tests`, como no SP6 e no SP6.1.

## 8. Decisões minhas (para o usuário conferir) e o que fica com o builder

**Decisões minhas:**
- O nome da chave é `eap-<código com hífens>` (4.3).
- Num desacoplamento, o card é obrigatório: o slug `rf-…` é recusado (4.1).
- O `validar` de uma fatia pede o plano dela `revisado`; nada além disso depende do plano (4.4).
- O tipo é definido pelo primeiro card e só muda antes de algum card estar em produção (5).
- Dependências avisam, não bloqueiam (5).
- O documento das fatias tem duas tabelas (fatias e cards) e substitui o `refactors/chaves.md` e a tabela de fatias dos documentos de desacoplamento (4.6).
- O plano de subida fica em `refactors/fatias/<código>/plano-subida.md` (4.4).
- Uma validação que falha volta a fatia para "em andamento", e a correção é por refactor (4.5).

**Com o builder:**
- os nomes dos subcomandos do `ws refactor` e do comando do plano de subida;
- o formato exato das duas tabelas e do `plano-subida.md`;
- o texto do aviso do `ws start` e o prazo dele;
- o que acontece com os relatórios de validação, desacoplar e remover, que passam a ser por fatia (`refactors/fatias/<código>/`).

## 9. Em aberto

- Nada que mude o que se constrói.
