#!/usr/bin/env python3
"""Importa registros públicos de 2025/2026 do SAPL de Guariba.

Não infere aprovação, sanção, execução nem resultados eleitorais.
Somente associa autoria quando o ID do autor foi confirmado no SAPL.
"""
from __future__ import annotations
from datetime import datetime
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
import json
import re
import sys
import time

BASE = "https://sapl.guariba.sp.leg.br"
API = BASE + "/api/"
ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "materias.json"
YEARS = (2025, 2026)
# Mapeamento exato: ID do autor -> slug do perfil dos eleitos em 2024.
# IDs auditados contra /api/base/autor/, jamais inferidos pela semelhança de nomes.
ELECTED_AUTHOR_IDS = {
    16: "cassio-santa-cruz", 49: "fabiano-da-bocha",
    35: "marcia-alves", 46: "andinho", 2: "marquinhos-osti",
    53: "anselmo-gimenes", 51: "roberto-carosio-filho",
    12: "paulo-de-sa", 34: "calao-galeto", 38: "magna-rocha",
    48: "paulo-da-sucata",
}
EXPECTED_NAMES = {
    16: "Cassio Santa Cruz", 49: "Fabiano Da Bocha",
    35: "Márcia Alves", 46: "Andinho", 2: "Marquinhos Osti",
    53: "Anselmo Gimenes", 51: "Roberto Carósio Filho",
    12: "Paulo de Sa", 34: "Calão - Galeto", 38: "Magna Rocha",
    48: "Paulo Da Sucata",
}

def get_json(path: str, params: dict) -> dict:
    url = API + path + "?" + urlencode(params)
    for attempt in range(3):
        try:
            req = Request(url, headers={
                "Accept": "application/json",
                "User-Agent": "GuaribaTransparente/0.2 (consulta de dados publicos)",
            })
            with urlopen(req, timeout=25) as response:
                if response.status != 200 or "json" not in response.headers.get("Content-Type", ""):
                    raise ValueError("Resposta não JSON ou HTTP não 200")
                payload = json.load(response)
            if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
                raise ValueError("Formato inesperado da API")
            return payload
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
            if attempt == 2:
                raise RuntimeError(f"Falha ao coletar {url}: {exc}") from exc
            time.sleep(1 + attempt * 2)
    raise AssertionError("Inalcançável")

def collect(path: str, params: dict | None = None, max_pages: int = 100) -> list[dict]:
    params = params or {}
    rows = []
    seen = set()
    first = get_json(path, {**params, "page": 1})
    pagination = first.get("pagination", {})
    total_pages = pagination.get("total_pages")
    expected_count = pagination.get("total_entries")
    if not isinstance(total_pages, int) or not (1 <= total_pages <= max_pages):
        raise RuntimeError(f"Quantidade de páginas inesperada em {path}: {total_pages}")
    for page in range(1, total_pages + 1):
        obj = first if page == 1 else get_json(path, {**params, "page": page})
        if obj.get("pagination", {}).get("page") != page:
            raise RuntimeError(f"Página incorreta recebida em {path}: {page}")
        for row in obj["results"]:
            ident = row.get("id")
            if not isinstance(ident, int) or ident in seen:
                raise RuntimeError(f"ID ausente/repetido no endpoint {path}: {ident}")
            seen.add(ident)
            rows.append(row)
    if not isinstance(expected_count, int) or len(rows) != expected_count:
        raise RuntimeError(f"Coleta incompleta em {path}: {len(rows)} de {expected_count}")
    return rows

def clean(value: object) -> str:
    text = re.sub(r"<[^>]*>", " ", str(value or ""))
    return re.sub(r"\s+", " ", unescape(text)).strip()

