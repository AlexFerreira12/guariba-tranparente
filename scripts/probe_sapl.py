#!/usr/bin/env python3
"""Prova técnica da API pública do SAPL.

Não modifica a base editorial, pois schemas, resultados de votação e
vínculos de autoria precisam ser auditados antes de publicar status.
"""
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
import sys

URLS = [
    'https://sapl.guariba.sp.leg.br/api/materia/materialegislativa/?page=1',
    'https://sapl.guariba.sp.leg.br/api/parlamentares/parlamentar/?page=1',
]

def run():
    success = 0
    for url in URLS:
        print('Testando', url)
        try:
            with urlopen(Request(url, headers={'User-Agent':'GuaribaTransparente/0.1 (+pesquisa de dados publicos)','Accept':'application/json'}), timeout=18) as response:
                raw = response.read(500_000)
                content_type = response.headers.get('Content-Type', '')
                print('HTTP', response.status, 'Content-Type:', content_type, 'Bytes:', len(raw))
                if 'json' not in content_type:
                    print('Resposta não identificada como JSON; endpoint não validado.')
                    continue
                data = json.loads(raw)
                if isinstance(data, dict):
                    print('Campos:', ', '.join(sorted(data.keys())[:20]))
                    rows = data.get('results') or []
                elif isinstance(data, list):
                    rows = data
                else:
                    rows = []
                if rows and isinstance(rows[0], dict):
                    print('Campos do primeiro registro:', ', '.join(sorted(rows[0].keys())[:30]))
                success += 1
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
            print('Falhou:', str(exc))
    print(f'Endpoints JSON acessíveis: {success}/{len(URLS)}')
    return 0 if success == len(URLS) else 1

if __name__ == '__main__':
    sys.exit(run())
