# Regras da parametrização por cliente (ParametrizacaoPorClienteService)

> **Last updated:** 2026-10-06
> **Scope:** Regras em `src/Services/AWX.PedidosB2B/src/AWX.PedidosB2B.Application/Services` e `Core/Validators`; agrupamento pelo código, `[unverified]` como conceito de negócio
> **Mode:** code-only
> **Status:** code-derived, not validated by a person — see ../../_discovery/assumptions-register.md

Entidade única: `ParametrizacaoPorCliente` (tabela `geracao_demanda_parametrizacao_por_cliente`), com tipo de ordem (Franquia=1, Atacado=2, gravado como texto), cliente, lote, faixas mín./máx., validade, pedido franquia, auditoria e soft delete por `data_exclusao` (C-76).

## Regras

- **Validação** — tipo válido; cliente, lote e validade obrigatórios; mínimo ≤ máximo; pedido franquia só com tipo Franquia (C-77).
- **Unicidade** — um cliente ativo por lote, checado na aplicação (`ParametrizacaoPorCliente.ClienteDuplicadoNoLote`), sem índice único no banco (C-77).
- **Validação no ERP** — o cliente precisa existir no Linx (`ErpConnector.ClienteNaoEncontrado`); em Franquia com pedido, o pedido precisa existir e ser do cliente (`PedidoFranquiaInvalido`) (C-77).
- **Situação** — "Vigente" se a validade é hoje ou depois, senão "Vencido" (C-77).
- **Importação CSV** — a prévia marca inválidas as linhas repetidas no arquivo ou já existentes no banco e consulta o ERP em lote; a confirmação grava só as linhas marcadas válidas pelo cliente, sem revalidar (C-78).
- **Simulação de geração de demanda** — valida coleção, tipo de pedido, filial, grade e "gerar picking painel" e responde "Funcionalidade em desenvolvimento." (C-79).
- A API não autentica; o usuário vem na query ou no corpo (A-8).
