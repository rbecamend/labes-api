# DAD06 — Denominadores e amostra de validação por indicador

**Funcionalidade:** análise temporal de infraestrutura Escola × Município, SIE v2, Sprint 4.
**Estado:** auditoria empírica reportada como concluída; consolidação documental preparada para revisão, sem homologação metodológica.
**Autor da entrega documental:** Filipe Braga, sujeito à confirmação na revisão.
**Colaboradores:** participação ainda não registrada; não atribuída nesta versão.
**Revisor e aprovação:** revisor nominal a designar; nenhuma revisão ou aprovação atribuída nesta versão.
**Evidências examinadas:** implementação local em `app/domain/infraestrutura.py`, `app/repositories/infraestrutura_repository.py`, `app/services/infraestrutura_service.py` e `app/models/infraestrutura.py`; DAD01, DAD02, DAD05; matriz documental INEP; rascunho BE09 lido em `equipe/docs/BE09-contrato-composicao-detalhada` (commit `f883ca2`), sem checkout ou merge.
**Rastreabilidade nesta revisão:** os cinco SQLs, quatro [CSVs agregados Q8B e seu manifesto](evidencias/dad06/MANIFESTO_EVIDENCIAS_Q8B.md) estão presentes em `evidencias/dad06/`. Os CSVs originais localizados em Downloads foram conferidos e copiados sem alteração. Saídas separadas de Q0–Q8, logs, planos `EXPLAIN`, data/hora e identificador de snapshot não foram localizados. Os resultados de Q0–Q8 continuam baseados no relato da auditoria anterior; esta revisão não executou SQL nem acessou PostgreSQL.

## 1. Objetivo e escopo

Definir as unidades, os numeradores e os denominadores da composição dos 17 indicadores para a escola e suas comparadoras municipais em cada ano de 2022 a 2025. Estabelecer um procedimento reprodutível para auditar as contagens e conferir manualmente uma amostra. Esta DAD06 prepara a avaliação do alerta informativo de cobertura; não homologa o conjunto de indicadores, o limiar de 60% ou a publicação de resultados.

O grão esperado é uma observação por `(CO_ENTIDADE, NU_ANO_CENSO)` em `silver.infraestrutura_comum`. A unicidade deve ser verificada antes de qualquer agregação; a observação histórica não constitui garantia permanente da carga. Toda comparação é anual e usa `CO_MUNICIPIO` da linha histórica da escola naquele ano.

## 2. Conjunto candidato dos 17 indicadores

As chaves de contrato abaixo correspondem às colunas homônimas em maiúsculas da Silver. A ordem é a de `METRIC_KEYS` no repositório. A DAD02 documenta consistência dos atributos de dicionário em 2022–2025, mas a equivalência semântica e o conjunto final `S` ainda dependem de aprovação.

| Nº | Chave de contrato | Coluna Silver |
|---:|---|---|
| 1 | `in_agua_potavel` | `IN_AGUA_POTAVEL` |
| 2 | `in_energia_rede_publica` | `IN_ENERGIA_REDE_PUBLICA` |
| 3 | `in_esgoto_rede_publica` | `IN_ESGOTO_REDE_PUBLICA` |
| 4 | `in_lixo_servico_coleta` | `IN_LIXO_SERVICO_COLETA` |
| 5 | `in_banheiro` | `IN_BANHEIRO` |
| 6 | `in_banheiro_pne` | `IN_BANHEIRO_PNE` |
| 7 | `in_biblioteca` | `IN_BIBLIOTECA` |
| 8 | `in_sala_leitura` | `IN_SALA_LEITURA` |
| 9 | `in_laboratorio_ciencias` | `IN_LABORATORIO_CIENCIAS` |
| 10 | `in_laboratorio_informatica` | `IN_LABORATORIO_INFORMATICA` |
| 11 | `in_sala_multiuso` | `IN_SALA_MULTIUSO` |
| 12 | `in_sala_atendimento_especial` | `IN_SALA_ATENDIMENTO_ESPECIAL` |
| 13 | `in_cozinha` | `IN_COZINHA` |
| 14 | `in_refeitorio` | `IN_REFEITORIO` |
| 15 | `in_quadra_esportes` | `IN_QUADRA_ESPORTES` |
| 16 | `in_patio_coberto` | `IN_PATIO_COBERTO` |
| 17 | `in_auditorio` | `IN_AUDITORIO` |

