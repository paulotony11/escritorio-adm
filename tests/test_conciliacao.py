from datetime import date

import pandas as pd

from escritorio.conciliacao import conciliar, ler_csv, normalizar_lancamentos


def extrato():
    return pd.DataFrame(
        {
            "data": [date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 10)],
            "valor_centavos": [150000, -30000, 9999],
            "descricao": ["TED cliente A", "Aluguel", "Tarifa"],
            "id": ["1", "2", "3"],
        }
    )


def lancamentos():
    return normalizar_lancamentos(
        pd.DataFrame(
            {
                "data": ["02/10/2026", "03/10/2026", "20/10/2026"],
                "valor": ["1.500,00", "-300,00", "-45,00"],
                "descricao": ["Honorários A", "Aluguel outubro", "Material"],
            }
        )
    )


def test_concilia_por_valor_exato_e_tolerancia_de_data():
    conciliados, sem_extrato, sem_lanc = conciliar(extrato(), lancamentos(), tolerancia_dias=3)
    assert len(conciliados) == 2
    assert list(sem_extrato["descricao"]) == ["Tarifa"]
    assert list(sem_lanc["descricao"]) == ["Material"]


def test_fora_da_tolerancia_fica_pendente():
    conciliados, _, _ = conciliar(extrato(), lancamentos(), tolerancia_dias=0)
    assert len(conciliados) == 0


def test_cada_lancamento_casa_uma_unica_vez():
    duplicado = pd.concat([extrato().iloc[[0]], extrato().iloc[[0]]], ignore_index=True)
    conciliados, sem_extrato, _ = conciliar(duplicado, lancamentos(), tolerancia_dias=3)
    assert len(conciliados) == 1
    assert len(sem_extrato) == 1


def test_ler_csv_com_formato_brasileiro(tmp_path):
    arquivo = tmp_path / "extrato.csv"
    arquivo.write_text(
        "Data;Valor;Descrição\n01/10/2026;1.500,00;TED\n02/10/2026;-300,00;Aluguel\n",
        encoding="utf-8",
    )
    lido = ler_csv(arquivo, "Data", "Valor", "Descrição")
    assert list(lido["valor_centavos"]) == [150000, -30000]
    assert lido.at[0, "data"] == date(2026, 10, 1)
