---
name: reajuste-honorarios
description: Reajusta honorários pelo IPCA ou IGP-M com memória de cálculo. Use quando pedirem reajuste anual de contrato ou valor corrigido.
---

# Reajuste de honorários

## Dados necessários (pergunte se faltar)
Valor atual, índice do contrato (IPCA ou IGPM), mês do reajuste (AAAA-MM), se o contrato admite redução quando o índice é negativo e a regra de janela do contrato.

## Antes
Leia `conhecimento/Regras/Modalidades-de-honorarios.md`. **Confira a cláusula do contrato** sobre a janela de apuração: o padrão do script é 12 meses terminando 1 mês antes do reajuste (`--defasagem 1`). Se o contrato disser outra coisa, ajuste `--defasagem` e registre.

## Passos
1. Atualize os índices: `uv run python -m escritorio indices --desde 2022-01-01`
2. Calcule:
   `uv run python -m escritorio reajuste --valor <valor> --indice <IPCA|IGPM> --mes-reajuste <AAAA-MM> [--defasagem N] [--sem-reducao]`
3. Entregue a memória de cálculo completa (cada competência, fator acumulado, valor final).

## Regras
- Se o script acusar competências ausentes, pare e informe. Não estime índice.
- Fonte dos índices: API do Banco Central (séries SGS 433 e 189). Cite a data da consulta.
- O valor reajustado é uma **proposta**: quem aprova é a pessoa com alçada.