## 3. Domínio, notação e regras de integridade

`1` é uma resposta válida de presença; `0`, resposta válida de ausência; `NULL`, informação indisponível ou indeterminada, sem equivalência automática com ausência do recurso. Um valor diferente de `0`, `1` e `NULL` é inválido. As interpretações operacionais de não resposta e não aplicabilidade na fonte continuam pendentes. Não recodificar `NULL` nem valores inválidos.

Seja `e` a escola selecionada, `y` um ano, `m(e,y)` seu código municipal na linha daquele ano, e `P(e,y)` o conjunto de **outras** escolas com uma linha naquele município e ano. O total `T(e,y)=|P(e,y)|` só representa escolas após conferir a unicidade escola/ano. Para indicador `i`, conte nos pares `p_i` valores `1`, `a_i` valores `0`, `u_i` valores `NULL` e `z_i` valores inválidos. `v_i=p_i+a_i`. Em dados íntegros, `p_i+a_i+u_i=T` e `z_i=0`.

Duplicidade da escola selecionada bloqueia a determinação do município e da composição daquele ano. Valor inválido na selecionada bloqueia seu índice e a diferença, conforme recomendação da DAD05; sua linha única ainda permite auditar o município e os pares. Duplicidade ou inválido em potencial comparadora afeta a referência municipal. A DAD05 recomenda não publicar a referência afetada sem resolução ou regra aprovada; não define uma exclusão automática. As consultas Q6–Q8 expõem contagens diagnósticas e deixam nulas as métricas de contrato diante de anomalia no alvo ou no grupo de referência. Esse bloqueio cautelar das saídas preparadas para auditoria não constitui nova política metodológica ou mudança no backend. A extensão da publicação parcial por indicador permanece para decisão dos responsáveis. Não escolher linha, deduplicar ou eliminar valor inválido silenciosamente.

## 4. Matriz de numeradores e denominadores

| Medida anual | Numerador | Denominador | Resultado quando denominador é zero |
|---|---|---|---|
| Índice da escola `I(e,y)` | Indicadores da escola iguais a `1` | Indicadores da escola iguais a `0` ou `1`, `n(e,y)` | `NULL`, jamais 0% |
| Cobertura da escola | `n(e,y)` | 17 indicadores candidatos | 0% para linha existente com 17 `NULL`; ausência de linha é registrada separadamente |
| Presença municipal do indicador `i` | `p_i` | `v_i=p_i+a_i` | `NULL` |
| Cobertura municipal do indicador `i` | `v_i` | `T(e,y)` outras escolas encontradas | `NULL` |
| Média municipal dos índices `R(e,y)` | Soma dos índices individuais calculáveis dos pares | Número de pares com índice calculável, `N(e,y)` | `NULL` |
| Cobertura dos pares | `N(e,y)` | `T(e,y)` | `NULL` |
| Diferença em pontos percentuais | `I(e,y)-R(e,y)` | Não há divisão adicional | `NULL` se qualquer parcela estiver indisponível |

Com denominadores positivos, `I=100×presentes_escola/n`, `presença_i=100×p_i/v_i`, `cobertura_i=100×v_i/T`, `R=(Σ índices individuais dos N pares)/N` e `cobertura_pares=100×N/T`. O índice é calculável no MVP com `n>0`; `cobertura_minima_percentual` permanece `NULL`. A DAD05 não aprovou exclusão por 17/17 nem por 80% para o MVP.

**Presença por indicador e média geral têm unidades distintas.** Presença é a proporção de escolas que responderam `1` entre as que responderam `0/1` ao mesmo indicador. A média municipal calcula primeiro um índice por escola e atribui peso igual a cada escola com índice calculável. Somar respostas de várias escolas ou tirar a média simples dos 17 percentuais municipais não reproduz necessariamente `R`, sobretudo se a cobertura diferir entre escolas ou indicadores.

## 5. Município, anos e casos de ausência

Para cada `y`, selecionar a linha de `e` naquele ano e usar seu `CO_MUNICIPIO` como chave da referência. Não usar o município do registro mais recente para anos anteriores. Excluir `CO_ENTIDADE=e` no conjunto de pares, antes das contagens. `NO_MUNICIPIO` é identificação de exibição; divergências entre nome e código exigem auditoria territorial, sem correção automática. Nenhum denominador anual soma observações de 2022, 2023, 2024 e 2025.

