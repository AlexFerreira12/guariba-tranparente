# Guariba Transparente

Portal cívico independente de Guariba/SP que facilita o acesso a dados oficiais sobre vereadores, proposições legislativas e contas públicas.

> **Versão 0.1 (MVP):** interface navegável e responsiva, 11 perfis dos vereadores eleitos em 2024 e uma **amostra de matérias legislativas com fontes oficiais**. As bases de contas públicas e emendas ainda não estão integradas. Nenhum valor financeiro é simulado como real.

## Como executar

Não há dependências externas para rodar o site.

```bash
python3 -m http.server 8080
```

Abra `http://localhost:8080`. Não use `file://`, porque o navegador bloqueia `fetch` dos arquivos JSON locais.

## Páginas

- **Início:** apresentação e panorama dos registros disponíveis na amostra.
- **Vereadores:** perfis dos 11 eleitos em 2024, pesquisa e filtro por partido.
- **Atividade legislativa:** projetos e indicações com filtro por ano, tipo e status; registros com fonte oficial.
- **Contas públicas:** links verificados para consulta nos portais municipais (importação financeira pendente).
- **Obras e emendas:** fontes de dados públicos e status de integração.
- **Fontes e método:** origem e limites das informações.

## Integridade e transparência

1. Dados em `data/vereadores.json` e `data/materias.json` são uma amostra inicial editada a partir de fontes públicas oficiais.
2. Uma matéria aprovada pela Câmara não será classificada como lei sem comprovação da norma vinculada.
3. Uma indicação não comprova a execução de uma obra ou serviço.
4. Um repasse não comprova a execução de um gasto ou conclusão da obra.
5. A ausência de matéria no site não significa ausência de atuação parlamentar.
6. O projeto não tem ligação institucional com a Câmara ou Prefeitura de Guariba.
7. Para novas matérias, atualizar o JSON com a fonte, o autor, a situação e a data após conferência.

## Atualização automática — próximo passo

O SAPL possui interface pública de consulta. **Ainda não confirmamos que sua API permite a coleta esperada**, então não afirmamos que a sincronização automática esteja funcionando.

Para testar os endpoints antes de programar uma importação:

```bash
python3 scripts/probe_sapl.py
```

No GitHub, também há o fluxo manual em **Actions > Testar API SAPL (manual)**. Ele apenas diagnostica a disponibilidade e os campos básicos retornados. Não muda a base editorial. Se o teste validar acesso, o passo seguinte será um importador paginado de matérias, autores, tramitações e normas com critérios de verificação, deduplicação, trilha de auditoria e alerta de falhas.

## Publicar no GitHub Pages

1. O repositório está em `AlexFerreira12/guariba-tranparente`.
2. O conteúdo foi enviado à branch `main`.
3. Em **Settings > Pages**, escolha **Deploy from a branch**, branch `main` e pasta `/ (root)`.
4. Aguarde a confirmação do próprio GitHub Pages e use a URL exibida na configuração de Pages.

O site pode ser publicado sem custo de hospedagem em um repositório público. GitHub Pages é hospedagem de conteúdo estático; não fornece sozinho um banco de dados privado ou consultas seguras a serviços que exijam segredos de API.

## Testes

```bash
node --check assets/app.js
python3 scripts/validar_dados.py
```

## Próximas entregas técnicas

- Testar contratos e disponibilidade real da API SAPL de Guariba.
- Implementar importação completa de parlamentares, autoria, matérias, tramitações, normas e votações.
- Tratar substituições de mandato e autores conjuntos.
- Conectar receitas e despesas oficiais com definição clara de empenhado, liquidado e pago.
- Importar contratos, obras e emendas com links e trilha de fontes.
- Acrescentar governança editorial, rotina de revisão, log e monitoramento de erros.
- Avaliar backend quando as fontes exigirem tratamento de PDFs, autenticação ou grande volume de dados.

## Aviso

Dados públicos e explicações informativas. Não é um órgão oficial nem substitui as bases originais.