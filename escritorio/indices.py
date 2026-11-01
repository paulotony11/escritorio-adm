"""Índices de reajuste (IPCA, IGP-M): cache em CSV e atualização pelo Banco Central.

O arquivo contexto/indices.csv tem as colunas: indice, competencia (AAAA-MM),
variacao_percentual. Nenhum valor vem embutido no código: a fonte é o BCB (SGS)
ou o que o escritório digitar/conferir no CSV.
"""

import csv
import json
import urllib.request
from datetime import date
from decimal import Decimal
from pathlib import Path

# Códigos SGS do Banco Central. Confirme em https://www3.bcb.gov.br/sgspub/
SGS = {"IPCA": 433, "IGPM": 189}
CAMPOS = ("indice", "competencia", "variacao_percentual")

Serie = dict[str, Decimal]


class IndiceAusente(Exception):
    """Faltam competências do índice no CSV."""


def somar_meses(competencia: str, meses: int) -> str:
    ano, mes = (int(p) for p in competencia.split("-"))
    total = ano * 12 + (mes - 1) + meses
    return f"{total // 12:04d}-{total % 12 + 1:02d}"


def janela(mes_reajuste: str, meses: int = 12, defasagem: int = 1) -> tuple[str, ...]:
    """Competências acumuladas: `meses` meses terminando `defasagem` meses antes do reajuste."""
    fim = somar_meses(mes_reajuste, -defasagem)
    inicio = somar_meses(fim, -(meses - 1))
    return tuple(somar_meses(inicio, i) for i in range(meses))


def carregar(caminho: Path) -> dict[str, Serie]:
    series: dict[str, Serie] = {}
    if not caminho.exists():
        return series
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            nome = linha["indice"].strip().upper()
            series.setdefault(nome, {})[linha["competencia"].strip()] = Decimal(
                linha["variacao_percentual"].strip().replace(",", ".")
            )
    return series


def salvar(caminho: Path, series: dict[str, Serie]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(CAMPOS)
        for nome in sorted(series):
            for competencia in sorted(series[nome]):
                escritor.writerow([nome, competencia, series[nome][competencia]])


def fator_acumulado(serie: Serie, competencias: tuple[str, ...]) -> Decimal:
    faltantes = [c for c in competencias if c not in serie]
    if faltantes:
        raise IndiceAusente(
            f"Faltam competências no índice: {', '.join(faltantes)}. "
            "Rode 'python -m escritorio indices' ou confira contexto/indices.csv."
        )
    fator = Decimal(1)
    for competencia in competencias:
        fator *= Decimal(1) + serie[competencia] / Decimal(100)
    return fator


URL_SGS = (
    "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
    "?formato=json&dataInicial={inicio}&dataFinal={fim}"
)


def baixar_bcb(nome: str, inicio: str, fim: str | None = None) -> Serie:
    """Baixa a série mensal do BCB (API SGS). `inicio` e `fim` em AAAA-MM-DD.

    O BCB limita consultas de séries diárias a 10 anos; as de IPCA e IGP-M são
    mensais, mas mantenha janelas curtas (poucos anos).
    """
    inicio_data = date.fromisoformat(inicio)
    fim_data = date.fromisoformat(fim) if fim else date.today()
    url = URL_SGS.format(
        codigo=SGS[nome.upper()],
        inicio=inicio_data.strftime("%d/%m/%Y"),
        fim=fim_data.strftime("%d/%m/%Y"),
    )
    with urllib.request.urlopen(url, timeout=30) as resposta:  # noqa: S310 (URL fixa https)
        registros = json.load(resposta)
    serie: Serie = {}
    for item in registros:
        dia, mes, ano = item["data"].split("/")
        serie[f"{ano}-{mes}"] = Decimal(item["valor"])
    return serie


def atualizar(caminho: Path, inicio: str) -> dict[str, Serie]:
    """Atualiza o CSV com IPCA e IGP-M; devolve as séries completas."""
    series = carregar(caminho)
    for nome in SGS:
        series[nome] = {**series.get(nome, {}), **baixar_bcb(nome, inicio)}
    salvar(caminho, series)
    return series
