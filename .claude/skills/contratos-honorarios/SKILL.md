---
name: contratos-honorarios
description: Lê contratos de honorários (PDF ou Word) e monta a base estruturada de contratos. Use ao cadastrar contratos novos, aditivos ou revisar vencimentos e reajustes.
---

# Base de contratos de honorários

## Entrada
Contratos em `dados/contratos/` (PDF com texto ou Word).

## Campos a extrair
Cliente, modalidade (fixo mensal, êxito, misto, por hora), valor ou percentual, piso e teto, índice de reajuste e mês-base, regra de janela do índice, se admite redução, dia de vencimento, multa e juros previstos, vigência e prazo de rescisão.

## Passos
1. Extraia o texto (pdfplumber para PDF; python-docx para Word).
2. Preencha uma linha por contrato em `relatorios/base-contratos.xlsx`, incluindo a coluna **"trecho de origem"** com a cláusula (número e frase curta) de onde cada dado veio.
3. Valide CPF/CNPJ com `validate_docbr`; marque inválidos.
4. Liste os contratos com campo ausente ou ambíguo, em vez de preencher por suposição.

## Regras
- Nunca interprete cláusula ambígua: cite o trecho e peça a decisão.
- PDF escaneado sem texto: informe; não digite de memória.
- Esta base contém dados de clientes: fica em `relatorios/` ou `dados/`, nunca no cofre nem no Git.
