#!/usr/bin/env python3
"""Relaciona matérias legislativas aos históricos oficiais de tramitação do SAPL.

Nunca interpreta o arquivamento como reprovação nem presume obra executada.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from collections import Counter
import json
import sys

from importar_sapl import ROOT, BASE, collect, clean

DEST=ROOT/"data"/"materias.json"
WORKERS=3

def main():
    original=json.loads(DEST.read_text(encoding="utf-8"))
    matters=original.get("materias",[])
    if original.get("apuracao")!="normas-e-votacoes" or len(matters)<400:
        raise RuntimeError("Execute importar_sapl.py e enriquecer_sapl.py antes.")
    statuses=collect("materia/statustramitacao/",max_pages=20)
    status_by_id={s["id"]:clean(s.get("descricao")) for s in statuses}
    if len(status_by_id)<50:
        raise RuntimeError("Catálogo de tramitação incompleto")
    targets=[m["saplId"] for m in matters]
    if len(set(targets))!=len(targets):
        raise RuntimeError("Matérias repetidas")

    def read_one(mid):
        all_rows=collect("materia/tramitacao/",{"materia":mid},max_pages=20)
        result=[]
        for r in all_rows:
            if r.get("materia")!=mid:
                raise RuntimeError(f"Tramitação vinculada a matéria errada: {mid}")
            status_id=r.get("status")
            if status_id not in status_by_id:
                raise RuntimeError(f"Status não catalogado: {status_id}, matéria {mid}")
            result.append({
                "id": r["id"],
                "data": str(r.get("data_tramitacao") or ""),
                "status": status_by_id[status_id],
                "descricao": clean(r.get("texto"))[:800],
                "fonte": f"{BASE}/materia/{mid}",
            })
        result.sort(key=lambda x:(x["data"],x["id"]),reverse=True)
        return mid,result

    histories={}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures=[pool.submit(read_one,ident) for ident in targets]
        for f in as_completed(futures):
            ident,history=f.result()
            histories[ident]=history
    if len(histories)!=len(targets):
        raise RuntimeError("Coleta de tramitações incompleta")
    any_history=0
    for m in matters:
        history=histories[m["saplId"]]
        m["totalTramitacoes"]=len(history)
        m["andamento"]=history[0] if history else None
        m["historico"]=history[:12]
        any_history+=bool(history)
    if any_history<300:
        raise RuntimeError(f"Tramitações insuficientes: {any_history} de {len(matters)}")
    previous=json.loads(DEST.read_text(encoding="utf-8"))
    if previous.get("materias")==matters and previous.get("apuracaoTramitacao")=="api-sapl":
        print("Tramitações sem alterações.")
        return
    original["apuracaoTramitacao"]="api-sapl"
    original["atualizadoEm"]=datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat()
    original["detalhesTramitacao"]="Histórico informado pelo SAPL; a última movimentação não equivale automaticamente à decisão final nem comprova execução administrativa."
    temp=DEST.with_suffix(".tmp")
    temp.write_text(json.dumps(original,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    temp.replace(DEST)
    print(f"TRAMITAÇÕES IMPORTADAS: {any_history}/{len(matters)} matérias com histórico.")
if __name__=="__main__":
    try: main()
    except Exception as exc:
        print("ERRO NA TRAMITAÇÃO:",exc,file=sys.stderr)
        sys.exit(1)
