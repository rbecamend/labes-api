# SIE — DAD-04 | Conciliação técnica da API oficial Escola × Município

- **Data da execução:** 16/10/2026
- **Repositório/worktree:** `rbecamend/labes-api`, `labes-api-sie30-dad04`
- **Branch e commit de referência:** `feature/SIE-47-dad04-official`, `7c43848d6c609c09a69d42e1162879c81d9ae68c`
- **Endpoint:** `GET /infraestrutura/analise-temporal/escolas/{co_entidade}/comparacao-municipio`

## 1. Escopo e distinção histórica

Este relatório registra a conciliação complementar da **API oficial** integrada pelas PRs #9, #10 e #11. O commit `7c43848` contém os três merges. O trabalho não alterou o backend, o contrato HTTP, o frontend, a rota experimental ou o PostgreSQL.

A DAD-04 anterior (`DAD-04_CONCILIACAO_API_REFERENCIA.md`) pertence à documentação histórica trabalhada na PR #7 e pode ainda não estar integrada à branch compartilhada. Ela concluiu uma validação técnica **exploratória** da rota da PR #44. Seu perfil experimental exigia cobertura completa 17/17. A API oficial identifica sua metodologia como `infraestrutura-v2-provisoria`, `homologada=false` e `cobertura_minima_percentual=null`. Por isso, resultados da validação experimental não foram aceitos automaticamente como expectativas do MVP atual.

## 2. Contrato efetivamente exercitado

A rota e os schemas retornam quatro pontos anuais, de 2022 a 2025. Cada ponto expõe índice da escola, indicadores presentes e válidos, cobertura dos 17 indicadores, média municipal, diferença em pontos percentuais, quantidade e denominador de pares e cobertura dos pares. O índice usa `100 × presentes / válidos`; `0` é válido e `NULL` não entra no denominador. A referência usa o município da observação anual, exclui a escola selecionada e calcula a média simples dos índices individuais dos demais estabelecimentos com índice válido. Os cálculos usam frações exatas até o arredondamento final para duas casas.

Os estados públicos observados são `disponivel`, `escola_sem_dados`, `sem_pares_validos` e `sem_pares_municipio`. O cabeçalho municipal corresponde à identificação mais recente da escola; o grupo de pares de cada ano corresponde ao município histórico daquele registro. A documentação BE-08 prevê HTTP `404`, `422`, `500` e `503`.

## 3. Conciliação HTTP com repositório controlado

O teste `tests/routes/test_dad04_conciliacao_oficial.py` usa `httpx.AsyncClient`, `ASGITransport` e a aplicação FastAPI de `main.py`. A única dependência substituída é `get_infraestrutura_repository`. Rota, validação dos schemas, `InfraestruturaService` e funções de domínio executam sem substituição. O repositório controlado recebe somente registros artificiais nos testes versionados; não abre conexão SQL.

O **oráculo independente da DAD-04** está declarado no teste, sem chamar funções de cálculo do backend: conta `1`, `0` e `None` dos 17 indicadores; forma frações exatas com `fractions.Fraction`; exclui a escola consultada; filtra pares pelo município e ano; calcula média simples, diferença e coberturas; arredonda somente os campos públicos. A comparação verifica o **ponto anual completo** retornado pelo HTTP, não apenas campos escolhidos.

| Verificação | Resultado |
|---|---|
| Índice, contagens, denominador e cobertura de indicadores | Concordantes com o oráculo sintético. |
| Exclusão da selecionada, município histórico e ano dos pares | Concordantes; chamadas ao repositório conferidas por ano. |
| Pares válidos, denominador, cobertura municipal e média não ponderada | Concordantes, inclusive par integralmente nulo e índices parciais. |
| Precisão da média e da diferença | Concordantes com frações exatas; cenários distinguem arredondamento intermediário. |
| Valores nulos, ano sem observação e série 2022–2025 | Preservados na resposta HTTP. |
| Quatro estados de disponibilidade | Todos exercitados por HTTP. |
| HTTP `404`, `422`, `503` e `500` | Confirmados nos cenários aplicáveis. |

Valores inválidos na selecionada ou em par, e duplicidades da selecionada ou de par, interrompem o cálculo; a rota retorna `500/internal_error` nos quatro cenários sintéticos. Nenhum resultado parcial é publicado nesses casos. **Limitação contratual:** o erro público não distingue a causa de integridade. Outro limite é que ano sem observação e observação integralmente nula compartilham o estado `escola_sem_dados`, embora contagens e eventual média municipal ajudem a diferenciá-los. São comportamentos existentes, registrados para decisão separada; nenhum código HTTP ou regra foi alterado.

