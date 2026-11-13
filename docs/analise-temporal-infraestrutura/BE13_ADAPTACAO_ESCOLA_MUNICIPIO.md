# BE13 — Adaptar análise Escola × Município

## Endpoint

`GET /infraestrutura/analise-temporal/escolas/{co_entidade}/comparacao-municipio`

## Parâmetros

- `rede_ensino`: opcional e repetível; valores `Federal`, `Estadual`, `Municipal` e `Privada`. Restringe **as escolas de referência**. A escola consultada permanece como alvo, independentemente da rede selecionada.
- `ano_inicio`: ano inicial do recorte (padrão 2022).
- `ano_fim`: ano final do recorte (padrão 2025). A diferença entre `ano_fim` e `ano_inicio` deve ser de pelo menos dois anos completos.

A validação de intervalo é aplicada tanto na rota quanto no serviço.

## Anos da série

O repositório consulta os anos distintos efetivamente disponíveis em `silver.infraestrutura_comum` dentro do intervalo. A resposta lista esses anos em `data.metodologia.anos` e produz um ponto para cada ano disponível. Se um ano existe na fonte, mas a escola selecionada não tem observação nele, o ponto conserva `situacao = escola_sem_dados`, `registro_historico_disponivel = false` e `quantidade_indicadores_presentes = 0`.

## Filtro da rede de referência

O filtro é aplicado à consulta de pares, via `gold.dim_tp_dependencia.no_tp_dependencia`. Sem `rede_ensino`, todas as redes são consideradas. Os dados históricos da escola selecionada não são filtrados pela rede, pois ela é o alvo da comparação.

## Contrato da resposta

`data.filtros` registra a rede e os limites do período solicitado. `data.metodologia.anos` lista os anos encontrados no banco. `data.serie` deve corresponder exatamente a essa lista, em ordem crescente. Os metadados de escola, metodologia e os estados anuais já existentes são preservados, inclusive `quantidade_indicadores_presentes`.

## Validação

Os testes BE13 cobrem descoberta de anos, seleção da rede nos pares, período dinâmico, lacunas históricas, validação do intervalo e documentação OpenAPI. A validação em PostgreSQL/warehouse real continua necessária antes do merge.