| Situação | Tratamento metodológico |
|---|---|
| Escola não encontrada na Silver | Sem identificação; rota atual retorna 404. |
| Escola existe, mas não tem linha no ano | Sem município histórico seguro, composição escolar indisponível e nenhuma referência inventada. Distinguir de linha totalmente nula. |
| Linha existente, 17 valores `NULL` | Município histórico conhecido; índice escolar `NULL`, cobertura escolar 0%; composição dos pares pode ser auditada. |
| Município histórico `NULL` | Não selecionar pares arbitrários; referência indisponível e ocorrência sinalizada. |
| `T=0` | Contagens municipais zero; presença e cobertura municipais `NULL`; média e diferença `NULL`. |
| `T>0`, `N=0` | Cobertura dos pares 0%; média e diferença `NULL`, mesmo que a escola tenha índice. |
| `N=1` | Média matematicamente definida; aviso de comparadora única proposto pela DAD05, ainda sem homologação. |
| Valor inválido no alvo | Índice próprio e diferença bloqueados; município e pares ainda podem ser diagnosticados. Contrato público pendente de decisão. |
| Valor inválido ou chave duplicada nas comparadoras | Sinalizar a referência afetada; consultas mantêm contagens diagnósticas e não emitem métricas de contrato como válidas. |

## 6. Precisão e arredondamento

Contagens são inteiras. As frações, a média e a subtração usam numeradores e denominadores não arredondados. Arredondar percentuais e diferença para duas casas apenas na apresentação. Comparar um possível alerta de cobertura com a razão exata, antes de arredondar. Uma cobertura indefinida por denominador zero não é baixa cobertura. A regra de arredondamento numérico do domínio atual usa `Fraction` e `round`; a implementação SQL preparada expõe razões `numeric` sem arredondamento para a conferência, deixando o arredondamento final ao consumidor. O modo exato de empate na segunda casa entre Python e PostgreSQL deve ser conciliado antes de afirmar equivalência em todos os casos.

## 7. Auditoria empírica 2022–2025: execução reportada e evidência disponível

O arquivo `evidencias/dad06/01_consultas_select.sql` organiza Q0–Q8 e Q8B. Q0 confirma metadados; Q1 distingue grupos e linhas com `CO_ENTIDADE` nulo, duplicidades e registros com ano nulo, estes fora dos denominadores anuais. Q2 separa os quatro estados de cada indicador por ano; Q3 mede completude. Q4 distingue escola ausente da Silver de escola existente sem histórico em 2022–2025 e preserva o município histórico anual. Q5 enumera pares; Q6 produz composição municipal por indicador; Q7 calcula a média dos índices individuais; Q8 analisa um alvo e ano. Q8B percorre o universo por município, indicador e ano, simulando a exclusão de cada escola-alvo e registrando denominadores pequenos e grupos com integridade pendente. Q5–Q8 requerem `:co_entidade_alvo` e `:ano_alvo`, vinculados pelo cliente SQL em ambiente controlado. Q8B não usa escola-alvo. Q1 e a validação de domínio precedem qualquer interpretação de Q6–Q8B. Se os controles falharem, preservar as contagens diagnósticas e solicitar decisão sobre o tratamento; faixas bloqueadas não constituem evidência de cobertura válida.

As execuções foram informadas como realizadas em PostgreSQL 18 pela conta `sie_auditoria`, em transações `REPEATABLE READ READ ONLY` com timeout. Os quatro CSVs Q8B agora permitem conferir os agregados e têm hashes registrados no manifesto. Não foram localizados logs da sessão, snapshot, data exata de extração, parâmetros capturados nem saídas separadas de Q0–Q8; os CSVs não demonstram por si só as condições da sessão. Esta revisão documental não acessou o banco.

### Q0–Q3 — estrutura, chaves, domínio e completude

Segundo o relato da auditoria atual, Q0 confirmou a tabela e os 17 campos; Q1 não encontrou duplicidade escola/ano nem chave escolar nula entre 2022 e 2025; Q2 encontrou somente `0`, `1` e `NULL`; Q3 não encontrou linha parcialmente preenchida. As contagens anuais reportadas são:

| Ano | Registros escola/ano | Completos (17/17) | Todos os 17 `NULL` |
|---:|---:|---:|---:|
| 2022 | 3.583 | 3.131 | 452 |
| 2023 | 3.396 | 3.138 | 258 |
| 2024 | 3.393 | 3.132 | 261 |
| 2025 | 3.392 | 3.114 | 278 |
| **Total** | **13.764** | **12.515** | **1.249** |

