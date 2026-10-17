# Arquitetura de transição: LINX, AWX e legado WMS

Explicação do usuário em 2026-10-17, durante o SP6. Até então não estava documentada.

## Visão de futuro
O WMS inteiro vai ser migrado para dentro do `industria-logistica.wms.awx.monorepo`. Hoje a arquitetura é de transição, e vai continuar assim por um bom tempo: o foco agora é o desacoplamento do LINX, e a migração vem depois. O AWX vai estrangular o legado WMS aos poucos.

## AWX.ERP.Connector
É o contexto do awx.monorepo que funciona como ACL (middleware). Toda comunicação entre o ERP LINX e o WMS passa por ele, nos dois sentidos:
- **inbound** (do ponto de vista do AWX): requisições do LINX que o WMS (AWX) precisa atender;
- **outbound**: requisições do WMS (AWX) que o LINX precisa atender.

Regras:
- nenhum contexto de serviço do AWX fala direto com o LINX; sempre passa pelo `AWX.ERP.Connector`, que chama o `integracoes.wms.servicos-linx-wms.monorepo`;
- o `servicos-linx-wms` não fala direto com os contextos de serviço; sempre passa pelo `AWX.ERP.Connector`.

Exemplos:
- **Cadastro de produtos (a fonte da verdade é o LINX):** um worker do `servicos-linx-wms` identifica o produto novo e chama o endpoint de sync de produtos no `AWX.ERP.Connector`, que chama o sync de produtos no `AWX.Estoque`.
- **Consulta de produto que não está no AWX:** o `AWX.Estoque` chama um endpoint do `AWX.ERP.Connector`, que chama um endpoint do `servicos-linx-wms` para consultar o produto.

## Legado WMS
1. **Legado → LINX:** `AWX.IntegracaoLegadoWMS` → contexto de serviço do AWX (opcional) → `AWX.ERP.Connector` → `servicos-linx-wms`.
2. **LINX → legado:** `servicos-linx-wms` → `AWX.ERP.Connector` → contexto de serviço do AWX (opcional) → `AWX.IntegracaoLegadoWMS`.

O `AWX.IntegracaoLegadoWMS` fala com o legado WMS de várias formas, nos dois sentidos: HTTP, leitura e escrita direto no banco, stored procedures e mensageria.

## Onde isso entra no harness
É o "Padrão do caminho novo" do documento do desacoplamento do LINX (`refactors/desacoplamentos/linx.md`, SP6). Ainda não há ADR. Pela regra IV da constitution, a decisão pede um ADR aprovado por humano, no AWX ou em `docs/adr/` do workspace.
