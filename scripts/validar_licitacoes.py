#!/usr/bin/env python3
"""Verificação conservadora de licitações publicadas no PNCP para Guariba/SP."""
from pathlib import Path
import json,sys,math,re
FILE=Path(__file__).resolve().parents[1]/"data"/"licitacoes.json"
def main():
    if not FILE.exists():
        print("PNCP aguardando primeira importação validada.")
        return
    d=json.loads(FILE.read_text(encoding="utf-8"))
    assert d["origem"]=="pncp-api" and str(d["ibge"])=="3518602"
    assert d["municipio"]=="Guariba/SP" and sorted(d["modalidades"])==[6,8]
    rows=d["registros"]
    assert len(rows)>=100
    seen=set()
    for r in rows:
        ident=r["id"]
        assert ident and ident not in seen
        seen.add(ident)
        assert r["modalidadeId"] in (6,8)
        assert isinstance(r["objeto"],str) and r["objeto"].strip()
        assert r["fonte"].startswith("https://pncp.gov.br/")
        assert re.fullmatch(r"20\d{2}-\d{2}-\d{2}",r["publicadoEm"])
        for k in ("valorEstimado","valorHomologado"):
            v=r[k]
            assert v is None or (isinstance(v,(int,float)) and math.isfinite(v) and v>=0)
    print("PNCP validado:",len(rows),"publicações sem IDs duplicados.")
if __name__=="__main__":
    try:main()
    except (AssertionError,KeyError,TypeError,ValueError) as e:
        print("ERRO DE INTEGRIDADE PNCP:",e,file=sys.stderr);sys.exit(1)
