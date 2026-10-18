# Guariba Transparente

Portal cívico **independente**, gratuito e dedicado **exclusivamente à cidade de Guariba/SP** nesta primeira etapa. Organiza dados oficiais sobre os vereadores e prepara os módulos de contas públicas, obras e emendas.

**Portal de testes:** https://alexferreira12.github.io/guariba-tranparente/

## Estado atual — MVP legislativo v0.2

- Interface responsiva para celular e computador.
- Perfis dos **11 eleitos em 2024** com links para as páginas oficiais do SAPL.
- **571 matérias legislativas** (371 de 2025, 200 de 2026) na primeira coleta de 17/10/2026.
- Dessas, **409 matérias** estão vinculadas a pelo menos um dos 11 eleitos, conforme os IDs oficiais de autoria da API. Matérias conjuntas podem aparecer em mais de um perfil.
- Pesquisa por tipo, assunto, ano e situação, com paginação na listagem principal.
- Atualização automatizada por GitHub Actions, diariamente ou por execução manual.
- Links para consulta das bases de contas públicas. **Valores financeiros ainda não foram importados.**

### Limites e compromisso editorial

**A importação é factual, não uma auditoria de resultados.** O SAPL fornece registros, ementas, autorias, tipos e datas. A situação **“Solicitado”** aparece nas indicações; **“A verificar”** significa que ainda não conferimos votação, sanção, veto e norma vinculada.

**Não** deduzimos que uma matéria virou lei apenas porque foi arquivada ou porque `em_tramitacao` é falso. Da mesma forma, não presumimos execução de obras, pagamentos ou emendas sem documento de comprovação.

Os registros com autoria da Prefeitura, comissões ou outros agentes também integram a base pública; **não** são atribuídos indevidamente aos 11 perfis. A lista dos eleitos em 2024 não substitui a composição atual em exercício, que pode variar por licenças ou suplência.

Este site **não é um portal oficial**, nem contém rankings ou pontuações de vereadores.

## Como executar localmente

Requer Python 3 e navegador moderno. O frontend é HTML, CSS e JavaScript sem dependências de produção.

```bash
python3 -m http.server 8080
```

Abra `http://localhost:8080`. Não abra diretamente via `file://`, pois o navegador precisa buscar os arquivos JSON.

## Organização

- `index.html` e `assets/`: interface.
- `data/vereadores.json`: perfis de eleitos de 2024 e IDs oficiais.
- `data/materias.json`: registros obtidos automaticamente do SAPL.
- `scripts/importar_sapl.py`: importação paginada e associação conservadora de autoria.
- `scripts/validar_dados.py`: integridade dos dados e checagem de fontes.
- `scripts/probe_sapl.py`: diagnóstico técnico de endpoints.
- `.github/workflows/atualizar-sapl.yml`: sincronização diária e publicação no repositório, com validação antes do commit.
- `.github/workflows/validar.yml`: testes automáticos em cada atualização do código.

Para executar a importação:

```bash
python3 scripts/importar_sapl.py
python3 scripts/validar_dados.py
node --check assets/app.js
```

A rotina de importação **interrompe o processo** se houver erro de conexão, inconsistência da paginação, duplicação de IDs, mudança no cadastro dos autores ou formato inesperado. A última versão previamente validada permanece disponível no site se houver falha na coleta. O GitHub registra o histórico das alterações.

**Não edite manualmente `data/materias.json` para atribuir situação legislativa**, porque a próxima sincronização automática substitui o arquivo. A próxima fase implementará uma base separada de decisões confirmadas, sem misturar registros automáticos e revisão documental.

## Fontes

- [SAPL — Câmara de Guariba](https://sapl.guariba.sp.leg.br/)
- [Portal da Transparência — Prefeitura](https://www.guariba.sp.gov.br/portal-da-transparencia)
- [Portal do Tribunal de Contas do Estado de SP](https://www.transparencia.tce.sp.gov.br/conjunto-de-dados)
- [TSE — dados eleitorais](https://dadosabertos.tse.jus.br/)

## Próximos passos

1. Ligar tramitações, votações e normas jurídicas aos registros e verificar seus resultados.
2. Conferir situação de indicações, requerimentos, autores coletivos e substituições de mandato.
3. Importar receitas, despesas, contratos, obras e emendas sem misturar valores empenhados, liquidados e pagos.
4. Testar acessibilidade, desempenho e confiabilidade editorial antes de divulgação pública ampla.

**Sem monetização na fase atual.**
