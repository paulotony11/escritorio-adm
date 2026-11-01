"""Contas a receber: aging por faixa de atraso e encargos."""

from datetime import date
from decimal import Decimal

import pandas as pd

from escritorio.dinheiro import arredondar, dec

COLUNAS = ("cliente", "documento", "vencimento", "valor")
FAIXAS = ("A vencer", "1-30 dias", "31-60 dias", "61-90 dias", "Acima de 90 dias")


class ColunasAusentes(ValueError):
    """A planilha não tem as colunas obrigatórias."""


def faixa(dias_atraso: int) -> str:
    if dias_atraso <= 0:
        return FAIXAS[0]
    if dias_atraso <= 30:
        return FAIXAS[1]
    if dias_atraso <= 60:
        return FAIXAS[2]
    if dias_atraso <= 90:
        return FAIXAS[3]
    return FAIXAS[4]


def aging(contas: pd.DataFrame, hoje: date) -> pd.DataFrame:
    """Acrescenta dias_atraso e faixa. Ignora linhas com data_pagamento preenchida."""
    faltam = [c for c in COLUNAS if c not in contas.columns]
    if faltam:
        raise ColunasAusentes(f"Colunas ausentes: {', '.join(faltam)}")

    abertas = contas.copy()
    if "data_pagamento" in abertas.columns:
        abertas = abertas[abertas["data_pagamento"].isna()]
    abertas["vencimento"] = pd.to_datetime(abertas["vencimento"], dayfirst=True).dt.date
    abertas["valor"] = abertas["valor"].map(dec)
    abertas["dias_atraso"] = abertas["vencimento"].map(lambda v: (hoje - v).days)
    abertas["faixa"] = abertas["dias_atraso"].map(faixa)
    return abertas.sort_values(["dias_atraso", "cliente"], ascending=[False, True]).reset_index(drop=True)


def resumo_por_faixa(contas_com_aging: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for nome in FAIXAS:
        grupo = contas_com_aging[contas_com_aging["faixa"] == nome]
        linhas.append(
            {
                "faixa": nome,
                "titulos": len(grupo),
                "valor": sum(grupo["valor"], Decimal(0)),
            }
        )
    return pd.DataFrame(linhas)


def encargos(valor, dias_atraso: int, multa_pct, juros_mensal_pct) -> Decimal:
    """Multa única + juros simples pro rata dia (mês de 30 dias). Confira o contrato."""
    if dias_atraso <= 0:
        return Decimal(0)
    base = dec(valor)
    multa = base * dec(multa_pct) / Decimal(100)
    juros = base * dec(juros_mensal_pct) / Decimal(100) / Decimal(30) * dias_atraso
    return arredondar(multa + juros)
