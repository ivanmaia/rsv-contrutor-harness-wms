# PoC SP2: Spec Kit 1.0.12 com extensão e preset locais (DESCARTÁVEL)

Feita em 2026-09-25 com `uvx --from git+https://github.com/github/spec-kit.git@v1.0.12 specify`, num repo git vazio. A pasta `work/` foi apagada; ficam só as conclusões.

| Pergunta | Resultado |
|---|---|
| `specify init --here --force --non-interactive --integration claude --script sh` | Cria 10 skills `speckit-*` em `.claude/skills/`, scripts bash em `.specify/scripts/bash/`, templates, `memory/constitution.md` e o workflow. A extensão `git` **não** é instalada por padrão, e nenhuma branch é criada. |
| O `specify` cria `specs/NNN-<feature>/` sem a extensão `git`? | **Sim.** `create-new-feature.sh --json --short-name X "desc"` criou `specs/001-X/` e `.specify/feature.json`, sem branch. O SKILL do `speckit-specify` diz: "The spec directory and file are always created by this command, never by the hook". |
| Como a branch é criada | Por um hook `before_specify` registrado em `.specify/extensions.yml`. O agente lê o arquivo e invoca a skill do hook; `optional: false` torna o hook obrigatório. É instrução para o agente, não execução determinística. |
| Extensão local | `specify extension add --dev <dir>` instalou `ws` (um `extension.yml`, um comando e um script bash). Registrou o hook `before_specify` e gerou `.claude/skills/speckit-ws-feature/SKILL.md` com o caminho `.specify/extensions/ws/scripts/bash/ws-feature.sh`. |
| Preset local | `specify preset add --dev <dir>` com `strategy: append` no `spec-template`. `resolve-template.sh spec-template` devolveu o template do núcleo mais a seção "Repos afetados". O núcleo não foi editado. |
| Suporte a `AGENTS.md` | A extensão `agent-context`, que vem no pacote, aceita `context_files: [AGENTS.md, CLAUDE.md]` e mantém uma seção gerenciada entre marcadores. Também vêm no pacote as extensões `assess` e `bug`, e os presets `lean` e `constitution-sync`. |