**Reproduções e propostas para revisão separada:** os quatro casos de integridade estão parametrizados no teste `test_http_bloqueia_integridade_com_erro_atual`; pode-se definir futuramente erro tipado de integridade e resposta pública específica, após decisão contratual. Os casos `test_http_preserva_ano_sem_observacao_e_sem_pares_validos` e `test_http_compara_serie_e_oraculo_sintetico_independente` demonstram ausência anual e linha integralmente nula com o mesmo estado; um estado próprio para ausência de observação exigiria revisão do schema, da BE-08 e dos consumidores. Essas propostas não foram aplicadas nem consideradas falhas contra o contrato vigente.

**Resultado:** nove casos HTTP sintéticos aprovados. Com o caso histórico descrito abaixo, a suíte DAD-04 registrou **10 aprovados, zero falhas, zero ignorados** na execução local mais recente. A seleção ampliada de infraestrutura, incluindo DAD-04 e testes BE existentes, registrou **98 aprovados, zero falhas, zero ignorados** na execução anterior do Codex.

## 4. Conciliação controlada do pacote histórico DAD-03B

O pacote restrito foi lido diretamente de uma pasta temporária fora do Git, indicada ao teste por `DAD03B_PACKAGE_DIR`. Nenhum Q1–Q4, oráculo com registros individuais, manifesto ou identificador escolar foi copiado para este worktree. A disponibilidade da pasta temporária é volátil.

Antes das contas, o teste conferiu:

- **Integridade:** os dez arquivos enumerados em `SHA256SUMS.txt` tiveram SHA-256 recalculado, com **10 concordâncias e zero divergências**.
- **Fonte e snapshot interno:** `manifest.json`, Q1, Q2 e `independent_calculations.json` declaram o mesmo identificador de snapshot; os hashes de consulta Q1/Q2 coincidem com o manifesto. Isso vincula os arquivos do pacote entre si, sem comprovar identidade com qualquer banco ativo.
- **Recorte e alvo:** Q1 tem um registro por ano de 2022 a 2025 e um único identificador de escola selecionada; Q2 sinaliza exatamente uma linha selecionada por ano para esse alvo, no município de referência da Q1. Foram conferidos o número de linhas, os parâmetros tipados da Q2, a população identificada por ano e a unicidade das chaves escola/ano utilizadas.
- **Campos e integridade:** os 17 campos candidatos estão presentes em Q2; as linhas do município de referência usadas na comparação têm valores `0`, `1` ou `NULL`, sem chave duplicada ou valor inválido no recorte testado.
- **Cobertura:** o oráculo experimental usa 17/17. Nesta amostra, as demais escolas são completas ou integralmente nulas: as escolas com índice válido sob a regra atual são exatamente as comparadoras `eligible` do oráculo histórico em **cada um dos quatro anos**. A igualdade foi verificada pela identidade das comparadoras, não inferida apenas de `N` igual.

Em seguida, a Q2 alimentou somente o repositório controlado. Para cada ano, as frações exatas do índice da selecionada, dos índices individuais das comparadoras, da média e da diferença foram recalculadas independentemente e confrontadas com `independent_calculations.json`. A resposta da rota oficial foi confrontada com essas contas, incluindo contagens, denominador de pares e cobertura.

| Ano | Identidade, recorte e comparadoras | Frações exatas do pacote × conta independente | HTTP oficial × conta independente |
|---:|---|---|---|
| 2022 | Concordantes | Concordantes | Concordantes |
| 2023 | Concordantes | Concordantes | Concordantes |
| 2024 | Concordantes | Concordantes | Concordantes |
| 2025 | Concordantes | Concordantes | Concordantes |

**Resultado:** quatro de quatro anos concordantes **no ambiente HTTP controlado com as linhas Q2 do pacote**. A comparabilidade vale para esse snapshot extraído e esse recorte, pois a população elegível foi confirmada como igual. Não se extrapola a equivalência das políticas de cobertura para outros municípios, anos ou cargas com indicadores parciais.

## 5. Integração real com PostgreSQL

**Não executada.** O worktree não contém configuração local de conexão; não havia variável de conexão disponível nem listener local na porta padrão 5432 na verificação inicial. Não se iniciou serviço, não se restaurou banco e não se consultou PostgreSQL. O teste histórico substitui o repositório por dados Q2 em memória e, portanto, não valida o SQL da rota oficial contra uma instância PostgreSQL nem demonstra que um banco ativo mantém o snapshot do pacote.

