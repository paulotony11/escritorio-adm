---
revisado_em: [PREENCHER]
---

# POP: conciliação bancária

## Contas e bancos
- [PREENCHER] (banco, tipo de conta, formato de extrato disponível: OFX ou CSV)

## Frequência
Diária em dias úteis; completa no fechamento mensal.

## Passos
1. Baixar o extrato do dia anterior (OFX quando o banco oferecer) e salvar em `dados/extratos/`.
2. Atualizar a planilha de lançamentos (entradas positivas, saídas negativas).
3. Pedir ao Claude: `/conciliacao-bancaria`.
4. Tratar as pendências: [PREENCHER como o escritório trata tarifas, estornos, depósitos sem identificação].
5. Registrar exceções em `Decisoes/`.

## Tolerância de data
[PREENCHER] dias (padrão do script: 3).

## Quando escalar
[PREENCHER] (ex.: pendência acima de R$ X ou mais antiga que N dias).
