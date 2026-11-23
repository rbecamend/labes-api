-- DAD06 / PostgreSQL / RASCUNHO NÃO EXECUTADO.
-- Somente SELECT. Fonte confirmada no modelo: silver.infraestrutura_comum.
-- Colunas maiúsculas requerem aspas. :co_entidade_alvo e :ano_alvo são parâmetros
-- nomeados do cliente SQL (por exemplo, SQLAlchemy text), não valores literais.
-- Executar Q0 e Q1 antes de interpretar agregados. Q2/Q3 auditam domínio.
-- Executar Q4-Q8 para cada ano 2022, 2023, 2024, 2025, em ambiente controlado.
-- Q8B percorre os quatro anos e municípios; não usa escola-alvo.
-- Resultados com identificadores individuais não devem ser publicados.
-- As consultas retornam razão numeric sem arredondar; arredondar só na apresentação.

-- Q0 — metadados e tipos. Confirmar contra o catálogo antes da execução seguinte.
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'silver'
  AND table_name = 'infraestrutura_comum'
  AND column_name IN (
    'CO_ENTIDADE','NU_ANO_CENSO','CO_MUNICIPIO','NO_MUNICIPIO',
    'IN_AGUA_POTAVEL','IN_ENERGIA_REDE_PUBLICA','IN_ESGOTO_REDE_PUBLICA',
    'IN_LIXO_SERVICO_COLETA','IN_BANHEIRO','IN_BANHEIRO_PNE',
    'IN_BIBLIOTECA','IN_SALA_LEITURA','IN_LABORATORIO_CIENCIAS',
    'IN_LABORATORIO_INFORMATICA','IN_SALA_MULTIUSO',
    'IN_SALA_ATENDIMENTO_ESPECIAL','IN_COZINHA','IN_REFEITORIO',
    'IN_QUADRA_ESPORTES','IN_PATIO_COBERTO','IN_AUDITORIO')
ORDER BY column_name;

-- Q1 — grão, nulos de chave e duplicidades. A linha de ano NULL é diagnóstico
-- separado e NÃO pertence a denominador anual. Grupos e linhas não se confundem.
WITH chaves AS (
  SELECT "NU_ANO_CENSO" AS ano, "CO_ENTIDADE" AS escola, count(*) AS linhas
  FROM silver.infraestrutura_comum
  WHERE "NU_ANO_CENSO" IN (2022,2023,2024,2025)
     OR "NU_ANO_CENSO" IS NULL
  GROUP BY "NU_ANO_CENSO", "CO_ENTIDADE"
)
SELECT ano,
       CASE WHEN ano IS NULL THEN 'ANO_NULO_FORA_DENOMINADOR' ELSE 'ANO_ANUAL' END AS escopo,
       count(*) AS grupos_escola_ano, sum(linhas) AS linhas,
       count(*) FILTER (WHERE escola IS NULL) AS grupos_sem_escola,
       coalesce(sum(linhas) FILTER (WHERE escola IS NULL),0) AS linhas_sem_escola,
       count(*) FILTER (WHERE escola IS NOT NULL AND linhas > 1) AS grupos_duplicados,
       coalesce(sum(linhas - 1) FILTER (WHERE escola IS NOT NULL AND linhas > 1),0) AS linhas_excedentes_duplicadas
FROM chaves GROUP BY ano ORDER BY ano;

-- Q2 — 0/1/NULL/inválido por indicador e ano. Executar Q1 primeiro.
WITH dados AS (
  SELECT i."NU_ANO_CENSO" AS ano, v.indicador, v.valor
  FROM silver.infraestrutura_comum i
  CROSS JOIN LATERAL (VALUES
    ('in_agua_potavel',i."IN_AGUA_POTAVEL"),
    ('in_energia_rede_publica',i."IN_ENERGIA_REDE_PUBLICA"),
    ('in_esgoto_rede_publica',i."IN_ESGOTO_REDE_PUBLICA"),
    ('in_lixo_servico_coleta',i."IN_LIXO_SERVICO_COLETA"),
    ('in_banheiro',i."IN_BANHEIRO"),
    ('in_banheiro_pne',i."IN_BANHEIRO_PNE"),
    ('in_biblioteca',i."IN_BIBLIOTECA"),
    ('in_sala_leitura',i."IN_SALA_LEITURA"),
    ('in_laboratorio_ciencias',i."IN_LABORATORIO_CIENCIAS"),
    ('in_laboratorio_informatica',i."IN_LABORATORIO_INFORMATICA"),
    ('in_sala_multiuso',i."IN_SALA_MULTIUSO"),
    ('in_sala_atendimento_especial',i."IN_SALA_ATENDIMENTO_ESPECIAL"),
    ('in_cozinha',i."IN_COZINHA"),
    ('in_refeitorio',i."IN_REFEITORIO"),
    ('in_quadra_esportes',i."IN_QUADRA_ESPORTES"),
    ('in_patio_coberto',i."IN_PATIO_COBERTO"),
    ('in_auditorio',i."IN_AUDITORIO")
  ) v(indicador,valor)
  WHERE i."NU_ANO_CENSO" IN (2022,2023,2024,2025)
)
SELECT ano, indicador, count(*) AS linhas,
       count(*) FILTER (WHERE valor=1) AS presentes,
       count(*) FILTER (WHERE valor=0) AS ausentes,
       count(*) FILTER (WHERE valor IS NULL) AS sem_dados,
       count(*) FILTER (WHERE valor IS NOT NULL AND valor NOT IN (0,1)) AS invalidos
