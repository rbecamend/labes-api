# SIE — DAD-04 | Conciliação API × referência DAD-03

**Estado:** CONCLUÍDA — VALIDAÇÃO TÉCNICA EXPLORATÓRIA.  
**Perfil:** experimental, não homologado.  
**Data desta preparação:** 2026-10-12.

**Destino da implementação:** os resultados abaixo documentam a experiência da PR #44 (`LABES-SI/labes-api`), que não deve ser incorporada ao backend compartilhado. A conciliação deverá ser repetida após a implementação oficial da BE-07, com a integração BE-08 e o contrato HTTP BE-05.

> **Atualização transversal (16/10/2026):** a repetição técnica ocorreu na [DAD-04 da API oficial](DAD-04_CONCILIACAO_API_OFICIAL.md), integrada pela [PR #12](https://github.com/rbecamend/labes-api/pull/12): 10 testes HTTP controlados aprovados e 4/4 anos do pacote DAD-03B concordantes. A validação SQL/PostgreSQL real permanece pendente. As afirmações temporais abaixo pertencem ao experimento original.

## 1. Objetivo e resultado da descoberta

A rota preexistente `GET /infraestrutura/analise-temporal` **não atende** à comparação Escola × Município. Em `app/routes/infraestrutura.py`, ela recebe `metrica` e `pibid` e chama `build_analise_temporal`; em `app/services/infraestrutura_service.py`, o serviço cria gráficos por localização e dependência. O caminho não recebe escola/município/ano como comparação, não exclui a selecionada de uma referência municipal e não calcula média não ponderada dos índices das demais escolas.

O repositório existente também contém um tratamento legado de valores ausentes com `COALESCE(col, 0)` em `app/repositories/infraestrutura_repository.py::find_pontos_mapa_raw`. A nova rota não chama esse método e não converte `NULL` em zero.

Foi criada, somente na implementação experimental anterior, a rota separada:

`GET /infraestrutura/analise-temporal/escola-municipio`

Ela preserva a rota legada e não publica nem altera seus resultados. O endpoint lê a observação da escola alvo para cada ano e, em seguida, somente os pares ano/código municipal presentes nessas observações, usando os valores brutos das 17 colunas sem `COALESCE`. O cálculo da resposta usa frações exatas.

**Contrato oficial do MVP:** `GET /infraestrutura/analise-temporal/escolas/{co_entidade}/comparacao-municipio`. A rota experimental acima foi substituída como referência contratual. O código local consultado contém domínio e schemas preparatórios da BE-07, mas ainda não a rota oficial; portanto os resultados desta DAD-04 não validam empiricamente o contrato oficial.

## 2. Contrato experimental implementado

A resposta inclui escola, código e nome municipal observados, ano, versão do contrato e do conjunto candidato, status não homologado, contagens de `sim`, `não`, `NULL`, inválidos e válidos, cobertura, elegibilidade, índice individual, N, referência não ponderada das demais escolas, diferença em pontos percentuais, estado, motivo de indisponibilidade, alertas territoriais e problemas de integridade.

A regra de cobertura completa está identificada apenas como perfil experimental condicional. Escolas parciais e all-NULL são excluídas da referência sem bloquear comparadoras válidas. Valores inválidos ou duplicidades em potenciais comparadoras bloqueiam a referência afetada; problemas da selecionada bloqueiam seu índice/contraste. `N=0` mantém referência e diferença nulas. `N=1` retorna a conta matemática com aviso. Código municipal variável por ano usa o código da observação anual e gera alerta. Não existe corte de 80%.

O endpoint retorna frações na forma `numerador/denominador` para evitar arredondamento intermediário. O conjunto S continua marcado como candidato e não homologado; nenhum campo implica autorização de publicação.

### Diferenças frente ao MVP acordado

| Aspecto | Experimento da PR #44 | MVP/BE-05 e código compartilhado consultado |
|---|---|---|
| Caminho | `/infraestrutura/analise-temporal/escola-municipio` | `/infraestrutura/analise-temporal/escolas/{co_entidade}/comparacao-municipio` |
| Cobertura | Exige 17/17 válidos no perfil experimental | Sem cobertura mínima: `cobertura_minima_percentual = null` no schema; índice com qualquer quantidade positiva de válidos no domínio |
| Disponibilidade | Estados e motivos próprios do experimento | `disponivel`, `escola_sem_dados`, `sem_pares_validos`, `sem_pares_municipio` no domínio/schema compartilhados |
| Pares | `N` de comparadoras elegíveis sob 17/17 | `quantidade_pares_validos` sobre `denominador_pares` das demais escolas do mesmo município/ano; `cobertura_pares_percentual` é nula quando o denominador é zero |
| Precisão | Frações exatas na resposta experimental | Domínio local arredonda índices, média e diferença a duas casas; a política de precisão intermediária e apresentação requer alinhamento |
| Integração | Exercitada via HTTP e PostgreSQL local | Ainda depende de BE-07/BE-08; não há validação empírica da rota oficial nesta DAD |

O schema compartilhado exige código INEP escolar de oito dígitos na identificação da resposta (`10_000_000` a `99_999_999`). A validação do parâmetro de entrada, os parâmetros de consulta e os códigos HTTP exatos da BE-05 não puderam ser confirmados no contrato local. O schema preparatório define corpos de erro `not_found`, `internal_error` e `warehouse_unavailable`, sem demonstrar aqui o mapeamento de status HTTP. Esses pontos dependem do contrato validado no Plane e da implementação/testes da BE-08; não são inferidos da rota experimental.

## 3. Evidência DAD-03B localizada e identidade do alvo

O pacote complementar foi encontrado fora do repositório, em armazenamento temporário local. Seu `manifest.json` registra Q1=4, Q2=155, Q3=16 e Q4=4; o estado SQL e a validação estão `complete`, e a homologação permanece `pending`. O armazenamento temporário é volátil; este relatório não o trata como arquivo permanente nem copia seus dados para o Git. A localização atual da evidência detalhada e seu armazenamento de acesso controlado ainda precisam ser confirmados pela equipe.

O registro anterior informa que as quatro linhas reais de Q1 foram lidas localmente. Em cada ano 2022–2025, Q1 apontava o mesmo município e escola selecionada da primeira execução reportada na DAD-03B. Os identificadores foram omitidos desta PR documental para evitar extrato escolar identificável. O snapshot da primeira execução não está identificado, portanto as execuções permanecem snapshots distintos; não se afirma identidade de snapshot nem se repete a conferência nesta revisão.

Na execução anterior, o manifesto de checksums foi reportado como recalculado localmente: **10 arquivos verificados, zero divergências SHA-256**. Nenhuma credencial foi registrada no relatório. Os dez artefatos não estão neste checkout; localização, conteúdo e hashes não foram reconfirmados nesta revisão.

## 4. Conciliação HTTP com Q2 e cálculos independentes

A rota foi exercitada via HTTP/ASGI, com o repositório substituído por fixture em memória carregada das linhas brutas de Q2 da pasta temporária. O serviço recebeu os indicadores originais da Q2; a resposta HTTP foi comparada com `independent_calculations.json`, sem arredondamento. Isso valida a integração HTTP e a lógica de cálculo sobre o snapshot exportado, mas **não exercita o método SQL do repositório nem uma conexão PostgreSQL**.

As quatro comparações anuais entre a resposta HTTP experimental e o cálculo independente foram reportadas como concordantes. A verificação utilizou os valores de Q2 em memória. As frações, contagens por ano e demais resultados da escola selecionada foram retirados da versão publicável. A lista dos 17 campos e os registros brutos também não acompanham esta PR. A evidência detalhada deve permanecer em armazenamento de acesso controlado, cuja localização e disponibilidade ainda precisam ser confirmadas pela equipe.

## 5. Testes

A suíte HTTP nova exercita a rota, não apenas a função de serviço, contra os cenários sintéticos DAD-03A:

- T01–T15, incluindo T13A e T13B separadamente e T14 em 2022 e 2023;
- escola não observada, all-NULL, parcial, N=0, N=1, inválido selecionado, inválido em comparadora, duplicidade selecionada e em comparadora;
- exclusão da escola selecionada, média de índices escolares, precisão exata, diferença em pp e parâmetros de ano;
- conjunto sintético (S^*={A,B,C}) é marcado como sintético e não homologado. A execução real usa os 17 candidatos fixos.

**Resultado:** `tests/routes/test_infraestrutura_escola_municipio.py` — **18 passed**. A conciliação HTTP com linhas brutas Q2 — **4/4 anos concordantes**.

A suíte completa foi executada: **63 passed, 1 failed**. A falha isolada e reproduzida é `tests/services/test_conectividade_service.py::test_escolas_hover_traz_pibid_e_ideb`: o teste espera o valor inteiro `7`, mas o serviço retorna a string `'7'`. Esse teste e o serviço de conectividade não foram alterados nesta DAD-04; a falha é alheia à rota experimental.

Nenhum teste fez conexão ao PostgreSQL. Não houve alteração de dados, schema, migration, frontend, auditorias anteriores ou documentos metodológicos.

## 6. Integração experimental e evidências reportadas

A integração real da rota experimental foi reportada como executada manualmente no PowerShell local pelo caminho HTTP → FastAPI → repositório → PostgreSQL local. Esta revisão não acessou o banco nem repetiu consultas. A chamada foi concluída com status `experimental_nao_homologado` para o alvo restrito da DAD-03B no período 2022–2025; os identificadores individuais foram omitidos da PR documental.

Os quatro anos foram reportados como concordantes em N e nas frações exatas do índice, da referência e da diferença para o mesmo alvo da DAD-03B, embora as execuções tenham snapshots distintos. A tabela anual de resultados individuais foi retirada da versão publicável. Os JSONs, Q1/Q2 brutos e extratos individuais não acompanham esta PR; a guarda da evidência detalhada em armazenamento de acesso controlado ainda precisa ser confirmada.

A validação adicional dos denominadores e da cobertura foi reportada sem divergências nos quatro anos. As contagens e coberturas individuais foram retiradas da versão publicável.

A evidência HTTP foi reportada fora do Git sob o nome `SIE_DAD04_HTTP_20261012T220030Z.json`. O caminho absoluto da máquina anterior foi omitido; este checkout não contém o arquivo e sua disponibilidade atual não foi reconfirmada. SHA-256 registrado na execução anterior: `001DEC67ECF314348507870A474EC80B3D6212139ADDC7F3CA6611108D64D341`.

A evidência complementar de denominadores foi reportada fora do Git sob o nome `DAD04_DENOMINADORES.json`. O caminho absoluto da máquina anterior foi omitido; este checkout não contém o arquivo e sua disponibilidade atual não foi reconfirmada. SHA-256 registrado na execução anterior: `7477D03AD941CFD6C7A44F938F96034E6703E4D318BFAE0772CF58F02C50E154`. Os hashes históricos não foram recalculados nesta revisão. Nenhum dado escolar individual deve acompanhar a PR documental.

### Escopo das validações

- **Testes sintéticos:** exercitaram os cenários artificiais da DAD-03A por HTTP/ASGI e validaram os comportamentos da rota experimental sem PostgreSQL.
- **Q2 em memória:** as linhas brutas exportadas de Q2 alimentaram um repositório em memória; a resposta HTTP foi comparada com o cálculo independente. Os quatro anos concordaram, mas esse exercício não chamou o repositório SQL nem abriu conexão ao banco.
- **Integração real:** a execução manual descrita nesta seção percorreu a rota HTTP, FastAPI, repositório e PostgreSQL local e concordou com a DAD-03B nos quatro anos. Essa validação técnica exploratória não constitui homologação semântica.

## 7. Decisão técnica e pendências do projeto

**DAD-04: CONCLUÍDA — VALIDAÇÃO TÉCNICA EXPLORATÓRIA DA ROTA EXPERIMENTAL.** Foi reportada integração pelo caminho real até o PostgreSQL local, concordância dos quatro resultados anuais com a DAD-03B e conferência dos denominadores e da cobertura. Os hashes SHA-256 dos artefatos externos foram verificados à época; a disponibilidade atual desses arquivos não foi confirmada neste checkout.

A suíte nova da rota registrou `18 passed`. A suíte completa registrou **63 passed, 1 failed** e, portanto, não está aprovada como um todo. A falha isolada é `tests/services/test_conectividade_service.py::test_escolas_hover_traz_pibid_e_ideb`: o teste espera o inteiro `7` e recebe a string `'7'`. O serviço e o teste de conectividade não foram alterados nesta DAD-04; essa falha permanece registrada como pendência separada.

A conclusão não homologa o significado dos indicadores nem autoriza uso oficial ou publicação. Permanecem explicitamente os estados do projeto: **DAD-01 — NÃO HOMOLOGADA; DAD-02 — matriz preliminar; DAD-05 — contrato metodológico condicional; conjunto S — indicadores candidatos, sem homologação semântica; publicação de indicadores oficiais — não autorizada.**

As próximas etapas incluem repetir a conciliação com a rota oficial após BE-07/BE-08 e resolver as decisões/homologações metodológicas pendentes. A falha histórica da suíte completa permanece registrada; não há evidência nesta revisão de que tenha sido corrigida. A validação técnica exploratória concluída aqui não substitui esses passos.
