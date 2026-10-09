# Regras da NF de expedição (RegistrarNotaFiscalService)

> **Last updated:** 2026-10-06
> **Scope:** Regras em `src/Services/AWX.Expedicao/src/AWX.Expedicao.Application/NotaFiscal`; agrupamento pelo código, `[unverified]` como conceito de negócio
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../../_discovery/assumptions-register.md

Entidade única: NF de expedição (`expedicao.notas_fiscais`) com chave (44, única), pedido, filial, transportadora, loja de retirada, número, séries interna e externa e status Pendente/EmLote/Enviada/Cancelada; só Pendente é usado (C-84).

## Regras

- **Registro** — chega por `POST /api/v1/expedicao/notas-fiscais` ou pelo evento `awx.faturamento.pedido-b2c-concluido`; valida campos (chave até 44, `TraceId` obrigatório mas não gravado) e grava como Pendente (C-85).
- **Chave duplicada** — devolve Conflict `NotaFiscal.ChaveJaRegistrada`. No consumer, só erro de validação vai direto para a DLQ; Conflict passa pelo retry 10/30/60s e termina na DLQ `[assumption]` (C-85).
- O 201 aponta para um GET que não existe; nenhum código do repo chama a API nem publica o evento (A-10).
- Api e Worker hospedam o mesmo consumer (C-86).
