from datetime import date

import pytest

from escritorio.boleto import BoletoInvalido, _mod10, _mod11, ler


def montar_linha(banco="001", moeda="9", livre="1" * 25, fator="9500", valor="0000012345"):
    """Monta uma linha digitável válida a partir dos componentes (apoio de teste)."""
    c1 = banco + moeda + livre[:5]
    c2 = livre[5:15]
    c3 = livre[15:25]
    sem_dv = banco + moeda + fator + valor + livre
    dv_geral = str(_mod11(sem_dv))
    return (
        c1 + str(_mod10(c1))
        + c2 + str(_mod10(c2))
        + c3 + str(_mod10(c3))
        + dv_geral + fator + valor
    )


def test_le_valor_e_banco():
    boleto = ler(montar_linha(), referencia=date(2026, 10, 31))
    assert str(boleto.valor) == "123.45"
    assert boleto.banco == "001"


def test_fator_antes_do_reinicio_de_2025():
    # fator 9500 = 1997-10-07 + 9500 dias
    boleto = ler(montar_linha(fator="9500"), referencia=date(2023, 6, 1))
    assert boleto.vencimento == date(2023, 10, 11)


def test_fator_apos_reinicio_de_2025():
    # fator 1000 volta a valer em 22/02/2025
    boleto = ler(montar_linha(fator="1000"), referencia=date(2025, 3, 1))
    assert boleto.vencimento == date(2025, 2, 22)


def test_fator_zero_significa_sem_vencimento():
    assert ler(montar_linha(fator="0000")).vencimento is None


def test_aceita_pontuacao_e_espacos():
    linha = montar_linha()
    formatada = f"{linha[:5]}.{linha[5:10]} {linha[10:15]}.{linha[15:21]} {linha[21:26]}.{linha[26:32]} {linha[32]} {linha[33:]}"
    assert ler(formatada).codigo_barras == ler(linha).codigo_barras


def test_digito_errado_e_recusado():
    linha = montar_linha()
    errada = linha[:9] + str((int(linha[9]) + 1) % 10) + linha[10:]
    with pytest.raises(BoletoInvalido):
        ler(errada)


def test_tamanho_errado_e_arrecadacao_sao_recusados():
    with pytest.raises(BoletoInvalido):
        ler("123")
    with pytest.raises(BoletoInvalido):
        ler("8" * 48)
