# Recebimento de NF de entrada

> **Last updated:** 2026-10-06
> **Scope:** Fluxo da NF de entrada do Linx até o banco do WMS legado e o retorno da contagem; nome a partir do código, `[unverified]` como fluxo de negócio
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../_discovery/assumptions-register.md

**Atores:** ERP Linx, conferente (contagem, fora do AWX) · **Gatilho:** `POST /api/recebimento/nota-fiscal-entrada/sincronizar` no ERP.Connector · **Resultado:** NF e itens em `Recebimento.NotaFiscal*`; depois da contagem, romaneios de sobra/falta no ERP

```mermaid
flowchart TD
  linx([Linx envia NFs]) --> erp[ERP.Connector: garante SKUs no Estoque]
  erp -->|SKU sem descrição/NCM/grade| falha1[RECEBIMENTO_PRODUTO_INCOMPLETO]
  erp --> lotes[Lotes de 100 para o AWX.Recebimento]
  lotes --> val[Recebimento valida o lote]
  val -->|inválido| r400[400, nada segue]
  val --> nota[Para cada nota: POST na ACL]
  nota --> acl[ACL: dedup, INSERT cabeçalho + itens em transação]
  acl -->|duplicada| j409[409 = já importada]
  acl --> ok[importada]
  cont([Contagem concluída]) --> acl2[ACL POST /recebimento/contagem-concluida]
  acl2 --> erp2[ERP.Connector → Linx contagem]
  erp2 --> ent[ACL grava ENVIADO e entidades externas]
```

- **Decisões:** origem precisa ser Fornecedor, Loja ou CrossDockingRepa; 409 da ACL não é falha (C-47, C-81, C-82; [rules-recebimento-service.md](../areas/recebimento/rules-recebimento-service.md), [rules-integracao-legado-application.md](../areas/integracao-legado/rules-integracao-legado-application.md)).
- **Caminhos de erro:** lote com erro no Recebimento conta todas as notas como falha no conector, que avisa que elas "serão reenviadas"; ACL indisponível vira `RECEBIMENTO_LEGADO_INDISPONIVEL`; falha do ERP na contagem grava FALHA (C-66, C-46).
- **Lacunas:** quem chama a contagem concluída na ACL não aparece no repo; a rota do Recebimento (`importar` × `sincronizar`) depende da URL configurada (A-3).
