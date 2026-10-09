# Modelo do produto (AWX.Estoque)

> **Last updated:** 2026-10-06
> **Scope:** Entidades do AWX.Estoque (`src/Services/AWX.Estoque`)
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../../_discovery/assumptions-register.md

| Entidade (tabela) | O que representa | Atributos que importam | Relações |
|---|---|---|---|
| Produto (`produtos`) | Cadastro do SKU | `sku` (100, único), `codigo_produto`, `cor_produto`, `tamanho`, `grade`, `grife`, `grupo`, `sub_grupo`, `descricao`, `codigo_barra`, `ncm`, `updated_at` (hora de Brasília convertida para UTC) | — |
| Vínculo CUP (`produtos_cup`) | CUP → SKU | `cup_id` (14, único), `sku` (25), `pedido`, `data_validade`, `data_importacao` | SKU por valor |
| Código de barras (`produtos_codigo_barra`) | Código de barras → SKU | `codigo_barra` (único), `sku` | SKU por valor |

Sem chaves estrangeiras nem campos de status (C-60). `produtos_cup.sku` tem 25 caracteres e `produtos.sku` tem 100 (A-17).

## Regras

- **Sync de produtos** — upsert por SKU; a atualização não muda código nem cor. Código de barras vazio é ignorado; código já ligado a outro SKU é ignorado com aviso (C-60).
- **Sync de CUP** — upsert por CUP; pode trocar o SKU do CUP (C-60).
- **Resolver por CUP** — se o vínculo e o produto existem localmente, responde sem ir ao ERP; senão importa do ERP.Connector, grava o produto (com código de barras = SKU) e depois o vínculo, sem pedido nem validade. ERP 404 vira `CupNaoEncontrado`/`ProdutoNaoEncontrado` (C-60).
- **Resolver por SKU** — igual, sem criar vínculo (C-60).
- Listas vazias dão 400 com mensagem por rota. A API não autentica (A-8).