FROM dados GROUP BY ano, indicador ORDER BY ano, indicador;

-- Q3 — completude por linha escola/ano; a saída é distribuição, sem IDs.
WITH linhas AS (
  SELECT i."NU_ANO_CENSO" AS ano, i."CO_ENTIDADE" AS escola,
         (SELECT count(*) FILTER (WHERE x IN (0,1)) FROM unnest(ARRAY[
           i."IN_AGUA_POTAVEL",i."IN_ENERGIA_REDE_PUBLICA",i."IN_ESGOTO_REDE_PUBLICA",
           i."IN_LIXO_SERVICO_COLETA",i."IN_BANHEIRO",i."IN_BANHEIRO_PNE",
           i."IN_BIBLIOTECA",i."IN_SALA_LEITURA",i."IN_LABORATORIO_CIENCIAS",
           i."IN_LABORATORIO_INFORMATICA",i."IN_SALA_MULTIUSO",
           i."IN_SALA_ATENDIMENTO_ESPECIAL",i."IN_COZINHA",i."IN_REFEITORIO",
           i."IN_QUADRA_ESPORTES",i."IN_PATIO_COBERTO",i."IN_AUDITORIO"
         ]) x) AS validos,
         (SELECT count(*) FILTER (WHERE x IS NOT NULL AND x NOT IN (0,1))
          FROM unnest(ARRAY[
           i."IN_AGUA_POTAVEL",i."IN_ENERGIA_REDE_PUBLICA",i."IN_ESGOTO_REDE_PUBLICA",
           i."IN_LIXO_SERVICO_COLETA",i."IN_BANHEIRO",i."IN_BANHEIRO_PNE",
           i."IN_BIBLIOTECA",i."IN_SALA_LEITURA",i."IN_LABORATORIO_CIENCIAS",
           i."IN_LABORATORIO_INFORMATICA",i."IN_SALA_MULTIUSO",
           i."IN_SALA_ATENDIMENTO_ESPECIAL",i."IN_COZINHA",i."IN_REFEITORIO",
           i."IN_QUADRA_ESPORTES",i."IN_PATIO_COBERTO",i."IN_AUDITORIO"
         ]) x) AS invalidos
  FROM silver.infraestrutura_comum i
  WHERE i."NU_ANO_CENSO" IN (2022,2023,2024,2025)
)
SELECT ano, validos, invalidos, count(*) AS linhas
FROM linhas GROUP BY ano, validos, invalidos ORDER BY ano, validos, invalidos;

-- Q4 — distingue escola inexistente de escola existente fora de 2022–2025.
WITH anos AS (SELECT generate_series(2022,2025) AS ano),
existencia AS (
 SELECT count(*) AS linhas_silver_total
 FROM silver.infraestrutura_comum WHERE "CO_ENTIDADE"=:co_entidade_alvo
)
SELECT a.ano, e.linhas_silver_total>0 AS escola_existe_na_silver,
       e.linhas_silver_total, count(i."CO_ENTIDADE") AS linhas_historicas,
       CASE WHEN e.linhas_silver_total=0 THEN 'ESCOLA_INEXISTENTE'
            WHEN count(i."CO_ENTIDADE")=0 THEN 'SEM_REGISTRO_ANUAL'
            WHEN count(i."CO_ENTIDADE")>1 THEN 'DUPLICIDADE_ALVO'
            ELSE 'REGISTRO_ANUAL' END AS situacao_ano,
       CASE WHEN count(i."CO_ENTIDADE")=1 THEN min(i."CO_MUNICIPIO") END AS co_municipio_historico,
       CASE WHEN count(i."CO_ENTIDADE")=1 THEN min(i."NO_MUNICIPIO") END AS no_municipio_historico
FROM anos a CROSS JOIN existencia e LEFT JOIN silver.infraestrutura_comum i
  ON i."NU_ANO_CENSO"=a.ano AND i."CO_ENTIDADE"=:co_entidade_alvo
GROUP BY a.ano,e.linhas_silver_total ORDER BY a.ano;

