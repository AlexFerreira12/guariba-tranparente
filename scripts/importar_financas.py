#!/usr/bin/env python3
"""Importação conservadora do Balanço Patrimonial (DCA 2025) de Guariba/SP.

Não confundir saldos patrimoniais com receita arrecadada, despesas pagas ou saldo bancário livre.
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "contas-2025.json"
IBGE = 3518602
BASE = "https://apidatalake.tesouro.gov.br/ords/cdwhprd/siconfi/tt/dca"
PARAMS = {"an_exercicio": 2025, "no_anexo": "DCA-Anexo I-AB", "id_ente": IBGE}
SOURCE = BASE + "?" + urlencode(PARAMS)

def main():
    req = Request(SOURCE, headers={"User-Agent":"GuaribaTransparente/0.3 (dados abertos)", "Accept":"application/json"})
    with urlopen(req, timeout=40) as response:
        if response.status != 200 or "json" not in response.headers.get("Content-Type",""):
            raise RuntimeError("Resposta inválida do Tesouro")
        data = json.load(response)
    items = data.get("items", [])
    if not isinstance(items, list) or len(items) < 50 or data.get("hasMore"):
        raise RuntimeError(f"DCA sem todos os itens: {len(items) if isinstance(items,list) else 'inválido'}")
    rows = []
    seen = set()
    for r in items:
        if r.get("cod_ibge") != IBGE or r.get("exercicio") != 2025 or r.get("anexo") != "DCA-Anexo I-AB":
            raise RuntimeError("Dado fora do município, exercício ou anexo")
        if r.get("instituicao") != "Prefeitura Municipal de Guariba - SP" or r.get("coluna") != "31/12/2025":
            raise RuntimeError("Instituição/coluna inesperadas no balanço")
        key = (r.get("cod_conta"),r.get("coluna"))
        if not key[0] or key in seen:
            raise RuntimeError(f"Conta contábil duplicada: {key}")
        seen.add(key)
        try:
            value = Decimal(str(r["valor"]))
            if not value.is_finite():
                raise InvalidOperation("valor não finito")
        except (InvalidOperation, ValueError, KeyError) as exc:
            raise RuntimeError(f"Valor monetário inválido: {key}") from exc
        rows.append({
            "codigo": str(key[0]),
            "conta": str(r.get("conta","")).strip(),
            "valor": float(value.quantize(Decimal("0.01"))),
        })
    rows.sort(key=lambda x:x["codigo"])
    expected = {"P1.0.0.0.0.00.00":"Ativo", "P1.1.1.0.0.00.00":"Caixa e Equivalentes de Caixa"}
    for code,label in expected.items():
        if len([x for x in rows if x["codigo"]==code]) != 1:
            raise RuntimeError(f"Conta principal ausente: {label}")
    result = {
        "origem": "siconfi-dca",
        "municipio": "Guariba/SP",
        "codigoIbge": IBGE,
        "instituicao": "Prefeitura Municipal de Guariba - SP",
        "exercicio": 2025,
        "dataPosicao": "2025-12-31",
        "anexo": "DCA-Anexo I-AB",
        "titulo": "Balanço patrimonial da Prefeitura",
        "nota": "Valores contábeis em reais referentes à posição de 31/12/2025. Contas hierárquicas contêm totais e subtotais: não somar todas as linhas. Não são dados de receita arrecadada nem de despesas pagas.",
        "fonte": SOURCE,
        "contas": rows,
    }
    old = json.loads(DEST.read_text(encoding="utf-8")) if DEST.exists() else {}
    def canonical(x):
        y=dict(x)
        y.pop("coletadoEm",None)
        return y
    if canonical(old)==canonical(result):
        print("DCA 2025 sem mudança:",len(rows),"contas.")
        return
    result["coletadoEm"] = datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat()
    tmp=DEST.with_suffix(".tmp")
    tmp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    tmp.replace(DEST)
    print("DCA 2025 importada:",len(rows),"contas verificadas; fonte:",SOURCE)

if __name__ == "__main__":
    try: main()
    except Exception as exc:
        print("ERRO AO IMPORTAR DCA:",exc,file=sys.stderr)
        sys.exit(1)
