#!/usr/bin/env python3
"""Importa pregões e dispensas publicados no PNCP em Guariba/SP.

Cobre modalidades 6 (Pregão Eletrônico) e 8 (Dispensa) publicadas desde 2025.
Uma contratação publicada NÃO significa serviço entregue, pago ou homologado.
"""
from datetime import datetime,date
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlencode
from urllib.error import HTTPError,URLError
from zoneinfo import ZoneInfo
import json,time,sys
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"data"/"licitacoes.json"
BASE="https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
MODES=(6,8)
START_YEAR=2025
IBGE="3518602"
def get(params):
    url=BASE+"?"+urlencode(params)
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={"Accept":"application/json","User-Agent":"GuaribaTransparente/0.5"}),timeout=40) as res:
                data=json.load(res)
            if not isinstance(data,dict) or not isinstance(data.get("data"),list):
                raise ValueError("Formato de resposta inesperado")
            return data
        except (HTTPError,URLError,ValueError,TimeoutError,OSError) as exc:
            if attempt==2:raise RuntimeError(f"Falha no PNCP {url}: {exc}") from exc
            time.sleep(2*(attempt+1))
def collect(year,mode,until):
    end=f"{year}1231" if year<until.year else until.strftime("%Y%m%d")
    common={"dataInicial":f"{year}0101","dataFinal":end,"codigoModalidadeContratacao":mode,
            "codigoMunicipioIbge":IBGE,"tamanhoPagina":50}
    first=get({**common,"pagina":1})
    total=first.get("totalRegistros",0)
    pages=first.get("totalPaginas",0)
    if not isinstance(total,int) or total<0 or not isinstance(pages,int) or pages<0 or pages>180:
        raise RuntimeError("Total de registros/páginas inválido no PNCP")
    if total==0 and pages==0:return []
    if pages<1:raise RuntimeError("PNCP retornou paginação inconsistente")
    all_rows=[]
    for page in range(1,pages+1):
        p=first if page==1 else get({**common,"pagina":page})
        if p.get("totalPaginas")!=pages:
            raise RuntimeError("PNCP alterou contagem de páginas durante a coleta")
        all_rows.extend(p["data"])
        time.sleep(0.15)
    if len(all_rows)!=total:
        raise RuntimeError(f"PNCP incompleto, {len(all_rows)} de {total}")
    return all_rows
def main():
    now=datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    rows=[]
    seen=set()
    for year in range(START_YEAR,now.year+1):
        for mode in MODES:
            items=collect(year,mode,now)
            for p in items:
                city=p.get("unidadeOrgao") or {}
                org=p.get("orgaoEntidade") or {}
                if str(city.get("codigoIbge"))!=IBGE or org.get("esferaId")!="M":
                    raise RuntimeError("Registro não municipal ou de cidade diferente dentro da consulta filtrada")
                ident=p.get("numeroControlePNCP")
                if not ident or ident in seen:
                    raise RuntimeError(f"ID ausente/duplicado no PNCP: {ident}")
                seen.add(ident)
                value=p.get("valorTotalEstimado")
                winning=p.get("valorTotalHomologado")
                if value is not None and not isinstance(value,(int,float)):
                    raise RuntimeError("Valor estimado inesperado no PNCP")
                if winning is not None and not isinstance(winning,(int,float)):
                    raise RuntimeError("Valor homologado inesperado no PNCP")
                rows.append({
                    "id":str(ident),
                    "objeto":str(p.get("objetoCompra") or "").strip(),
                    "modalidade":str(p.get("modalidadeNome") or ("Pregão Eletrônico" if mode==6 else "Dispensa")),
                    "modalidadeId":mode,
                    "publicadoEm":str(p.get("dataPublicacaoPncp") or "")[:10],
                    "anoCompra":p.get("anoCompra"),
                    "situacao":str(p.get("situacaoCompraNome") or "Situação não informada"),
                    "valorEstimado":value if value and value>0 else None,
                    "valorHomologado":winning if winning and winning>0 else None,
                    "orgao":str(org.get("razaoSocial") or ""),
                    "cnpj":str(org.get("cnpj") or ""),
                    "fonte":"https://pncp.gov.br/app/editais",
                })
    if len(rows)<100:
        raise RuntimeError(f"Base PNCP pequena demais para este escopo: {len(rows)}")
    rows.sort(key=lambda r:(r["publicadoEm"],r["id"]),reverse=True)
    prev=json.loads(DEST.read_text(encoding="utf-8")) if DEST.exists() else {}
    out={"origem":"pncp-api","municipio":"Guariba/SP","ibge":IBGE,
         "cobertura":"Pregões eletrônicos e dispensas de âmbito municipal publicados de 2025 até a data da última consulta. Outras modalidades e o histórico anterior a 2025 ainda não estão incluídos.",
         "nota":"Valor estimado e homologado não são pagamentos. Licitação publicada não comprova assinatura de contrato, entrega ou execução.",
         "modalidades":[6,8],"anoInicial":START_YEAR,"anoFinal":now.year,
         "registros":rows}
    ptest=dict(prev);ptest.pop("atualizadoEm",None)
    if ptest==out:
        print("PNCP sem alterações:",len(rows),"registros")
        return
    out["atualizadoEm"]=now.isoformat()
    tmp=DEST.with_suffix(".tmp")
    tmp.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    tmp.replace(DEST)
    print("LICITAÇÕES PNCP IMPORTADAS:",len(rows),"registros Guariba/SP modalidades 6 e 8.")
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("ERRO IMPORTAÇÃO PNCP:",exc,file=sys.stderr)
        sys.exit(1)
