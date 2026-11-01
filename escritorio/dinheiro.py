"""Conversão e formatação de valores monetários com Decimal (sem float)."""

from decimal import ROUND_HALF_UP, Decimal

CENTAVO = Decimal("0.01")


def dec(valor) -> Decimal:
    """Converte número ou texto (aceita '1.234,56') em Decimal."""
    if isinstance(valor, Decimal):
        return valor
    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    return Decimal(texto)


def arredondar(valor: Decimal) -> Decimal:
    """Arredonda para centavos (meio para cima)."""
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def para_centavos(valor) -> int:
    return int(arredondar(dec(valor)) * 100)


def brl(valor: Decimal) -> str:
    """Formata como R$ 1.234,56."""
    texto = f"{arredondar(valor):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")
