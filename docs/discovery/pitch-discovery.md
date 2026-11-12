🚀 *Discovery*

O Discovery foi o ônibus espacial que mais voou: 39 missões, cargas diferentes em cada uma, e todas voltaram pra casa.

Por isso o nosso harness se chama Discovery: é a nave que leva cada entrega do WMS da spec até a produção, com segurança, quantas vezes for preciso.

*O problema*

Levanta a mão quem já pegou um card e passou o primeiro dia só descobrindo _onde_ mexer. 🙋

O WMS tem 18 repos. Tem código legado, tem AWX, tem a integração com a LINX, e tem regra de negócio que só existe na cabeça de quem já saiu da empresa.

E o difícil quase nunca é escrever o código. O difícil é:
• descobrir quais sistemas uma mudança afeta;
• levar a mesma entrega para três, quatro repos ao mesmo tempo;
• subir PR por PR, para homolog e depois para produção, sem esquecer nenhum;
• mexer no legado sem parar a operação do CD;
• e deixar tudo de um jeito que o próximo dev entenda o que foi feito.

Até hoje, cada missão dependia da memória de alguém e de um processo que cada dev seguia do seu jeito.

*O que é o Discovery*

O Discovery é o nosso jeito de trabalhar no WMS, só que transformado em ferramenta. Ele junta todos os repos num workspace só, e o dev e o Claude seguem o mesmo plano de voo. Ele tem quatro peças.

*1. Uma nave só para todos os repos* 🛰️
Uma branch leva a entrega inteira, em quantos sistemas ela tocar. O Discovery cuida de entregar cada pedaço no repo certo.

*2. Um plano de voo para cada tipo de missão* 🗺️
• _Feature:_ especifica, planeja e divide em estágios pequenos, que sobem um de cada vez.
• _Bug:_ diagnostica, corrige e testa, e deixa o relatório registrado.
• _Refactor:_ fatia o legado, protege com chave e sobe em rollout controlado.

*3. O Atlas, o nosso telescópio* 🔭
Foi o Discovery que levou o Hubble pra órbita, um telescópio pra enxergar longe. O nosso também leva o seu: o Atlas, que mostra o sistema inteiro antes de você mexer.
• Mostra o mapa dos sistemas e o impacto de cada mudança.
• Confere a documentação contra o código antes de alguém confiar nela.
• O conhecimento que vivia na cabeça das pessoas passa a viver no repositório, e cada missão deixa o Atlas mais completo.

*4. O controle de missão* 📡
Um comando abre todos os PRs. Primeiro vem o teste em solo, na homolog. Depois vem o lançamento, no main. O time é avisado no Chat a cada etapa, a revisão vem guiada e os comentários são resolvidos pelo próprio fluxo. Nenhum PR fica perdido em órbita.

*Para quem é*
• _Dev:_ foca no problema de negócio, não na burocracia de quatro repos e doze PRs.
• _Quem acabou de chegar:_ fica produtivo em dias, não em meses. O Atlas e o plano de voo ensinam o caminho.
• _Tech lead e revisor:_ toda entrega chega no mesmo formato, rastreável da spec ao PR.
• _PO e QA:_ sabem o que está em teste, o que vai para produção e por quê.
• _A IA:_ trabalha com contexto e com regras claras, sem chute.

*O valor*
• _Velocidade com segurança:_ estágios pequenos e PRs coordenados geram menos retrabalho e menos surpresa em produção.
• _Conhecimento que fica:_ as pessoas mudam, o Atlas permanece.
• _Previsibilidade:_ a mesma missão segue o mesmo caminho, não importa quem pilota.
• _Coragem para mexer no legado:_ com fatias e chave, dá para tocar no que ninguém tinha coragem de tocar.

A gente sempre teve paixão pelo ofício. O Discovery é o que deixa essa paixão ir pro problema certo: a operação do CD, a experiência de quem compra, o negócio. A parte repetitiva fica com a nave.

Ele não substitui o piloto. Ele cuida de tudo que não é pilotar.

🚀 *Discovery: da spec à produção, toda missão volta pra casa.*