def transform(m: dict, authors: dict[int, str], kinds: dict[int, dict]) -> dict:
    ident = m["id"]
    year = m.get("ano")
    number = m.get("numero")
    kind = kinds.get(m.get("tipo"))
    if year not in YEARS or not isinstance(ident, int) or not isinstance(number, int) or not kind:
        raise RuntimeError(f"Dados essenciais inválidos da matéria {ident}")
    author_ids = m.get("autores", [])
    if not isinstance(author_ids, list):
        raise RuntimeError(f"Autoria em formato inesperado: matéria {ident}")
    missing = [i for i in author_ids if i not in authors]
    if missing:
        raise RuntimeError(f"ID(s) de autor desconhecidos em {ident}: {missing}")
    official_authors = [authors[i] for i in author_ids]
    linked = [ELECTED_AUTHOR_IDS[i] for i in author_ids if i in ELECTED_AUTHOR_IDS]
    summary = clean(m.get("ementa"))
    day = m.get("data_apresentacao")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(day or "")):
        raise RuntimeError(f"Data inválida na matéria {ident}")
    if not summary:
        summary = "Ementa não disponibilizada na API; consulte o documento oficial."
    sigla = str(kind.get("sigla", "")).upper()
    is_indication = sigla == "IND"
    return {
        "id": f"sapl-{ident}",
        "saplId": ident,
        "tipo": clean(kind.get("descricao")),
        "sigla": sigla,
        "numero": f"{number}/{year}",
        "ano": year,
        "titulo": summary[:145] + ("…" if len(summary) > 145 else ""),
        "resumo": summary,
        "autores": linked,
        "autoresOficiais": official_authors,
        "status": "solicitado" if is_indication else "nao-verificado",
        "situacao": ("Indicação registrada no SAPL. O encaminhamento e a execução precisam de confirmação."
                     if is_indication else
                     "Matéria registrada no SAPL. Resultado legislativo e norma vinculada ainda não auditados."),
        "data": day,
        "categoria": "Atividade legislativa",
        "fonte": f"{BASE}/materia/{ident}",
        "origem": "sapl-api",
    }

def main() -> None:
    authors_raw = collect("base/autor/", max_pages=20)
    authors = {r["id"]: clean(r.get("nome")) for r in authors_raw}
    for ident, expected in EXPECTED_NAMES.items():
        if authors.get(ident) != expected:
            raise RuntimeError(f"Autor {ident} divergiu: esperado {expected!r}; recebido {authors.get(ident)!r}")
    kinds_raw = collect("materia/tipomaterialegislativa/", max_pages=10)
    kinds = {r["id"]: r for r in kinds_raw}
    collected = [m for year in YEARS for m in collect(
        "materia/materialegislativa/", {"ano": year}, max_pages=100)]
    ids = [m.get("id") for m in collected]
    if len(ids) != len(set(ids)) or len(collected) < 400:
        raise RuntimeError("Coleta possivelmente incompleta ou com IDs duplicados")
    matters = sorted((transform(m, authors, kinds) for m in collected),
                     key=lambda x: (x["data"], x["saplId"]), reverse=True)
    counts = {str(y): sum(m["ano"] == y for m in matters) for y in YEARS}
    # Só o conteúdo efetivamente modificado gera atualização/commit.
    previous = json.loads(DEST.read_text(encoding="utf-8")) if DEST.exists() else {}
    if previous.get("origem") == "sapl-api" and previous.get("materias") == matters:
        print("Sem alterações nos dados oficiais:", len(matters), "registros.")
        return
    day = datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat()
    output = {
        "origem": "sapl-api",
        "atualizadoEm": day,
        "cobertura": "Matérias de 2025 e 2026 devolvidas pela API pública do SAPL de Guariba na última coleta; tramitação, votações e sanção não auditadas automaticamente.",
        "anos": counts,
        "fonte": f"{BASE}/",
        "materias": matters,
    }
    temp = DEST.with_suffix(".tmp")
    temp.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(DEST)
    linked = sum(bool(m["autores"]) for m in matters)
    print(f"Importados {len(matters)} registros: {counts}, {linked} vinculados a pelo menos um dos 11 eleitos.")
    print("AVISO: status de aprovação e execução NÃO foram inferidos.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        sys.exit(1)
