"""Leitura da linha digitável de boleto bancário (47 dígitos).

Cobre boletos de cobrança bancária. Boletos de arrecadação (contas de consumo e
tributos, 48 dígitos) não são tratados: a função recusa e pede conferência manual.
"""

import re
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

BASE_FATOR = date(1997, 10, 7)
CICLO_FATOR = 9000  # o fator volta a 1000 após 9999 (reinício em 22/02/2025)


class BoletoInvalido(ValueError):
    """Linha digitável inválida ou não suportada."""


@dataclass(frozen=True)
class Boleto:
    banco: str
    valor: Decimal
    vencimento: date | None
    codigo_barras: str


def _mod10(campo: str) -> int:
    soma, peso = 0, 2
    for digito in reversed(campo):
        produto = int(digito) * peso
        soma += produto // 10 + produto % 10
        peso = 1 if peso == 2 else 2
    return (10 - soma % 10) % 10


def _mod11(codigo: str) -> int:
    soma, peso = 0, 2
    for digito in reversed(codigo):
        soma += int(digito) * peso
        peso = 2 if peso == 9 else peso + 1
    dv = 11 - soma % 11
    return 1 if dv in (0, 10, 11) else dv


def _vencimento(fator: int, referencia: date) -> date | None:
    if fator == 0:
        return None
    candidata = BASE_FATOR + timedelta(days=fator)
    # escolhe, entre as repetições do ciclo, a data mais próxima da referência
    passos = round((referencia - candidata).days / CICLO_FATOR)
    return candidata + timedelta(days=passos * CICLO_FATOR)


def ler(linha_digitavel: str, referencia: date | None = None) -> Boleto:
    digitos = re.sub(r"\D", "", linha_digitavel)
    if len(digitos) == 48:
        raise BoletoInvalido("Boleto de arrecadação (48 dígitos): confira manualmente.")
    if len(digitos) != 47:
        raise BoletoInvalido(f"Esperados 47 dígitos, recebidos {len(digitos)}.")

    for inicio, fim in ((0, 10), (10, 21), (21, 32)):
        campo = digitos[inicio:fim]
        if _mod10(campo[:-1]) != int(campo[-1]):
            raise BoletoInvalido(f"Dígito verificador inválido no campo {inicio // 10 + 1}.")

    codigo = (
        digitos[0:4] + digitos[32] + digitos[33:47]
        + digitos[4:9] + digitos[10:20] + digitos[21:31]
    )
    sem_dv = codigo[:4] + codigo[5:]
    if _mod11(sem_dv) != int(codigo[4]):
        raise BoletoInvalido("Dígito verificador geral inválido.")

    return Boleto(
        banco=digitos[0:3],
        valor=Decimal(int(digitos[37:47])) / Decimal(100),
        vencimento=_vencimento(int(digitos[33:37]), referencia or date.today()),
        codigo_barras=codigo,
    )