Em cada linha da tabela, completos + totalmente nulos = registros. Os totais coincidem com os resultados históricos **reportados** na DAD01. A coincidência não substitui a inspeção das saídas Q0–Q3 atuais, ausentes do worktree. O diagnóstico de `NU_ANO_CENSO IS NULL` previsto em Q1 não foi informado no resumo recebido.

### Q4–Q8 — cenário piloto

Foi informada validação de uma escola-piloto em Porto de Moz (`CO_MUNICIPIO=1505908`), com uma linha histórica única em cada ano. O identificador individual fica no registro de acesso controlado e não é reproduzido nesta versão publicável. Em 2025 foram reportadas 104 comparadoras: 101 com informação válida e três sem informação. A cobertura de pares é `100 × 101/104 = 97,115384615…%` (97,115385% no relato); a média dos índices individuais foi reportada como 26,732673%. O CSV Q8B de 2025 mostra, para Porto de Moz, `N=105`, `V=102` e três `NULL` por indicador, compatíveis com os totais do piloto após excluir um alvo válido; o CSV agregado não identifica esse alvo. Os vetores dos 17 indicadores, as frações por comparadora e as saídas Q4–Q8 não estão disponíveis aqui para conferência independente. Outros casos previstos em Q4–Q8 não devem ser marcados como testados por inferência a partir deste piloto.

### Q8B — universo municipal e desempenho

O relato informa que a Q8B original funcionou no piloto e que a execução conjunta de 2022–2025 terminou com `canceling statement due to statement timeout` sob limite de 20 segundos. A expansão em 17 indicadores e as leituras, junções e agrupamentos repetidos são hipótese técnica para o custo; não há plano `EXPLAIN` local que identifique o operador responsável. As versões algébricas separadas por ano (`02` a `05`) foram informadas como executadas. Seus quatro CSVs foram conferidos nesta revisão: cada um contém 22 municípios × 17 indicadores = 374 combinações, com chaves únicas, os 17 indicadores esperados e reconciliação das contagens, denominadores, faixas e coberturas. Os totais de escolas e respostas válidas por indicador coincidem com Q1–Q3 informados; a origem operacional da exportação permanece sem log ou snapshot.

## 8. Amostra manual: casos reportados e seleção pendente

Selecionar separadamente em cada ano 2022, 2023, 2024 e 2025. Primeiro, construir a população de chaves escola/ano únicas e classificar cada linha por completude, validade e município. Depois, por ano e estrato, ordenar candidatos de modo determinístico por `CO_MUNICIPIO`, `CO_ENTIDADE`; escolher o primeiro elegível. Documentar consulta, snapshot, quantidade de candidatos e regra de desempate. A seleção real e os identificadores permanecem em armazenamento controlado, fora de artefatos públicos. Se um estrato não existir naquele ano, registrar ausência e não fabricar um caso.

Estratos mínimos: linha completa; linha com 17 `NULL`; escola existente com lacuna anual; município com `T=0`; município com `T>0,N=0`; município com `N=1`; mudança de município histórico ou divergência territorial, se observada; cobertura municipal abaixo, igual e acima de 60%, se existirem casos; extremos de presença 0% e 100%, quando observados. Reservar casos de duplicidade, inválido e cobertura escolar parcial para observação real somente se Q1–Q3 os encontrarem. Caso contrário, preparar exemplos sintéticos identificados separadamente para conferir a matemática e a política de bloqueio. A DAD01 reportou somente linhas completas ou totalmente nulas naquele recorte; não afirmar que cobertura escolar parcial foi validada empiricamente.

Para cada escola/ano amostrado, registrar os 17 valores da selecionada e de **todas** as comparadoras do município/ano, em ambiente restrito. Conferir manualmente, para cada indicador, `p_i`, `a_i`, `u_i`, `z_i`, `v_i`, `T`, presença e cobertura; conferir `p_i+a_i+u_i=T` somente quando `z_i=0` e as chaves forem únicas. Recalcular também o índice de cada comparadora, `N`, média simples, cobertura de pares e diferença. Não combinar anos.

