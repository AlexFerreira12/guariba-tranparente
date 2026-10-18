#!/usr/bin/env python3
"""Importa a DCA anual de 2025: receitas e despesas oficiais de Guariba.

Atenção: receitas brutas, deduções, empenhos, liquidações e pagamentos
representam conceitos contábeis diferentes e não devem ser somados entre si.
"""
from datetime import datetime
from decimal import Decimal,InvalidOperation
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
import json,re,sys,time

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"data"/"orcamento-2025.json"
BASE="https://apidatalake.tesouro.gov.br/ords/cdwhprd/siconfi/tt/dca"
IBGE=3518602
ANNEXES={
    "DCA-Anexo I-C":"Receitas orçamentárias",
    "DCA-Anexo I-D":"Despesas por natureza",
    "DCA-Anexo I-E":"Despesas por função",
}
COLUMNS={
    "DCA-Anexo I-C":{"Receitas Brutas Realizadas","Deduções - FUNDEB","Outras Deduções da Receita"},
    "DCA-Anexo I-D":{"Despesas Empenhadas","Despesas Liquidadas","Despesas Pagas"},
    "DCA-Anexo I-E":{"Despesas Empenhadas","Despesas Liquidadas","Despesas Pagas"},
}
def source(annex):
    return BASE+"?"+urlencode({"an_exercicio":2025,"no_anexo":annex,"id_ente":IBGE})
def fetch(annex):
    req=Request(source(annex),headers={"Accept":"application/json","User-Agent":"GuaribaTransparente/0.4"})
    with urlopen(req,timeout=45) as response:
        if response.status!=200 or "json" not in response.headers.get("Content-Type",""):
            raise RuntimeError("Resposta inválida do Tesouro: "+annex)
        data=json.load(response)
    items=data.get("items")
    if not isinstance(items,list) or len(items)<50 or data.get("hasMore"):
        raise RuntimeError("Conjunto incompleto: "+annex)
    return items
def main():
    rows=[]
    sources={}
    seen=set()
    for annex in ANNEXES:
        items=fetch(annex)
        sources[annex]=source(annex)
        for r in items:
            if (r.get("cod_ibge")!=IBGE or r.get("exercicio")!=2025 or
                r.get("instituicao")!="Prefeitura Municipal de Guariba - SP" or
                r.get("anexo")!=annex or r.get("coluna") not in COLUMNS[annex]):
                raise RuntimeError("Registro fora da competência, instituição ou coluna: "+annex)
            key=(annex,str(r.get("cod_conta")),str(r.get("conta")),str(r.get("coluna")))
            if key in seen or not r.get("conta"):
                raise RuntimeError("Registro duplicado ou sem nome de conta: "+str(key))
            seen.add(key)
            try:
                amount=Decimal(str(r["valor"]))
                if not amount.is_finite(): raise InvalidOperation("Não finito")
            except (InvalidOperation,KeyError,TypeError):
                raise RuntimeError("Valor inválido da DCA: "+str(key))
            rows.append({"anexo":annex,"codigo":key[1],"conta":key[2],"coluna":key[3],
                         "valor":float(amount.quantize(Decimal("0.01")))})
        time.sleep(1.1)
    def metric(annex,code,column):
        found=[r["valor"] for r in rows if r["anexo"]==annex and r["codigo"]==code and r["coluna"]==column]
        if len(found)!=1: raise RuntimeError(f"Indicador ausente/duplicado: {annex} {code} {column}")
        return found[0]
    keys={
        "receitasBrutasExcetoIntra":metric("DCA-Anexo I-C","ReceitasExcetoIntraOrcamentarias","Receitas Brutas Realizadas"),
        "deducoesFundebExcetoIntra":metric("DCA-Anexo I-C","ReceitasExcetoIntraOrcamentarias","Deduções - FUNDEB"),
        "outrasDeducoesExcetoIntra":metric("DCA-Anexo I-C","ReceitasExcetoIntraOrcamentarias","Outras Deduções da Receita"),
        "despesasEmpenhadas":metric("DCA-Anexo I-D","TotalDespesas","Despesas Empenhadas"),
        "despesasLiquidadas":metric("DCA-Anexo I-D","TotalDespesas","Despesas Liquidadas"),
        "despesasPagas":metric("DCA-Anexo I-D","TotalDespesas","Despesas Pagas"),
    }
    if not (keys["despesasEmpenhadas"]>=keys["despesasLiquidadas"]>=keys["despesasPagas"]>=0):
        raise RuntimeError("Inconsistência no total de estágios das despesas")
    functions=sorted([{"funcao":r["conta"],"valor":r["valor"]}
                      for r in rows if r["anexo"]=="DCA-Anexo I-E" and
                      r["codigo"]=="TotalDespesas" and r["coluna"]=="Despesas Pagas" and
                      re.match(r"^\d{2}\s*-\s+",r["conta"])],key=lambda r:r["funcao"])
    if len(functions)<8:
        raise RuntimeError(f"Funções orçamentárias insuficientes: {len(functions)}")
    out={
        "origem":"siconfi-dca-orcamentaria",
        "codigoIbge":IBGE,
        "instituicao":"Prefeitura Municipal de Guariba - SP",
        "exercicio":2025,
        "titulo":"Receitas e despesas orçamentárias anuais",
        "metodologia":"Dados anuais da DCA enviados ao Tesouro Nacional. Valores de receitas são BRUTOS exceto intraorçamentárias; deduções informadas separadamente. Despesas são apresentadas por estágio. Não somar linhas de totais e subtotais dos anexos.",
        "indicadores":keys,
        "despesasPorFuncaoPagas":functions,
        "fontes":sources,
        "registros":rows,
    }
    previous=json.loads(DEST.read_text(encoding="utf-8")) if DEST.exists() else {}
    test=dict(previous)
    test.pop("coletadoEm",None)
    if test==out:
        print("Orçamento DCA 2025 sem mudanças:",len(rows),"registros")
        return
    out["coletadoEm"]=datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat()
    tmp=DEST.with_suffix(".tmp")
    tmp.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    tmp.replace(DEST)
    print("ORÇAMENTO DCA 2025 IMPORTADO:",len(rows),"registros;",len(functions),"funções.")
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("ERRO ORÇAMENTO DCA:",exc,file=sys.stderr)
        sys.exit(1)
