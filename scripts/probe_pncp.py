#!/usr/bin/env python3
"""Diagnóstico não destrutivo dos dados públicos de contratações do PNCP."""
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError,URLError
import json,time
BASE="https://pncp.gov.br/api/consulta/v1/"
TESTS=[
 ("contratos-2025","contratos",{"dataInicial":"20250101","dataFinal":"20251231","codigoMunicipioIbge":3518602,"pagina":1,"tamanhoPagina":10}),
 ("contratos-2026","contratos",{"dataInicial":"20260101","dataFinal":"20261017","codigoMunicipioIbge":3518602,"pagina":1,"tamanhoPagina":10}),
 ("licitacao-pregao","contratacoes/publicacao",{"dataInicial":"20260101","dataFinal":"20261017","codigoModalidadeContratacao":6,"codigoMunicipioIbge":3518602,"pagina":1,"tamanhoPagina":10}),
 ("licitacao-dispensa","contratacoes/publicacao",{"dataInicial":"20260101","dataFinal":"20261017","codigoModalidadeContratacao":8,"codigoMunicipioIbge":3518602,"pagina":1,"tamanhoPagina":10}),
]
for title,endpoint,params in TESTS:
    url=BASE+endpoint+"?"+urlencode(params)
    try:
        with urlopen(Request(url,headers={"User-Agent":"GuaribaTransparente/0.5","Accept":"application/json"}),timeout=30) as res:
            payload=json.load(res)
        rows=payload.get("data",[]) if isinstance(payload,dict) else []
        if not isinstance(rows,list): rows=[]
        print("PNCP",title,"itens",len(rows),"total",payload.get("totalRegistros"),"paginas",payload.get("totalPaginas"),"campos",list(rows[0]) if rows else [])
        for row in rows[:2]:
            keys=("numeroControlePNCP","objetoCompra","objetoContrato","valorTotalEstimado","valorGlobal","orgaoEntidade","unidadeOrgao","dataPublicacaoPncp","numeroCompra","modalidadeNome","linkSistemaOrigem")
            print("PNCP EXEMPLO",title,json.dumps({k:row.get(k) for k in keys if k in row},ensure_ascii=False,default=str)[:1300])
    except HTTPError as exc:
        print("PNCP FALHA",title,"HTTP",exc.code,exc.read(300).decode("utf-8","replace")[:250])
    except (URLError,ValueError,OSError,TimeoutError) as exc:
        print("PNCP FALHA",title,str(exc)[:250])
    time.sleep(1)