| Estrato | Estado da evidência atual |
|---|---|
| Escola com histórico único nos quatro anos e município de alta cobertura | Piloto em Porto de Moz reportado; saídas linha a linha ausentes. |
| Município abaixo do cenário de 60% | `1503804` observado nos quatro CSVs Q8B agregados; conferência manual de escolas ainda pendente. |
| Escola com lacuna anual; escola inexistente | Casos previstos no plano, sem resultado de execução fornecido. |
| Município com `T=0`, `N=0` ou denominador de 1 a 4 | Nenhum cenário sem pares ou com denominador de 1 a 4 nos CSVs Q8B; menor denominador observado: 36. Casos de referência escolar Q5–Q8 e amostra manual permanecem sem comprovação própria. |
| Duplicidade, inválido ou cobertura escolar parcial | Não observados no resumo Q1–Q3; exemplos sintéticos podem testar cálculo, sem constituir evidência empírica. |

O manifesto da amostra, snapshot, parâmetros, vetores de indicadores e conferência manual individual continuam pendentes de localização ou incorporação em área controlada. Não registrar cenário previsto como validado.

## 9. Limiar informativo de 60% e dependências REQ05/BE09

O rascunho BE09 registra conflito: o relatório REQ05 chama 60% de limiar oficial, enquanto os critérios da DAD06 e a wiki da Sprint 4 o deixam pendente de validação por Dados; a DAD05 não homologa esse valor. A BE09 propõe `limiar_alerta_cobertura_percentual=60.0`, `limiar_alerta_cobertura_status=provisorio_pendente_dad06`, alerta quando a razão exata é estritamente menor que 60%, sem bloquear o resultado. Esta DAD06 **não escolhe valor definitivo**.

Q8 permite conferir o cenário de um alvo. Q8B produz a distribuição entre alvos elegíveis, por indicador, município e ano: total de observações, respostas válidas e ausentes, casos sem pares, denominadores de 1 a 4, mínimo, máximo e média da cobertura, e contagens abaixo, iguais e acima de 60%. Q8B subtrai a escola simulada da referência. Grupos com duplicidade, identificador nulo ou inválido em qualquer dos 17 indicadores ficam identificados e fora das faixas calculadas; a distribuição observada pode, portanto, ter cobertura limitada pela integridade da fonte. Comparar municípios e os quatro anos separadamente antes de qualquer síntese do período. A análise informa a decisão, mas não demonstra sozinha que 60% é um limite metodológico adequado. Valor, escopo, texto e responsável precisam de decisão registrada antes do fechamento da BE09.

O município `1503804` apresenta as seguintes **médias de cobertura simulada conferidas nos CSVs**, arredondadas a duas casas. Foi o único município com média abaixo de 60% em cada ano; nos CSVs, os 17 indicadores de cada município compartilham a mesma cobertura média porque não houve preenchimento parcial.

| Ano | Cobertura média simulada conferida de `1503804` | Relação com 60% provisórios |
|---:|---:|---|
| 2022 | 57,14% | Abaixo |
| 2023 | 56,63% | Abaixo |
| 2024 | 55,42% | Abaixo |
| 2025 | 53,66% | Abaixo |

A queda de 3,48 pontos percentuais entre os valores arredondados de 2022 e 2025 é apenas comparação descritiva; não identifica causa. As taxas globais de completude escolar calculáveis da tabela Q0–Q3 são 87,38%, 92,40%, 92,31% e 91,80% por ano, respectivamente. Essas taxas usam todas as escolas observadas na Silver em cada ano. A média simulada por município da Q8B usa a referência **excluindo cada alvo**; não se obtém por média simples das taxas globais. O recorte de 22 municípios da Silver não representa cobertura estadual.

| Ano | Cenários abaixo de 60% | Iguais a 60% | Acima de 60% | Sem pares | Denominador de 1 a 4 | Menor denominador de pares |
|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 1.428 | 0 | 59.483 | 0 | 0 | 36 |
| 2023 | 1.411 | 0 | 56.321 | 0 | 0 | 37 |
| 2024 | 1.411 | 0 | 56.270 | 0 | 0 | 39 |
| 2025 | 1.394 | 0 | 56.270 | 0 | 0 | 39 |

As faixas somam uma observação por escola-alvo simulada **em cada um dos 17 indicadores**; não contam escolas distintas. Cada ano teve um município abaixo e 21 acima de 60% pelas médias municipais conferidas, sem cenário exatamente em 60%. O zero em `sem_pares` e `denominador_1_a_4` descreve somente o universo dos CSVs Q8B. A ausência observada desses casos não substitui a amostra manual de cenários-limite nem decide a política para denominador zero. [Manifesto e hashes](evidencias/dad06/MANIFESTO_EVIDENCIAS_Q8B.md).

