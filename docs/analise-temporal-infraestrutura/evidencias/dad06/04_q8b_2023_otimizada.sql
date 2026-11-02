-- DAD06 / Q8B isolada / piloto anual 2023 / NÃO EXECUTADA NESTA ETAPA.
-- Somente SELECT. Executar via psql \i dentro de transação
-- REPEATABLE READ READ ONLY com statement_timeout=20s e lock_timeout=5s.
-- Preserva as colunas e a política diagnóstica da Q8B original.
-- Cada linha escola/ano é expandida uma vez em 17 indicadores.
-- Para N escolas e V respostas válidas em um indicador, a exclusão de cada
-- escola-alvo produz V cenários (V-1)/(N-1) e N-V cenários V/(N-1).
-- Todas as comparações com 60 usam inteiros, antes do arredondamento.
WITH escola_ano AS (
 SELECT i."NU_ANO_CENSO",i."CO_MUNICIPIO",i."CO_ENTIDADE",
        i."IN_AGUA_POTAVEL",i."IN_ENERGIA_REDE_PUBLICA",i."IN_ESGOTO_REDE_PUBLICA",
        i."IN_LIXO_SERVICO_COLETA",i."IN_BANHEIRO",i."IN_BANHEIRO_PNE",
        i."IN_BIBLIOTECA",i."IN_SALA_LEITURA",i."IN_LABORATORIO_CIENCIAS",
        i."IN_LABORATORIO_INFORMATICA",i."IN_SALA_MULTIUSO",
        i."IN_SALA_ATENDIMENTO_ESPECIAL",i."IN_COZINHA",i."IN_REFEITORIO",
        i."IN_QUADRA_ESPORTES",i."IN_PATIO_COBERTO",i."IN_AUDITORIO",
        CASE WHEN i."CO_ENTIDADE" IS NOT NULL
             THEN count(*) OVER (PARTITION BY i."NU_ANO_CENSO",i."CO_ENTIDADE")
        END AS linhas_chave
 FROM silver.infraestrutura_comum i
 WHERE i."NU_ANO_CENSO"=2023
), indicadores AS (
 SELECT i."NU_ANO_CENSO" AS ano, i."CO_MUNICIPIO" AS municipio,
        i."CO_ENTIDADE" AS escola, i.linhas_chave, v.indicador, v.valor
 FROM escola_ano i
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
), agregados AS (
 SELECT ano,municipio,indicador,
        count(*) AS escolas_linhas,
        count(*) FILTER (WHERE valor=1) AS presentes,
        count(*) FILTER (WHERE valor=0) AS ausentes,
        count(*) FILTER (WHERE valor IS NULL) AS sem_dados,
        count(*) FILTER (WHERE valor IN (0,1)) AS validos,
        count(*) FILTER (WHERE valor IS NOT NULL AND valor NOT IN (0,1)) AS invalidos_indicador,
        count(*) FILTER (WHERE escola IS NULL) AS linhas_sem_escola_diagnostico,
        count(*) FILTER (WHERE linhas_chave>1) AS linhas_chave_duplicada_diagnostico
 FROM indicadores
 GROUP BY ano,municipio,indicador
), grupos AS (
 SELECT a.*,
        sum(invalidos_indicador) OVER (PARTITION BY ano,municipio) AS valores_invalidos_grupo
 FROM agregados a
), calculo AS (
 SELECT g.*,
        CASE WHEN municipio IS NULL THEN 'SEM_MUNICIPIO'
             WHEN linhas_sem_escola_diagnostico>0 OR linhas_chave_duplicada_diagnostico>0
               OR valores_invalidos_grupo>0 THEN 'GRUPO_COM_INTEGRIDADE_PENDENTE'
             ELSE 'APTO_A_ANALISE' END AS estado
 FROM grupos g
)
SELECT ano,municipio,indicador,
       escolas_linhas AS observacoes_grupo,
       presentes,ausentes,sem_dados,validos,invalidos_indicador,
       linhas_sem_escola_diagnostico,linhas_chave_duplicada_diagnostico,
       valores_invalidos_grupo,estado,
       CASE WHEN estado='APTO_A_ANALISE' THEN escolas_linhas ELSE 0 END AS cenarios_alvo_validos,
       CASE WHEN estado='APTO_A_ANALISE' AND escolas_linhas=1 THEN 1 ELSE 0 END AS sem_pares,
       CASE WHEN estado='APTO_A_ANALISE' AND escolas_linhas BETWEEN 2 AND 5
            THEN escolas_linhas ELSE 0 END AS denominador_1_a_4,
       CASE WHEN estado='APTO_A_ANALISE' AND escolas_linhas>1 THEN
         (CASE WHEN 100*(validos-1)<60*(escolas_linhas-1) THEN validos ELSE 0 END)
         +(CASE WHEN 100*validos<60*(escolas_linhas-1) THEN escolas_linhas-validos ELSE 0 END)
         ELSE 0 END AS abaixo_60,
       CASE WHEN estado='APTO_A_ANALISE' AND escolas_linhas>1 THEN
         (CASE WHEN 100*(validos-1)=60*(escolas_linhas-1) THEN validos ELSE 0 END)
         +(CASE WHEN 100*validos=60*(escolas_linhas-1) THEN escolas_linhas-validos ELSE 0 END)
         ELSE 0 END AS igual_60,
       CASE WHEN estado='APTO_A_ANALISE' AND escolas_linhas>1 THEN
         (CASE WHEN 100*(validos-1)>60*(escolas_linhas-1) THEN validos ELSE 0 END)
         +(CASE WHEN 100*validos>60*(escolas_linhas-1) THEN escolas_linhas-validos ELSE 0 END)
         ELSE 0 END AS acima_60,
       CASE WHEN estado='APTO_A_ANALISE' THEN escolas_linhas-1 END AS menor_denominador_pares,
       CASE WHEN estado='APTO_A_ANALISE' THEN escolas_linhas-1 END AS maior_denominador_pares,
       CASE WHEN estado='APTO_A_ANALISE' AND escolas_linhas>1 THEN
         CASE WHEN validos>0 THEN 100.0*(validos-1)/(escolas_linhas-1)
              ELSE 100.0*validos/(escolas_linhas-1) END END AS menor_cobertura_exata,
       CASE WHEN estado='APTO_A_ANALISE' AND escolas_linhas>1 THEN
         CASE WHEN escolas_linhas-validos>0 THEN 100.0*validos/(escolas_linhas-1)
              ELSE 100.0*(validos-1)/(escolas_linhas-1) END END AS maior_cobertura_exata,
       CASE WHEN estado='APTO_A_ANALISE' AND escolas_linhas>1 THEN
         100.0*(validos*(validos-1)+(escolas_linhas-validos)*validos)
         /NULLIF(escolas_linhas*(escolas_linhas-1),0) END AS media_cobertura_exata
FROM calculo
ORDER BY ano,municipio,indicador;
