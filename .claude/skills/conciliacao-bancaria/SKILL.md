---
name: conciliacao-bancaria
description: Concilia o extrato bancário (OFX ou CSV) com os lançamentos do escritório e lista pendências. Use quando a administradora pedir conciliação, conferência de extrato ou "o que não bateu".
---

# Conciliação bancária

## Entradas
- Extrato em `dados/extratos/` (OFX preferido; CSV aceito).
- Lançamentos em `dados/` (planilha com colunas `data`, `valor`, `descricao`; entradas positivas, saídas negativas).

## Antes
Leia `conhecimento/Processos/Conciliacao-bancaria.md` e `conhecimento/Regras/Plano-de-contas.md`. Pergunte conta e período se não vierem no pedido.

## Passos
1. Rode:
   `uv run python -m escritorio conciliar --extrato <arquivo> --lancamentos <planilha> [--tolerancia 3]`
   Para CSV de banco, informe `--col-data`, `--col-valor` e `--col-descricao` conforme o cabeçalho.
2. Abra o Excel gerado em `relatorios/` (abas: conciliados, extrato_sem_lancamento, lancamento_sem_extrato).
3. Para cada pendência, **sugira** a causa provável (tarifa, data diferente, lançamento duplicado, falta de lançamento), sem alterar nada.

## Regras
- O casamento é por valor exato e data dentro da tolerância. O que não casa fica pendente; não force.
- Não crie lançamentos novos. Apenas sugira.
- Se o arquivo não abrir, informe o banco e peça uma amostra sem dados reais ao responsável técnico.

## Entrega
Resumo com contagens, caminho do arquivo gerado, lista das pendências com sugestão e o que precisa de decisão humana.
