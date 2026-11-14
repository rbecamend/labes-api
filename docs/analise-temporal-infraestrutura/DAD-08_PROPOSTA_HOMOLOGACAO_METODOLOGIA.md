# SIE — DAD08 | Proposta de homologação da metodologia dos indicadores

**Atividade:** [DAD08 — tarefa #70, Sprint 5](https://tree.taiga.io/project/rebecamendonca-sie-v2/t/70).
**Finalidade:** subsidiar a decisão metodológica antes da integração final da [BE13 (#71)](https://tree.taiga.io/project/rebecamendonca-sie-v2/t/71) e da [BE15 (#72)](https://tree.taiga.io/project/rebecamendonca-sie-v2/t/72).
**Estado:** **PROPOSTA PARA REVISÃO — NÃO HOMOLOGADA**. Não houve parecer ou assinatura dos responsáveis nesta análise.
**Data da análise documental:** 13–14/11/2026; conferência local deste pacote em 13/11/2026, horário de Fortaleza.
**Natureza da entrega:** documentação e oráculos aritméticos sintéticos. Nenhuma modificação do backend/frontend, banco de dados, contrato HTTP, PR ou branch remota nesta etapa.
**Branch de integração de referência:** `feature/SIE-72-sprint5-temporal-infrastructure`.
**Referências de implementação examinadas:** [BE15 `63ce24c`](https://github.com/rbecamend/labes-api/commit/63ce24cb527fda69967b7db325b6dec478fb3f6a); [BE13 PR #21](https://github.com/rbecamend/labes-api/pull/21), head consultado `0c2a80d575070307968246c87afff9bb551ca90a`.

> **Aviso de escopo:** a DAD08 trata das **duas visões simplificadas** da REQ07: Escola × Município (duas linhas) e visão municipal (uma linha no conceito funcional informado). **Não** implementa a comparação múltipla da REQ06/DAD07, diferida para backlog futuro. A DAD08 não deve confundir a curva municipal agregada com a média dos índices escolares.

## 1. Objetivo, perguntas e autoridade da decisão

O critério de aceite da tarefa exige: (a) validar fórmula municipal e efeito da dependência administrativa/rede; (b) definir `NULL`, denominadores zero e amostras `N=0` e `N=1`; (c) apresentar pelo menos três exemplos calculados manualmente; (d) confirmar que a exclusão da escola selecionada ocorre **somente** na visão de referência Escola × Município.

Este documento apresenta **cálculos tecnicamente verificáveis** e uma **proposta explícita de decisão**. As aprovações institucionais e decisões sobre integridade, semântica dos 17 indicadores, redes elegíveis e política de aviso/supressão devem ser registradas pelas equipes responsáveis. A homologação aqui solicitada **não** decorre automaticamente do merge das DADs anteriores ou da existência de implementação na BE13/BE15.

| Fonte | O que fundamenta | Limitação atual |
|---|---|---|
| [DAD01](https://github.com/rbecamend/labes-api/blob/feature/SIE-54-sprint4-infrastructure-composition/docs/analise-temporal-infraestrutura/DAD-01_AUDITORIA_E_HOMOLOGACAO.md) | 2022–2025; inventário e auditoria do recorte, integridade territorial | Parecer anterior **NÃO HOMOLOGADA**; ETL/snapshot sem linhagem integral |
| [DAD02](https://github.com/rbecamend/labes-api/blob/feature/SIE-54-sprint4-infrastructure-composition/docs/analise-temporal-infraestrutura/DAD-02_MATRIZ_COMPARABILIDADE_TEMPORAL.md) | 17 indicadores candidatos e comparabilidade documental anual | Semântica/aplicabilidade do conjunto ainda sujeita a aprovação |
| [DAD05](https://github.com/rbecamend/labes-api/blob/feature/SIE-72-sprint5-temporal-infrastructure/docs/analise-temporal-infraestrutura/DAD-05_CONTRATO_METODOLOGICO.md) | Índice escolar, média aritmética de escolas elegíveis, exclusão do alvo, `N=0/1` | Política de integridade e aviso para comparadora única pendentes |
| [DAD06 complementar — PR #16, mesclada na Sprint 4](https://github.com/rbecamend/labes-api/pull/16) | Recontagem Porto de Moz 2025, Q8B e casos sintéticos | Recontagem real limitada a um agregado, sem exclusão individual; snapshot histórico não identificado |
| [DAD07 — PR #17, mesclada na Sprint 4](https://github.com/rbecamend/labes-api/pull/17) | Histórico da REQ06 V2 e encaminhamento para REQ07 | Comparação múltipla diferida; não é contrato da Sprint 5 |
| [REQ07 (#69)](https://tree.taiga.io/project/rebecamendonca-sie-v2/t/69) | Recorte funcional simplificado, conforme informações da equipe | Texto completo do card e definição visual de “uma linha” não foram obtidos diretamente nesta revisão; URL fornecida pelo pacote, sem confirmação independente do conteúdo do card |
| [BE13 PR #21](https://github.com/rbecamend/labes-api/pull/21) | Código em desenvolvimento: seleção de anos e filtro de redes apenas para pares | PR aberta quando consultada; não executada nesta análise |
| [BE15 commit 63ce24c](https://github.com/rbecamend/labes-api/commit/63ce24cb527fda69967b7db325b6dec478fb3f6a) | Série municipal por indicador, contagens distintas, presença e cobertura | 120 testes **reportados pela equipe**, não reexecutados aqui; riscos estáticos de integridade |

## 2. Unidade, população e domínio dos dados

**Unidade de observação pretendida:** par `(CO_ENTIDADE, NU_ANO_CENSO)` dentro do município histórico `(CO_MUNICIPIO, NU_ANO_CENSO)`. A interpretação pressupõe identificação escolar não nula, unicidade verificada e valores íntegros para cada indicador. Não aceitar duas linhas conflitantes do mesmo par como uma escola normalizada sem diagnóstico.

**Conjunto candidato:** os 17 indicadores especificados em DAD02 e no catálogo de infraestrutura da aplicação. A BE15 usa esse conjunto por padrão quando `indicadores` é omitido; se uma lista é informada, os resultados são **por indicador escolhido**. A seleção definitiva e a equivalência semântica nos quatro anos dependem de aprovação.

Para cada indicador binário: `1` = recurso presente; `0` = recurso ausente (resposta válida); `NULL` = informação ausente e **não** ausência do recurso; outros valores = **inválidos**, não automaticamente `NULL`. Falta de linha escola/ano é diferente de linha com os 17 indicadores `NULL`. Em todos os percentuais, manter contagens inteiras, calcular antes de arredondar e apresentar duas casas decimais na saída.

**Filtro `rede_ensino`:** valores admitidos nos endpoints: `Federal`, `Estadual`, `Municipal`, `Privada`, associados à dimensão `gold.dim_tp_dependencia` por `TP_DEPENDENCIA`; o filtro atua na população anual. Múltiplas redes significam união dos tipos selecionados, não cálculo de média entre redes. Ausência de filtro (incluindo `[]` no código consultado) seleciona todas as redes, sujeito à política de integridade cadastral.

## 3. Fórmulas e semânticas distintas

Seja `j` uma escola, `y` um ano e `i` um indicador. Seja `S` o conjunto de indicadores candidatos.

### 3.1 Índice da escola (BE13)

`n(j,y) = quantidade de indicadores de S com resposta 0 ou 1` e `p(j,y) = quantidade desses indicadores com resposta 1`.

**Índice escolar**: `I(j,y) = 100 × p(j,y) / n(j,y)`, se `n>0` e os controles de integridade permitirem; `I=NULL` se `n=0`. O denominador **não é necessariamente 17**, pois `NULL` não é convertido em zero. Cobertura dos indicadores escolares: `100 × n/17` no conjunto de 17. O alerta funcional de `<60%` é **informativo e restrito à escola**; não exclui índice calculável nem classifica uma cobertura municipal.

### 3.2 Referência municipal da escola selecionada (BE13)

Para escola selecionada `e`, município histórico `m(e,y)` e filtro de redes `r`, defina `P(e,y,r)` como **todas as outras escolas** no mesmo município e ano e nas redes incluídas, **antes de excluir escolas sem índice calculável**. O alvo é excluído explicitamente por `CO_ENTIDADE != e` mesmo quando sua rede seria permitida. `T_pares = |P|`; `P_val = {j em P: I(j,y) calculável}`; `N_pares = |P_val|`.

- **Média de referência**: `R(e,y,r) = soma(I(j,y) para j em P_val) / N_pares`, quando `N_pares>0`; senão `NULL`.
- **Cobertura dos pares**: `100 × N_pares / T_pares` quando `T_pares>0`; senão `NULL`.
- **Diferença**: `Delta(e,y,r) = I(e,y) - R(e,y,r)` em pontos percentuais, se ambos existirem; senão `NULL`.

Cada comparadora válida tem peso igual. **Não** é a proporção de todos os indicadores com `1` acumulados entre escolas. A escola selecionada permanece como **alvo** mesmo se sua rede for diferente da selecionada para as comparadoras. O município usado é o da linha histórica do **respectivo ano**, nunca o município mais recente retroativamente.

### 3.3 Visão territorial municipal (BE15)

Para município `m`, ano `y`, redes `r` e indicador `i`, seja `U(m,y,r)` o conjunto de escolas **distintas** e elegíveis do recorte, sem exclusão de escola-alvo: `T=|U|`. Conte `a1_i` escolas com resposta `1`, `a0_i` com resposta `0`, `V_i=a1_i+a0_i`, `aNULL_i` sem resposta. Em dados íntegros e únicos: `T=V_i+aNULL_i`.

- **Presença percentual do indicador**: `100 × a1_i / V_i` se `V_i>0`; senão `NULL`.
- **Cobertura percentual do indicador**: `100 × V_i / T` se `T>0`; senão `NULL`.
- **Quantidade de escolas do ano:** `T`. Quando `T=0`, devolver `T=0`, contagens zero e **ambos os percentuais `NULL`**.

A BE15 **não calcula, nesse endpoint, a média dos índices individuais das escolas**. Seus resultados são agregados **por indicador**, com dois percentuais semanticamente distintos. Embora a REQ07 mencione uma linha territorial, é necessária confirmação de qual medida/indicador alimenta essa linha no frontend; **não** inventar índice composto global dos 17 indicadores.

### 3.4 Precisão e estados

Usar frações exatas nos exemplos e arredondar resultados públicos somente ao final, a duas casas. Na BE15, o serviço usa arredondamento a duas casas; o schema valida os percentuais contra as contagens. Diferença escola-referência deve ser calculada **sem arredondar índices intermediários**, para evitar discrepâncias de centésimos.

## 4. Estados de ausência, N=0, N=1 e integridade

| Condição | Resultado matemático | Situação de decisão |
|---|---|---|
| Escola com `n=0` (17 `NULL`) | Índice escolar `NULL`; cobertura escolar 0% | Preservar como sem informação, não como recurso ausente |
| BE13 `T_pares=0` | Cobertura dos pares `NULL`; `N_pares=0`; referência e diferença `NULL` | Exibir motivo “sem comparadoras”, sem inventar 0% |
| BE13 `T_pares>0`, `N_pares=0` | Cobertura dos pares 0%; referência e diferença `NULL` | Diferenciar “nenhuma comparadora” de “comparadoras sem índice” |
| BE13 `N_pares=1` | Média igual ao índice da única comparadora; diferença pode ser calculada | **Aviso/supressão pública pendentes**: DAD05 propõe aviso, ainda sem homologação |
| BE15 `T=0` | Presença `NULL`, cobertura `NULL` por indicador | Retornar ano e `quantidade_escolas=0` conforme implementação consultada |
| BE15 `T>0`, `V_i=0` | Presença `NULL`, cobertura 0% | Não converter “ninguém respondeu” em “ninguém tem o recurso” |
| Valores fora de `0/1/NULL` | **Inválido**, distinto de `NULL` | Necessária regra formal de bloqueio/sinalização |
| Duplicidade contraditória escola/ano | Não há índice/agregado confiável sem resolução | Necessária política de unicidade, conciliação e diagnóstico |
| Código de rede não mapeado | População indeterminada para filtro de rede | Registrar perdas por junção e definir política com Dados/Backend |

**Nota sobre 60%:** com 17 indicadores escolares fixos, cobertura igual a 60% exatamente exigiria 10,2 indicadores válidos, impossível. O teste genérico com 3 de 5 valida a fronteira matemática, mas não é dado real da escola. O limite não deve migrar automaticamente para BE15.

## 5. Exemplos manuais — evidência anexa

Os três exemplos foram construídos e recalculados independentemente, com frações exatas, no documento [EVIDENCIAS_DAD08_EXEMPLOS_MANUAIS.md](evidencias/dad08/EVIDENCIAS_DAD08_EXEMPLOS_MANUAIS.md). Os dados são **fictícios** e **não** resultam de consultas PostgreSQL, testes de API ou carga oficial. O [script de verificação](evidencias/dad08/verificar_exemplos_dad08.py) foi reexecutado com Python 3.12.10 fora da `.venv`, em pasta temporária: **35/35 verificações aritméticas aprovadas**. O JSON gerado reproduziu [o resultado registrado](evidencias/dad08/RESULTADOS_VERIFICACAO_SINTETICA_DAD08.json) byte a byte (`SHA-256: 4d4f4668e148701af94280128e6a2761f4c11be4f7049c6b20637ebc53613499`). **Dezessete frações/resultados centrais** e a fronteira de 60% também foram recalculados independentemente nesta revisão.

- **E1 — BE15:** cinco escolas (redes Municipal/Estadual), um indicador com `1/0/NULL`. Todas as redes: presença **66,67%**, cobertura **60,00%**; só Municipal: **50,00%** e **66,67%**; só Estadual: **100,00%** e **50,00%**.
- **E2 — BE13:** alvo Estadual com `12/17=70,59%`, comparadoras Municipal/Estadual, incluindo uma totalmente `NULL`. Sem filtro: referência **66,67%**, diferença **+3,92 pp**, cobertura de pares **75,00%**. Com filtro Municipal: referência **80,00%**, diferença **−9,41 pp**, cobertura de pares **66,67%**; alvo Estadual permanece exibível.
- **E3 — casos-limite:** `T=0,N=0`, `T>0,N=0`, `N=1`, indicador `V=0,T>0` e escola com 17 `NULL`; preservar a diferença entre `NULL` e 0%.

## 6. Verificação estática de BE13 e BE15

| Questão | Código/indício examinado | Parecer |
|---|---|---|
| BE13: filtro aplicado só às comparadoras | `find_pares_municipais`: `CO_ENTIDADE != alvo`, município histórico/ano e JOIN em `dim_tp_dependencia` quando `rede_ensino` | **Compatível**, sob unicidade e dimensão correta |
| BE13: alvo não filtrado por rede | `find_historico_escola` busca escola por código independentemente do filtro de pares | **Compatível** |
| BE13: média de índices e `N=0/1` | domínio e DAD05; sem corte de cobertura mínima no MVP | **Compatível matematicamente**; aviso de `N=1` depende de decisão |
| BE13: anos disponíveis | Consulta anos globalmente observados na Silver dentro do recorte; pontos sem escola preservados quando o ano existe | **Implementado**; confirmar expectativa de UX/REQ07 |
| BE13: mínimo de anos | Serviço/schema/rota exigem `ano_fim - ano_inicio >= 2` | **Pendência semântica:** isso admite mínimo de **3 anos civis inclusivos**, enquanto “mínimo de 2 anos” pode significar dois anos consecutivos; formalizar interpretação |
| BE15: fórmula por indicador | SQL `COUNT(DISTINCT CASE WHEN indicador=1 THEN CO_ENTIDADE END)` e `COUNT(DISTINCT CASE WHEN indicador IN (0,1) THEN CO_ENTIDADE END)`; `T=COUNT(DISTINCT CO_ENTIDADE)` | **Compatível em base íntegra** com exemplos E1/E3 |
| BE15: aplicação da rede | JOIN `silver.infraestrutura_comum.TP_DEPENDENCIA = gold.dim_tp_dependencia.co_tp_dependencia`, filtro em `no_tp_dependencia` | **Compatível** sob correspondência cadastral/sem duplicação da dimensão |
| BE15: sem exclusão de alvo | Consulta municipal não recebe `co_entidade_excluida` e não usa filtro `CO_ENTIDADE != alvo` | **Confirmado por leitura do código** |
| BE15: 17 indicadores | Serviço usa catálogo de 17 como padrão quando filtro omitido; contrato aceita seleção de subconjunto | **Compatível** com BE15, sem definição de índice municipal único |
| BE15: duplicidades conflitantes | `COUNT(DISTINCT ...)` por condição pode aceitar a mesma escola com valores `0` e `1` sem diagnóstico | **Risco material**, sem ocorrência empírica comprovada; exigir política/teste |
| BE15: valores inválidos | `quantidade_sem_dados = T - V` agrupa qualquer valor fora de 0/1 na classe “sem dados” | **Risco material**, sem ocorrência empírica comprovada; requer diagnóstico separado |
| BE15: código escolar nulo | Filtro `CO_ENTIDADE IS NOT NULL` exclui linhas sem código | Definir contagem de exclusões diagnósticas antes de homologar |
| BE15: rede desconhecida | JOIN interno com dimensão ao filtrar pode suprimir códigos não mapeados | Definir diagnóstico de correspondência de rede |

**Fontes dos achados:** [repositório BE13 na PR #21](https://github.com/rbecamend/labes-api/pull/21/files), [repositório BE15](https://github.com/rbecamend/labes-api/blob/63ce24cb527fda69967b7db325b6dec478fb3f6a/app/repositories/infraestrutura_repository.py), [serviço BE15](https://github.com/rbecamend/labes-api/blob/63ce24cb527fda69967b7db325b6dec478fb3f6a/app/services/infraestrutura_service.py), [testes BE15](https://github.com/rbecamend/labes-api/tree/63ce24cb527fda69967b7db325b6dec478fb3f6a/tests), [domínio](https://github.com/rbecamend/labes-api/blob/63ce24cb527fda69967b7db325b6dec478fb3f6a/app/domain/infraestrutura.py).

**Exemplo de falha possível, não observada:** duas linhas para mesma escola/ano, indicador `0` e `1`: `COUNT(DISTINCT escola)` = 1, `validos` = 1 e `presentes` = 1; presença reportada como 100%, embora o registro seja contraditório. Em outra escola com valor `2`, `T=1,V=0`, e o serviço indicaria `sem_dados=1` em vez de `invalidos=1`. Esses casos precisam de testes e política de bloqueio; não foram demonstrados no banco.

## 7. Matriz de critérios de aceite da DAD08

| Critério | Evidência entregue nesta análise | Estado para revisão | O que falta à homologação |
|---|---|---|---|
| Fórmula municipal e filtro de rede | Regras separadas BE13/BE15, código examinado, E1/E2 calculados | **Atendido documentalmente e aritmeticamente** | Decisão sobre população/rede e integridade, conferência empírica conforme equipe |
| `NULL`, denominador zero, `N=0`, `N=1` | Matriz de estados e E3, frações e casos-limite | **Atendido na definição matemática** | Decidir aviso/supressão em N=1, inválidos, duplicatas, códigos não mapeados |
| Ao menos três exemplos manuais | E1, E2 e E3 com insumos e oráculos; script reexecutado 35/35, JSON idêntico e conferência aritmética independente | **Atendido como exemplos sintéticos** | Aceite dos responsáveis; testes de sistema são distintos |
| Escola excluída só como referência comparativa | Inspeção BE13 `CO_ENTIDADE != alvo` e BE15 sem exclusão | **Atendido em inspeção estática** | Validar comportamento em integração com a base e filtros aprovados |
| Homologação formal | Nenhum parecer formal apresentado nesta rodada | **Pendente** | Registrar responsáveis, data, versão, escopo, ressalvas e assinatura/aceite |

## 8. Decisões para Dados, Requisitos, Backend e QA

**Decisões bloqueantes para homologação metodológica sem ressalvas:**

1. **D1 — Integridade:** ocorrendo duplicidade conflitante, valor inválido ou perda de rede na dimensão, qual é o comportamento público? Recomenda-se não calcular um percentual aparentemente normal sobre grupo de composição ambígua. Definir bloqueio por escola, indicador, ano e município, e representação de erro distinta de `NULL`.
2. **D2 — População por rede:** confirmar que `rede_ensino` seleciona dependências administrativas na população de referência BE13 e em todas as escolas da BE15; decidir política para rede desconhecida e códigos de dimensão sem correspondência.
3. **D3 — N=1:** média tecnicamente definida. Confirmar aviso de comparadora única e se ela pode ser exibida sem ressalva, especialmente quando apenas uma escola constitui referência.
4. **D4 — Anos:** decidir se o mínimo da BE13 significa dois anos civis **inclusivos** (`ano_fim−ano_inicio≥1`) ou dois anos completos **de diferença** (`≥2`), regra atualmente implementada. Não alterá-la sem decisão da REQ07.
5. **D5 — Linha única territorial:** REQ07/Frontend deve especificar se o gráfico exibe a presença de um indicador selecionado, a cobertura do indicador ou outro índice explicitamente contratado; BE15 não retorna um escalar municipal composto em sua resposta atual.
6. **D6 — Linhagem e semântica:** decidir o conjunto oficial dos 17 indicadores, a aplicação/semântica por ano e o risco herdado de DAD01/DAD02/DAD06; o merge dessas DADs não é homologação automática.

**Responsáveis a consultar:** Dados/autor da DAD08, Requisitos/PO (REQ07), Backend (BE13/BE15), Frontend/UX (representação e alertas), QA (oráculos de aceitação) e responsável pela homologação indicado pelo projeto. **Não atribuir aprovação nominal sem registro.**

## 9. Verificações locais e limites desta etapa

**Verificado neste computador:** o worktree documental isolado já existente, na branch `docs/DAD08-proposta-homologacao-metodologia`, está baseado no mesmo `63ce24cb527fda69967b7db325b6dec478fb3f6a` da referência remota `equipe/feature/SIE-72-sprint5-temporal-infrastructure`; `git status`, remotos, worktrees e novo fetch da integração foram conferidos. O código BE13/BE15, as DADs anteriores, **17 frações/resultados centrais com aritmética racional independente** e a fronteira de 60% foram inspecionados. O script sintético foi reexecutado em cópia temporária com Python 3.12.10: **35/35**, com JSON idêntico byte a byte ao artefato preservado após fixar quebras LF na gravação. Também passaram **14 testes BE15 selecionados** (SQL em SQLite em memória, serviço e rota) com o Python externo e os pacotes locais da `.venv`, sem PostgreSQL.

**Não executado nesta revisão local:** a suíte completa da aplicação, testes BE13 no checkout da PR #21, consulta PostgreSQL, conferência da base real e chamadas à API com dados reais. A `.venv` local permanece quebrada; o Python 3.12.10 externo foi usado no script sintético e nos 14 testes isolados. Os **120 testes** mencionados para a BE15 são um **relato da equipe** e não foram reexecutados como suíte completa. Os cards Taiga fornecidos no pacote não puderam ser abertos nesta sessão, de modo que seus textos e estados não foram confirmados diretamente.

**Atenção à integração:** na conferência remota, a branch da Sprint 5 não continha o arquivo DAD07 nem as complementações finais da DAD06 que já foram mescladas na Sprint 4. Sincronizar essas evidências de modo controlado, sem reintroduzir a comparação múltipla na Sprint 5, antes do aceite final dos documentos.

### Parecer

**A documentação é tecnicamente suficiente para iniciar a revisão metodológica da DAD08**, incluindo três exemplos inteiramente calculados, regras de presença/cobertura e distinção entre as visões. **A DAD08 ainda não está homologada.** Recomenda-se obter decisão formal especialmente sobre D1, D3, D4 e D5 e exigir verificação de integridade/QA antes de declarar BE13/BE15 integradas sob metodologia homologada.
