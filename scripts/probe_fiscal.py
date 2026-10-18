#!/usr/bin/env python3
"""Sonda endpoints públicos do SICONFI: nenhuma cifra é publicada sem validação."""
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError,URLError
import json
BASES=["https://apidatalake.tesouro.gov.br/ords/cdwhprd/siconfi/tt/",
       "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/"]
cases=[
 ("extrato_entregas",{"id_ente":3518602,"an_referencia":2025}),
 ("rreo",{"an_exercicio":2025,"nr_periodo":6,"co_tipo_demonstrativo":"RREO",
          "no_anexo":"RREO-Anexo 01","co_esfera":"M","id_ente":3518602}),
 ("rreo",{"an_exercicio":2025,"nr_periodo":6,"co_tipo_demonstrativo":"RREO",
          "no_anexo":"RREO-Anexo 01","id_ente":3518602}),
 ("dca",{"an_exercicio":2025,"no_anexo":"DCA-Anexo I-AB","id_ente":3518602}),
]
for base in BASES:
    for endpoint,params in cases:
        url=base+endpoint+"?"+urlencode(params)
        try:
            with urlopen(Request(url,headers={"User-Agent":"GuaribaTransparente/0.3","Accept":"application/json"}),timeout=20) as response:
                body=json.load(response)
            records=body.get("items",[])
            print("FISCAL",base,endpoint,str(params),"itens",len(records),"keys",list(records[0]) if records else [],"amostra",json.dumps(records[:1],ensure_ascii=False)[:1800])
        except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
            print("FISCAL FALHA",base,endpoint,str(exc)[:200])
