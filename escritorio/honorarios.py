"""Reajuste de honorários e cálculo de êxito, sempre com memória de cálculo."""

from dataclasses import dataclass
from decimal import Decimal

from escritorio.dinheiro import arredondar, brl, dec
from escritorio.indices import Serie, fator_acumulado, janela


@dataclass(frozen=True)
class Resultado:
    valor_original: Decimal
    valor_final: Decimal
    memoria: tuple[str, ...]


def reajustar(
    valor,
    indice: str,
    serie: Serie,
    mes_reajuste: str,
    defasagem: int = 1,
    permitir_reducao: bool = True,
) -> Resultado:
    """Reajusta `valor` pelo acumulado de 12 meses do índice.

    A janela termina `defasagem` meses antes de `mes_reajuste`. Confira a
    cláusula do contrato: algumas usam o mês anterior, outras o mesmo mês.
    """
    original = dec(valor)
    competencias = janela(mes_reajuste, meses=12, defasagem=defasagem)
    fator = fator_acumulado(serie, competencias)
    reduzido = fator < 1 and not permitir_reducao
    fator_aplicado = Decimal(1) if reduzido else fator
    final = arredondar(original * fator_aplicado)

    memoria = [
        f"Valor original: {brl(original)}",
        f"Índice: {indice.upper()}",
        f"Mês do reajuste: {mes_reajuste} (defasagem de {defasagem} mês)",
        f"Competências: {competencias[0]} a {competencias[-1]}",
        *(f"  {c}: {serie[c]}%" for c in competencias),
        f"Fator acumulado: {fator:.8f} (variação de {(fator - 1) * 100:.4f}%)",
    ]
    if reduzido:
        memoria.append("Variação negativa: contrato não admite redução, valor mantido.")
    memoria.append(f"Valor reajustado: {brl(final)}")
    return Resultado(original, final, tuple(memoria))


def calcular_exito(base, percentual, piso=None, teto=None) -> Resultado:
    """Honorários de êxito = base × percentual, limitados por piso e teto."""
    base_valor = dec(base)
    pct = dec(percentual)
    bruto = arredondar(base_valor * pct / Decimal(100))
    final = bruto
    memoria = [
        f"Base de cálculo: {brl(base_valor)}",
        f"Percentual: {pct}%",
        f"Resultado: {brl(bruto)}",
    ]
    if piso is not None and final < dec(piso):
        final = arredondar(dec(piso))
        memoria.append(f"Aplicado piso contratual: {brl(final)}")
    if teto is not None and final > dec(teto):
        final = arredondar(dec(teto))
        memoria.append(f"Aplicado teto contratual: {brl(final)}")
    memoria.append(f"Honorários de êxito: {brl(final)}")
    return Resultado(base_valor, final, tuple(memoria))
