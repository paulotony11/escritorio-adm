from decimal import Decimal

import pytest

from escritorio.honorarios import calcular_exito, reajustar
from escritorio.indices import IndiceAusente, janela, somar_meses


def serie_sintetica(valor="1.0", inicio="2025-01", meses=24):
    # dados fictícios, só para testar a aritmética
    return {somar_meses(inicio, i): Decimal(valor) for i in range(meses)}


def test_janela_termina_um_mes_antes_do_reajuste():
    comps = janela("2026-03", meses=12, defasagem=1)
    assert comps[0] == "2025-03"
    assert comps[-1] == "2026-02"
    assert len(comps) == 12


def test_reajuste_composto_de_doze_meses():
    resultado = reajustar("1000", "IPCA", serie_sintetica("1.0"), "2026-03")
    # 1,01 ^ 12 = 1,12682503 -> 1126,83
    assert resultado.valor_final == Decimal("1126.83")


def test_reajuste_aceita_formato_brasileiro():
    resultado = reajustar("1.000,00", "IPCA", serie_sintetica("0"), "2026-03")
    assert resultado.valor_final == Decimal("1000.00")


def test_variacao_negativa_sem_reducao_mantem_valor():
    resultado = reajustar(
        "1000", "IGPM", serie_sintetica("-0.5"), "2026-03", permitir_reducao=False
    )
    assert resultado.valor_final == Decimal("1000.00")
    assert any("não admite redução" in linha for linha in resultado.memoria)


def test_variacao_negativa_com_reducao_aplica():
    resultado = reajustar("1000", "IGPM", serie_sintetica("-0.5"), "2026-03")
    assert resultado.valor_final < Decimal("1000")


def test_indice_ausente_lista_competencias():
    serie = serie_sintetica("1.0", meses=3)
    with pytest.raises(IndiceAusente) as erro:
        reajustar("1000", "IPCA", serie, "2026-03")
    assert "2025-04" in str(erro.value)


def test_memoria_traz_cada_competencia():
    resultado = reajustar("1000", "IPCA", serie_sintetica("1.0"), "2026-03")
    assert sum("2025-" in linha or "2026-" in linha for linha in resultado.memoria) >= 12


def test_exito_percentual_simples():
    assert calcular_exito("100000", "20").valor_final == Decimal("20000.00")


def test_exito_aplica_teto_e_piso():
    assert calcular_exito("100000", "20", teto="15000").valor_final == Decimal("15000.00")
    assert calcular_exito("1000", "20", piso="500").valor_final == Decimal("500.00")