Conferência estática com BE09: `data.serie[].municipio_referencia` usa a linha anual; `registro_historico_disponivel` distingue lacuna de linha nula; `composicao_escola` tem 17 chaves `1/0/null`; `composicao_municipal` tem, por chave, `quantidade_presentes`, `quantidade_validos`, `quantidade_sem_dados`, `quantidade_escolas_referencia`, `percentual_presentes`, `cobertura_percentual` e `cobertura_reduzida`. As invariantes propostas são `0≤presentes≤validos`, `validos+sem_dados=escolas_referencia` e `escolas_referencia=denominador_pares`. Valor inválido ou duplicidade rompe a premissa do contrato e exige decisão de sinalização pública. O backend vigente lança `ValueError` para valor inválido ou duplicidade, enquanto a BE09 ainda não define um estado de composição para essas ocorrências; as consultas DAD06 não antecipam esse contrato. A BE09 ainda depende de decisão sobre o alerta, exemplo completo de quatro anos e revisão das equipes responsáveis; nenhum desses itens foi concluído aqui.

## 10. Limitações herdadas e decisões pendentes

- **DAD01:** 13.764 linhas, 12.515 completas e 1.249 integralmente nulas são resultados reportados, não reexecutados. ETL original, causa dos nulos, critério operacional do recorte intencional de 22 municípios, garantia de unicidade e divergências territoriais permanecem pendentes. DAD01: não homologada.
- **DAD02:** 68 verificações documentais sustentam os 17 candidatos comuns; instruções operacionais, aplicabilidade, linhagem Silver e homologação semântica de `S` permanecem pendentes.
- **DAD05:** princípio da média aritmética aprovado; população elegível, integridade, N=1, territorialidade, publicação e demais decisões complementares não foram homologadas. O MVP não usa corte mínimo de cobertura.
- **BE09/REQ05:** resolver a divergência do alerta e confirmar comportamento público quando há integridade comprometida, sem alterar o rascunho BE09 nesta etapa.
- **Evidência da execução atual:** os SQLs e CSVs Q8B agregados estão no worktree, com hashes e reconciliação local. Faltam saídas separadas Q0–Q8, logs, datas/snapshots, parâmetros capturados e planos. A conferência dos CSVs não reexecutou SQL nem comprova a sessão de origem. Manter registros individuais fora do Git.
- **Universo e denominadores vazios:** os CSVs conferem 22 municípios e 374 combinações em cada ano, sem pares ausentes nem denominadores de 1 a 4 nesse recorte. A política pública para denominador zero e a elegibilidade territorial precisam de decisão explícita.

## 11. Critérios de aceite e estado de aprovação

| Critério | Estado nesta etapa |
|---|---|
| 17 indicadores e fórmulas com numeradores, denominadores e zero definidos | Documentados; sujeitos a revisão |
| `1/0/NULL` e inválidos; ausência de linha versus linha nula | Definidos; Q1–Q3 reportados sem inválidos ou cobertura parcial, saídas originais pendentes |
| Município histórico, exclusão da selecionada e separação anual | Documentados no método e nas consultas preparadas |
| Duplicidades, inválidos e bloqueio de resultado afetado | Plano de controle preparado; política definitiva pendente |
| Q0–Q8 e Q8B somente leitura, com parâmetros e limites | SQLs presentes; quatro CSVs Q8B agregados conferidos; saídas Q0–Q8 e logs locais ausentes |
| Amostra real 2022–2025 e conferência manual dos 17 indicadores | Piloto reportado e agregados Q8B conferidos; manifesto da amostra e vetores controlados pendentes |
| Avaliação do alerta de 60% | Persistência e distribuição Q8B conferidas nos CSVs; decisão formal pendente |
| Revisão nominal, evidências empíricas, aprovação metodológica e homologação | Pendentes |

**Próxima etapa:** revisar os quatro CSVs agregados e o manifesto incorporados, localizar os metadados de execução ainda ausentes, completar os estratos da amostra e registrar decisões de semântica, integridade, universo e limiar. A entrega documental está preparada para revisão; não equivale a homologação ou autorização de publicação oficial.
