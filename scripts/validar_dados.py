#!/usr/bin/env python3
"""Validação conservadora dos dados exibidos no Guariba Transparente."""
from datetime import date
from pathlib import Path
import json
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    with (ROOT / 'data' / name).open(encoding='utf-8') as f:
        return json.load(f)

def valid_source(url):
    u = urlsplit(url)
    return u.scheme == 'https' and u.hostname is not None and (
        u.hostname == 'sapl.guariba.sp.leg.br'
        or u.hostname == 'www.guariba.sp.leg.br'
        or u.hostname == 'www.guariba.sp.gov.br'
        or u.hostname == 'dadosabertos.tse.jus.br'
    )

def run():
    people = read('vereadores.json')['vereadores']
    matters = read('materias.json')['materias']
    assert len(people) == 11, 'A lista inicial deve ter 11 eleitos em 2024'
    ids = [p['id'] for p in people]
    assert len(ids) == len(set(ids)), 'IDs de vereadores duplicados'
    numbers = set()
    for p in people:
        assert p['nome'] and p['partido'] and p['votos2024'] >= 0
    for m in matters:
        assert m['id'] not in numbers, f'Matéria duplicada: {m["id"]}'
        numbers.add(m['id'])
        assert m['tipo'] and m['numero'] and m['titulo'] and m['resumo']
        assert m['status'] in {'virou-lei','aprovado-camara','solicitado','nao-verificado'}
        assert m['autores'] and all(a in ids for a in m['autores'])
        assert valid_source(m['fonte']), f'Fonte inesperada: {m["id"]}'
        assert date.fromisoformat(m['data']) <= date.today(), f'Data futura: {m["id"]}'
        assert m['situacao'], f'Situação não explicada: {m["id"]}'
    print(f'OK: {len(people)} vereadores, {len(matters)} matérias, IDs e URLs válidos.')

if __name__ == '__main__':
    try:
        run()
    except (AssertionError, ValueError, KeyError, FileNotFoundError) as exc:
        print(f'ERRO: {exc}', file=sys.stderr)
        sys.exit(1)