-- Q5 — pares do ano e município da linha histórica; resultado interno, sem publicação de IDs.
WITH alvo AS (
 SELECT count(*) AS linhas, min("CO_MUNICIPIO") AS municipio
 FROM silver.infraestrutura_comum
 WHERE "CO_ENTIDADE"=:co_entidade_alvo AND "NU_ANO_CENSO"=:ano_alvo
   AND :ano_alvo IN (2022,2023,2024,2025)
), pares AS (
 SELECT i."CO_ENTIDADE" AS escola, count(*) AS linhas
 FROM silver.infraestrutura_comum i CROSS JOIN alvo a
 WHERE a.linhas=1 AND a.municipio IS NOT NULL
   AND i."NU_ANO_CENSO"=:ano_alvo AND i."CO_MUNICIPIO"=a.municipio
   AND i."CO_ENTIDADE" IS NOT NULL AND i."CO_ENTIDADE"<>:co_entidade_alvo
 GROUP BY i."CO_ENTIDADE"
)
SELECT p.escola, p.linhas, (SELECT linhas FROM alvo) AS linhas_alvo,
       CASE WHEN p.linhas>1 THEN 'duplicado' ELSE 'unico' END AS integridade
FROM pares p ORDER BY p.escola;

-- Q6 — composição municipal. Qualquer duplicidade ou inválido bloqueia as métricas.
WITH alvo AS (
 SELECT count(*) AS linhas, min(i."CO_MUNICIPIO") AS municipio,
        coalesce(sum(av.invalidos),0) AS invalidos_alvo
 FROM silver.infraestrutura_comum i
 CROSS JOIN LATERAL (
  SELECT count(*) FILTER (WHERE x IS NOT NULL AND x NOT IN (0,1)) AS invalidos
  FROM unnest(ARRAY[
   i."IN_AGUA_POTAVEL",i."IN_ENERGIA_REDE_PUBLICA",i."IN_ESGOTO_REDE_PUBLICA",
   i."IN_LIXO_SERVICO_COLETA",i."IN_BANHEIRO",i."IN_BANHEIRO_PNE",
   i."IN_BIBLIOTECA",i."IN_SALA_LEITURA",i."IN_LABORATORIO_CIENCIAS",
   i."IN_LABORATORIO_INFORMATICA",i."IN_SALA_MULTIUSO",i."IN_SALA_ATENDIMENTO_ESPECIAL",
   i."IN_COZINHA",i."IN_REFEITORIO",i."IN_QUADRA_ESPORTES",
   i."IN_PATIO_COBERTO",i."IN_AUDITORIO"
  ]) x
 ) av
 WHERE i."CO_ENTIDADE"=:co_entidade_alvo AND i."NU_ANO_CENSO"=:ano_alvo
   AND :ano_alvo IN (2022,2023,2024,2025)
), base AS (
 SELECT i."CO_ENTIDADE" AS escola, v.indicador, v.valor
 FROM silver.infraestrutura_comum i CROSS JOIN alvo a
 CROSS JOIN LATERAL (VALUES
  ('in_agua_potavel',i."IN_AGUA_POTAVEL"),('in_energia_rede_publica',i."IN_ENERGIA_REDE_PUBLICA"),
  ('in_esgoto_rede_publica',i."IN_ESGOTO_REDE_PUBLICA"),('in_lixo_servico_coleta',i."IN_LIXO_SERVICO_COLETA"),
  ('in_banheiro',i."IN_BANHEIRO"),('in_banheiro_pne',i."IN_BANHEIRO_PNE"),
  ('in_biblioteca',i."IN_BIBLIOTECA"),('in_sala_leitura',i."IN_SALA_LEITURA"),
  ('in_laboratorio_ciencias',i."IN_LABORATORIO_CIENCIAS"),('in_laboratorio_informatica',i."IN_LABORATORIO_INFORMATICA"),
  ('in_sala_multiuso',i."IN_SALA_MULTIUSO"),('in_sala_atendimento_especial',i."IN_SALA_ATENDIMENTO_ESPECIAL"),
  ('in_cozinha',i."IN_COZINHA"),('in_refeitorio',i."IN_REFEITORIO"),
  ('in_quadra_esportes',i."IN_QUADRA_ESPORTES"),('in_patio_coberto',i."IN_PATIO_COBERTO"),
  ('in_auditorio',i."IN_AUDITORIO")
 ) v(indicador,valor)
 WHERE a.linhas=1 AND a.municipio IS NOT NULL AND i."NU_ANO_CENSO"=:ano_alvo
   AND i."CO_MUNICIPIO"=a.municipio AND i."CO_ENTIDADE" IS NOT NULL
   AND i."CO_ENTIDADE"<>:co_entidade_alvo
), duplicadas AS (
 SELECT escola FROM base GROUP BY escola HAVING count(*)<>17
), indicadores AS (
 SELECT unnest(ARRAY[
  'in_agua_potavel','in_energia_rede_publica','in_esgoto_rede_publica',
  'in_lixo_servico_coleta','in_banheiro','in_banheiro_pne','in_biblioteca',
  'in_sala_leitura','in_laboratorio_ciencias','in_laboratorio_informatica',
  'in_sala_multiuso','in_sala_atendimento_especial','in_cozinha',
  'in_refeitorio','in_quadra_esportes','in_patio_coberto','in_auditorio'
 ]) AS indicador
), totais AS (
 SELECT indicador, count(*) AS escolas_referencia,
        count(*) FILTER (WHERE valor=1) AS presentes,
        count(*) FILTER (WHERE valor=0) AS ausentes,
        count(*) FILTER (WHERE valor IS NULL) AS sem_dados,
        count(*) FILTER (WHERE valor IS NOT NULL AND valor NOT IN (0,1)) AS invalidos
 FROM base GROUP BY indicador
), controle AS (
 SELECT coalesce(sum(invalidos),0) AS invalidos_pares
 FROM totais
)
SELECT ids.indicador,
 CASE WHEN a.linhas=0 THEN 'SEM_REGISTRO'
      WHEN a.linhas>1 THEN 'DUPLICIDADE_ALVO'
      WHEN a.municipio IS NULL THEN 'SEM_MUNICIPIO'
      WHEN a.invalidos_alvo>0 THEN 'ALVO_INVALIDO_REVISAO'
      WHEN EXISTS(SELECT 1 FROM duplicadas) OR c.invalidos_pares>0 THEN 'REFERENCIA_AFETADA_REVISAO'
      ELSE 'OK' END AS estado,
 a.invalidos_alvo, c.invalidos_pares, coalesce(t.escolas_referencia,0) AS linhas_pares_diagnostico,
 coalesce(t.presentes,0) AS presentes_diagnostico,
 coalesce(t.ausentes,0) AS ausentes_diagnostico,
 coalesce(t.sem_dados,0) AS sem_dados_diagnostico,
 CASE WHEN a.linhas=1 AND a.municipio IS NOT NULL AND a.invalidos_alvo=0 AND NOT EXISTS(SELECT 1 FROM duplicadas) AND c.invalidos_pares=0 THEN coalesce(t.presentes,0) END AS quantidade_presentes,
 CASE WHEN a.linhas=1 AND a.municipio IS NOT NULL AND a.invalidos_alvo=0 AND NOT EXISTS(SELECT 1 FROM duplicadas) AND c.invalidos_pares=0 THEN coalesce(t.ausentes,0) END AS quantidade_ausentes,
 CASE WHEN a.linhas=1 AND a.municipio IS NOT NULL AND a.invalidos_alvo=0 AND NOT EXISTS(SELECT 1 FROM duplicadas) AND c.invalidos_pares=0 THEN coalesce(t.sem_dados,0) END AS quantidade_sem_dados,
 CASE WHEN a.linhas=1 AND a.municipio IS NOT NULL AND a.invalidos_alvo=0 AND NOT EXISTS(SELECT 1 FROM duplicadas) AND c.invalidos_pares=0 THEN coalesce(t.presentes,0)+coalesce(t.ausentes,0) END AS quantidade_validos,
 CASE WHEN a.linhas=1 AND a.municipio IS NOT NULL AND a.invalidos_alvo=0 AND NOT EXISTS(SELECT 1 FROM duplicadas) AND c.invalidos_pares=0 THEN coalesce(t.escolas_referencia,0) END AS quantidade_escolas_referencia,
 coalesce(t.invalidos,0) AS invalidos_diagnostico,
 CASE WHEN a.linhas=1 AND a.municipio IS NOT NULL AND a.invalidos_alvo=0 AND NOT EXISTS(SELECT 1 FROM duplicadas) AND c.invalidos_pares=0
      THEN 100.0*coalesce(t.presentes,0)/NULLIF(coalesce(t.presentes,0)+coalesce(t.ausentes,0),0) END AS percentual_presentes_exato,
 CASE WHEN a.linhas=1 AND a.municipio IS NOT NULL AND a.invalidos_alvo=0 AND NOT EXISTS(SELECT 1 FROM duplicadas) AND c.invalidos_pares=0
      THEN 100.0*(coalesce(t.presentes,0)+coalesce(t.ausentes,0))/NULLIF(coalesce(t.escolas_referencia,0),0) END AS cobertura_percentual_exata
