# SIE — DAD-04 | Plano operacional de conciliação API × DAD-03

**Estado de partida (histórico):** DAD-03B tecnicamente validada segundo execução e verificações reportadas; naquele momento, DAD-04 estava **EM EXECUÇÃO**, ainda sem resposta real da API confrontada. Este plano não homologa indicadores nem modifica a metodologia.

**Leitura atual:** “EM EXECUÇÃO” descreve a data deste plano. O relatório [DAD-04 — Conciliação](DAD-04_CONCILIACAO_API_REFERENCIA.md) registra a conclusão exploratória posterior com a rota experimental `/infraestrutura/analise-temporal/escola-municipio`. Essa rota e a PR #44 não integram o contrato vigente. A conciliação da rota oficial `GET /infraestrutura/analise-temporal/escolas/{co_entidade}/comparacao-municipio` deverá ser repetida após BE-07/BE-08; os passos abaixo são protocolo histórico sob cobertura experimental 17/17.

## 1. Objetivo e decisão inicial

Confrontar um endpoint **real** do backend FastAPI com os casos sintéticos DAD-03A e a amostra exploratória DAD-03B, usando a resposta HTTP efetiva (ASGI/HTTPX ou Uvicorn) — não chamar somente a função de cálculo como substituto da DAD-04. O backend local (branch `develop`) já possui `GET /infraestrutura/analise-temporal`, porém não está demonstrado que implemente a comparação **Escola × média das demais escolas do município**. Verificar primeiro código, serviço, repositório, schemas, documentação OpenAPI e comportamento; não inferir equivalência pelo nome.

Se a rota já satisfizer integralmente o contrato, realizar testes e registrar evidências. Se não satisfizer, implementar **apenas em ambiente local e de forma experimental** uma rota/serviço separado para o caso Escola × Município, preservando endpoints existentes e respeitando a arquitetura FastAPI. Evitar publicar como resultado oficial. A DAD-04 só é concluída quando uma resposta real da API for confrontada.

## 2. Fontes e restrições

1. `docs/analise-temporal-infraestrutura/DAD-03B_VALIDACAO_EMPIRICA_EXPLORATORIA.md` — documento local presente nesta pasta; os artefatos brutos da validação não acompanham a PR.
2. `docs/analise-temporal-infraestrutura/DAD-03A_AMOSTRA_SINTETICA_E_PLANO_VALIDACAO.md` — cenários T01–T15.
3. `docs/analise-temporal-infraestrutura/DAD-05_CONTRATO_METODOLOGICO.md` — fórmulas, elegibilidade e indisponibilidade **condicionais**.
4. `docs/analise-temporal-infraestrutura/DAD-01_AUDITORIA_E_HOMOLOGACAO.md` e DAD-02 — limitações de origem, território e comparabilidade.
5. `DAD04_ORACULO_EXPLORATORIO.json` — oráculo histórico referido no plano, ausente deste checkout e excluído da PR; não substitui os vetores brutos de Q2.
6. Evidências DAD-03B reportadas historicamente fora do Git, em pasta temporária cujo identificador foi omitido da versão publicável; localização permanente não confirmada neste checkout. Não incorporar dados brutos ao Git.

**Bloqueios permanentes para publicação:** DAD-01 não homologada; DAD-02 preliminar; S de 17 indicadores candidatos não homologado; DAD-05 condicional. Conclusão técnica exploratória da DAD-04 não equivale a homologação semântica.

## 3. Fluxo de execução sem retrabalho

**DAD-04.1 — Descoberta (obrigatória, curta).** Inspecionar `git status`, o estado da branch, o `main.py`, a rota `/infraestrutura/analise-temporal`, seus schemas/serviços/queries e os testes. Classificar: `atende`, `atende_parcialmente` ou `não_atende` ao caso Escola × Município, com caminhos/linhas. Comparar campos e semântica com DAD-05; identificar `COALESCE(...,0)` e outras transformações arriscadas sem alterar as rotas existentes.

**DAD-04.2 — Contrato e oráculo.** Congelar a versão experimental de S (17 candidatos), o recorte 2022–2025, cobertura completa provisória, contagens de `sim`, `não`, `NULL`, índice do selecionado, referência municipal **não ponderada** (escola excluída), `N_ref`, `difference_pp`, status e motivo. A resposta deve permitir identificar município por ano, versão condicional, parâmetros e população. Não arredondar antes de comparar ou de subtrair.

