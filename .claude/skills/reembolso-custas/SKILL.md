---
name: reembolso-custas
description: Consolida custas e despesas reembolsáveis por cliente e processo e gera o relatório de reembolso. Use ao fechar o mês ou ao cobrar despesas de um cliente.
---

# Reembolso de custas e despesas

## Entrada
Planilha de despesas em `dados/custas/` com data, cliente, referência do processo, descrição, valor e comprovante (nome do arquivo).

## Antes
Leia a política de reembolso em `conhecimento/Escritorio/Politica-de-cobranca.md` (o que é reembolsável, prazo, necessidade de comprovante).

## Passos
1. Agrupe por cliente e por referência de processo; some com `Decimal`.
2. Marque despesas **sem comprovante** ou fora da política.
3. Gere um relatório Excel por cliente em `relatorios/` e um resumo geral.
4. Se pedirem, redija um **rascunho** de carta de reembolso a partir de `modelos/`.

## Regras
- Um relatório nunca mistura clientes.
- Não inclua conteúdo processual, apenas a referência (número) do processo e a natureza da despesa.
- Valor sem comprovante entra como "pendente de documentação", não como reembolsável.
