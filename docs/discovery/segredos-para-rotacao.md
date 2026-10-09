# Segredos para rotação (só locais, sem valores)

Consolidado dos relatórios do discovery por repo. Caminhos relativos a `repos/<repo>/`.

| Repo | Local | Tipo |
|---|---|---|
| wms.picking.backend | `src/Reserva.WMS.Picking.API/appsettings.Development.json` | connection string com usuário/senha |
| (sessão 2026-09-23) | histórico da sessão | senha do login `lwms` (réplica de prod) |
| wms.conector.backend | `src/ReservaNet.Linx.API/appsettings.json:15` | connection string com usuário/senha (`LegacyConnection`) |
| wms.conector.backend | `src/ReservaNet.Linx.API/appsettings.json:16` | connection string com usuário/senha (`LegacyReadOnlyConnection`) |
| wms.conector.backend | `src/ReservaNet.Linx.API/appsettings.Development.json:15-16` | as mesmas duas connection strings |
| wms.conector.backend | `Dockerfile:2,7` | PAT do feed NuGet via build-arg (sem valor no arquivo; conferir pipeline) |
| wms.ecommerce.backend | `src/ReservaNet.ECommerce.API/appsettings.txt:15-17` | connection strings com usuário/senha |
| wms.ecommerce.backend | `src/ReservaNet.ECommerce.API/appsettings.Development.txt:15-17` | connection strings com usuário/senha |
| wms.ecommerce.backend | `tests/ReservaNet.ECommerce.UnitTests/appsettings.json:4-7` | connection strings com usuário/senha |
| wms.ecommerce.backend | tabela `ecommerce.cache` (runtime) | senha WMS do operador cifrada com chave vazia (A-8) |
| wms.servidor.backend | `Reserva.WMS3.API/Web.config:62,64,66,68,70` | connection strings |
| wms.servidor.backend | `Reserva.WMS3.API/Web.config:24,26,32,42,43,47,50,58` | tokens, segredo SSO, senha RabbitMQ, chave de criptografia, chaves de API |
| wms.servidor.backend | `Reserva.WMS3.Tasks/Web.config:53,55,57,59` | connection strings |
| wms.servidor.backend | `Reserva.WMS3.Tasks/Web.config:26,28,34,41,42,44,47` | tokens, SendGrid, RabbitMQ, chaves |
| wms.servidor.backend | `UseReserva.Web/Web.config:8,10,12,14` | connection strings |
| wms.servidor.backend | `UseReserva.Web/Web.config:23,27,36,38,101` | senhas, tokens, SMTP |
| wms.servidor.backend | `UseReserva.Web/Web.Token.config:20,24,88` | senhas, SMTP |
| wms.servidor.backend | `Reserva.WMS3.Testes/app.config:5,7,9,11,17,19,27` | connection strings/credenciais |
| wms.servidor.backend | `Reserva.WMS3.Testes.Integracao/app.config:5,7,9,11,17,19,27,29` | connection strings/credenciais |
| wms.servidor.backend | `Reserva.WMS3.Testes/Infraestrutura/Configurations/ConnectionStringConfigurationFactoryTestes.cs:11-30` | connection strings |
| wms.awx.monorepo | `src/Integrations/AWX.ERP.Connector/src/Presentation/AWX.ERP.Connector.Worker/appsettings.json:11-12` | usuário/senha RabbitMQ (não vazios) |
| wms.awx.monorepo | `src/Services/AWX.Estoque/src/AWX.Estoque.{Api,Worker}/appsettings.Development.json:16-17` | usuário/senha RabbitMQ padrão (localhost) — baixo risco |
| wms.awx.monorepo | `src/Services/AWX.Recebimento/README.md:53` | connection string de exemplo com usuário/senha inline |
| wms.app.frontend | `src/enviroments/production.ts:3` | chave de deployment Revopush (produção) |
| wms.app.frontend | `src/enviroments/production.ts:7` | DSN do Sentry |
| wms.app.frontend | `android/sentry.properties:2`, `ios/sentry.properties:2` | token de API do Sentry |
| wms.app.frontend | `android/gradle.properties:49-50` + `android/app/reservawms.keystore` | senhas e keystore de release Android |
| wms.app.frontend | `android/app/build.gradle:93,95` | senhas do keystore de debug — baixo risco |
| wms.app.frontend | AsyncStorage do dispositivo + eventos no Sentry (runtime) | senha do operador em claro; corpo de login enviado ao Sentry (`sendDefaultPii`) |
| backoffice.frontend (Fly) | `src/services/Faccylita/etiquette.service.ts:13-14` | chave de API hardcoded (bundle client) |
| backoffice.frontend (Fly) | `src/services/Faccylita/faccao.service.ts:6-7` | chave de API hardcoded (bundle client) |
| backoffice.frontend (Fly) | `src/services/Faccylita/solicitacaoReimpressao.service.ts:14-15` | chave de API hardcoded (bundle client) |
| backoffice.frontend (Fly) | `src/config.ts:14` | chave de API `NEXT_PUBLIC_*` exposta ao client |
| backoffice.frontend (Fly) | `.env.test.example` | não aberto — conferir |
| reserva-net.autenticacao.monolito | `src/Presentation/SSO/appsettings.json:4,21-22,28` | connection string com senha; usuário/senha LDAP; chave JWT |
| reserva-net.autenticacao.monolito | `src/Presentation/SSO/Development-appsettings.txt:4,21-22` | connection string com senha; usuário/senha LDAP |
| reserva-net.autenticacao.monolito | `src/UserManager/SSO.LDAP/LDAPService.cs:105` (+ `:100,:108` senha em log) | credencial LDAP no código; senha escrita em log |
| reserva-net.autenticacao.monolito | `src/Application/Commands/SSO.Commands/RealizarLoginMobile/RealizarLoginMobileCommandHandler.cs:143` | chave de assinatura JWT no código (tokens mobile forjáveis) |
| reserva-net.autenticacao.monolito | `src/Presentation/SSO/tempkey.jwk` | chave privada de assinatura IdentityServer |
| reserva-net.b2b.backend | `src/ReservaNet.B2B.API/Properties/launchSettings.json:28-31,32,38` | connection strings com senha; `sa` local; senha SFTP |
| reserva-net.b2b.backend | `src/ReservaNet.B2B.API/Development.appsettings.txt:15-17,27` | connection strings com senha; `sa` local; senha SFTP |
| reserva-net.b2b.backend | `README.md:10,35,44` | senhas de exemplo (SA local, SFTP) — conferir se são reais |
| reserva-net.b2b.backend | `Dockerfile:2` | `ARG PAT` do feed (sem valor no arquivo) |
| wms.ecommerce.frontend | `src/environments/environment{,.dev,.release,.prod,.prod-gcp}.ts:6` | chave de API do hubprodutividade (bundle público) |
| wms.ecommerce.frontend | `src/environments/environment.prod.ts:18-19`, `environment.prod-gcp.ts:18-19` | client token / app id do Datadog RUM |
| wms.ecommerce.frontend | `.npmrc:7-12` (comentado) | usuário/`_password` do feed Azure Artifacts |
| wms.hubprodutividade.backend | `README.md:16,51-53` | host interno + usuário de banco e do Amazon MQ reais (senhas placeholder) — exposição de topologia, não credencial |
| print-zebra.utilitario.backend | `src/appsettings.json:10` | connection string com servidor/usuário/senha (histórico git pode ter valores antigos) |
| print-zebra.utilitario.backend | `Dockerfile:2,7` | `ARG PAT` do feed NuGet (sem valor no arquivo) |
| reserva-net.api-gateway.backend | `Dockerfile:2,6` | `ARG PAT` do feed Azure Artifacts (sem valor no arquivo) |
| wms.tms.backend | `IntegracaoRepositoryData/Data/App.config:4,5,8-9` | connection strings SQL Server e MySQL com senha; usuário/senha de e-mail |
| wms.tms.backend | `IntelipostPedidoService/App.config:4,5(comentada),8` | connection strings com senha; token da API Intelipost |
| wms.tms.backend | `Reserva-Services Hangfire/Properties/App.config:4-5,8-9,12-13` | connection strings; e-mail; tokens Intelipost (teste e produção) |
| wms.tms.backend | `Reserva-Services Hangfire/appsettings.json:5` | senha do dashboard Hangfire |
| wms.tms-finished.backend | `Sincroniza/App.config:10,11` | connection strings com usuário/senha (`ReservaContext`, `ReservaContextReadOnly`) |
| (banco, msdb de produção) | job `Manutencao_Estoque_Entradas_Ecommerce`, `Manutencao_Faturamento`, `Manutencao_Vendas`, `RSV_Update_LDB_Franquias`, `RSV_Update_LDB_LOJAS`, `RSV_INTEGRACAO_DEPENDENTES`, `RSV_WFA_INTEGRACAO_SAP`, passo SSIS | connection string com senha em texto no comando do passo (login `usr_olap_2018`) |
| (banco, msdb de produção) | job `RSV_INTEGRACAO_VENDEDOR_AUXILIAR`, passo 2 PowerShell | connection string com senha em texto (login `usr_middleware`) |
