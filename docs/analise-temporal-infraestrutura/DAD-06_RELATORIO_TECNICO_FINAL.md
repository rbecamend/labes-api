# DAD06 — Relatório técnico de consolidação da auditoria

**Atividade:** Sprint 4 do SIE v2, comparação temporal de infraestrutura Escola × Município.
**Estado:** consolidação documental revisada tecnicamente; auditoria empírica reportada, sem homologação metodológica.
**Autor da entrega documental:** Filipe Braga de Menezes.
**Revisão e aprovação:** Rebeca Mendonça, revisão técnica documental em 02/11/2026. A aprovação metodológica permanece pendente.
**Worktree/branch da entrega original:** `labes-api-sie30-dad06` / `docs/DAD06-denominadores-indicadores`.
**Worktree/branch da complementação:** `labes-api-sie54-dad06-complemento` / `docs/DAD06-complemento-amostra-manual`.
**Fonte de dados declarada:** PostgreSQL 18, `silver.infraestrutura_comum`, conta `sie_auditoria`.

## 1. Objetivo e alcance do parecer

Consolidar as regras dos denominadores, as execuções Q0–Q8 e Q8B informadas para 2022–2025, as reconciliações comunicadas e os limites de rastreabilidade antes da revisão final da DAD06. A consolidação inicial não acessou PostgreSQL; esta complementação executou **um SELECT agregado** para conferir Porto de Moz, 2025, e `IN_AGUA_POTAVEL`. Isso não substitui a homologação semântica dos indicadores. O limiar informativo de 60% e seu escopo foram definidos pelo REQ05; esta auditoria avalia sua aplicação empírica, sem alterar a regra de negócio.

Os quatro CSVs originais Q8B foram localizados em Downloads, conferidos e incorporados ao worktree. As saídas separadas Q0–Q8 continuam ausentes. Assim, **“reportado”** significa informação recebida no pedido de consolidação; **“conferido neste worktree”** significa algo verificável nos arquivos locais; **“recontado na Silver”** aplica-se exclusivamente à combinação documentada nesta complementação. A coincidência com uma tabela histórica da DAD01 é uma comparação documental, não uma segunda execução independente.

## 2. Ambiente e controles de execução informados

A auditoria anterior foi comunicada como realizada no PostgreSQL 18 com a conta `sie_auditoria`, transações `REPEATABLE READ READ ONLY` e controles de timeout. A Q8B original completou o piloto; a tentativa conjunta 2022–2025 foi cancelada pelo servidor com `canceling statement due to statement timeout` sob limite de 20 segundos. Foram então usadas versões algébricas anuais. Não há log, horário, identificador de snapshot, valores de `statement_timeout` e `lock_timeout` de cada **exportação Q8B anterior**, nem plano `EXPLAIN` desses arquivos. A recontagem agregada desta complementação tem horário, controles de sessão e privilégio de leitura da tabela registrados em [evidência própria](evidencias/dad06/06_amostra_manual_porto_de_moz_2025.md); não supre os metadados das exportações anteriores.

O cancelamento por timeout é fato reportado. A ampliação para 17 linhas por observação e o reaproveitamento do conjunto expandido por CTEs, junções e agrupamentos da Q8B original são explicação de custo **hipotética**, sem plano de execução local para atribuir tempo a um operador. A versão anual calcula os cenários de exclusão de forma algébrica, após agrupar por ano, município e indicador; seus CSVs foram reconciliados localmente. O SELECT novo confere somente um agregado municipal e não reexecuta Q8B.

## 3. Fontes e inventário das evidências

