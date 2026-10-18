#!/usr/bin/env python3
"""Verifica dados abertos fiscais de Guariba no Tesouro (sem publicar números)."""
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError,URLError
import json
from itertools import islice
BASE="https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
for ano,periodo in ((2025,6),(2026,4),(2026,5)):
    params={"an_exercicio":ano,"nr_periodo":periodo,"co_tipo_demonstrativo":"RREO","no_anexo":"RREO-Anexo 01","co_esfera":"M","id_ente":3518602}
    url=BASE+"?"+urlencode(params)
    print("CONSULTA",ano,periodo,url)
    try:
        with urlopen(Request(url,headers={"User-Agent":"GuaribaTransparente/0.3","Accept":"application/json"}),timeout=25) as res:
            data=json.load(res)
        rows=data.get("items",[])
        print("RESPOSTA",len(rows),"hasMore",data.get("hasMore"),"campos",list(rows[0]) if rows else [],"first",json.dumps(rows[:3],ensure_ascii=False)[:3800])
        found=[x for x in rows if any(term in str(x).upper() for term in ("TOTAL DAS RECEITAS","TOTAL DE RECEITAS","TOTAL DAS DESPESAS","RECEITAS REALIZADAS"))]
        for x in found[:5]: print("SOMA-CANDIDATA",json.dumps(x,ensure_ascii=False)[:1100])
    except (HTTPError,URLError,TimeoutError,OSError,ValueError) as e:
        print("FALHA",str(e)[:400])
