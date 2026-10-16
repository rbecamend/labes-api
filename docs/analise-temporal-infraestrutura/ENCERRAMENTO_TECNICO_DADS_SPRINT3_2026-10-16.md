# SIE — Encerramento técnico documental das DADs | Sprint 3

**Data de corte:** 16/10/2026\
**Base Git:** `equipe/feature/SIE-30-school-municipality-analysis` em `19be3efa1f7cb315c72042322cc3a7407f2c550b` (PR #12 integrada).\
**Natureza:** proposta de aceite documental com ressalvas; não é homologação de dados, indicadores ou método.

## Critério operacional e precedência

A wiki Taiga **“Decisão Operacional Provisória da Sprint 3”**, conforme os critérios informados para esta revisão, admite provisoriamente **17 indicadores candidatos**, **sem corte mínimo** de cobertura, índice sobre respostas válidas (`0` e `1`, excluindo `NULL`), **média aritmética não ponderada dos índices dos pares** por município/ano, série fixa **2022–2025** e os estados `disponivel`, `escola_sem_dados`, `sem_pares_validos` e `sem_pares_municipio`. O contrato **BE-05 v2** é a referência HTTP vigente; REQ-02 e REQ-04/Figma orientam a apresentação. A decisão operacional permite implementação e teste do MVP, mas não homologa equivalência semântica, população, território, interpretação como qualidade escolar ou publicação oficial.

**Rastreabilidade da fonte externa:** os links/exports da wiki Taiga, BE-05 v2 e REQ-02/REQ-04 não estão neste checkout e não foram abertos nesta revisão. Os critérios acima vêm do enunciado de entrega; rota, série, estados e cálculos foram confrontados com o código e os documentos versionados. Antes do aceite, a equipe deve anexar os links canônicos e conferir a redação vigente dessas fontes. Nenhum artefato restrito foi incorporado ao Git.

## Estado e evidência por DAD

| DAD | Estado em 16/10 | Evidência entregue e limite |
|---|---|---|
| [DAD-01](DAD-01_AUDITORIA_E_HOMOLOGACAO.md) | Parecer emitido; atividade **Done**; parecer **NÃO HOMOLOGADA** | Auditoria e ressalvas documentadas na [PR #7](https://github.com/rbecamend/labes-api/pull/7). Faltam decisão sobre ETL/nulos, recorte dos 22 municípios e divergências territoriais. |
| [DAD-02](DAD-02_MATRIZ_COMPARABILIDADE_TEMPORAL.md) | **Ready for Test** no último quadro | 68 verificações documentais (17 × 4) e lista candidata na [PR #7](https://github.com/rbecamend/labes-api/pull/7). Sem decisão final do conjunto S ou equivalência semântica. |
| [DAD-03A](DAD-03A_AMOSTRA_SINTETICA_E_PLANO_VALIDACAO.md) | Encerrada no escopo sintético e de planejamento | Casos e plano históricos preservados na [PR #7](https://github.com/rbecamend/labes-api/pull/7); não são homologação. |
| [DAD-03B](DAD-03B_VALIDACAO_EMPIRICA_EXPLORATORIA.md) | Encerrada no escopo empírico exploratório | Relatório histórico na [PR #7](https://github.com/rbecamend/labes-api/pull/7); pacote individual e Q1–Q4 permanecem fora do Git. |
| [DAD-04](DAD-04_CONCILIACAO_API_OFICIAL.md) | **Done** no Taiga; conciliação oficial integrada | [PR #12](https://github.com/rbecamend/labes-api/pull/12): 10 testes HTTP/ASGI controlados aprovados, 4/4 anos DAD-03B concordantes após conferência da população, hashes SHA-256 10/10. [Conciliação experimental](DAD-04_CONCILIACAO_API_REFERENCIA.md) preservada como referência histórica na PR #7. SQL/PostgreSQL real na rota oficial **não** foi validado. |
| [DAD-05](DAD-05_CONTRATO_METODOLOGICO.md) | Contrato condicional; **Ready for Test**, sem Sprint 3 atribuída no último export | Documento da [PR #7](https://github.com/rbecamend/labes-api/pull/7), com atualização factual nesta revisão. O professor aprovou expressamente apenas o princípio da média aritmética; demais regras exigem deliberação. |

## Verificações concluídas e limites

- [PR #9](https://github.com/rbecamend/labes-api/pull/9) corrigiu precisão e validação da comparação municipal; [PR #10](https://github.com/rbecamend/labes-api/pull/10) disponibilizou a integração do endpoint no backend para consumo pelo frontend e [PR #11](https://github.com/rbecamend/labes-api/pull/11) corrigiu os testes de rota. A rota, os erros HTTP, os quatro estados e a série constam também da [documentação BE-08](../BE-08-INTEGRACAO-FRONTEND.md).
- A [DAD-04 oficial](DAD-04_CONCILIACAO_API_OFICIAL.md) registra a execução dos 10 testes com pacote restrito, o confronto independente dos quatro anos e a integridade dos dez arquivos. O oráculo usa o pacote extraído no repositório controlado; **não comprova** execução da consulta SQL, identidade com banco ativo ou resultado de produção.
- Esta revisão conferiu por leitura o relatório, a presença da rota em `app/routes/infraestrutura.py` e o uso de `Fraction` antes do arredondamento público em `app/domain/infraestrutura.py`. Os testes não foram reexecutados neste worktree documental. A suíte completa informada na DAD-04 teve 143 aprovados e uma falha preexistente de Conectividade, fora deste escopo.
- Os documentos DAD-03A/B e DAD-04 experimental registram o contexto e as pendências **à época de suas execuções**. A PR #12 é a atualização transversal: a conciliação da rota oficial já ocorreu no escopo controlado indicado acima.

## Pendências objetivas para a Sprint 4

1. Professor/equipe: deliberar e registrar, com responsável, data e escopo, a comparabilidade semântica dos 17 candidatos e o conjunto S; decidir ou aceitar expressamente as limitações de ETL, nulos e território da DAD-01.
2. Professor/equipe: decidir elegibilidade e população dos pares, exclusões, `NULL`/não aplicabilidade, casos N=0/N=1, inválidos e duplicidades, tratamento territorial e apresentação de arredondamento/cobertura/avisos conforme REQ-02 e REQ-04/Figma. A aprovação da média aritmética não resolve essas escolhas.
3. Backend e Dados: se houver fonte autorizada e snapshot comprovadamente comparável, conciliar a rota oficial com o repositório SQL e PostgreSQL real contra oráculo independente; registrar ambiente, recorte, diferenças e limites sem versionar dados individuais.
4. Equipe: conferir os links e textos vigentes de Taiga, BE-05 v2, REQ-02 e REQ-04/Figma; registrar decisão de aceite documental e encaminhar pendências com responsáveis na Sprint 4.

## Proposta de aceite

Solicita-se ao professor/equipe **aceite explícito da entrega documental técnica com as ressalvas acima**, registrando quais pendências seguem para a Sprint 4. Até essa decisão, DAD-02 e DAD-05 permanecem **Ready for Test**; não há base para movê-las automaticamente a Done. O aceite documental não altera o parecer **NÃO HOMOLOGADA** da DAD-01, não homologa o conjunto S nem a DAD-05 e não autoriza interpretar o índice como qualidade escolar ou publicar indicadores oficiais.
