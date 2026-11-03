# DAD06 — Complementação da amostra manual: Porto de Moz, 2025

## Identificação e proveniência

| Campo | Registro |
|---|---|
| Fonte recontada | PostgreSQL local, banco `sie`, tabela `silver.infraestrutura_comum` |
| Recorte | `NU_ANO_CENSO=2025`, `CO_MUNICIPIO=1505908` (Porto de Moz), `IN_AGUA_POTAVEL` |
| Grão | Agregado municipal do indicador, **antes** da exclusão de qualquer escola-alvo |
| Execução bem-sucedida | 2026-11-02, início 21:46:01 e fim 21:46:02, horário local `-03:00` |
| Cliente e conta | `psql` no contêiner `sie-postgres`, usuário `sie_auditoria`, sem credenciais expostas |
| Controles | `REPEATABLE READ READ ONLY`, `statement_timeout='20s'`, `lock_timeout='5s'`, `ON_ERROR_STOP=1`; transação encerrada com `COMMIT` somente leitura |
| Arquivo confrontado | [CSV Q8B 2025](DAD06_Q8B_2025_otimizada.csv), chave `(2025,1505908,in_agua_potavel)` |
| Integridade do CSV | SHA-256 `D1CC8EA8A80EA1F2653922CD447424BA11C1AE9FF3B85622FB484AE4A0AADB08`, igual ao [manifesto](MANIFESTO_EVIDENCIAS_Q8B.md) |

Antes da recontagem, `\d silver.infraestrutura_comum` confirmou `CO_MUNICIPIO`, `NU_ANO_CENSO`, `CO_ENTIDADE` e `IN_AGUA_POTAVEL` como `integer`. `\du sie_auditoria` não mostrou atributos especiais; `\dp silver.infraestrutura_comum` mostrou `sie_auditoria=r/sie` na tabela. A conexão usou `-U sie_auditoria -d sie -w -X`; não se leu `.env` nem se exibiu segredo.

Uma tentativa inicial em 2026-11-02 às 21:45:43 `-03:00` falhou antes de retornar dados: a passagem do SQL como argumento do PowerShell retirou as aspas dos identificadores e o PostgreSQL respondeu `column "nu_ano_censo" does not exist`. A sessão encerrou sem escrita. A execução bem-sucedida enviou o mesmo SELECT pela entrada padrão do `psql`, preservando os identificadores. Seu código de saída foi zero e a saída confirmou `BEGIN`, os dois `SET` e `COMMIT`.

## SELECT executado

```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
SET LOCAL statement_timeout = '20s';
SET LOCAL lock_timeout = '5s';

SELECT
    "NU_ANO_CENSO" AS ano,
    "CO_MUNICIPIO" AS municipio,
    COUNT(*) AS observacoes,
    COUNT(DISTINCT "CO_ENTIDADE") AS escolas_distintas,
    COUNT(*) FILTER (WHERE "IN_AGUA_POTAVEL" = 1) AS presentes,
    COUNT(*) FILTER (WHERE "IN_AGUA_POTAVEL" = 0) AS ausentes,
    COUNT(*) FILTER (WHERE "IN_AGUA_POTAVEL" IS NULL) AS sem_dados,
    COUNT(*) FILTER (WHERE "IN_AGUA_POTAVEL" IN (0, 1)) AS validos,
    COUNT(*) FILTER (
        WHERE "IN_AGUA_POTAVEL" IS NOT NULL
          AND "IN_AGUA_POTAVEL" NOT IN (0, 1)
    ) AS invalidos,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE "IN_AGUA_POTAVEL" = 1)
        / NULLIF(COUNT(*) FILTER (WHERE "IN_AGUA_POTAVEL" IN (0, 1)), 0), 2
    ) AS percentual_presentes,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE "IN_AGUA_POTAVEL" IN (0, 1))
        / NULLIF(COUNT(*), 0), 2
    ) AS cobertura_percentual
FROM silver.infraestrutura_comum
WHERE "NU_ANO_CENSO" = 2025
  AND "CO_MUNICIPIO" = 1505908
GROUP BY "NU_ANO_CENSO", "CO_MUNICIPIO";

COMMIT;
```

## Resultado agregado e reconciliação

| Medida | SELECT independente na Silver | CSV Q8B versionado |
|---|---:|---:|
| Linhas do resultado para a chave | 1 | 1 |
| Observações / escolas | 105 observações; 105 escolas distintas | 105 observações do grupo; o CSV não traz identificadores individuais |
| Presentes (`1`) | 53 | 53 |
| Ausentes (`0`) | 49 | 49 |
| Sem dados (`NULL`) | 3 | 3 |
| Válidos (`0` ou `1`) | 102 | 102 |
| Inválidos | 0 | 0 |
| Presença do indicador | 51,96% após arredondamento | `100 × 53/102 = 51,960784…%` calculado das contagens |
| Cobertura do indicador | 97,14% após arredondamento | `100 × 102/105 = 97,142857…%` calculado das contagens |

Conferências: `53+49=102` válidos; `102+3+0=105` observações; `COUNT(DISTINCT CO_ENTIDADE)=COUNT(*)=105` **neste recorte**. Presença usa somente o denominador válido: `100 × 53/102 = 51,960784313725…%`. Cobertura usa todas as escolas observadas: `100 × 102/105 = 97,142857142857…%`. `0` é ausência de infraestrutura e permanece no denominador da presença; `NULL` é ausência de informação e fica fora dele. A coincidência foi obtida sem ajustar os valores esperados.

O campo `media_cobertura_exata` da Q8B registra a **média das coberturas após exclusão simulada de cada alvo**; seu valor `97.1428571428571429` coincide numericamente com a cobertura do agregado municipal neste caso. Os conceitos e denominadores de cada cenário, porém, permanecem distintos. A recontagem não reconstrói os pares, a média dos índices escolares nem a exclusão de uma escola-alvo específica.

## Limitações

O CSV não contém horário de exportação, identificador de snapshot nem log `psql`. A igualdade com a consulta atual demonstra reprodução do agregado consultado, **não** identidade entre os snapshots da exportação e da recontagem. Esta é uma amostra de **um indicador, município e ano**; os demais estratos, 17 indicadores por escola e cenários de integridade do plano manual continuam pendentes. Não há registro escolar individual nem credencial neste artefato.
