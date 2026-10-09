# Contexto fornecido pelo usuário (2026-09-23)

Fonte primária, validada pelo responsável. Prevalece sobre o export do IcePanel em caso de conflito.

1. **Legado** = tudo o que está no sistema **WMS** (WMS3.WEB/API/TASKS, Coletor, ReservaNet.Ecommerce, Full Picking, Printers API, Intelipost, SSO, ERP Módulo WMS etc.).
2. **AWX** (Azzas Warehouse eXecution System) é a arquitetura-alvo de longo prazo. Hoje o trabalho é estruturar e criar o que é **novo** no AWX.
3. **Fly** é o novo frontend (Next.js, monorepo, deploy segmentado por módulo). Os fronts legados migrarão para ele algum dia. Features totalmente novas já nascem no Fly (ex.: Trakta, novo checkout B2B).
4. **Não confundir WMS com Logística Integrada**: são sistemas distintos no IcePanel (Logística Integrada = Fly + Logistica.Integrada.BFF + Helix, integrando lojas/SAC/painéis).
5. O **WMS Legado nasceu dentro do LINX** (ERP) e foi se emancipando, mas continua **fortemente acoplado ao LINX via banco de dados** (bancos Reserva / Banco Reserva Linx, procs, jobs, tabelas ATG etc.).
6. Existe uma demanda de **desacoplamento**: o **AWX.ERP.Connector** (ACL) está sendo usado para trocar o acoplamento via banco por integração via serviços (REST/eventos RabbitMQ).

## Fontes
- `repos-inventario.csv`: os 16 repos do escopo inicial.
- `icepanel-export.md`: export C4 do IcePanel (2026-09-23), com visão preliminar e **não verificada** das relações.

## Escopo do SP0 (decidido em 2026-09-23)
- **Dentro:** os 16 repos do inventário mais o **Fly** (`integracoes.core.plataforma.backoffice.frontend`).
- **Fora (ignorar):** wms.deflator-estoque.backend, wms.erp-dinossauro.backend, ondemand.gestao-producao.backend/frontend, integracoes.wms.servicos-linx-wms.monorepo, Logistica.Integrada.BFF, Helix.
