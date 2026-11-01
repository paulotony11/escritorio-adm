"""Conciliação bancária: leitura de extrato (OFX/CSV) e casamento com lançamentos."""

from pathlib import Path

import pandas as pd

from escritorio.dinheiro import para_centavos

COLUNAS_EXTRATO = ["data", "valor_centavos", "descricao", "id"]


def ler_ofx(caminho: Path) -> pd.DataFrame:
    from ofxtools.Parser import OFXTree

    arvore = OFXTree()
    arvore.parse(str(caminho))
    ofx = arvore.convert()
    linhas = [
        {
            "data": t.dtposted.date(),
            "valor_centavos": para_centavos(t.trnamt),
            "descricao": (t.memo or t.name or "").strip(),
            "id": t.fitid,
        }
        for extrato in ofx.statements
        for t in extrato.transactions
    ]
    return pd.DataFrame(linhas, columns=COLUNAS_EXTRATO)


def ler_csv(
    caminho: Path,
    col_data: str,
    col_valor: str,
    col_descricao: str,
    separador: str = ";",
) -> pd.DataFrame:
    bruto = pd.read_csv(caminho, sep=separador, dtype=str, encoding="utf-8-sig")
    return pd.DataFrame(
        {
            "data": pd.to_datetime(bruto[col_data], dayfirst=True).dt.date,
            "valor_centavos": bruto[col_valor].map(para_centavos),
            "descricao": bruto[col_descricao].fillna("").str.strip(),
            "id": bruto.index.astype(str),
        }
    )


def normalizar_lancamentos(lancamentos: pd.DataFrame) -> pd.DataFrame:
    """Espera colunas data, valor (entradas positivas, saídas negativas) e descricao."""
    return pd.DataFrame(
        {
            "data": pd.to_datetime(lancamentos["data"], dayfirst=True).dt.date,
            "valor_centavos": lancamentos["valor"].map(para_centavos),
            "descricao": lancamentos["descricao"].fillna("").astype(str).str.strip(),
            "id": lancamentos.index.astype(str),
        }
    )


def conciliar(
    extrato: pd.DataFrame,
    lancamentos: pd.DataFrame,
    tolerancia_dias: int = 3,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Casa um a um por valor exato e data dentro da tolerância.

    Devolve (conciliados, extrato_sem_par, lancamentos_sem_par). Nunca decide
    sozinho em caso de dúvida: o que não casa exatamente fica pendente.
    """
    livres = set(lancamentos.index)
    pares = []
    for i, linha in extrato.sort_values("data").iterrows():
        candidatos = [
            (abs((lancamentos.at[j, "data"] - linha["data"]).days), j)
            for j in livres
            if lancamentos.at[j, "valor_centavos"] == linha["valor_centavos"]
            and abs((lancamentos.at[j, "data"] - linha["data"]).days) <= tolerancia_dias
        ]
        if not candidatos:
            continue
        _, escolhido = min(candidatos)
        livres.discard(escolhido)
        pares.append((i, escolhido))

    conciliados = pd.DataFrame(
        [
            {
                "data_extrato": extrato.at[i, "data"],
                "data_lancamento": lancamentos.at[j, "data"],
                "valor": extrato.at[i, "valor_centavos"] / 100,
                "descricao_extrato": extrato.at[i, "descricao"],
                "descricao_lancamento": lancamentos.at[j, "descricao"],
            }
            for i, j in pares
        ]
    )
    usados_extrato = {i for i, _ in pares}
    return (
        conciliados,
        extrato[~extrato.index.isin(usados_extrato)].reset_index(drop=True),
        lancamentos[lancamentos.index.isin(livres)].reset_index(drop=True),
    )
