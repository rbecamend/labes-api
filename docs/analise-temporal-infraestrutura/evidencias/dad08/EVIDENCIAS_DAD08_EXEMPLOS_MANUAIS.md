# DAD08 — Evidências de exemplos manuais e verificações independentes

**Tarefa:** [DAD08 #70](https://tree.taiga.io/project/rebecamendonca-sie-v2/t/70) — Sprint 5.
**Estado:** exemplos **sintéticos**, reproduzíveis aritmeticamente. **Não** são registros extraídos da Silver, execução da API BE13/BE15, resultados de pytest, homologação ou amostra real.
**Documento principal:** [DAD-08_PROPOSTA_HOMOLOGACAO_METODOLOGIA.md](../../DAD-08_PROPOSTA_HOMOLOGACAO_METODOLOGIA.md).
**Oráculo independente:** [verificar_exemplos_dad08.py](verificar_exemplos_dad08.py) e [RESULTADOS_VERIFICACAO_SINTETICA_DAD08.json](RESULTADOS_VERIFICACAO_SINTETICA_DAD08.json).

## Convenções para os três exemplos

- Considerar uma linha por escola/ano, sem duplicações, erros de identificação ou valores fora de `0`, `1`, `NULL`, exceto nos contrafactuais de integridade explicitamente identificados.
- As redes são os valores cadastrais `Municipal` e `Estadual` usados nos exemplos; o filtro seleciona a população **antes** de calcular contagens e porcentagens.
- Frações mantidas exatas; a apresentação arredonda a duas casas decimais. `NULL` significa resultado indisponível, distinto de 0%.
- BE13 calcula **índice de cada escola e média de índices de comparadoras**; BE15 calcula **presença e cobertura de cada indicador na população municipal**. São grandezas diferentes.
- Os códigos de município e de escola foram omitidos por se tratar de dados hipotéticos; cada exemplo usa um único município fictício e um ano fictício do recorte, salvo estado sem ano com dados indicado.

## E1 — BE15: filtro de rede, presença e cobertura de água potável

Considere o indicador `IN_AGUA_POTAVEL`, município **M**, ano **2025**, e as cinco escolas fictícias abaixo.

| Escola | Rede | `IN_AGUA_POTAVEL` | Interpretação |
|---|---|---:|---|
| A | Municipal | `1` | Possui o recurso |
| B | Municipal | `0` | Não possui o recurso; resposta válida |
| C | Municipal | `NULL` | Não se sabe se possui o recurso |
| D | Estadual | `1` | Possui o recurso |
| E | Estadual | `NULL` | Informação ausente |

### E1.1 — Sem filtro de rede

`T=5` escolas; `a1=2` presentes (A,D); `a0=1` ausente (B); `V=2+1=3` respostas válidas; `NULL=2` (C,E). Conferir `3+2=5`.

- **Presença:** `100 × a1/V = 100 × 2/3 = 66,666...% → 66,67%`.
- **Cobertura:** `100 × V/T = 100 × 3/5 = 60,00%`.
- Não apresentar presença `2/5 = 40%` como se fosse a regra BE15; essa fração mede outra grandeza.

### E1.2 — Filtro `rede_ensino=Municipal`

População = {A,B,C}; `T=3`, `a1=1`, `a0=1`, `V=2`, `NULL=1`.

- Presença `100 × 1/2 = 50,00%`.
- Cobertura `100 × 2/3 = 66,666...% → 66,67%`.

### E1.3 — Filtro `rede_ensino=Estadual`

População = {D,E}; `T=2`, `a1=1`, `a0=0`, `V=1`, `NULL=1`.

- Presença `100 × 1/1 = 100,00%`.
- Cobertura `100 × 1/2 = 50,00%`.

| Seleção | `T` | `a1` | `a0` | `V` | `NULL` | Presença | Cobertura |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas | 5 | 2 | 1 | 3 | 2 | 66,67% | 60,00% |
| Municipal | 3 | 1 | 1 | 2 | 1 | 50,00% | 66,67% |
| Estadual | 2 | 1 | 0 | 1 | 1 | 100,00% | 50,00% |

**Conclusão E1:** o recorte por rede altera os dois denominadores (`V` e `T`). O percentual de presença **não é** cobertura. Nenhuma escola é excluída como “alvo” na BE15; nenhuma escola-alvo existe neste cenário territorial. Os `NULL` não são `0`.

## E2 — BE13: escola-alvo preservada, exclusão individual e média municipal

Considere cinco escolas fictícias no município histórico M no ano **2025** e o conjunto candidato de **17 indicadores**. A escola-alvo E é **Estadual**. Os índices estão definidos pelas respostas válidas de cada escola.

| Escola | Papel | Rede | `1` presentes | `0` ausentes | `NULL` | Indicadores válidos | Índice escolar |
|---|---|---|---:|---:|---:|---:|---:|
| E | Alvo selecionado | Estadual | 12 | 5 | 0 | 17 | `100×12/17 = 70,588...%` |
| A | Comparadora | Municipal | 9 | 6 | 2 | 15 | `100×9/15 = 60,00%` |
| B | Comparadora | Municipal | 17 | 0 | 0 | 17 | `100×17/17 = 100,00%` |
| C | Comparadora | Estadual | 4 | 6 | 7 | 10 | `100×4/10 = 40,00%` |
| D | Comparadora | Municipal | 0 | 0 | 17 | 0 | `NULL`, pois `n=0` |

Os 17 campos de cada escola satisfazem `presentes+ausentes+NULL=17`. `NULL` não reduz artificialmente o índice, mas limita sua comparabilidade, motivo para preservar a cobertura de indicadores no contrato.

### E2.1 — Referência sem filtro de rede

A escola E é removida **antes** da seleção de comparadoras. População de outras escolas = {A,B,C,D}: `T_pares=4`; calculáveis = {A,B,C}: `N_pares=3`.

- Média municipal exata: `R = (60 + 100 + 40) / 3 = 200/3 = 66,666...% → 66,67%`.
- Cobertura dos pares: `100 × 3/4 = 75,00%`.
- Índice da escola E: `100 × 12/17 = 1200/17 = 70,588...% → 70,59%`.
- Diferença **sem arredondamento intermediário**: `1200/17 − 200/3 = 200/51 = 3,921568... pp → +3,92 pp`.

### E2.2 — Referência com filtro `rede_ensino=Municipal`

O filtro é aplicado apenas às comparadoras. E **continua como alvo Estadual**. População de outras escolas municipais = {A,B,D}: `T_pares=3`; calculáveis = {A,B}: `N_pares=2`.

- Média municipal filtrada exata: `R = (60+100)/2 = 80,00%`.
- Cobertura dos pares: `100 × 2/3 = 66,666...% → 66,67%`.
- Índice de E **inalterado**: `1200/17 → 70,59%`.
- Diferença: `1200/17 − 80 = −160/17 = −9,411764... pp → −9,41 pp`.

| Recorte das comparadoras | `T_pares` | `N_pares` | Cobertura pares | Referência | Alvo E | Diferença |
|---|---:|---:|---:|---:|---:|---:|
| Todas as redes | 4 | 3 | 75,00% | 66,67% | 70,59% | +3,92 pp |
| Somente Municipal | 3 | 2 | 66,67% | 80,00% | 70,59% | −9,41 pp |

**Conclusão E2:** a escola-alvo não deve entrar na média do seu município, mas não deixa de existir na própria série por estar fora da rede selecionada para **as comparadoras**. A agregação é média de índices individuais, não a proporção de indicadores presentes somados em todas as escolas.

## E3 — Casos-limite: `T=0`, `N=0`, `N=1`, `V=0` e linha totalmente `NULL`

Este exemplo é uma **coleção de subcenários alternativos e fictícios**, não uma única situação simultânea.

### E3.1 — BE13: escola sozinha no município/ano (`T_pares=0,N_pares=0`)

Alvo E existe e tem índice `12/17=70,59%`, mas depois de excluí-lo não há outras escolas.

- `T_pares=0`, `N_pares=0`.
- Cobertura dos pares = `100×0/0`, **indefinida → `NULL`**.
- Média da referência = `NULL`; diferença = `NULL`.
- O índice da escola E continua calculável: **70,59%**. Não fabricar referência de `0%`.

### E3.2 — BE13: existem três comparadoras, todas com 17 `NULL` (`T_pares=3,N_pares=0`)

- `T_pares=3`, `N_pares=0`.
- Cobertura dos pares = `100×0/3 = 0%`.
- Média = `NULL` (não dividir por zero); diferença = `NULL`.
- A situação **não** é a mesma de E3.1: existem escolas, mas nenhuma tem índice calculável.

### E3.3 — BE13: uma comparadora calculável entre duas (`T_pares=2,N_pares=1`)

- Comparadora A tem `7` presentes, `10` ausentes e `0 NULL`: `I(A)=100×7/17 = 700/17 = 41,176470...% → 41,18%`.
- Comparadora B tem 17 `NULL`: `I(B)=NULL`.
- `T_pares=2`, `N_pares=1`, cobertura dos pares = `100×1/2=50,00%`.
- Média de referência = índice da única comparadora = **41,18%**. **A aritmética é definida, mas o aviso de comparadora única ainda depende de homologação.**

### E3.4 — BE15: município sem escola após recorte (`T=0,V=0`)

Para um indicador e um ano sem escolas da rede selecionada: `T=0`, `a1=0`, `a0=0`, `V=0`, `NULL=0`.

- Presença: `100×0/0`, logo **`NULL`**.
- Cobertura: `100×0/0`, logo **`NULL`**.
- Retornar quantidade de escolas **0**, não percentual 0%.

### E3.5 — BE15: três escolas, todas `NULL` no indicador (`T=3,V=0`)

- `T=3`, `a1=0`, `a0=0`, `V=0`, `NULL=3`.
- Presença: `100×0/0` → **`NULL`**.
- Cobertura: `100×0/3=0,00%`.
- Interpretar como **informação indisponível**, não como inexistência do recurso.

### E3.6 — Escola com 17 indicadores `NULL`

- `n=0`, índice escolar `NULL`; cobertura escolar de indicadores `100×0/17=0%`.
- Não criar índice escolar `0%`; não suprimir, por esse motivo, uma referência automática que tenha outras escolas elegíveis.

| Subcenário | Denominador relevante | Presença / média | Cobertura | Decisão pendente |
|---|---|---|---|---|
| E3.1 BE13 sem pares | `T=0,N=0` | Referência `NULL` | Pares `NULL` | Mensagem de ausência de comparadoras |
| E3.2 BE13 nenhum par válido | `T=3,N=0` | Referência `NULL` | Pares 0% | Mensagem de escolas sem índice |
| E3.3 BE13 uma comparadora | `T=2,N=1` | Média 41,18% | Pares 50% | Aviso/supressão para `N=1` |
| E3.4 BE15 sem escolas | `T=0,V=0` | Presença `NULL` | Indicador `NULL` | Estado vazio por ano |
| E3.5 BE15 só `NULL` | `T=3,V=0` | Presença `NULL` | Indicador 0% | Distinguir zero de indisponibilidade |
| E3.6 Escola 17 `NULL` | `n=0` | Índice `NULL` | Indicadores 0% | Sinalização não bloqueante |

## E4 — Testes de integridade contrafactuais, NÃO aprovados

Os casos abaixo não foram executados contra PostgreSQL e não representam registros constatados. São propostas para testes da BE15, descobertas na inspeção da consulta:

1. **Duas linhas da mesma escola com valores opostos:** `(escola=A, ano=2025, indicador=1)` e `(escola=A, ano=2025, indicador=0)`. Pelo uso de `COUNT(DISTINCT CASE ...)` da BE15, os conjuntos dão `T=1`, `validos=1`, `presentes=1` e presença **100%**. Como existe contraditoriedade no mesmo grão, **esse resultado não pode ser homologado como taxa confiável**. Exigir diagnóstico de duplicidade e política de bloqueio/recuperação.
2. **Valor fora do domínio:** escola A com indicador `2`. A consulta BE15 produziria `T=1,V=0,presentes=0`; o serviço transforma `T−V=1` em `quantidade_sem_dados=1`, apesar de se tratar de **inválido**, não `NULL`. Propor contagem de inválidos separada e tratamento explícito.
3. **Rede sem dimensão correspondente:** o JOIN interno da BE15 e BE13, quando o filtro de rede é informado, pode deixar escola com `TP_DEPENDENCIA` não mapeado fora do agregado. Exigir diagnóstico e política de tratamento antes de afirmar que a população anual está completa.

**Conclusão E4:** testes de robustez e decisões de política são pré-requisitos para homologação irrestrita da integridade; não requerem alteração da fórmula matemática em si. Nenhum cenário foi apresentado como falha observada em produção.

## Execução e independência

O script anexado usa **somente** `fractions.Fraction` da biblioteca-padrão de Python sobre as entradas inventadas neste documento. Foi reexecutado em cópia temporária com Python 3.12.10 fora da `.venv`: **35/35 comparações aprovadas**. O JSON produzido coincidiu byte a byte com o [artefato registrado](RESULTADOS_VERIFICACAO_SINTETICA_DAD08.json) (`SHA-256: 4d4f4668e148701af94280128e6a2761f4c11be4f7049c6b20637ebc53613499`). A gravação do script foi fixada em LF para tornar a reprodução byte a byte estável no Windows. **Dezessete frações/resultados centrais** e a fronteira de 60% também foram conferidos independentemente com aritmética racional. O script não importa módulos SIE, não lê a Silver, não executa SQL e não consulta endpoints. O JSON preserva cada assertiva de entrada/resultado esperado.

**Alcance:** demonstra consistência dos três exemplos e dos casos de fronteira, mas não substitui os testes unitários/integração da BE13/BE15 nem o aceite de Dados, Requisitos, QA ou professor. Os **120 testes** da BE15 foram reportados pela equipe; esta evidência não os reexecutou.

## Fontes de implementação para comparação futura

- [BE13 — PR #21, mudanças e testes](https://github.com/rbecamend/labes-api/pull/21/files).
- [BE15 — repositório no commit 63ce24c](https://github.com/rbecamend/labes-api/blob/63ce24cb527fda69967b7db325b6dec478fb3f6a/app/repositories/infraestrutura_repository.py).
- [BE15 — serviço no commit 63ce24c](https://github.com/rbecamend/labes-api/blob/63ce24cb527fda69967b7db325b6dec478fb3f6a/app/services/infraestrutura_service.py).
- [BE15 — testes do repositório](https://github.com/rbecamend/labes-api/blob/63ce24cb527fda69967b7db325b6dec478fb3f6a/tests/repositories/test_be15_visao_temporal_municipio_sql.py).
- [DAD05 — contrato metodológico](https://github.com/rbecamend/labes-api/blob/feature/SIE-72-sprint5-temporal-infrastructure/docs/analise-temporal-infraestrutura/DAD-05_CONTRATO_METODOLOGICO.md).
