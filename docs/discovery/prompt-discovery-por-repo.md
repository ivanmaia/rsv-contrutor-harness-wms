# Prompt base do discovery por repo (v2, com os ajustes do piloto)

Substituir `<REPO>` pelo nome da pasta em `repos/`. Raiz do workspace: `C:\src\00-harness_big_brown_field`.

---

Você vai rodar o discovery de um repositório seguindo a skill em `C:\src\00-harness_big_brown_field\.agents\skills\codebase-discovery\SKILL.md` (leia a SKILL.md e os playbooks/templates/references que ela mandar ler). Não há ninguém para responder perguntas durante a execução.

**Parâmetros já decididos (equivalem às respostas da Fase 0):**
- Target: `C:\src\00-harness_big_brown_field\repos\<REPO>`. **Somente leitura**: não edite, não crie arquivos, não rode comandos git que alterem o clone (log/show/ls-files/blame são permitidos).
- Modo **code-only** (pula a Fase 2; a entrevista será consolidada depois entre todos os repos).
- Output root: `C:\src\00-harness_big_brown_field\docs\discovery\repos\<REPO>\` (confirmado pelo usuário). README do repo → `project-readme.md` no output root. Não criar CLAUDE.md/AGENTS.md. Agent file retido.
- Exclusões: node_modules, bin, obj, dist, packages, build, coverage, arquivos gerados/minificados, migrations geradas, lockfiles.
- Consentimentos (reescrever README, sign-offs da Fase 5 etc.) → não conceda: registre como *needs SME* no assumptions-register. Fases 0 e 5 mínimas.
- **Pular** `business/user-personas.md` e documentos de requisitos.
- Evidência extra (só leitura): `docs/discovery/sources/contexto-usuario.md` (contexto validado pelo usuário), `docs/discovery/sources/icepanel-export.md` (use **só grep**, é grande), `docs/discovery/sources/repos-inventario.csv`, catálogo do banco de homologação em `extract/db-hml/{WMS,Reserva,ReservaNet}/` (objects.csv, columns.csv, dependencies.csv, synonyms.csv, foreign_keys.csv, `modules/<tipo>/` com o SQL de procs/views/functions). Use grep nesses arquivos, não os leia inteiros.
- Referência de formato e profundidade: o piloto em `docs/discovery/repos/industria-logistica.wms.picking.backend/` (veja `tech/integrations.md`). Não o modifique.

**Repo grande (> ~1000 arquivos rastreados):** leia por camadas. Primeiro o que o repo declara (README, soluções/projetos, manifests, configs, pipelines, pontos de entrada, rotas/controllers, consumidores de fila, jobs, connection strings). Depois só os hotspots de regra de negócio. Registre no ledger o que ficou sem cobertura em vez de tentar ler tudo.

**Saídas obrigatórias além das da skill:**

1. `_discovery/edges.csv` com cabeçalho exato `app,tipo,alvo,detalhe,evidencia`. Uma linha por aresta.
   - `app`: `<REPO>` (ou o subprojeto, se for monorepo: `<REPO>/<subprojeto>`).
   - `tipo` ∈ `db-read, db-write, db-exec, http-in, http-out, mq-pub, mq-sub, job`.
   - `alvo`: banco.schema.objeto (ex.: `WMS.Picking.Onda`, `Reserva.dbo.entradas`), host/serviço HTTP ou chave de config de base URL, nome de fila/exchange, nome do job.
   - `detalhe`: rota + verbo, operação SQL, routing key, cron etc.
   - `evidencia`: `caminho/relativo/ao/repo:linha`.
   - Campos com vírgula entre aspas duplas (CSV RFC 4180).
2. `tech/integrations.md` com estas seções fixas, nesta ordem: **Visão geral**; **Banco de dados** (tabela R/W/Exec por objeto); **HTTP exposto (inbound)**; **HTTP consumido (outbound)**; **Filas e mensageria**; **Jobs e agendamentos**; **Quem mais toca o meu schema** (a partir de `extract/db-hml/*/dependencies.csv`, `synonyms.csv` e `modules/`: procs/views/sinônimos de outros schemas/bancos que referenciam os objetos que este repo usa ou possui). Seção sem conteúdo fica com "Nenhum encontrado no código" e a busca feita.

**Segredos:** siga a regra de segredos da skill: nunca copie valores. Registre só o local (`arquivo:linha` e o tipo: connection string, senha, token, DSN, chave de API).

**Relatório final (sua resposta, ≤ 350 palavras, em português):**
- Arquivos gerados (lista curta).
- O sistema em 2 a 3 frases.
- Integrações principais (bancos/objetos-chave, HTTP, filas, jobs) e nº de linhas em edges.csv.
- Pendências *needs SME* mais importantes (até 5).
- Segredos: lista `arquivo:linha — tipo` (sem valores).
- Notas de cobertura (o que ficou de fora, custo/limitações).
