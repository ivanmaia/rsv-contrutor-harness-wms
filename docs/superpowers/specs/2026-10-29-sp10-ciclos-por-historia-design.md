# SP10: ciclos por história antes do `speckit-tasks`

**Data:** 2026-10-29. **Status:** rascunho para aprovação do usuário.
**Onde o harness é implementado e testado:** clone `C:\ws\industria-logistica.wms.workspace`. O clone `c:\ws\dsv\industria-logistica.wms.workspace` é o de desenvolvimento do usuário (features); foi só lido, para ver um caso real. Esta spec fica aqui, como as dos SP anteriores.

## 1. Intenção e porquê

Uma feature do workspace (`ws-NNN`) reúne várias histórias do `specify`, e hoje o `speckit-tasks` gera um `tasks.md` único para todas. O time tem medo de que isso vire um PR gigante, ou vários. O histórico confirma: PRs com dezenas ou centenas de arquivos, de revisão trabalhosa e complicada.

Quer-se um **comando novo do harness**, rodado depois do `speckit-plan` e antes do `speckit-tasks`, que divide o trabalho restante em **ciclos, um por história**. Cada ciclo (tasks → implement → converge) entrega uma história pequena o bastante para revisar e **segura para ir sozinha à produção**.

"Segura" tem um sentido preciso, dado pelo usuário: dá para fazer o merge no `main` e subir para produção **sem deixar o fluxo do usuário pela metade**. Se a história 1 só faz sentido depois da história 2, subir a 1 sem a 2 é inseguro, e a 1 não pode depender de a 2 subir junto.

Hoje o time não tem nenhum mecanismo para esconder código incompleto em produção. A feature flag está só começando, e só no desacoplamento (chaves centrais). Este SP cria o mecanismo para features.

## 2. Metas, não-metas e anti-metas

**Metas**
- Dividir a feature em ciclos por história, com um plano de ciclos que o time confirma antes de gerar as tasks.
- Cada ciclo ser entregável em produção sozinho.
- Permitir trabalho em paralelo (dois devs) nas histórias independentes.
- Registrar feature flags de feature nova, criadas dentro do ciclo.
- O `converge` verificar, no fim de cada ciclo, o que o plano de ciclos prometeu.

**Não-metas**
- Uma biblioteca compartilhada de feature flag para os repos: o harness define o registro, a regra e o padrão, mas não entrega código de biblioteca.
- Reusar o mecanismo das chaves centrais do desacoplamento (é outro tipo de flag, com outro registro).
- Criar um comando de verify novo: o `speckit-implement` já executa os testes e valida que passam.
- Fatiar uma feature específica: o comando fatia qualquer feature; a `ws-003` só valida o design.
- Mudar a spec ou o plan.
- Retomar uma feature cujas tasks já foram geradas antes deste comando. O comando vale para features que ainda não rodaram o `speckit-tasks`. A `ws-003` está nesse estado (tem spec e plan, sem `tasks.md`).

**Anti-metas** (falharia mesmo que tecnicamente funcionasse)
- Vários PRs pequenos que, na prática, não entregam valor nenhum. O usuário prefere um PR um pouco maior que entregue a história completa.
- Exigir flag em toda história. Nem todo caso precisa; só o que deixaria o fluxo pela metade.
- Deixar o time sem saída quando uma história ainda assim fica grande demais.

## 3. Decisões do usuário (conforme decididas)

