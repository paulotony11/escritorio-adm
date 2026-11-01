---
name: contas-a-pagar
description: Organiza boletos e notas de fornecedores em uma agenda de pagamentos para aprovação. Use ao triar boletos, montar a agenda da semana ou conferir uma linha digitável.
---

# Contas a pagar

## Entrada
Boletos e notas (PDF) em `dados/pagar/`. Para linha digitável avulsa, a administradora a informa no pedido.

## Passos
1. Para cada PDF, leia o texto (pdfplumber) e extraia: fornecedor, documento, valor, vencimento e linha digitável.
2. Valide cada linha digitável: `uv run python -m escritorio boleto "<linha digitável>"`. Compare valor e vencimento do script com os do PDF; divergência vai para a coluna "conferir".
3. Monte a agenda em Excel (`relatorios/`): fornecedor, documento, valor, vencimento, linha digitável, status da validação, observação.
4. Ordene por vencimento e destaque o que vence em até 3 dias úteis.

## Regras
- **Você não paga nem agenda pagamento.** A agenda é para aprovação de quem tem alçada (`conhecimento/Equipe/Responsaveis-e-alcadas.md`).
- Documento de 48 dígitos (conta de consumo ou tributo) não é validado pelo script: marque "conferir manualmente".
- PDF escaneado sem texto: informe e peça OCR ao responsável técnico. Não digite de memória.
- Suspeita de boleto adulterado (banco ou beneficiário diferente do fornecedor cadastrado): sinalize em destaque.