FROM indicadores ids CROSS JOIN alvo a CROSS JOIN controle c LEFT JOIN totais t ON t.indicador=ids.indicador
ORDER BY ids.indicador;

-- Q7 — média dos índices individuais. A razão de cada escola precede a média.
WITH alvo AS (
 SELECT count(*) AS linhas, min(i."CO_MUNICIPIO") AS municipio,
        coalesce(sum(av.invalidos),0) AS invalidos_alvo
 FROM silver.infraestrutura_comum i
 CROSS JOIN LATERAL (
  SELECT count(*) FILTER (WHERE x IS NOT NULL AND x NOT IN (0,1)) AS invalidos
  FROM unnest(ARRAY[
   i."IN_AGUA_POTAVEL",i."IN_ENERGIA_REDE_PUBLICA",i."IN_ESGOTO_REDE_PUBLICA",
   i."IN_LIXO_SERVICO_COLETA",i."IN_BANHEIRO",i."IN_BANHEIRO_PNE",
   i."IN_BIBLIOTECA",i."IN_SALA_LEITURA",i."IN_LABORATORIO_CIENCIAS",
   i."IN_LABORATORIO_INFORMATICA",i."IN_SALA_MULTIUSO",i."IN_SALA_ATENDIMENTO_ESPECIAL",
   i."IN_COZINHA",i."IN_REFEITORIO",i."IN_QUADRA_ESPORTES",
   i."IN_PATIO_COBERTO",i."IN_AUDITORIO"
  ]) x
 ) av
 WHERE i."CO_ENTIDADE"=:co_entidade_alvo AND i."NU_ANO_CENSO"=:ano_alvo
   AND :ano_alvo IN (2022,2023,2024,2025)
), pares AS (
 SELECT i."CO_ENTIDADE" AS escola, v.valor
 FROM silver.infraestrutura_comum i CROSS JOIN alvo a
 CROSS JOIN LATERAL unnest(ARRAY[
  i."IN_AGUA_POTAVEL",i."IN_ENERGIA_REDE_PUBLICA",i."IN_ESGOTO_REDE_PUBLICA",
  i."IN_LIXO_SERVICO_COLETA",i."IN_BANHEIRO",i."IN_BANHEIRO_PNE",
  i."IN_BIBLIOTECA",i."IN_SALA_LEITURA",i."IN_LABORATORIO_CIENCIAS",
  i."IN_LABORATORIO_INFORMATICA",i."IN_SALA_MULTIUSO",i."IN_SALA_ATENDIMENTO_ESPECIAL",
  i."IN_COZINHA",i."IN_REFEITORIO",i."IN_QUADRA_ESPORTES",
  i."IN_PATIO_COBERTO",i."IN_AUDITORIO"
 ]) v(valor)
 WHERE a.linhas=1 AND a.municipio IS NOT NULL AND i."NU_ANO_CENSO"=:ano_alvo
   AND i."CO_MUNICIPIO"=a.municipio AND i."CO_ENTIDADE" IS NOT NULL
   AND i."CO_ENTIDADE"<>:co_entidade_alvo
), por_escola AS (
 SELECT escola, count(*) AS campos, count(*) FILTER(WHERE valor=1) AS presentes,
        count(*) FILTER(WHERE valor IN (0,1)) AS validos,
        count(*) FILTER(WHERE valor IS NOT NULL AND valor NOT IN (0,1)) AS invalidos
 FROM pares GROUP BY escola
), controle AS (
 SELECT count(*) FILTER(WHERE campos<>17 OR invalidos>0) AS escolas_problematicas,
        count(*) AS denominador_pares,
        count(*) FILTER(WHERE validos>0) AS quantidade_pares_validos
 FROM por_escola
)
SELECT CASE WHEN a.linhas=0 THEN 'SEM_REGISTRO'
            WHEN a.linhas>1 THEN 'DUPLICIDADE_ALVO'
            WHEN a.municipio IS NULL THEN 'SEM_MUNICIPIO'
            WHEN a.invalidos_alvo>0 THEN 'ALVO_INVALIDO_REVISAO'
            WHEN c.escolas_problematicas>0 THEN 'REFERENCIA_AFETADA_REVISAO'
            ELSE 'OK' END AS estado,
 a.invalidos_alvo, c.escolas_problematicas AS escolas_problematicas_diagnostico,
 c.denominador_pares AS pares_diagnostico,
 CASE WHEN a.linhas=1 AND a.municipio IS NOT NULL AND a.invalidos_alvo=0 AND c.escolas_problematicas=0 THEN c.denominador_pares END AS denominador_pares,
 CASE WHEN a.linhas=1 AND a.municipio IS NOT NULL AND a.invalidos_alvo=0 AND c.escolas_problematicas=0 THEN c.quantidade_pares_validos END AS quantidade_pares_validos,
 CASE WHEN a.linhas=1 AND a.municipio IS NOT NULL AND a.invalidos_alvo=0 AND c.escolas_problematicas=0
      THEN 100.0*c.quantidade_pares_validos/NULLIF(c.denominador_pares,0) END AS cobertura_pares_percentual_exata,
 CASE WHEN a.linhas=1 AND a.municipio IS NOT NULL AND a.invalidos_alvo=0 AND c.escolas_problematicas=0
      THEN (SELECT avg(100.0*presentes/NULLIF(validos,0)) FROM por_escola WHERE validos>0)
 END AS media_municipal_percentual_exata
