---
name: honorarios-exito
description: Calcula honorários de êxito (percentual sobre valor levantado ou acordo, com piso e teto) e prepara a minuta de cobrança. Use quando houver êxito a faturar.
---

# Honorários de êxito

## Dados necessários (pergunte se faltar)
Base de cálculo (valor levantado ou acordo, líquido ou bruto conforme o contrato), percentual, piso e teto, se houver, e o documento que comprova o valor.

## Passos
1. `uv run python -m escritorio exito --base <valor> --percentual <pct> [--piso <v>] [--teto <v>]`
2. Entregue a memória de cálculo e indique em qual documento o contrato define a base.
3. Se pedirem, redija a **minuta** de nota de débito a partir de `modelos/` (sem emitir nada).

## Regras
- Se o contrato for ambíguo sobre a base (bruta ou líquida, antes ou depois de custas), **não escolha**: apresente as duas opções e peça a decisão.
- A emissão fiscal é feita por pessoa, no sistema oficial.