1. **Um comando novo**, entre o `plan` e o `speckit-tasks`.
2. **Um ciclo por história** do `specify`. Cada ciclo: tasks, implement (que já roda os testes) e converge. Cada ciclo vira um PR.
3. **Uma feature `ws-NNN` com todas as histórias.** Não são features separadas.
4. **Limite de tamanho flexível e parametrizável no próprio harness**, em arquivos e linhas alteradas. Os valores ficam no **arquivo de configuração do harness**, que o time ajusta. Um PR um pouco maior que entregue a história completa é preferível a vários pequenos sem valor.
5. **O `speckit-tasks` roda uma vez** e já agrupa as tasks por história.
6. **Dependências:** o comando as propõe lendo a spec e o plan; o time confirma. Histórias independentes seguem em paralelo. Uma história que depende de outra só começa depois de a anterior estar mergeada.
7. **Segurança de produção:** quem decide, no plano de ciclos, o que precisa de flag é o comando de divisão. O `converge` verifica, no fim do ciclo.
8. **Quando a história 1 só faz sentido com a 2:** a 1 fica atrás de uma feature flag até a 2 chegar (não se juntam as duas num PR).
9. **Flag de feature:** a criação fica dentro do ciclo; a flag é registrada num arquivo no workspace; é um tipo diferente das chaves centrais, com outro registro. **Remover** a flag exige um ciclo de refactor.
10. **Alcance da feature flag:** o harness entrega só o **registro, a regra e um padrão** de como a flag é criada, nomeada e lida. Não entrega uma biblioteca, mas o padrão é **obrigatório**: nenhum dev implementa a flag do seu jeito. O padrão cobre as stacks dos repos do workspace (.NET, Angular, React Native e banco).
11. **História que sozinha estoura o limite:** o comando avisa, indica o que a faz crescer e o time escolhe entre **aceitar**, **dividir a história na spec** ou **marcar uma exceção registrada**.
12. **Exemplo da `ws-003` (não é regra do comando):** nesta feature, a US1 (gravar o modo SKU) fica por último, como interruptor, e as demais entram inertes antes dela. Isso vale só para este caso. A ordem de cada feature sai da análise que o comando faz dela (dependências e segurança de produção), não de uma regra fixa de "interruptor por último".

## 4. Escolhas do construtor (revisáveis pelo usuário)

- **Nome e artefato:** comando de divisão com nome no padrão do SP8 (em inglês para o dev) e artefato `cycles.md` na pasta da feature. O nome exato fica para o plano.
- **Uma branch por história**, para os PRs saírem em paralelo. "Mergeada" significa **no `main`** (é o que o usuário disse: dá para fazer o merge no `main` e ir para produção). Uma história que depende de outra só começa depois de a anterior estar no `main`, e a branch dela é atualizada com o `main` (pelo `ws sync`) antes de começar. O comando guarda o estado de cada ciclo no `cycles.md` (pendente, em andamento, mergeado), detectando o merge pelo `main`. Como a spec e o plan chegam ao `main` com o primeiro ciclo fica para o plano de implementação.
- **Como a segurança é obtida, em ordem de preferência:** primeiro a **ordem** dos ciclos e o comportamento **inerte por padrão**, isto é, o código novo só é alcançável quando algo o liga e o padrão mantém o comportamento de hoje. Só quando a ordem e o padrão não bastam, a história fica atrás de **flag** (decisão 8). Exemplo, só desta feature: na `ws-003` o modo padrão é CUP, que não muda nada, e só a US1 permite gravar o modo SKU; por isso as US2 a US8 não precisam de flag.
- **Como o comando decide "seguro" e "precisa de flag":** ele propõe, lendo a spec e o plan, e registra no `cycles.md` a justificativa; o time confirma, como nas dependências. O `converge` verifica de forma objetiva o que o plano prometeu: a história prevista como inerte ou atrás de flag está de fato assim, e a flag prevista está no registro.
- **Sem fork do Spec Kit:** o harness já adapta o Spec Kit por preset e extensão (o preset `multirepo` envolve o `speckit.specify`). O mesmo vale aqui: o `speckit-tasks` e o `speckit-converge` são envolvidos por preset, hooks e instruções, sem alterar o código do Spec Kit. As tasks que o `converge` acrescenta ficam na seção da história do ciclo.
- **Limite de tamanho:** os valores vivem no arquivo de configuração do harness. Para a estimativa e o `converge` funcionarem desde o início, o construtor põe valores iniciais no arquivo, marcados como ajustáveis; o time os acerta lá.
- **Bloqueios externos e cards:** o comando os extrai do texto da spec e do plan (o plan da `ws-003` já traz a emenda do AWX como dependência) e, quando não achar, pergunta ao time na confirmação do plano de ciclos.
- **"Um PR por história" é, na prática, um conjunto de PRs:** um por repo enviado mais o do workspace, como o harness faz hoje (`/ws-pr-homolog` e `/ws-pr-main`). Os limites de tamanho valem para a história, somando os PRs dela.
- **Limite como aviso, não bloqueio.** Antes de existir código, estima-se pelo plan (arquivos, camadas e repos tocados); depois de implementar, mede-se o diff real, e o `converge` compara com o limite.
- **O `converge` limitado à história do ciclo.** Hoje ele compara o código com todas as tasks e apontaria as outras histórias como pendentes.
- **Ciclo 0 de fundação:** o que não pertence a nenhuma história (por exemplo, coluna ou contrato compartilhado usado por várias) ganha um ciclo próprio, aditivo e seguro.
- **Bloqueios externos listados por ciclo** (por exemplo, uma aprovação de outro time), para o time ver antes de começar.
- **Ordem dos ciclos:** sai do grafo de dependências e da segurança de produção de cada feature. O comando não aplica uma regra fixa de "interruptor por último"; quando uma feature tem uma história que liga o comportamento novo, a análise pode pô-la por último, como na `ws-003`, mas isso é resultado da análise, não uma regra.