**DAD-04.3 — Endpoint, se necessário.** Desenvolver implementação **mínima, local e isolada**, sem modificar endpoints públicos existentes. Dar preferência ao padrão da arquitetura FastAPI do repositório. Nenhum `NULL` pode virar 0. Não juntar `gold.dim_entidade` como dimensão histórica automaticamente; território deriva da observação anual, com alertas em mudanças/discordâncias. Duplicidades e inválidos bloqueiam resultados afetados, não são silenciosamente excluídos. `N_ref=0` → referência/diferença `null`; `N_ref=1` matematicamente definido (aviso provisório); escola sem dado → `null` distinto de 0; não interpolar séries. Para casos inválidos, não publicar `N` artificialmente definitivo.

**DAD-04.4 — Testes automatizados.** Cobrir T01–T15 (incluindo T13A/T13B e T14 de ambos os anos); os casos sintéticos permanecem identificados como sintéticos. Usar fixtures isoladas e integração por cliente HTTP real (por exemplo `httpx.ASGITransport`) e não somente testes unitários de serviço. Checar campos presentes, tipo, nulos, erros, as mesmas fórmulas exatas e exclusões; registrar provas de execução. Se alguma regra ainda for proposta, mantê-la declarada como perfil experimental, sem alegar homologação.

**DAD-04.5 — Conciliação real (protocolo histórico).** A integração experimental contra o PostgreSQL local foi prevista para execução manual pelo usuário em PowerShell, fora do sandbox do Codex, com o backend local e sem expor `.env` ou credenciais. O plano usava identificadores de escola e município mantidos somente na evidência histórica restrita, omitidos da PR documental. Previa demonstrar a compatibilidade do recorte da API com a DAD-03B, ou classificar `não comparável — snapshot/recorte`; comparar os valores exatos do oráculo e, com Q2 bruto local, as 17 respostas, denominadores e inclusão/exclusão de cada escola; e registrar request, response higienizado, diferenças, hashes e condições de execução. O relatório DAD-04 registra o que foi efetivamente reportado. A repetição na rota oficial BE-05 permanece pendente.

**DAD-04.6 — Fechamento.** Produzir `docs/analise-temporal-infraestrutura/DAD-04_CONCILIACAO_API_REFERENCIA.md` com contrato efetivo, evidência de API/HTTP, tabela de testes, divergências identificadas/corrigidas/pendentes, limitações e decisão técnica. Aprovar **VALIDAÇÃO TÉCNICA EXPLORATÓRIA** somente se casos obrigatórios passaram, endpoint real foi exercitado, houve comparação exata com a amostra e divergências foram resolvidas ou impeditivos explicitamente marcados. Manter homologação/publicação pendentes.

## 4. Critérios de aceite e bloqueios

- Município e escola corretos por ano, sem trocar código pelo nome ou inferir continuidade territorial.
- Mesmo conjunto fixo de 17 candidatos durante o teste (não versão homologada).
- Respostas 0, 1 e `NULL` preservadas; contagens de `sim`, `não`, `n_valid_indicators`, cobertura e índice corretas.
- Escola selecionada excluída; média simples dos índices individuais elegíveis; `N_ref` correto, não contagem de todas as escolas.
- Diferenças em pp e sem arredondamento intermediário.
- Estados distintos para não observado, all-NULL, parcial, sem comparadoras, N=1, inválido, duplicado e território pendente.
- Todos os cenários DAD-03A comparados **via API** e amostra real DAD-03B conciliada no mesmo recorte.
- Evidências e logs sem segredos, hashes e identificação da execução; nenhuma escrita no PostgreSQL.
- Não expor a funcionalidade como indicador oficial; evitar commits/push e alterações no frontend até revisão.

## 5. Oráculo exploratório de acesso controlado

O plano histórico usou um oráculo com quatro resultados anuais para a escola selecionada, incluindo contagem de indicadores válidos, comparadoras, média municipal e diferença. A tabela e o índice individual foram retirados da versão publicável porque permitem caracterizar a escola mesmo sem seus identificadores. Os valores históricos não foram alterados. O oráculo e a amostra bruta devem permanecer em armazenamento de acesso controlado; sua localização e disponibilidade ainda precisam ser confirmadas pela equipe. A identidade do alvo e a comparabilidade dos snapshots dependem dessas evidências.
