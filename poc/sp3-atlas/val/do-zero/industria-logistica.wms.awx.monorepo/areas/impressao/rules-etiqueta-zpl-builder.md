# Regras de montagem de etiqueta (EtiquetaZplBuilder)

> **Last updated:** 2026-10-06
> **Scope:** Regras em `src/Integrations/AWX.Impressao/src/Application/Awx.Impressao.Application/Etiquetas`; agrupamento pelo código, `[unverified]` como conceito de negócio
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../../_discovery/assumptions-register.md

A Impressao não tem banco nem mensageria; recebe o payload, monta o ZPL e faz `POST {PrintersApiBaseUrl}/print` com `Extensao = "txt"` (C-87).

## Regras

- **Etiqueta de checkout** — transportadora cortada em 21 caracteres e UF em 2; "LOTE n" extraído da descrição do picking; nome do cliente quebra a linha acima de 17 caracteres; "SHIP TO" impresso quando a modalidade é `RETIRE_EM_LOJA`, `SHIP_TO`, "SHIP TO" ou "2"; CEP normalizado para `00000-000` (vazio se inválido) (C-88).
- **Mini-DANFE B2B** — transportadora sem "PRESS" (BrasPress) imprime sigla "000" e rota "00000" (C-88).
- **Simulação** — com `Impressao:ModoSimulacao=true` devolve o ZPL em texto em vez de imprimir (C-89).
- Erro da Printers API vira exceção não tratada (500). A API não autentica (A-8).
