---
name: regua-cobranca
description: Gera o aging de honorários a receber e rascunhos de cobrança por faixa de atraso. Use para "cobranças da semana", inadimplência ou aging.
---

# Régua de cobrança

## Entrada
Planilha de contas a receber em `dados/receber/` com colunas `cliente`, `documento`, `vencimento`, `valor` e, opcionalmente, `data_pagamento` (título com data de pagamento é ignorado).

## Antes
Leia `conhecimento/Escritorio/Politica-de-cobranca.md` (prazos, multa, juros, quando escalar) e `conhecimento/Regras/Tom-de-comunicacao.md`. Se estiverem com `[PREENCHER]`, avise e entregue só o aging.

## Passos
1. `uv run python -m escritorio aging --arquivo <planilha>`
2. Apresente o resumo por faixa (a vencer, 1-30, 31-60, 61-90, acima de 90).
3. Para cada título em atraso, escreva um **rascunho** de cobrança conforme a política e o tom definidos, em um arquivo de texto em `relatorios/`. Um rascunho por cliente, nunca misturando clientes.
4. Para atrasos acima do limite de escalonamento da política, não escreva cobrança: sinalize para decisão do sócio.

## Regras
- Não envie nada. Os rascunhos são lidos e enviados por pessoa.
- Encargos só se a política os definir. Nunca invente multa ou juros.
- Não revele no rascunho informações de outros clientes ou de processos.

## Entrega
Resumo por faixa, lista de clientes com rascunho pronto, lista para decisão do sócio e o caminho dos arquivos.
