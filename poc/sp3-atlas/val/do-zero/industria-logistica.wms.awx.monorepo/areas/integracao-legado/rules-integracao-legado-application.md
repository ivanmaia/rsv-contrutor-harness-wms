# Regras da ACL do WMS legado (Awx.IntegracaoLegadoWms.Application)

> **Last updated:** 2026-10-06
> **Scope:** Regras em `src/Integrations/AWX.IntegracaoLegadoWMS/src/Awx.IntegracaoLegadoWms.Application` e nos repositórios Dapper; agrupamento pelo código, `[unverified]` como conceito de negócio
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../../_discovery/assumptions-register.md

A ACL lê **e grava** no banco do legado, com duas connection strings (leitura e escrita). O README do projeto diz "somente leitura" `[outdated]` (A-1) (C-40).

## Regras

- **NF de entrada** — origem precisa ser Fornecedor, Loja ou CrossDockingRepa (transferência entre CDs fica fora); itens com quantidade > 0. Mesma `ChaveNFE`, ou mesmo fornecedor+número+série, devolve 409 `NotaFiscal.Duplicada` com os dados da nota existente. Cabeçalho e itens vão numa transação: qualquer falha desfaz tudo; item repetido vira 409 `NotaFiscal.ItemDuplicado`. O mapper grava `IdStatusNotaFiscal = 1`, corta o fornecedor em 25 caracteres e manda chave vazia como NULL. A leitura de dedup usa a conexão de escrita (C-47). O db/README diz que a ACL **não** deduplica `[contradicted]` (A-2).
- **Contagem concluída** — NF inexistente dá 404 `NF_NAO_ENCONTRADA`; já enviada ao ERP dá 409 `CONTAGEM_JA_ENVIADA`; se ainda não concluída marca CONCLUIDA/PENDENTE e grava os itens contados; envia ao ERP.Connector e grava ENVIADO ou FALHA (500 `ERP_CONNECTOR_FALHOU`); no sucesso registra até 7 entidades externas (romaneios e pedidos de sobra/falta). Os passos não estão numa transação comum (C-46).
- **CUP** — exige `CupId` e `Sku`; já existente ou violação de UNIQUE dá 409 `ProdutoCup.Duplicado` (C-48).
- **Resolver produto por CUP** — consulta o AWX.Estoque, faz upsert do produto e grava o vínculo; 409 do vínculo conta como sucesso (C-48).
- **Produtos em lote** — lote vazio dá 400; limites do validator: SKU 25, código 12, cor 10, descrição 40, código de barras 25, tamanho 1–48 (a tabela aceita SKU 50 e descrição 500) (C-48).
- **Pedido B2C** — tipo de pedido precisa existir em `dbo.TipoPedido` (404 `TipoPedido.NaoEncontrado`); número já existente devolve sucesso sem gravar; UF com 2 letras, CEP com 8 dígitos, tamanho 1–48, quantidade > 0. A atualização de status não confere linhas afetadas (C-49).
- **Volume de expedição** — armazém e canal > 0; repassa à API do legado e devolve o sequencial (C-41).
- **Triangulação fiscal** — uma consulta por pedido em `FATURAMENTO_PROD`/`FATURAMENTO` (NOLOCK), devolvendo volumes com NF de saída, série e chave (C-45).

## Onde são aplicadas

Validators e services de `Application/<Contexto>`; transação e dedup nos repositórios `Wms*Repository`. A API exige API key (C-11).
