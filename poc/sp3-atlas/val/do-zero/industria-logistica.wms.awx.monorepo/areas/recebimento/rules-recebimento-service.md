# Regras do recebimento (RecebimentoService)

> **Last updated:** 2026-10-06
> **Scope:** Regras em `src/Services/AWX.Recebimento/src/AWX.Recebimento.Application` e no client da ACL; agrupamento pelo código, `[unverified]` como conceito de negócio
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../../_discovery/assumptions-register.md

O serviço não guarda dados: o banco `recebimento` só tem o histórico de migrations, e o Worker não tem consumidores (C-80).

## Regras

- **Validação do lote** — lote vazio dá `RECEBIMENTO_LOTE_VAZIO`; campo obrigatório ausente, nota sem item, quantidade ≤ 0 ou origem fora de Fornecedor/Loja/CrossDockingRepa dão `RECEBIMENTO_NOTA_INVALIDA`; item sem SKU dá `RECEBIMENTO_ITEM_SEM_SKU`. Com erro de validação nenhuma nota segue para a ACL (400) (C-81).
- **Envio nota a nota** — a falha de uma nota não interrompe as outras. Resposta da ACL: 2xx = importada; 409 = já importada (não é falha); outro status = `RECEBIMENTO_LEGADO_RECUSOU`; sem resposta depois do retry = `RECEBIMENTO_LEGADO_INDISPONIVEL`. O resumo garante `importadas + jaImportadas + falhas = totalRecebidas` (C-82).
- **Rota** — o código expõe `POST api/v1/recebimento/notas-fiscais-entrada/importar`; o README e o contrato falam em `.../sincronizar` `[contradicted]`. O ERP.Connector chama a URL base configurada, sem sufixo, então a rota real depende da config de ambiente (A-3) (C-83).
- `RECEBIMENTO_NOTA_DUPLICADA` está definido e não é usado (C-81).
