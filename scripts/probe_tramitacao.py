#!/usr/bin/env python3
"""Diagnóstico de vínculos legislativos; nunca altera dados do site."""
import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError,URLError
BASE="https://sapl.guariba.sp.leg.br/api/"
URLS=[
 ("status","materia/statustramitacao/",{}),
 ("status-alt","materia/status/",{}),
 ("votacoes","sessao/registrovotacao/",{"page":1}),
 ("votos-parlamentares","sessao/votoparlamentar/",{"page":1}),
 ("norma-vinculada-PL","norma/normajuridica/",{"materia":11215,"page":1}),
 ("normas-2025","norma/normajuridica/",{"ano":2025,"page":1}),
 ("tram-ind","materia/tramitacao/",{"materia":11461,"page":1}),
 ("tram-subs","materia/tramitacao/",{"materia":11215,"page":1}),
 ("votacoes-filtradas","sessao/registrovotacao/",{"materia":11215,"page":1}),
 ("votacoes-ind","sessao/registrovotacao/",{"materia":11461,"page":1}),
 ("normas-2026","norma/normajuridica/",{"ano":2026,"page":1}),
 ("tipos-normas","norma/tiponormajuridica/",{"page":1}),
 ("tipos-resultado-votacao","sessao/tiporesultadovotacao/",{"page":1}),
]
for label,path,params in URLS:
    url=BASE+path+"?"+urlencode(params)
    try:
        with urlopen(Request(url,headers={"User-Agent":"GuaribaTransparente/0.3","Accept":"application/json"}),timeout=18) as res:
            data=json.load(res)
        rows=data.get("results",[]) if isinstance(data,dict) else []
        print(label,"TOTAL",data.get("pagination",{}).get("total_entries"),"fields",sorted(rows[0]) if rows else [])
        if label.startswith("status") or label.startswith("tipos-"):
            for x in rows[:12]:print(label,"status",json.dumps(x,ensure_ascii=False,default=str)[:600])
        else:
            for x in rows[:3]:
                allow=("id","materia","ano","numero","tipo","ementa","texto","status","resultado","tipo_resultado","observacao","data_tramitacao","data","data_sessao","link_detail_backend","autores","turno","votacao","norma")
                print(label,"row",json.dumps({k:x.get(k) for k in allow if k in x},ensure_ascii=False,default=str)[:1500])
    except (HTTPError,URLError,ValueError,TimeoutError,OSError) as exc:
        print(label,"ERROR",str(exc)[:280])
