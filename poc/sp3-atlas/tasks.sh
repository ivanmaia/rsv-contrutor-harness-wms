#!/bin/bash
# Roda as 6 tarefas numa configuração (padrao|serena). Descartável.
cfg=$1; cd /c/src/00-harness_big_brown_field/poc/sp3-atlas
S=industria-logistica.wms.servidor.backend; A=industria-logistica.wms.awx.monorepo; F=industria-logistica.wms.picking.frontend
bash run-task.sh T1s $S $cfg "Quais métodos chamam o método AtualizaCaixaStatus (declarado em ICaixaServico e implementado em CaixaServico) neste repositório, sem contar testes? Responda apenas com a lista no formato Classe.Metodo, um por linha."
bash run-task.sh T2s $S $cfg "Renomeie o método ObterNomeTipoEndereco para ObterNomeDoTipoEndereco em todo o repositório (declaração na interface, implementação e todas as chamadas). Não altere mais nada. Ao final, responda só 'feito'."
bash run-task.sh T1a $A $cfg "Quais métodos chamam ExisteAsync de IWmsPedidosRepository, sem contar testes? Responda apenas com a lista no formato Classe.Metodo, um por linha."
bash run-task.sh T2a $A $cfg "Renomeie o método ObterIdTipoPedidoAsync para ObterIdDoTipoPedidoAsync em todo o repositório (interface, implementação, chamadas e testes). Não altere mais nada. Ao final, responda só 'feito'."
bash run-task.sh T3a $A $cfg "Em WmsPedidosRepository, altere ObterIdTipoPedidoAsync para retornar null imediatamente, sem consultar o banco, quando tipoPedido for nulo, vazio ou só espaços (use string.IsNullOrWhiteSpace). Não altere mais nada. Ao final, responda só 'feito'."
bash run-task.sh T1f $F $cfg "Quais componentes Angular deste repositório injetam e usam o OndaService? Responda apenas com a lista de nomes de classe dos componentes, um por linha."
