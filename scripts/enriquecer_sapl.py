#!/usr/bin/env python3
"""Cruza matérias com normas jurídicas e votações registradas no SAPL de Guariba.

Regra editorial: uma votação registrada NÃO é considerada sanção de lei.
Só vinculamos 'virou lei' quando existe norma do tipo Lei/Lei Complementar
com campo materia apontando para a matéria original.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import sys

from importar_sapl import ROOT, BASE, YEARS, collect, clean

DEST = ROOT / "data" / "materias.json"
EXPECTED_RESULT = {0: "Desconhecido", 1: "Aprovado", 2: "Rejeitado"}

def main() -> None:
    with DEST.open(encoding="utf-8") as handle:
        obj = json.load(handle)
    records = obj["materias"]
    if obj.get("origem") != "sapl-api" or len(records) < 400:
        raise RuntimeError("Base principal ausente ou incompleta. Execute importar_sapl.py antes.")
    matter_ids = {x["saplId"] for x in records}
    types = {x["id"]: x for x in collect("norma/tiponormajuridica/", max_pages=10)}
    normas = [n for ano in YEARS for n in collect(
        "norma/normajuridica/", {"ano": ano}, max_pages=100)]
    indexed_norms = defaultdict(list)
    for n in normas:
        if n.get("materia") not in matter_ids:
            continue
        kind = types.get(n.get("tipo"))
        if not kind:
            raise RuntimeError(f"Tipo de norma desconhecido: {n.get('tipo')}")
        item = {
            "id": n["id"],
            "tipo": clean(kind.get("descricao")),
            "sigla": clean(kind.get("sigla")),
            "numero": str(n.get("numero") or ""),
            "ano": n.get("ano"),
            "data": str(n.get("data") or ""),
            "fonte": f"{BASE}/norma/{n['id']}",
        }
        indexed_norms[n["materia"]].append(item)

    # Esta API possui cerca de 220 páginas de votação de toda a história.
    # Percorrer todas evita depender de filtros por ano não documentados.
    votes_raw = collect("sessao/registrovotacao/", max_pages=500)
    indexed_votes = defaultdict(list)
    for v in votes_raw:
        if v.get("materia") not in matter_ids:
            continue
        result = v.get("tipo_resultado_votacao")
        if result not in EXPECTED_RESULT:
            raise RuntimeError(f"Resultado de votação desconhecido: {result}")
        indexed_votes[v["materia"]].append({
            "id": v["id"],
            "resultado": EXPECTED_RESULT[result],
            "sim": v.get("numero_votos_sim"),
            "nao": v.get("numero_votos_nao"),
            "abstencoes": v.get("numero_abstencoes"),
            "data": str(v.get("data_hora") or ""),
            "observacao": clean(v.get("observacao"))[:500],
            "fonte": f"{BASE}/materia/{v['materia']}",
        })
    published_laws = published_other = has_votes = 0
    for m in records:
        ident = m["saplId"]
        linked = sorted(indexed_norms[ident], key=lambda x: (x["data"], x["id"]))
        registered_votes = sorted(indexed_votes[ident], key=lambda x: (x["data"], x["id"]))
        m["normas"] = linked
        m["votacoes"] = registered_votes
        law = next((n for n in linked if n["sigla"] in ("LEI", "LC")), None)
        if law:
            published_laws += 1
            m["status"] = "virou-lei"
            m["situacao"] = ("Norma jurídica do tipo lei vinculada a esta matéria no SAPL: "
                            + law["tipo"] + " nº " + law["numero"] + "/" + str(law["ano"])
                            + ". Consulte a norma original.")
            m["documento"] = law["tipo"] + " nº " + law["numero"] + "/" + str(law["ano"])
        elif linked:
            published_other += 1
            m["status"] = "norma-publicada"
            top = linked[0]
            m["situacao"] = ("Norma jurídica vinculada no SAPL: " + top["tipo"]
                            + " nº " + top["numero"] + "/" + str(top["ano"]) + ".")
            m["documento"] = top["tipo"] + " nº " + top["numero"] + "/" + str(top["ano"])
        elif m["sigla"] == "IND":
            m["status"] = "solicitado"
            m["situacao"] = "Indicação registrada no SAPL; execução não comprovada automaticamente."
        else:
            m["status"] = "nao-verificado"
            m["situacao"] = ("Matéria cadastrada no SAPL. " +
                ("Há votação(ões) registrada(s); consulte os resultados abaixo. "
                 if registered_votes else "") +
                "Conclusão legislativa e eventual norma vinculada não confirmadas.")
        if registered_votes:
            has_votes += 1

    # Compatibilidade com o frontend. Evita gravar o JSON repetidamente quando nada mudou.
    compared = json.loads(DEST.read_text(encoding="utf-8"))
    if compared.get("materias") == records and compared.get("apuracao") == "normas-e-votacoes":
        print("Não houve alterações nas normas ou votações.")
        return
    obj["apuracao"] = "normas-e-votacoes"
    obj["detalhesApuracao"] = (
        "Status 'Virou lei' exige norma jurídica vinculada no SAPL. "
        "Votos são apresentados como registros de sessão e não substituem sanção/publicação."
    )
    obj["atualizadoEm"] = datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat()
    obj["contagensApuracao"] = {
        "materiasComLeiVinculada": published_laws,
        "materiasComOutraNormaVinculada": published_other,
        "materiasComVotacao": has_votes,
    }
    temp = DEST.with_suffix(".tmp")
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    temp.replace(DEST)
    print("APURAÇÃO:",len(records),"matérias;",published_laws,"com lei vinculada;",
          published_other,"com outras normas;",has_votes,"com votação registrada.")
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("ERRO NA APURAÇÃO:",str(exc),file=sys.stderr)
        sys.exit(1)