FROM controle c CROSS JOIN alvo a;

-- Q8 — distribuição/sensibilidade do cenário de 60%, por ano e indicador.
-- Reexecutar com cada :ano_alvo; denominadores e comparação são anuais.
WITH alvo AS (
 SELECT count(*) AS linhas, min("CO_MUNICIPIO") AS municipio
 FROM silver.infraestrutura_comum
 WHERE "CO_ENTIDADE"=:co_entidade_alvo AND "NU_ANO_CENSO"=:ano_alvo
   AND :ano_alvo IN (2022,2023,2024,2025)
), base AS (
 SELECT i."CO_ENTIDADE" AS escola, v.indicador, v.valor
 FROM silver.infraestrutura_comum i CROSS JOIN alvo a
 CROSS JOIN LATERAL (VALUES
  ('in_agua_potavel',i."IN_AGUA_POTAVEL"),('in_energia_rede_publica',i."IN_ENERGIA_REDE_PUBLICA"),
  ('in_esgoto_rede_publica',i."IN_ESGOTO_REDE_PUBLICA"),('in_lixo_servico_coleta',i."IN_LIXO_SERVICO_COLETA"),
  ('in_banheiro',i."IN_BANHEIRO"),('in_banheiro_pne',i."IN_BANHEIRO_PNE"),
  ('in_biblioteca',i."IN_BIBLIOTECA"),('in_sala_leitura',i."IN_SALA_LEITURA"),
  ('in_laboratorio_ciencias',i."IN_LABORATORIO_CIENCIAS"),('in_laboratorio_informatica',i."IN_LABORATORIO_INFORMATICA"),
  ('in_sala_multiuso',i."IN_SALA_MULTIUSO"),('in_sala_atendimento_especial',i."IN_SALA_ATENDIMENTO_ESPECIAL"),
  ('in_cozinha',i."IN_COZINHA"),('in_refeitorio',i."IN_REFEITORIO"),
  ('in_quadra_esportes',i."IN_QUADRA_ESPORTES"),('in_patio_coberto',i."IN_PATIO_COBERTO"),
  ('in_auditorio',i."IN_AUDITORIO")
 ) v(indicador,valor)
 WHERE a.linhas=1 AND a.municipio IS NOT NULL AND i."NU_ANO_CENSO"=:ano_alvo
   AND i."CO_MUNICIPIO"=a.municipio AND i."CO_ENTIDADE" IS NOT NULL
   AND i."CO_ENTIDADE"<>:co_entidade_alvo
), controle AS (
 SELECT count(*) FILTER(WHERE campos<>17) AS duplicadas
 FROM (SELECT escola,count(*) AS campos FROM base GROUP BY escola) x
), indicadores AS (
 SELECT unnest(ARRAY[
  'in_agua_potavel','in_energia_rede_publica','in_esgoto_rede_publica',
  'in_lixo_servico_coleta','in_banheiro','in_banheiro_pne','in_biblioteca',
  'in_sala_leitura','in_laboratorio_ciencias','in_laboratorio_informatica',
  'in_sala_multiuso','in_sala_atendimento_especial','in_cozinha',
  'in_refeitorio','in_quadra_esportes','in_patio_coberto','in_auditorio'
 ]) AS indicador
), cobertura_escola AS (
 SELECT count(*) FILTER (WHERE x.valor IN (0,1)) AS validos,
        count(*) FILTER (WHERE x.valor IS NOT NULL AND x.valor NOT IN (0,1)) AS invalidos
 FROM silver.infraestrutura_comum i
 CROSS JOIN LATERAL unnest(ARRAY[
  i."IN_AGUA_POTAVEL",i."IN_ENERGIA_REDE_PUBLICA",i."IN_ESGOTO_REDE_PUBLICA",
  i."IN_LIXO_SERVICO_COLETA",i."IN_BANHEIRO",i."IN_BANHEIRO_PNE",
  i."IN_BIBLIOTECA",i."IN_SALA_LEITURA",i."IN_LABORATORIO_CIENCIAS",
  i."IN_LABORATORIO_INFORMATICA",i."IN_SALA_MULTIUSO",i."IN_SALA_ATENDIMENTO_ESPECIAL",
  i."IN_COZINHA",i."IN_REFEITORIO",i."IN_QUADRA_ESPORTES",
  i."IN_PATIO_COBERTO",i."IN_AUDITORIO"
 ]) x(valor)
 WHERE i."CO_ENTIDADE"=:co_entidade_alvo AND i."NU_ANO_CENSO"=:ano_alvo
   AND :ano_alvo IN (2022,2023,2024,2025)
), por_indicador AS (
 SELECT indicador, count(*) AS total,
        count(*) FILTER(WHERE valor IN (0,1)) AS validos,
        count(*) FILTER(WHERE valor IS NOT NULL AND valor NOT IN (0,1)) AS invalidos
 FROM base GROUP BY indicador
)
SELECT :ano_alvo AS ano, ids.indicador, coalesce(p.total,0) AS denominador,
       coalesce(p.validos,0) AS validos, coalesce(p.invalidos,0) AS invalidos,
       CASE WHEN a.linhas=1 AND ce.invalidos=0 THEN 100.0*ce.validos/17 END AS cobertura_escola_percentual_exata,
       CASE WHEN a.linhas=0 THEN 'SEM_REGISTRO'
            WHEN a.linhas>1 THEN 'DUPLICIDADE_ALVO'
            WHEN ce.invalidos>0 THEN 'ALVO_INVALIDO_REVISAO'
            WHEN 100*ce.validos<60*17 THEN 'ABAIXO_60'
            WHEN 100*ce.validos=60*17 THEN 'IGUAL_60'
            ELSE 'ACIMA_60' END AS faixa_escola_provisoria,
       CASE WHEN a.linhas=0 THEN 'SEM_REGISTRO'
            WHEN a.linhas>1 THEN 'DUPLICIDADE_ALVO'
            WHEN a.municipio IS NULL THEN 'SEM_MUNICIPIO'
            WHEN ce.invalidos>0 THEN 'ALVO_INVALIDO_REVISAO'
            WHEN c.duplicadas>0 OR EXISTS(SELECT 1 FROM por_indicador WHERE invalidos>0) THEN 'REFERENCIA_AFETADA_REVISAO'
            WHEN coalesce(p.total,0)=0 THEN 'SEM_DENOMINADOR'
            WHEN 100*p.validos<60*p.total THEN 'ABAIXO_60'
            WHEN 100*p.validos=60*p.total THEN 'IGUAL_60'
            ELSE 'ACIMA_60' END AS faixa_provisoria,
       CASE WHEN a.linhas=1 AND a.municipio IS NOT NULL AND ce.invalidos=0
                 AND c.duplicadas=0 AND NOT EXISTS(SELECT 1 FROM por_indicador WHERE invalidos>0)
            THEN 100.0*p.validos/NULLIF(p.total,0) END AS cobertura_percentual_exata