Para encerrar essa etapa, é necessária uma conexão de leitura autorizada à fonte, com identificação comprovável de snapshot/recorte compatível, ou a disponibilização controlada do mesmo snapshot para reprodução. Só então a resposta HTTP pelo repositório SQL real poderá ser confrontada com o cálculo independente. Não houve resultado classificado como `não comparável` dentro dos quatro anos do pacote; uma eventual fonte PostgreSQL diferente permanece **sem comparabilidade demonstrada**.

## 6. Execução e evidências de teste

Na execução anterior do Codex, o Python da `.venv` compartilhada só conseguiu iniciar fora do sandbox; a primeira tentativa dentro dele falhou antes da coleta dos testes porque o interpretador base ficou inacessível. Uma execução intermediária do teste histórico revelou erro **no próprio teste** ao construir `Fraction` a partir de texto com denominador adicional; a leitura foi corrigida e repetida. Não houve defeito da API nesse episódio.

A execução local mais recente usou `uv run pytest` na `.venv` do próprio worktree DAD-04, com `DAD03B_PACKAGE_DIR` apontando para o pacote restrito. A suíte DAD-04 registrou **`10 passed in 2.14s`**, sem falhas nem testes ignorados, e a conciliação DAD-03B de 2022–2025 foi aprovada. As verificações finais do Ruff registraram **`uvx ruff check`: `All checks passed`** e **`uvx ruff format --check`: `1 file already formatted`** para o arquivo de teste DAD-04.

Para reproduzir a suíte DAD-04 a partir da raiz do worktree, com a `.venv` local disponível, defina `DAD03B_PACKAGE_DIR` para o diretório autorizado do pacote DAD-03B e execute:

```powershell
$env:DAD03B_PACKAGE_DIR = '<diretório local do pacote DAD-03B>'
uv run pytest tests/routes/test_dad04_conciliacao_oficial.py -q -ra --tb=short
uvx ruff check tests/routes/test_dad04_conciliacao_oficial.py
uvx ruff format --check tests/routes/test_dad04_conciliacao_oficial.py
```

As seleções ampliadas abaixo pertencem à execução anterior do Codex, feita com a `.venv` compartilhada, e não foram repetidas na execução local mais recente. Para reproduzir os mesmos recortes a partir da raiz do worktree, use:

```powershell
uv run pytest tests/domain/test_infraestrutura.py tests/repositories/test_be02_historico_escola.py tests/repositories/test_be03_pares_municipais.py tests/repositories/test_be04_recortes_vazios.py tests/services/test_be07_comparacao_service.py tests/schemas/test_be07_comparacao_infraestrutura.py tests/routes/test_be07_comparacao_route.py tests/routes/test_be08_integracao_endpoint.py tests/routes/test_dad04_conciliacao_oficial.py -q -ra --tb=short
uv run pytest -q -ra --tb=short
```

| Execução e origem | Aprovados | Falhos | Ignorados | Resultado |
|---|---:|---:|---:|---|
| Suíte DAD-04 com pacote; execução local mais recente | 10 | 0 | 0 | Aprovada em 2.14s. |
| Testes específicos de infraestrutura, incluindo DAD-04; execução anterior do Codex | 98 | 0 | 0 | Aprovada. |
| Suíte completa; execução anterior do Codex | 143 | 1 | 0 | Falha de Conectividade, alheia à DAD-04. |

A única falha da suíte completa na execução anterior do Codex é preexistente e pertence a `tests/services/test_conectividade_service.py::test_escolas_hover_traz_pibid_e_ideb`: espera inteiro `7`, recebe texto `'7'`. Foi reportada também na DAD-04 experimental. Nenhum arquivo de Conectividade foi modificado.

Os testes QA-01/QA-02 da equipe, no commit `aea7fb8` de `karensantos9/labes-tests`, registraram 19 aprovados sobre domínio e serviço do backend em `7c43848`. São evidências complementares ao oráculo independente da DAD-04, sem HTTP ou PostgreSQL; não foram contados como execução desta suíte.

## 7. Conclusão técnica e pendências

**Concluída a conciliação técnica da rota oficial no escopo HTTP/ASGI com repositório controlado e no escopo do pacote DAD-03B extraído: quatro anos concordantes com contas independentes e com o oráculo histórico após prova de comparabilidade da população.** A integração da rota oficial com PostgreSQL real permanece **pendente**. A suíte completa do repositório registrou uma falha preexistente de Conectividade na execução anterior do Codex.

Permanecem para decisão separada: tratamento público de inválidos e duplicidades (`500/internal_error`), distinção pública entre ausência de linha e linha integralmente nula, eventual comparação com PostgreSQL no mesmo snapshot e as decisões metodológicas de DAD-01, DAD-02 e DAD-05. Os 17 indicadores são candidatos; esta conciliação não homologa seu significado, não valida resultados oficiais contra PostgreSQL e não autoriza publicação.