| Fonte | Presença no worktree | Papel e limite |
|---|---|---|
| [Documento metodológico DAD06](DAD-06_DENOMINADORES_E_AMOSTRA_VALIDACAO.md) | Sim | Regras, fórmulas, resultados reportados e pendências. |
| [Q0–Q8B original](evidencias/dad06/01_consultas_select.sql) | Sim | Código das consultas; não é saída de execução. |
| [Q8B anual 2025](evidencias/dad06/02_q8b_2025_otimizada.sql) | Sim | Código da versão algébrica. |
| [Q8B anual 2022](evidencias/dad06/03_q8b_2022_otimizada.sql), [2023](evidencias/dad06/04_q8b_2023_otimizada.sql), [2024](evidencias/dad06/05_q8b_2024_otimizada.sql) | Sim | Códigos anuais, com o filtro temporal correspondente. |
| [Manifesto e CSVs Q8B 2022–2025](evidencias/dad06/MANIFESTO_EVIDENCIAS_Q8B.md) | Quatro CSVs presentes | Saídas agregadas conferidas; 374 linhas por ano, hashes e reconciliações no manifesto. Não comprovam sozinhos a sessão de origem. |
| [Amostra agregada independente, Porto de Moz 2025](evidencias/dad06/06_amostra_manual_porto_de_moz_2025.md) | Sim | SELECT na Silver, contagens e fórmulas de um indicador; não confere exclusão individual nem snapshot da exportação Q8B. |
| CSVs/saídas separados Q0–Q3 e Q4–Q8 | Não localizados | Resultados respectivos permanecem reportados; faltam as saídas para rechecagem direta. |
| Logs, planos `EXPLAIN`, data/hora e snapshot das exportações Q8B anteriores | Não localizados | Limite de rastreabilidade dessas exportações; a recontagem nova tem horário próprio. |
| [DAD01](DAD-01_AUDITORIA_E_HOMOLOGACAO.md), [DAD02](DAD-02_MATRIZ_COMPARABILIDADE_TEMPORAL.md), [DAD05](DAD-05_CONTRATO_METODOLOGICO.md) | Sim | Evidência histórica e regras condicionais; não são saídas desta auditoria. |

Os quatro CSVs de nome `DAD06_Q8B_<ano>_otimizada.csv` foram encontrados na pasta Downloads do usuário Windows, lidos em modo somente leitura e copiados para `evidencias/dad06/`, sem alterar os SQLs. Os arquivos contêm somente agregados por ano, município e indicador, sem identificador escolar ou credencial. Os hashes da cópia coincidem com os das fontes locais. O [manifesto](evidencias/dad06/MANIFESTO_EVIDENCIAS_Q8B.md) relaciona cada CSV ao SQL anual, ao ano e às contagens e explicita que a origem PostgreSQL é informada, sem log, data/hora ou snapshot capturado. Dados individuais devem ficar em armazenamento controlado fora do Git.

## 4. Método: denominadores, integridade e amostra

O conjunto candidato tem 17 indicadores presentes nos SQLs e listados no documento metodológico. `1` indica presença; `0`, ausência do recurso; `NULL`, informação indisponível, fora do denominador válido. Valor não nulo fora de `0/1` é inválido. Para escola `e` no ano `y`, seu índice é `100 × indicadores iguais a 1 / indicadores iguais a 0 ou 1`, quando o denominador é positivo. O MVP não aplica corte mínimo de cobertura.

O município de referência é `CO_MUNICIPIO` da linha histórica de `e` em `y`. A escola-alvo é excluída. Para indicador `i`, presença municipal é `100 × pares com i=1 / pares com i∈{0,1}`; cobertura é `100 × pares com i∈{0,1} / total de outras escolas`. A média municipal da DAD05 é a média aritmética dos **índices individuais** das outras escolas calculáveis, com peso igual por escola. A presença agregada de um indicador e essa média não são intercambiáveis. Denominador zero gera percentual indisponível, não 0%.

Q1 verifica unicidade e chaves antes das agregações; Q2 separa `0/1/NULL/inválido`; Q3 mede completude. Q6–Q8B preservam diagnóstico de duplicidade, identificador nulo e valor inválido, sem tratá-los como exclusões silenciosas. As versões Q8B anuais simulam cada alvo por `N` escolas e `V` respostas válidas: `(V−1)/(N−1)` para alvo com resposta válida e `V/(N−1)` para alvo `NULL`. Casos `N≤1` não recebem cobertura calculada. A política pública para anomalias continua pendente.

A amostra planejada usa ordenação determinística por ano, município e escola dentro de estratos de completude e cobertura. A execução comunicada inclui uma escola-piloto com histórico único em Porto de Moz; os CSVs Q8B cobrem 22 municípios por ano. Não há manifesto da **amostra manual**, vetores dos 17 indicadores ou registros da conferência individual para afirmar que estratos de lacuna anual, escola inexistente, comparadora única ou ausência de pares foram testados.

## 5. Q0–Q3: resultados anuais reportados

Q0 confirmou, conforme o relato, tabela e 17 colunas. Q1 reportou zero duplicidades escola/ano e zero chaves escolares nulas no período; não foi fornecida a contagem diagnóstica de linhas com ano nulo. Q2 reportou apenas `0`, `1` e `NULL` nos 17 indicadores. Q3 reportou apenas linhas completas ou totalmente nulas:

| Ano | Registros | 17 válidos | 17 `NULL` | Completude derivada |
|---:|---:|---:|---:|---:|
| 2022 | 3.583 | 3.131 | 452 | 87,38% |
| 2023 | 3.396 | 3.138 | 258 | 92,40% |
| 2024 | 3.393 | 3.132 | 261 | 92,31% |
| 2025 | 3.392 | 3.114 | 278 | 91,80% |
| **Total** | **13.764** | **12.515** | **1.249** | **90,93%** |

