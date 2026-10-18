#!/usr/bin/env python3
"""Validar origem, competência e integridade do balanço patrimonial público."""
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
import json, math, sys

FILE = Path(__file__).resolve().parents[1]/"data"/"contas-2025.json"
def main():
    if not FILE.exists():
        print("DCA ainda não importada: verificação financeira omitida.")
        return
    data=json.loads(FILE.read_text(encoding="utf-8"))
    assert data["origem"]=="siconfi-dca"
    assert data["codigoIbge"]==3518602
    assert data["instituicao"]=="Prefeitura Municipal de Guariba - SP"
    assert data["exercicio"]==2025 and data["dataPosicao"]=="2025-12-31"
    assert data["anexo"]=="DCA-Anexo I-AB"
    p=urlsplit(data["fonte"])
    assert p.scheme=="https" and p.netloc=="apidatalake.tesouro.gov.br"
    assert p.path.endswith("/siconfi/tt/dca")
    q=parse_qs(p.query)
    assert q.get("id_ente")==["3518602"] and q.get("an_exercicio")==["2025"]
    records=data["contas"]
    assert 50<=len(records)<=250, "Volume inesperado de contas"
    seen=set()
    for x in records:
        assert isinstance(x["codigo"],str) and x["codigo"] not in seen
        assert isinstance(x["conta"],str) and x["conta"]
        assert isinstance(x["valor"],(int,float)) and math.isfinite(x["valor"])
        seen.add(x["codigo"])
    assert {"P1.0.0.0.0.00.00","P1.1.1.0.0.00.00"}.issubset(seen)
    print("DCA validada:",len(records),"contas; órgão: Prefeitura de Guariba; competência: 2025.")
if __name__=="__main__":
    try: main()
    except (AssertionError,KeyError,ValueError,TypeError) as exc:
        print("Falha na validação financeira:",exc,file=sys.stderr)
        sys.exit(1)