FROM indicadores ids CROSS JOIN alvo a CROSS JOIN controle c CROSS JOIN cobertura_escola ce
LEFT JOIN por_indicador p ON p.indicador=ids.indicador ORDER BY ids.indicador;
-- Q8 é um cenário para um alvo; Q8B abaixo mede a distribuição do universo.

-- Q8B — universo por município/ano/indicador, simulando cada escola como alvo
-- e excluindo-a de seus pares. Sem parâmetro de escola. Município/ano com
-- qualquer chave duplicada, escola nula ou valor inválido permanece diagnóstico
-- de integridade: não entra nas faixas de cobertura. A decisão de 60% é pendente.
WITH linhas AS (
 SELECT i."NU_ANO_CENSO" AS ano, i."CO_MUNICIPIO" AS municipio,
        i."CO_ENTIDADE" AS escola, v.indicador, v.valor
 FROM silver.infraestrutura_comum i
 CROSS JOIN LATERAL (VALUES
  ('in_agua_potavel',i."IN_AGUA_POTAVEL"),('in_energia_rede_publica',i."IN_ENERGIA_REDE_PUBLICA"),
  ('in_esgoto_rede_publica',i."IN_ESGOTO_REDE_PUBLICA"),('in_lixo_servico_coleta',i."IN_LIXO_SERVICO_COLETA"),
  ('in_banheiro',i."IN_BANHEIRO"),('in_banheiro_pne',i."IN_BANHEIRO_PNE"),
  ('in_biblioteca',i."IN_BIBLIOTECA"),('in_sala_leitura',i."IN_SALA_LEITURA"),
  ('in_laboratorio_ciencias',i."IN_LABORATORIO_CIENCIAS"),('in_laboratorio_informatica',i."IN_LABORATORIO_INFORMATICA"),
  ('in_sala_multiuso',i."IN_SALA_MULTIUSO"),('in_sala_atendimento_especial',i."IN_SALA_ATENDIMENTO_ESPECIAL"),
  ('in_cozinha',i."IN_COZINHA"),('in_refeitorio',i."IN_REFEITORIO"),
  ('in_quadra_esportes',i."IN_QUADRA_ESPORTES"),('in_patio_coberto',i."IN_PATIO_COBERTO"),
  ('in_auditorio',i."IN_AUDITORIO")
 ) v(indicador,valor)
 WHERE i."NU_ANO_CENSO" IN (2022,2023,2024,2025)
), chaves AS (
 SELECT ano, escola, count(*) AS linhas_chave
 FROM linhas WHERE indicador='in_agua_potavel' AND escola IS NOT NULL
 GROUP BY ano, escola
), base AS (
 SELECT l.*, k.linhas_chave
 FROM linhas l LEFT JOIN chaves k ON k.ano=l.ano AND k.escola=l.escola
), integridade AS (
 SELECT ano, municipio,
        count(*) FILTER (WHERE escola IS NULL) AS campos_sem_escola,
        count(*) FILTER (WHERE linhas_chave>1) AS campos_chave_duplicada,
        count(*) FILTER (WHERE valor IS NOT NULL AND valor NOT IN (0,1)) AS valores_invalidos_grupo
 FROM base GROUP BY ano, municipio
), grupos AS (
 SELECT b.ano,b.municipio,b.indicador,count(*) AS escolas_linhas,
        count(*) FILTER (WHERE b.valor=1) AS presentes,
        count(*) FILTER (WHERE b.valor=0) AS ausentes,
        count(*) FILTER (WHERE b.valor IS NULL) AS sem_dados,
        count(*) FILTER (WHERE b.valor IN (0,1)) AS validos,
        count(*) FILTER (WHERE b.valor IS NOT NULL AND b.valor NOT IN (0,1)) AS invalidos_indicador
 FROM base b GROUP BY b.ano,b.municipio,b.indicador
), candidatos AS (
 SELECT b.ano,b.municipio,b.indicador,b.escola,
        g.escolas_linhas-1 AS denominador_pares,
        g.validos-CASE WHEN b.valor IN (0,1) THEN 1 ELSE 0 END AS validos_pares
 FROM base b JOIN grupos g ON g.ano=b.ano
   AND g.municipio IS NOT DISTINCT FROM b.municipio AND g.indicador=b.indicador
 JOIN integridade it ON it.ano=b.ano AND it.municipio IS NOT DISTINCT FROM b.municipio
 WHERE b.escola IS NOT NULL AND b.linhas_chave=1 AND b.municipio IS NOT NULL
   AND it.campos_sem_escola=0 AND it.campos_chave_duplicada=0
   AND it.valores_invalidos_grupo=0
)
SELECT g.ano,g.municipio,g.indicador,
       g.escolas_linhas AS observacoes_grupo,
       g.presentes,g.ausentes,g.sem_dados,g.validos,g.invalidos_indicador,
       it.campos_sem_escola/17 AS linhas_sem_escola_diagnostico,
       it.campos_chave_duplicada/17 AS linhas_chave_duplicada_diagnostico,
       it.valores_invalidos_grupo,
       CASE WHEN g.municipio IS NULL THEN 'SEM_MUNICIPIO'
            WHEN it.campos_sem_escola>0 OR it.campos_chave_duplicada>0
              OR it.valores_invalidos_grupo>0 THEN 'GRUPO_COM_INTEGRIDADE_PENDENTE'
            ELSE 'APTO_A_ANALISE' END AS estado,
       count(c.escola) AS cenarios_alvo_validos,
       count(c.escola) FILTER (WHERE c.denominador_pares=0) AS sem_pares,
       count(c.escola) FILTER (WHERE c.denominador_pares BETWEEN 1 AND 4) AS denominador_1_a_4,
       count(c.escola) FILTER (WHERE c.denominador_pares>0 AND 100*c.validos_pares<60*c.denominador_pares) AS abaixo_60,
       count(c.escola) FILTER (WHERE c.denominador_pares>0 AND 100*c.validos_pares=60*c.denominador_pares) AS igual_60,
       count(c.escola) FILTER (WHERE c.denominador_pares>0 AND 100*c.validos_pares>60*c.denominador_pares) AS acima_60,
       min(c.denominador_pares) AS menor_denominador_pares,
       max(c.denominador_pares) AS maior_denominador_pares,
       min(100.0*c.validos_pares/NULLIF(c.denominador_pares,0)) AS menor_cobertura_exata,
       max(100.0*c.validos_pares/NULLIF(c.denominador_pares,0)) AS maior_cobertura_exata,
       avg(100.0*c.validos_pares/NULLIF(c.denominador_pares,0)) AS media_cobertura_exata
FROM grupos g JOIN integridade it ON it.ano=g.ano
 AND it.municipio IS NOT DISTINCT FROM g.municipio
LEFT JOIN candidatos c ON c.ano=g.ano
 AND c.municipio IS NOT DISTINCT FROM g.municipio AND c.indicador=g.indicador
GROUP BY g.ano,g.municipio,g.indicador,g.escolas_linhas,g.presentes,g.ausentes,
         g.sem_dados,g.validos,g.invalidos_indicador,it.campos_sem_escola,
         it.campos_chave_duplicada,it.valores_invalidos_grupo
ORDER BY g.ano,g.municipio,g.indicador;
