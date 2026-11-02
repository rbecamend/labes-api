# DAD06 — Manifesto dos CSVs agregados Q8B

**Origem informada:** exportações anteriores da Q8B anual no PostgreSQL 18, banco `sie`, tabela `silver.infraestrutura_comum`, conta `sie_auditoria`; os quatro arquivos foram localizados em `C:\Users\Bragas dev\Downloads` e copiados sem alteração para este diretório. A conferência desta incorporação leu os CSVs locais; não acessou o banco. As condições de sessão, a data e hora da extração e o identificador de snapshot não podem ser comprovados pelos CSVs.

| CSV | SQL correspondente | Ano | Linhas de dados | SHA-256 |
|---|---|---:|---:|---|
| [DAD06_Q8B_2022_otimizada.csv](DAD06_Q8B_2022_otimizada.csv) | [03_q8b_2022_otimizada.sql](03_q8b_2022_otimizada.sql) | 2022 | 374 | `38E02632AF1CBB365B75671D55458F99A99A907BDDDED70ECC47F84404D7F82A` |
| [DAD06_Q8B_2023_otimizada.csv](DAD06_Q8B_2023_otimizada.csv) | [04_q8b_2023_otimizada.sql](04_q8b_2023_otimizada.sql) | 2023 | 374 | `A6120323473AC2DF2DB5FD224CB7399A4569B78547951FEBC7BE2C9AE296ABCF` |
| [DAD06_Q8B_2024_otimizada.csv](DAD06_Q8B_2024_otimizada.csv) | [05_q8b_2024_otimizada.sql](05_q8b_2024_otimizada.sql) | 2024 | 374 | `734CAF3D47EB37D8E1875B3B70D46C6B4B092168EABA6C155D11993FC95FD81C` |
| [DAD06_Q8B_2025_otimizada.csv](DAD06_Q8B_2025_otimizada.csv) | [02_q8b_2025_otimizada.sql](02_q8b_2025_otimizada.sql) | 2025 | 374 | `D1CC8EA8A80EA1F2653922CD447424BA11C1AE9FF3B85622FB484AE4A0AADB08` |

Cada arquivo contém um cabeçalho idêntico e apenas agregados por `(ano, municipio, indicador)`: contagens, diagnósticos de integridade, faixas de cobertura e coberturas exatas. Não há `CO_ENTIDADE`, vetor de uma escola individual, credencial ou configuração de conexão. Os hashes da cópia coincidem com os arquivos encontrados em Downloads. Os 17 indicadores, as 374 chaves anuais únicas e os 22 municípios foram conferidos nos quatro arquivos.

## Reconciliação local

| Ano | Escolas por indicador, somadas entre municípios | Válidas por indicador | Sem dados por indicador | Cenários abaixo de 60% | Iguais a 60% | Acima de 60% | Menor denominador de pares |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 | 3.583 | 3.131 | 452 | 1.428 | 0 | 59.483 | 36 |
| 2023 | 3.396 | 3.138 | 258 | 1.411 | 0 | 56.321 | 37 |
| 2024 | 3.393 | 3.132 | 261 | 1.411 | 0 | 56.270 | 39 |
| 2025 | 3.392 | 3.114 | 278 | 1.394 | 0 | 56.270 | 39 |

As três colunas de cenários contam **município × indicador × escola-alvo simulada**. Cada escola aparece em 17 indicadores; esses totais não são quantidades de escolas distintas. Em cada ano, a soma das três faixas é 17 vezes o total de escolas da primeira coluna. Todas as 1.496 linhas estão em `APTO_A_ANALISE`, com zero diagnósticos de duplicidade, identificador escolar nulo e valor inválido; `sem_pares=0` e `denominador_1_a_4=0` em todas. Para cada linha, foram conferidos `validos=presentes+ausentes`, `observacoes_grupo=validos+sem_dados+invalidos_indicador`, `cenarios_alvo_validos=observacoes_grupo`, a soma das faixas, o denominador de pares `N−1` e as coberturas mínima, máxima e média a partir das frações não arredondadas. Os totais escolares por indicador coincidem com os quantitativos Q1–Q3 informados, mas as saídas originais de Q0–Q3 não integram este manifesto.

## Limites de rastreabilidade

Os CSVs permitem repetir a aritmética agregada e verificar a estrutura das saídas; não demonstram, sozinhos, que foram gerados pelas versões SQL aqui vinculadas, com os controles de sessão declarados, sobre determinado snapshot. Não foram encontrados, junto aos quatro arquivos, log `psql`, plano `EXPLAIN`, horário de execução ou identificador de snapshot. A amostra manual por escola e os resultados separados de Q0–Q8 continuam sem artefatos de execução neste diretório. A classificação por 60% é uma análise de sensibilidade ao limiar informativo confirmado pelo REQ05 para a escola selecionada; não constitui homologação metodológica do valor.
