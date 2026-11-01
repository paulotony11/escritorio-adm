"""Linha de comando usada pelas skills: uv run python -m escritorio <comando>."""

import argparse
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from escritorio import boleto, cobranca, conciliacao, honorarios, indices
from escritorio.dinheiro import brl

RAIZ = Path.cwd()
CSV_INDICES = RAIZ / "contexto" / "indices.csv"
SAIDA = RAIZ / "relatorios"


def _ler_tabela(caminho: Path) -> pd.DataFrame:
    if caminho.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(caminho)
    return pd.read_csv(caminho, sep=None, engine="python", encoding="utf-8-sig")


def _caminho_saida(nome: str) -> Path:
    SAIDA.mkdir(parents=True, exist_ok=True)
    return SAIDA / f"{date.today().isoformat()}_{nome}.xlsx"


def cmd_reajuste(args) -> int:
    series = indices.carregar(CSV_INDICES)
    nome = args.indice.upper()
    if nome not in series:
        print(f"Índice {nome} ausente em {CSV_INDICES}. Rode: python -m escritorio indices")
        return 2
    resultado = honorarios.reajustar(
        args.valor, nome, series[nome], args.mes_reajuste,
        defasagem=args.defasagem, permitir_reducao=not args.sem_reducao,
    )
    print("\n".join(resultado.memoria))
    return 0


def cmd_exito(args) -> int:
    resultado = honorarios.calcular_exito(args.base, args.percentual, args.piso, args.teto)
    print("\n".join(resultado.memoria))
    return 0


def cmd_aging(args) -> int:
    contas = cobranca.aging(_ler_tabela(Path(args.arquivo)), date.today())
    resumo = cobranca.resumo_por_faixa(contas)
    destino = _caminho_saida("aging")
    with pd.ExcelWriter(destino) as escritor:
        resumo.assign(valor=resumo["valor"].map(brl)).to_excel(escritor, "resumo", index=False)
        contas.assign(valor=contas["valor"].map(brl)).to_excel(escritor, "detalhe", index=False)
    print(resumo.assign(valor=resumo["valor"].map(brl)).to_string(index=False))
    print(f"\nSalvo em {destino}")
    return 0


def cmd_conciliar(args) -> int:
    caminho = Path(args.extrato)
    if caminho.suffix.lower() in (".ofx", ".qfx"):
        extrato = conciliacao.ler_ofx(caminho)
    else:
        extrato = conciliacao.ler_csv(caminho, args.col_data, args.col_valor, args.col_descricao)
    lancamentos = conciliacao.normalizar_lancamentos(_ler_tabela(Path(args.lancamentos)))
    conciliados, sem_par_extrato, sem_par_lanc = conciliacao.conciliar(
        extrato, lancamentos, args.tolerancia
    )
    destino = _caminho_saida("conciliacao")
    with pd.ExcelWriter(destino) as escritor:
        conciliados.to_excel(escritor, "conciliados", index=False)
        sem_par_extrato.to_excel(escritor, "extrato_sem_lancamento", index=False)
        sem_par_lanc.to_excel(escritor, "lancamento_sem_extrato", index=False)
    print(
        f"Conciliados: {len(conciliados)} | extrato sem lançamento: {len(sem_par_extrato)} "
        f"| lançamento sem extrato: {len(sem_par_lanc)}\nSalvo em {destino}"
    )
    return 0


def cmd_boleto(args) -> int:
    try:
        lido = boleto.ler(args.linha)
    except boleto.BoletoInvalido as erro:
        print(f"Boleto não validado: {erro}")
        return 2
    venc = lido.vencimento.strftime("%d/%m/%Y") if lido.vencimento else "sem vencimento"
    print(f"Banco: {lido.banco} | Valor: {brl(lido.valor)} | Vencimento: {venc}")
    return 0


def cmd_indices(args) -> int:
    series = indices.atualizar(CSV_INDICES, args.desde)
    for nome, serie in series.items():
        ultima = max(serie)
        print(f"{nome}: {len(serie)} competências, última {ultima} ({serie[ultima]}%)")
    return 0


def montar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="escritorio")
    sub = parser.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("reajuste", help="reajusta um valor pelo IPCA ou IGPM")
    p.add_argument("--valor", required=True)
    p.add_argument("--indice", required=True, choices=["IPCA", "IGPM", "ipca", "igpm"])
    p.add_argument("--mes-reajuste", required=True, help="AAAA-MM")
    p.add_argument("--defasagem", type=int, default=1)
    p.add_argument("--sem-reducao", action="store_true")
    p.set_defaults(func=cmd_reajuste)

    p = sub.add_parser("exito", help="calcula honorários de êxito")
    p.add_argument("--base", required=True)
    p.add_argument("--percentual", required=True)
    p.add_argument("--piso")
    p.add_argument("--teto")
    p.set_defaults(func=cmd_exito)

    p = sub.add_parser("aging", help="aging de contas a receber")
    p.add_argument("--arquivo", required=True)
    p.set_defaults(func=cmd_aging)

    p = sub.add_parser("conciliar", help="concilia extrato com lançamentos")
    p.add_argument("--extrato", required=True)
    p.add_argument("--lancamentos", required=True)
    p.add_argument("--tolerancia", type=int, default=3)
    p.add_argument("--col-data", default="Data")
    p.add_argument("--col-valor", default="Valor")
    p.add_argument("--col-descricao", default="Descrição")
    p.set_defaults(func=cmd_conciliar)

    p = sub.add_parser("boleto", help="lê a linha digitável de um boleto")
    p.add_argument("linha")
    p.set_defaults(func=cmd_boleto)

    p = sub.add_parser("indices", help="atualiza IPCA e IGPM pelo Banco Central")
    p.add_argument("--desde", default="2020-01-01")
    p.set_defaults(func=cmd_indices)
    return parser


def main(argv: list[str] | None = None) -> int:
    # console do Windows costuma usar cp1252/cp850: força UTF-8 para acentos
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    args = montar_parser().parse_args(argv)
    try:
        return args.func(args)
    except (indices.IndiceAusente, cobranca.ColunasAusentes, FileNotFoundError, KeyError) as erro:
        print(f"Erro: {erro}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