As somas internas são coerentes: completos + totalmente nulos = registros em cada ano e no total. A taxa total é `100 × 12.515/13.764 = 90,93%` após arredondamento a duas casas. Em cada ano, as somas de `observacoes_grupo`, `validos` e `sem_dados` dos CSVs Q8B, feitas para **cada** indicador entre os 22 municípios, coincidem com os totais desta tabela. Os quantitativos também coincidem com os registrados anteriormente na DAD01. A matriz Q2 completa e a saída Q0 com tipos não estão disponíveis para rechecagem nesta revisão.

## 6. Q4–Q8: cenário piloto reportado

Uma escola-piloto em Porto de Moz (`1505908`) teve histórico único nos quatro anos, segundo o relato. Seu identificador individual não é reproduzido neste relatório. Para 2025 foram informadas 104 escolas comparadoras, das quais 101 com informações válidas e três sem informações. A cobertura de pares calculada desses totais é `100 × 101/104 = 97,115384615…%`, compatível com 97,115385% reportados. O CSV Q8B de 2025 contém `N=105`, `V=102` e três `NULL` por indicador nesse município, compatíveis com a exclusão de um alvo válido, mas não identifica qual escola foi usada no piloto. A média simples dos índices individuais foi reportada como 26,732673%; não é possível recalculá-la sem os índices ou vetores das comparadoras.

Q4–Q8 foram relatadas como validadas nesse piloto, incluindo município histórico, exclusão do alvo e denominadores. As saídas separadas de Q4, Q5, Q6, Q7 e Q8 não constam do worktree. Não se infere deste piloto a validação empírica de escola inexistente, histórico lacunar, `N=0`, `N=1`, duplicidade ou valor inválido.

### Complementação da amostra manual — Porto de Moz, 2025

Em 2026-11-02, uma recontagem independente por `SELECT` na `silver.infraestrutura_comum`, com a conta `sie_auditoria` e transação `REPEATABLE READ READ ONLY`, retornou uma linha agregada para o município `1505908` e `IN_AGUA_POTAVEL` em 2025. O [registro da evidência](evidencias/dad06/06_amostra_manual_porto_de_moz_2025.md) conserva a consulta, horário, timeouts, conferência de privilégio de leitura, saída e comparação com a linha do [CSV Q8B 2025](evidencias/dad06/DAD06_Q8B_2025_otimizada.csv).

| Ano | Município | Indicador | Escolas distintas | Presentes (`1`) | Ausentes (`0`) | Sem dados (`NULL`) | Válidos | Inválidos | Presença | Cobertura |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | Porto de Moz (`1505908`) | `IN_AGUA_POTAVEL` | 105 | 53 | 49 | 3 | 102 | 0 | `100 × 53/102 = 51,960784…%` (51,96%) | `100 × 102/105 = 97,142857…%` (97,14%) |

`53+49=102` e `102+3=105`. A presença divide os 53 casos com infraestrutura pelos 102 casos válidos; a cobertura divide os 102 válidos pelas 105 escolas observadas. As contagens coincidem com o CSV versionado. Esta amostra é o **agregado municipal antes da exclusão de qualquer escola-alvo**; portanto, não substitui o piloto de 104 pares, não recalcula a média de índices individuais e não cobre os demais estratos manuais. O snapshot do CSV anterior é desconhecido, ainda que seu agregado coincida com a Silver no momento desta recontagem.

## 7. Q8B: comparação temporal e sensibilidade a 60%

Os quatro CSVs Q8B anuais foram conferidos: cada um tem 22 municípios e 17 indicadores por município, ou 374 combinações com chave `(ano, municipio, indicador)` única. Os cabeçalhos e o conjunto de 17 indicadores são idênticos. Em cada linha, `presentes+ausentes=validos`, `validos+sem_dados+invalidos_indicador=observacoes_grupo`, a soma das três faixas é `cenarios_alvo_validos=observacoes_grupo`, o denominador de pares é `N−1` e as coberturas mínima, máxima e média conferem com as frações exatas. Todas as 1.496 linhas têm estado `APTO_A_ANALISE`, sem diagnóstico de duplicidade, chave escolar nula ou valor inválido.

| Ano | Cenários abaixo de 60% | Iguais a 60% | Acima de 60% | Sem pares | Denominador de 1 a 4 | Menor denominador de pares |
|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 1.428 | 0 | 59.483 | 0 | 0 | 36 |
| 2023 | 1.411 | 0 | 56.321 | 0 | 0 | 37 |
| 2024 | 1.411 | 0 | 56.270 | 0 | 0 | 39 |
| 2025 | 1.394 | 0 | 56.270 | 0 | 0 | 39 |

