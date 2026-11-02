# BE11 - Proposta de contrato HTTP para comparacao multipla

**Funcionalidade:** Analise temporal de infraestrutura - comparacao multipla

**Responsavel:** Rebeca Mendonca

**Revisao esperada:** Backend, Dados, Requisitos, Frontend e QA

**Estado:** rascunho de descoberta iniciado em 02/11/2026; REQ06 revisada e DAD07 ainda em andamento

**Versao proposta:** `infraestrutura-multipla-v1-provisoria`

**Historia do Taiga:** BE11 (#65)

## 1. Objetivo

Propor um contrato HTTP para comparar, em uma unica resposta, ate tres alvos de
infraestrutura. Um alvo pode ser uma escola ou um municipio.

Esta historia nao autoriza a implementacao do endpoint na Sprint 4. O documento
serve para alinhar a futura implementacao entre Backend, Dados, Requisitos,
Frontend e QA.

## 2. Fontes e precedencia

O rascunho considera:

1. REQ06, historia #64 do Taiga e o documento anexado em 27/10/2026;
2. criterios de aceite da BE11, historia #65 do Taiga;
3. DAD07, historia #63 do Taiga, ainda em andamento e sem evidencia anexada na data desta revisao;
4. [BE09 - Contrato HTTP v3 da composicao detalhada](https://github.com/rbecamend/labes-api/blob/562f1297587b6ad4775bc1ec9e549222a31048e0/docs/analise-temporal-infraestrutura/BE-09_CONTRATO_HTTP_COMPOSICAO_DETALHADA.md);
5. endpoint vigente da Sprint 3 para comparacao Escola x Municipio.

Em caso de divergencia, uma regra nao deve ser implementada silenciosamente. A
decisao deve ser registrada por Requisitos ou Dados, conforme a natureza da
divergencia.

## 3. Divergencias que impedem a versao final

### 3.1 Limite de selecao mista

A REQ06 registra dois enunciados diferentes:

- ate tres municipios e ate tres escolas;
- no cenario BDD com uma escola e dois municipios, devem existir exatamente tres linhas.

Se os limites forem independentes, uma requisicao poderia ter seis alvos e ainda
gerar referencias municipais adicionais para as escolas. Isso conflita com o
objetivo de legibilidade e com o cenario de tres linhas.

Decisao provisoria deste rascunho:

- o limite e de tres alvos principais no total, independentemente do tipo;
- a referencia municipal de uma escola fica dentro do ponto anual da propria escola;
- referencias territoriais nao viram series principais adicionais;
- Requisitos deve confirmar essa interpretacao antes da implementacao.

### 3.2 Agregacao municipal

A REQ06 proibe uma media combinada entre municipios, mas nao fecha a formula do
valor temporal de cada municipio. A DAD07 deve decidir:

- universo de escolas elegiveis por municipio e ano;
- denominador valido;
- media simples ou outra ponderacao;
- tratamento de registros ausentes e denominadores iguais a zero;
- efeitos de mudanca territorial e municipio historico.

Recomendacao provisoria para permitir a discussao do contrato:

- cada municipio e calculado separadamente em cada ano;
- nao existe agregacao entre municipios selecionados;
- o valor municipal e a media aritmetica dos indices calculaveis das escolas elegiveis daquele municipio e ano;
- registros sem nenhum indicador valido nao entram na media e permanecem na contagem de cobertura;
- a regra so pode ser marcada como confirmada depois da DAD07.

### 3.3 Quantidade de linhas da escola e de sua referencia

A REQ06 afirma que multiplas escolas devem ser comparadas com suas respectivas
referencias territoriais, mas o cenario BDD conta apenas os alvos selecionados
como linhas.

Decisao provisoria deste rascunho:

- `series` contem somente os alvos escolhidos;
- a referencia municipal anual da escola e retornada em `referencia_territorial`;
- o frontend pode mostrar a referencia no tooltip e no painel detalhado;
- uma futura decisao pode permitir desenhar a referencia como linha auxiliar,
  sem altera-la para uma serie principal nem mistura-la com outros municipios.

## 4. Rota proposta

```http
GET /infraestrutura/analise-temporal/comparacao-multipla
```

### Parametro de consulta

O parametro `alvo` e repetivel e preserva a ordem escolhida pelo usuario.

```http
GET /infraestrutura/analise-temporal/comparacao-multipla?alvo=escola:15012345&alvo=municipio:1501402&alvo=municipio:1500800
```

| Parametro | Tipo | Quantidade | Formato |
|---|---|---:|---|
| `alvo` | texto repetivel | 1 a 3 | `escola:{codigo_inep}` ou `municipio:{codigo_ibge}` |

Regras de validacao:

- escola usa codigo INEP com oito digitos;
- municipio usa codigo IBGE positivo conhecido pela base;
- o mesmo alvo nao pode aparecer mais de uma vez;
- escola e municipio com codigos numericamente iguais continuam sendo alvos distintos;
- a ordem da resposta acompanha a ordem dos parametros `alvo`;
- requisicao sem alvo, com mais de tres alvos, com tipo desconhecido ou formato invalido retorna `422`;
- o periodo permanece fixo em 2022, 2023, 2024 e 2025.

O formato tipado evita dois parametros independentes e torna explicito que o
limite provisorio e aplicado ao total da selecao mista.

## 5. Estrutura de sucesso

### `200 OK`

O exemplo e estrutural e abrevia os quatro pontos anuais e as 17 chaves de
composicao. A resposta real deve conter os quatro anos em cada serie e todas as
chaves definidas em `metodologia.indicadores`.

```json
{
  "descricao": "comparacao_multipla_infraestrutura",
  "data": {
    "metodologia": {
      "versao": "infraestrutura-multipla-v1-provisoria",
      "homologada": false,
      "anos": [2022, 2023, 2024, 2025],
      "total_indicadores": 17,
      "limite_alvos": 3,
      "limite_alvos_status": "provisorio_req06",
      "agregacao_entre_municipios": false,
      "agregacao_municipal_status": "pendente_dad07",
      "cobertura_minima_percentual": null,
      "precisao_percentual_casas": 2,
      "avisos": [
        "Metodologia provisoria e pendente de homologacao.",
        "Municipios sao calculados individualmente e nao formam uma media combinada."
      ]
    },
    "selecao": {
      "quantidade": 2,
      "alvos": ["escola:15012345", "municipio:1501402"]
    },
    "series": [
      {
        "id": "escola:15012345",
        "tipo": "escola",
        "entidade": {
          "codigo": 15012345,
          "nome": "EMEF Exemplo"
        },
        "situacao": "encontrado",
        "pontos": [
          {
            "ano": 2022,
            "situacao": "disponivel",
            "indice_percentual": 76.47,
            "cobertura_percentual": 100.0,
            "referencia_territorial": {
              "tipo": "municipio_historico",
              "codigo": 1501402,
              "nome": "Belem",
              "media_percentual": 64.71,
              "quantidade_escolas_validas": 85,
              "quantidade_escolas_total": 94,
              "cobertura_percentual": 90.43
            },
            "composicao": {
              "escola": {
                "in_agua_potavel": 1
              },
              "referencia": {
                "in_agua_potavel": {
                  "quantidade_presentes": 80,
                  "quantidade_validos": 83,
                  "quantidade_sem_dados": 11,
                  "quantidade_escolas_referencia": 94,
                  "percentual_presentes": 96.39,
                  "cobertura_percentual": 88.3
                }
              }
            }
          }
        ]
      },
      {
        "id": "municipio:1501402",
        "tipo": "municipio",
        "entidade": {
          "codigo": 1501402,
          "nome": "Belem"
        },
        "situacao": "encontrado",
        "pontos": [
          {
            "ano": 2022,
            "situacao": "disponivel",
            "indice_percentual": 65.02,
            "cobertura_percentual": 90.43,
            "quantidade_escolas_validas": 86,
            "quantidade_escolas_total": 95,
            "referencia_territorial": null,
            "composicao": {
              "municipio": {
                "in_agua_potavel": {
                  "quantidade_presentes": 81,
                  "quantidade_validos": 84,
                  "quantidade_sem_dados": 11,
                  "quantidade_escolas_referencia": 95,
                  "percentual_presentes": 96.43,
                  "cobertura_percentual": 88.42
                }
              }
            }
          }
        ]
      }
    ]
  }
}
```

## 6. Semantica das series

### 6.1 Serie de escola

- usa o registro historico da escola em cada ano;
- usa o municipio registrado naquele mesmo ano como referencia;
- exclui a escola selecionada das contagens e da media da referencia;
- preserva `0`, `1` e `null` na composicao individual;
- diferencia escola inexistente, ano sem registro e registro com 17 valores `null`;
- segue a composicao e as regras propostas pela BE09.

### 6.2 Serie de municipio

- usa somente escolas pertencentes ao municipio no ano consultado;
- nao combina escolas de municipios diferentes;
- nao exclui escola apenas porque ela tambem foi selecionada como outro alvo;
- expoe total de escolas, quantidade valida e cobertura;
- expoe a composicao percentual por indicador como `X de Y escolas`;
- usa formula de agregacao marcada como provisoria ate a DAD07.

### 6.3 Selecao mista

- cada alvo e processado de forma independente;
- a indisponibilidade de um ponto anual nao impede as outras series;
- nao existe media global dos alvos;
- o mesmo municipio pode aparecer como alvo principal e como referencia historica de uma escola;
- essa repeticao semantica nao e removida automaticamente.

## 7. Dados ausentes e cobertura

Cada serie contem sempre os anos de 2022 a 2025. Pontos ausentes nao sao
removidos do array.

Situacoes propostas para um ponto:

| Situacao | Significado |
|---|---|
| `disponivel` | Existe valor calculavel para o alvo no ano. |
| `sem_registro` | Nao existe registro historico seguro para o alvo no ano. |
| `sem_dados` | Existe registro, mas nao ha indicador valido para o calculo. |
| `sem_referencia` | A escola possui indice, mas a referencia territorial nao possui valor calculavel. |

Regras:

- `null` nunca e convertido automaticamente em zero;
- uma lacuna interrompe apenas o trecho daquela serie no grafico;
- outras series validas continuam visiveis;
- cobertura baixa nao bloqueia a resposta;
- o alerta de `60%` da BE09 aplica-se somente a cobertura da escola selecionada;
- nao se aplica automaticamente o mesmo alerta a municipios;
- denominador zero produz percentual `null`, nunca `0%`;
- contagens permanecem inteiras e percentuais sao arredondados somente na saida.

## 8. Precisao

- calculos intermediarios usam razoes exatas;
- percentuais e diferencas usam duas casas decimais na resposta;
- arredondamento ocorre apenas na apresentacao;
- valores arredondados nao alimentam calculos posteriores;
- `2/3 - 1/3` resulta em `33.33`, nao `33.34`;
- media de `0` e `2/3` resulta em `33.33`.

## 9. Validacao e erros

| HTTP | Codigo | Quando ocorre |
|---:|---|---|
| `422` | `invalid_selection` | Sem alvo, mais de tres alvos, duplicidade, tipo desconhecido ou codigo malformado. |
| `404` | `target_not_found` | Pelo menos um alvo solicitado nao existe no cadastro. |
| `500` | `internal_error` | Falha interna inesperada. |
| `503` | `warehouse_unavailable` | Dependencia de dados indisponivel. |

Corpo proposto para selecao invalida:

```json
{
  "code": "invalid_selection",
  "message": "Selecione de 1 a 3 alvos distintos.",
  "details": {
    "limite": 3,
    "recebidos": 4
  }
}
```

Corpo proposto para alvo inexistente:

```json
{
  "code": "target_not_found",
  "message": "Um ou mais alvos nao foram encontrados.",
  "details": {
    "alvos": ["escola:15099999"]
  }
}
```

A validacao e atomica: alvo inexistente retorna `404` e nenhuma serie parcial e
entregue. Ausencia de dados historicos para alvo existente retorna `200` com os
pontos anuais correspondentes em estado indisponivel.

## 10. Desempenho, paginacao e cache

### Paginacao

Nao e necessaria nesta proposta porque:

- existem no maximo tres alvos;
- cada alvo possui exatamente quatro pontos anuais;
- a ordem da selecao deve ser preservada.

Se o limite crescer no futuro, a decisao de paginar deve gerar nova versao do
contrato e nao pode remover silenciosamente series solicitadas.

### Consultas e paralelismo

- evitar uma consulta separada para cada indicador;
- buscar os 17 indicadores em lote por alvo e ano;
- reutilizar agregados quando uma referencia municipal tambem for alvo principal;
- limitar o paralelismo para nao multiplicar conexoes ao warehouse;
- medir o tamanho da resposta com as composicoes completas antes da implementacao.

### Cache

O metodo `GET` permite cache, mas a politica nao e obrigatoria nesta historia de
descoberta. Se adotada:

- a chave inclui versao metodologica e a lista ordenada de alvos;
- selecoes em ordens diferentes nao podem alterar os valores calculados;
- o servidor pode normalizar a chave de calculo, preservando a ordem somente na resposta;
- a invalidacao ocorre quando os dados anuais ou a versao metodologica mudarem;
- `ETag` e preferivel a definir um tempo longo de validade sem governanca dos dados.

## 11. Compatibilidade e versionamento

O endpoint vigente permanece inalterado:

```http
GET /infraestrutura/analise-temporal/escolas/{co_entidade}/comparacao-municipio
```

A nova rota nao substitui a atual e nao altera seus schemas. Isso permite:

- manter clientes da Sprint 3 funcionando;
- implementar e testar a comparacao multipla separadamente;
- comparar a serie de uma escola nas duas rotas durante a conciliacao;
- remover a rota antiga somente em uma futura versao com migracao anunciada.

A versao metodologica fica no corpo da resposta. Mudanca de formula, limite de
alvos, conjunto de indicadores ou semantica de cobertura exige nova versao.

## 12. Casos de validacao propostos

1. uma escola valida retorna quatro anos e o municipio historico correto em cada ano;
2. tres municipios validos retornam tres series independentes;
3. uma escola e dois municipios retornam exatamente tres series principais;
4. o quarto alvo retorna `422` e nao altera a selecao anterior no frontend;
5. alvo duplicado retorna `422`;
6. uma lacuna anual interrompe somente a serie afetada;
7. municipio sem valor calculavel retorna ponto nulo sem bloquear outros municipios;
8. escola existente sem historico retorna quatro pontos `sem_registro`;
9. alvo inexistente retorna `404` com a lista dos identificadores ausentes;
10. municipio selecionado tambem usado como referencia de escola nao gera media combinada;
11. `null` permanece `null` em todas as composicoes;
12. denominador zero produz percentual `null`;
13. precisao segue os casos `33.33` definidos na BE09;
14. composicao municipal apresenta `quantidade_presentes`, `quantidade_validos`, `quantidade_sem_dados` e percentual por indicador;
15. a resposta de uma escola e conciliada com o endpoint vigente para os mesmos dados.

## 13. Criterios de aceite da BE11

- [x] Rota e parametros propostos.
- [x] Resposta proposta com series, referencias territoriais e metadados.
- [x] Regras de dados ausentes, cobertura e precisao documentadas.
- [x] Casos de validacao e respostas de erro descritos.
- [x] Desempenho, paginacao e cache avaliados.
- [x] Compatibilidade com o endpoint vigente documentada.
- [ ] Limite total ou independente confirmado por Requisitos.
- [ ] Formula e denominadores municipais confirmados pela DAD07.
- [ ] Quantidade de linhas auxiliares da referencia confirmada por Requisitos e Frontend.
- [ ] Proposta revisada por Dados, Requisitos, Frontend e QA.
- [ ] Revisao e evidencias registradas no Taiga.

## 14. Fora de escopo da BE11

- implementar rota, schemas, servico ou repositorio;
- alterar o endpoint vigente;
- criar prototipo visual;
- implementar cache ou paginacao;
- ampliar o periodo alem de 2022 a 2025;
- comparar estados ou regioes;
- homologar metodologia ou fonte de dados.
