# Guariba Transparente

[**Abrir portal de Guariba**](https://alexferreira12.github.io/guariba-tranparente/)

Portal cívico **independente**, gratuito, dedicado exclusivamente a **Guariba/SP** no lançamento. Reúne atividades legislativas e prestações de contas públicas com acesso aos documentos oficiais. Não é produto oficial da Prefeitura nem da Câmara Municipal.

## Cobertura efetiva da versão v0.4 — outubro de 2026

| Módulo | Origem | Cobertura disponível |
|---|---|---|
| Vereadores | TSE e SAPL | 11 eleitos em 2024, partidos, votos, cadastro oficial |
| Atividade legislativa | API SAPL | 571 matérias de 2025–2026 (371 + 200), 409 com autoria de pelo menos um dos 11 eleitos |
| Normas e votação | API SAPL | 132 matérias com lei vinculada, 31 com outra norma, 263 com registros de votação na primeira coleta |
| Tramitação | API SAPL | 551 matérias com histórico; mostra última movimentação e até 12 etapas recentes |
| Prestação de contas | SICONFI / DCA 2025 | 397 linhas de receita/despesa e 102 linhas patrimoniais; 16 funções orçamentárias |
| Licitações | PNCP | 507 publicações de pregões e dispensas municipais de 2025–2026, após remover registros de outras cidades |

**Atualizações:** consulta de matérias e licitações programada diariamente no GitHub Actions; DCA programada mensalmente. A periodicidade de consulta não significa disponibilidade de novos dados oficiais, nem atualização instantânea.

### O que os números significam

- **Matéria apresentada** ≠ matéria aprovada.
- **Indicação solicitada** ≠ obra/serviço executado.
- **Votação registrada** ≠ lei sancionada.
- **Norma jurídica vinculada** identifica documento oficial publicado. Não comprova implementação da política pública.
- **Valor estimado/homologado no PNCP** ≠ despesa efetivamente paga.
- **Receitas brutas, deduções, despesas empenhadas, liquidadas e pagas** são categorias contábeis diferentes; não somar saldos patrimoniais ou subtotais.
- **Participação de vereador na articulação de emenda** só será vinculada com documento que a comprove; não basta a destinação de deputado.
- Os **11 eleitos em 2024 não comprovam a composição atual em exercício** diante de licenças, suplências ou mudanças de partido.

## O que ainda falta para considerar completo

O portal é **versão de desenvolvimento**, não 100% concluída. Os principais trabalhos pendentes são:

1. **Fiscalização legislativa aprofundada:** decisões finais de projetos sem norma vinculada, vetos, votações nominais quando disponíveis, presenças e sessões.
2. **Execução orçamentária atual:** receitas e pagamentos mensais de 2026, com competência e método, separados do balanço anual DCA de 2025.
3. **Contratos e fornecedores:** valor efetivamente contratado, vigência, aditivos, pagamentos e execução documental, após confirmar fonte filtrável por Guariba.
4. **Obras e emendas:** obra, objeto, origem, repasses, medição e execução demonstrada; vereador articulador somente com prova.
5. **Qualidade e acessibilidade:** revisão editorial contínua, tratamento de divergências, ajustes móveis e monitoramento de erros/falhas de coleta.
6. **Cobertura do PNCP:** atualmente apenas modalidades 6 e 8 (pregões eletrônicos e dispensas) e publicações a partir de 2025. Não inferir que é a totalidade das licitações de Guariba.

## Tecnologia

Front-end simples em HTML, CSS e JavaScript, responsivo, publicado no GitHub Pages. Dados oficiais baixados pelos scripts Python, validados e versionados no repositório. Nenhuma chave privada de API precisa ser publicada no navegador.

O repositório contém:

- `index.html`, `assets/styles.css`, `assets/app.js`: interface pública.
- `data/vereadores.json`: eleitos de 2024 e perfis oficiais.
- `data/materias.json`: matérias, normas, votações e tramitações do SAPL.
- `data/contas-2025.json`: balanço patrimonial anual do Tesouro.
- `data/orcamento-2025.json`: receitas e despesas anuais, natureza e funções.
- `data/licitacoes.json`: pregões eletrônicos e dispensas PNCP filtrados por município.
- `scripts/`: importadores, diagnósticos e verificadores.
- `.github/workflows/`: sincronização programada, CI e testes de navegador com Chrome headless.

### Testar localmente

```bash
python3 -m http.server 8080
```

Abra `http://localhost:8080`.

### Validar

```bash
python3 scripts/validar_dados.py
python3 scripts/validar_financas.py
python3 scripts/validar_licitacoes.py
node --check assets/app.js
```

Os testes de navegação e de integração são executados em GitHub Actions. Os robôs recusam publicar resultados quando a consulta está incompleta ou os vínculos de município/autoria não podem ser confirmados, preservando a última cópia aprovada.

## Fontes oficiais

- [SAPL — Câmara Municipal de Guariba](https://sapl.guariba.sp.leg.br/)
- [Prefeitura — Transparência](https://guariba.sp.gov.br/portal-da-transparencia)
- [Tesouro Nacional / SICONFI](https://apidatalake.tesouro.gov.br/docs/siconfi/)
- [Portal Nacional de Contratações Públicas](https://pncp.gov.br/app/editais)
- [TSE — dados abertos eleitorais](https://dadosabertos.tse.jus.br/)

## Princípios editoriais

Sem monetização na fase inicial; preservamos os links oficiais e a data de coleta. Não atribuímos irregularidade sem provas, não inventamos números faltantes, não transformamos quantidade de proposições em ranking de vereadores e não atribuímos resultados ou verbas sem documento. Para corrigir erros de associação ou apresentar fonte complementar, use as **Issues** deste repositório.