Cada cenário é uma combinação município × indicador × escola-alvo simulada; uma escola é contada em 17 indicadores, não como escola única. As faixas somam 17 vezes o total anual de escolas. Foi observado um município com média simulada abaixo de 60% e 21 acima em cada ano, sem cenário igual a 60%; não houve grupos sem pares nem denominadores de 1 a 4 nesse recorte. Isso não substitui a amostra manual de escolas nem resolve a política para denominador zero.

O município `1503804` foi conferido abaixo de 60% nos quatro CSVs, conforme as médias simuladas a duas casas:

| Ano | Cobertura média simulada conferida | Relação com o limiar provisório |
|---:|---:|---|
| 2022 | 57,14% | Abaixo |
| 2023 | 56,63% | Abaixo |
| 2024 | 55,42% | Abaixo |
| 2025 | 53,66% | Abaixo |

A mudança entre os extremos arredondados é de −3,48 pontos percentuais. É uma diferença descritiva; a causa não foi verificada. Os CSVs mostram a distribuição agregada dos cenários desse município, sem substituir a conferência manual de suas escolas. A completude global de Q0–Q3 usa todas as escolas de cada ano e não substitui a cobertura municipal por indicador **excluindo cada escola-alvo**. A persistência conferida desse município sustenta investigar o alerta, mas não homologa 60% nem demonstra que seja o melhor valor.

## 8. Problemas, limites e decisões abertas

- **Rastreabilidade:** os CSVs Q8B e hashes permitem conferir seus 374 agregados anuais. Faltam saídas separadas Q0–Q8, logs, snapshots, parâmetros capturados e planos das exportações anteriores; não se comprovou operacionalmente a sessão de extração. A recontagem nova tem parâmetros e horário próprios.
- **Semântica:** DAD02 documenta consistência de dicionário dos 17 candidatos; aplicabilidade, linhagem da Silver e homologação semântica de `S` permanecem pendentes.
- **Origem e população:** DAD01 permanece não homologada; ETL original e causa das 1.249 linhas totalmente nulas não estão demonstrados. Os 22 municípios são recorte intencional reportado, não cobertura estadual. A regra operacional de elegibilidade territorial ainda precisa de confirmação.
- **Integridade futura:** ausência de duplicatas/inválidos no resumo atual não estabelece garantia da carga. BE09 precisa de regra pública para anomalias, grupos sem denominador válido e indicadores indisponíveis.
- **Limiar:** REQ05, a wiki da Sprint 4 e a BE09 estão conciliados em `60%`, somente para a escola selecionada e sem bloqueio do resultado. A Q8B não encontrou cenário exatamente igual a 60%, que permanece pendente de teste sintético.
- **Amostra:** um agregado de indicador/município/ano foi recontado na Silver; manifesto da seleção manual **por escola**, exclusão individual e casos-limite além do piloto não estão comprovados localmente. Nomes e resultados de arquivos privados de outras sessões não são inferidos.

## 9. Parecer técnico e encaminhamento

| Dimensão | Parecer |
|---|---|
| Auditoria empírica | **Reportada como executada e tecnicamente consistente** nos cenários anteriores descritos. A consolidação conferiu os quatro CSVs Q8B e suas fórmulas; esta complementação recontou **um agregado** diretamente na Silver, com resultado coincidente. Saídas separadas Q0–Q8, exclusão individual e os demais estratos manuais não foram auditados nesta revisão. |
| Entrega documental | **Revisada tecnicamente e complementada para nova revisão.** Método, SQLs, quatro CSVs Q8B, manifesto, evidência da recontagem e lacunas estão identificados; metadados das exportações anteriores e amostra manual por escola ainda faltam. |
| Aprovação metodológica | **Pendente.** Conjunto dos 17 indicadores, universo territorial, tratamento público da integridade, denominador zero e autorização de publicação exigem decisão dos responsáveis. O limiar informativo permanece conforme REQ05 e BE09. |

Recomenda-se localizar as saídas separadas Q0–Q8, recuperar metadados das exportações anteriores quando possível e completar a amostra manual por escola, sem atribuir ao agregado aqui recontado a validação desses cenários. A PR #14 foi mesclada em `e1f90df`; a branch desta complementação parte da versão atual de `equipe/feature/SIE-54-sprint4-infrastructure-composition`. Esta complementação não realizou commit, push ou nova PR e não declara a DAD06 homologada.
