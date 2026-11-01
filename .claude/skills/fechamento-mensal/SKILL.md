---
name: fechamento-mensal
description: Conduz o fechamento mensal e a previsão de caixa: verificações, DRE gerencial, caixa realizado versus previsto e análise de variações. Use no fim do mês ou para a previsão das próximas semanas.
---

# Fechamento mensal

## Pré-requisitos (verifique, não presuma)
- Todas as contas conciliadas até o último dia do mês (`/conciliacao-bancaria`), com pendências justificadas.
- Reajustes e êxitos do mês calculados e aprovados.
- Reembolsos de custas consolidados.
Se algo faltar, liste e pare.

## Antes
Leia `conhecimento/Escritorio/Calendario-fechamento.md` e `conhecimento/Regras/Plano-de-contas.md`.

## Passos
1. Consolide receitas e despesas do mês por conta do plano de contas (duckdb ou pandas sobre as planilhas de `dados/`).
2. Monte a DRE gerencial e o caixa realizado versus previsto em um Excel em `relatorios/AAAA-MM/`.
3. Compare com o mês anterior; para variações acima de 20% (ou o limite definido no calendário), liste as **contas e lançamentos** que explicam. Só proponha causa se estiver nos lançamentos.
4. Rode o aging (`/regua-cobranca`) e inclua a inadimplência.
5. Modo previsão: com contas a receber e a pagar já conhecidas, projete o caixa das próximas 4 semanas, separando "confirmado" de "estimado".

## Regras
- Totais devem bater com os saldos do banco; se não baterem, o fechamento **não está fechado**.
- Toda exceção tratada vai para `conhecimento/Decisoes/` (proposta, para o curador).
- Skills de apoio: plugin `finance` (reconciliation, financial-statements, variance-analysis, close-management).