## 5. Restrições do ambiente (levantadas lendo o clone `dsv`, que tinha o mesmo harness do `main`)

- O `speckit-tasks` tem hooks `before_tasks` e `after_tasks`. O comando novo pode ser uma skill avulsa ou um hook, e o `speckit-tasks` precisa ler o plano de ciclos.
- O `speckit-tasks` já gera uma fase por história com grafo de dependências. O preset `multirepo` agrupa por repo e fecha cada grupo com uma verificação de build e testes. Os dois agrupamentos precisam conviver.
- O `speckit-converge` só acrescenta tasks no fim do `tasks.md` e não toca spec, plan nem código. O hook `after_converge` do workspace atualiza o Atlas dos repos tocados e segue a skill `ws-commit-push`. Hoje isso vale para a feature inteira.
- O `speckit-implement` executa as tasks de teste e valida no fim que os testes passam.
- Não existe verify de feature, só o `speckit-refactor-verify`.
- O plan do caso real é organizado por repo, e as histórias atravessam repos. O comando precisa montar o mapa inverso: por história, os repos, objetos de banco e FRs tocados.
- Constitution do workspace 1.5.1; nomes de comandos em inglês, documentos em português (SP8).

## 6. Caso de validação: `ws-003-b2c-operacao-ecommerce`

Branch já baixada em `c:\ws\dsv\industria-logistica.wms.workspace`, com spec (8 histórias, 76 FRs, 5 repos) e plan prontos. Serve para validar o design, não para ser fatiada à mão aqui. O comando, ao rodar nela, deveria chegar a algo equivalente a:

- **Grafo pela spec:** US1 (modo) é base de todas; US2 → US3 → US4; US5 e US6 → US7; US8 depende do modo e do saldo.
- **Ciclo 0:** a fundação (coluna `CodigoBarra`, movimentação por ID de item, alteração aditiva da `prConsultaDadosMovimentacao`).
- **US1 por último**, como interruptor (a gravação do modo SKU na API do AWX), com as demais entrando inertes no modo CUP.
- **Bloqueio externo na US1:** a emenda à constitution do AWX, feita pelo time do AWX.
- **Estimativa de tamanho:** US6 (colmeia) e US7 (checkout) são as maiores; o plano de ciclos deve avisar o risco de passarem do limite.
- **Cards:** as histórias não mapeiam 1:1 aos cards (US6 tem três; US1 e US5 não têm card). O comando não pode assumir um card por história.

## 7. O que fica para o construtor

- Formato do `cycles.md`, nome do comando e da skill, e como o `speckit-tasks` o lê (hook ou instrução).
- Como as tasks por história convivem com o agrupamento por repo do preset `multirepo`.
- Como limitar o `converge` e o hook `after_converge` à história do ciclo.
- Onde mora a configuração do limite de tamanho e como o formato do registro de flags de feature é definido.
- Como o aviso de limite estourado e as três saídas (aceitar, dividir na spec, exceção registrada) aparecem no `cycles.md` e onde a exceção é registrada.
- Qual é o padrão de flag em cada stack (nome, onde é lida, valor padrão, registro de onde é lida) e como o `converge` confere que o código o segue.
- Como o ciclo de refactor que remove a flag é aberto (reaproveitar o `ws refactor`, se couber).
- Como a spec e o plan chegam ao `main` com o primeiro ciclo.
- O resultado da seção 6 é **ilustrativo**, não um critério de aceite rígido: o comando deve chegar a um plano equivalente e coerente com o grafo, a segurança de produção e o ciclo 0.

## 8. Pontos em aberto com o usuário

Nenhum. Os três que restavam (alcance da flag, história que estoura o limite e valores do limite) foram decididos em 2026-10-29 e estão nas decisões 4, 10 e 11.
