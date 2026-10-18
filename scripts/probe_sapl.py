#!/usr/bin/env python3
"""Diagnóstico SOMENTE LEITURA dos endpoints públicos do SAPL de Guariba."""
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
from urllib.parse import urlencode

BASE="https://sapl.guariba.sp.leg.br/api/"
PATHS=[
    ("materias-2025","materia/materialegislativa/",{"ano":2025,"page":1}),
    ("materias-2026","materia/materialegislativa/",{"ano":2026,"page":1}),
    ("parlamentares","parlamentares/parlamentar/",{"page":1}),
    ("autoria","materia/autoria/",{"page":1}),
    ("tramitacao","materia/tramitacao/",{"page":1}),
    ("tipomateria","materia/tipomaterialegislativa/",{"page":1}),
    ("norma","norma/normajuridica/",{"page":1}),
    ("base-autor","base/autor/",{"page":1}),
    ("autores-parlamentar","base/autor/",{"parlamentar":31,"page":1}),
    ("autoria-filtro","materia/autoria/",{"materia":11461,"page":1}),
    ("tramitacao-filtro","materia/tramitacao/",{"materia":11461,"page":1}),
]
def sample(label, endpoint, query):
    url=BASE+endpoint+"?"+urlencode(query)
    try:
        with urlopen(Request(url,headers={"User-Agent":"GuaribaTransparente/0.2 dados-publicos","Accept":"application/json"}), timeout=18) as response:
            payload=json.load(response)
            assert isinstance(payload,dict) and isinstance(payload.get("results"),list), "JSON com formato inesperado"
            rows=payload["results"]
            print(label,"HTTP",response.status,"pagination",json.dumps(payload.get("pagination"),ensure_ascii=False)[:500],"rows",len(rows))
            for row in rows[:2]:
                wanted=["id","ano","numero","tipo","ementa","autores","autor","parlamentar","materia","data_apresentacao","data_tramitacao","status","status_id","unidade_tramitacao_local","descricao","sigla","descricao_original","texto","norma","resultado","em_tramitacao","link_detail_backend","nome_parlamentar","nome","tipo","autor","parlamentar","autor_id","partido","descricao","descricao_original","cargo","ativo","tipo_autor"]
                obj={k:row[k] for k in wanted if k in row}
                print(label,"sample",json.dumps(obj,ensure_ascii=False,default=str)[:1600])
    except (HTTPError,URLError,TimeoutError,ValueError,TypeError,AssertionError,OSError) as err:
        print(label,"ERRO",str(err)[:250])
if __name__=="__main__":
    for args in PATHS:
        sample(*args)
