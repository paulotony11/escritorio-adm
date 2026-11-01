from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from escritorio.cobranca import ColunasAusentes, aging, encargos, faixa, resumo_por_faixa

HOJE = date(2026, 10, 31)


def test_faixas_nos_limites():
    assert faixa(0) == "A vencer"
    assert faixa(1) == "1-30 dias"
    assert faixa(30) == "1-30 dias"
    assert faixa(31) == "31-60 dias"
    assert faixa(91) == "Acima de 90 dias"


def contas():
    return pd.DataFrame(
        {
            "cliente": ["A", "B", "C"],
            "documento": ["1", "2", "3"],
            "vencimento": ["30/10/2026", "01/08/2026", "15/12/2026"],
            "valor": ["1.000,00", "2.500,50", "300,00"],
        }
    )


def test_aging_calcula_dias_e_ordena_por_atraso():
    resultado = aging(contas(), HOJE)
    assert list(resultado["cliente"]) == ["B", "A", "C"]
    assert list(resultado["faixa"]) == ["Acima de 90 dias", "1-30 dias", "A vencer"]


def test_aging_ignora_titulos_pagos():
    base = contas().assign(data_pagamento=[None, "05/08/2026", None])
    assert set(aging(base, HOJE)["cliente"]) == {"A", "C"}


def test_resumo_soma_decimal_sem_erro_de_ponto_flutuante():
    resumo = resumo_por_faixa(aging(contas(), HOJE))
    linha = resumo[resumo["faixa"] == "Acima de 90 dias"].iloc[0]
    assert linha["valor"] == Decimal("2500.50")
    assert linha["titulos"] == 1


def test_colunas_obrigatorias():
    with pytest.raises(ColunasAusentes):
        aging(pd.DataFrame({"cliente": ["A"]}), HOJE)


def test_encargos_multa_e_juros_pro_rata():
    # 1000 * 2% = 20 de multa; 1% a.m. em 15 dias = 5 -> 25,00
    assert encargos("1000", 15, "2", "1") == Decimal("25.00")
    assert encargos("1000", 0, "2", "1") == Decimal("0")
