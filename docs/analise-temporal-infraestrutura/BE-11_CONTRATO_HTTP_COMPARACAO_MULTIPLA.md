# BE11 - Proposta de contrato HTTP para comparacao multipla

**Funcionalidade:** Analise temporal de infraestrutura - comparacao multipla

**Responsavel:** Rebeca Mendonca

**Revisao:** Backend, Dados, Requisitos, Frontend e QA

**Estado:** proposta tecnica finalizada para revisao; implementacao funcional fora do escopo da Sprint 4

**Versao proposta:** `infraestrutura-multipla-v1-provisoria`

**Historia do Taiga:** BE11 (#65)

## 1. Objetivo

Propor o contrato HTTP de uma futura comparacao temporal entre escolas e
municipios. O usuario podera escolher manualmente ate tres alvos, em qualquer
combinacao entre escolas e municipios.

Cada escola escolhida gera obrigatoriamente uma serie adicional com sua
referencia municipal. Essa referencia nao consome uma vaga do seletor manual.
Por isso, a resposta pode conter ate seis series.

Esta historia documenta o comportamento esperado, mas nao implementa o novo
endpoint na Sprint 4.

## 2. Fontes e precedencia

Esta proposta considera:

1. REQ06 e seus criterios de aceite;
2. os cinco esclarecimentos posteriores de Requisitos sobre selecao mista,
   referencias automaticas, municipios coincidentes, dados insuficientes e o
   limiar de 60%;
3. DAD07, com a proposta de agregacao municipal;
4. DAD05 e DAD06, com as regras de cobertura e denominador;
5. BE09 e BE12, com o contrato e a implementacao da composicao detalhada;
6. o endpoint da Sprint 3 para comparacao Escola x Municipio.

Os esclarecimentos posteriores de Requisitos prevalecem sobre a interpretacao
inicial de que existiriam apenas tres linhas no grafico. Se REQ06 ainda mostrar
essa interpretacao antiga no Taiga, o documento deve ser atualizado antes da
implementacao funcional.

## 3. Decisoes consolidadas

### 3.1 Limites

Considere:

- `E` como a quantidade de escolas selecionadas manualmente;
- `M` como a quantidade de municipios selecionados manualmente.

As regras sao:

```text
E + M <= 3
referencias_automaticas = E
total_series = E + M + referencias_automaticas
total_series = M + 2 * E
total_series <= 6
```

Exemplos:

| Selecao manual | Referencias automaticas | Total de series |
|---|---:|---:|
| 3 municipios | 0 | 3 |
| 1 escola + 2 municipios | 1 | 4 |
| 2 escolas + 1 municipio | 2 | 5 |
| 3 escolas | 3 | 6 |

### 3.2 Referencia municipal automatica

- Cada escola selecionada gera uma referencia municipal propria.
- A referencia exclui somente a escola que a originou.
- O municipio de referencia e obtido do registro historico da escola em cada ano.
- Duas escolas do mesmo municipio geram referencias separadas, porque cada uma
  exige uma exclusao individual.
- A legenda usa `Referencia municipal da [Nome da Escola]`.
- O tooltip informa o nome e o codigo do municipio historico daquele ano.

### 3.3 Municipio selecionado manualmente

- A serie manual usa a media geral das escolas elegiveis do municipio.
- Uma escola-alvo nao e excluida dessa serie apenas por tambem estar selecionada.
- A referencia automatica e a serie manual permanecem separadas quando apontam
  para o mesmo municipio.
- Elas tambem permanecem separadas quando seus valores numericos forem iguais.
- O frontend diferencia a serie manual com linha solida e a referencia
  automatica com linha tracejada, alem de consolidar os valores no tooltip.

### 3.4 Dados ausentes e falhas parciais

- `NULL` permanece `null`; nao deve ser convertido em zero.
- A falta de indice da escola em um ano interrompe somente a linha da escola.
- A referencia automatica continua visivel quando possuir dados validos.
- Uma falha ou ausencia que afete uma serie nao bloqueia as demais series.
- Codigo invalido ou entidade inexistente gera erro HTTP especifico.
- Denominador zero gera `null` no valor correspondente e metadado explicativo.

### 3.5 Cobertura

- O limiar de 60% aplica-se exclusivamente aos pontos de escola.
- Cobertura escolar exatamente igual a 60% nao gera alerta.
- Cobertura escolar abaixo de 60% gera alerta, mas nao oculta o valor calculado.
- Referencias municipais e municipios manuais exibem suas coberturas, mas nao
  recebem automaticamente o mesmo alerta escolar.

## 4. Rota proposta

```http
GET /infraestrutura/analise-temporal/comparacao-multipla
```

O parametro `alvo` e repetivel e preserva a ordem da selecao manual.

```http
GET /infraestrutura/analise-temporal/comparacao-multipla?alvo=escola:15012345&alvo=municipio:1501402&alvo=municipio:1500800
```

| Parametro | Tipo | Quantidade | Formato |
|---|---|---:|---|
| `alvo` | texto repetivel | 1 a 3 | `escola:{codigo_inep}` ou `municipio:{codigo_ibge}` |

Validacoes:

- escola usa codigo INEP com oito digitos;
- municipio usa codigo IBGE positivo e conhecido pela base;
- o mesmo alvo manual nao pode aparecer mais de uma vez;
- escola e municipio sao tipos distintos;
- requisicao sem alvo ou com mais de tres alvos retorna `422`;
- tipo desconhecido ou formato invalido retorna `422`;
- entidade inexistente retorna `404`;
- o periodo permanece fixo em 2022, 2023, 2024 e 2025.

## 5. Estrutura de sucesso

### `200 OK`

O exemplo abaixo abrevia os quatro anos e as 17 chaves de composicao. A resposta
real deve devolver todos os anos em cada serie e todas as chaves descritas em
`metodologia.indicadores`.

```json
{
  "descricao": "comparacao_multipla_infraestrutura",
  "data": {
    "metodologia": {
      "versao": "infraestrutura-multipla-v1-provisoria",
      "homologada": false,
      "anos": [2022, 2023, 2024, 2025],
      "total_indicadores": 17,
      "limite_alvos_manuais": 3,
      "limite_series": 6,
      "referencias_automaticas_consumem_limite_manual": false,
      "agregacao_entre_municipios": false,
      "limiar_alerta_escola_percentual": 60.0,
      "limiar_aplica_se_a_referencias_municipais": false,
      "precisao_percentual_casas": 2,
      "avisos": [
        "Metodologia ainda sujeita a homologacao final.",
        "Municipios sao calculados individualmente e nao formam uma media combinada."
      ]
    },
    "selecao": {
      "quantidade_alvos_manuais": 2,
      "alvos_manuais": [
        "escola:15012345",
        "municipio:1501402"
      ],
      "quantidade_referencias_automaticas": 1,
      "quantidade_series": 3
    },
    "series": [
      {
        "id": "escola:15012345",
        "tipo": "escola",
        "origem": "selecao_manual",
        "entidade": {
          "codigo": 15012345,
          "nome": "EMEF Exemplo"
        },
        "rotulo": "EMEF Exemplo",
        "estilo_sugerido": "linha_solida",
        "pontos": [
          {
            "ano": 2022,
            "situacao": "disponivel",
            "indice_percentual": 76.47,
            "cobertura_percentual": 100.0,
            "alerta_cobertura": false,
            "composicao": {
              "in_agua_potavel": 1
            }
          }
        ]
      },
      {
        "id": "referencia-escola:15012345",
        "tipo": "referencia_municipal_automatica",
        "origem": "escola:15012345",
        "entidade_referenciada": {
          "codigo": 15012345,
          "nome": "EMEF Exemplo"
        },
        "rotulo": "Referencia municipal da EMEF Exemplo",
        "estilo_sugerido": "linha_tracejada",
        "pontos": [
          {
            "ano": 2022,
            "situacao": "disponivel",
            "municipio_historico": {
              "codigo": 1501402,
              "nome": "Belem"
            },
            "indice_percentual": 64.71,
            "cobertura_percentual": 90.43,
            "escola_excluida": 15012345,
            "quantidade_escolas_validas": 85,
            "quantidade_escolas_referencia": 94,
            "composicao": {
              "in_agua_potavel": {
                "quantidade_presentes": 80,
                "quantidade_validos": 83,
                "quantidade_sem_dados": 11,
                "percentual_presentes": 96.39,
                "cobertura_percentual": 88.3
              }
            }
          }
        ]
      },
      {
        "id": "municipio:1501402",
        "tipo": "municipio_manual",
        "origem": "selecao_manual",
        "entidade": {
          "codigo": 1501402,
          "nome": "Belem"
        },
        "rotulo": "Belem",
        "estilo_sugerido": "linha_solida",
        "pontos": [
          {
            "ano": 2022,
            "situacao": "disponivel",
            "indice_percentual": 65.02,
            "cobertura_percentual": 90.53,
            "quantidade_escolas_validas": 86,
            "quantidade_escolas_referencia": 95,
            "composicao": {
              "in_agua_potavel": {
                "quantidade_presentes": 81,
                "quantidade_validos": 84,
                "quantidade_sem_dados": 11,
                "percentual_presentes": 96.43,
                "cobertura_percentual": 88.42
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

### 6.1 Escola

- Representa um alvo escolhido manualmente.
- Devolve os quatro anos, mesmo que algum ponto tenha `indice_percentual: null`.
- A composicao individual usa `1`, `0` ou `null` para cada indicador.
- O alerta de 60% e avaliado somente nessa serie.

### 6.2 Referencia municipal automatica

- E criada para cada escola escolhida.
- Nao conta no limite de tres alvos manuais.
- Usa o municipio historico da escola em cada ano.
- Exclui somente a escola que originou a referencia.
- Duas referencias do mesmo municipio continuam separadas quando suas escolas
  de origem forem diferentes.
- Nao recebe automaticamente o alerta escolar de 60%.

### 6.3 Municipio manual

- Representa um municipio escolhido diretamente pelo usuario.
- Usa a media geral das escolas elegiveis daquele municipio e ano.
- Nao exclui escolas apenas porque elas tambem aparecem na selecao manual.
- Nao e agregado com outros municipios escolhidos.
- Permanece separado de uma referencia automatica do mesmo territorio.

## 7. Composicao e denominadores

Cada indicador territorial deve informar, por ano:

- `quantidade_presentes`;
- `quantidade_validos`;
- `quantidade_sem_dados`;
- `percentual_presentes`;
- `cobertura_percentual`.

Formulas propostas:

```text
percentual_presentes = quantidade_presentes / quantidade_validos * 100
cobertura_percentual = quantidade_validos / quantidade_escolas_referencia * 100
```

Regras:

- `quantidade_escolas_referencia` exclui a escola-alvo apenas nas referencias
  automaticas;
- no municipio manual, a quantidade considera a rede elegivel completa;
- `quantidade_validos = 0` produz `percentual_presentes: null`;
- `quantidade_escolas_referencia = 0` produz `cobertura_percentual: null`;
- cada serie conserva seu proprio denominador;
- valores sao arredondados para duas casas apenas na apresentacao final.

## 8. Erros

| Status | Condicao |
|---:|---|
| `422` | nenhum alvo, mais de tres alvos, duplicidade, tipo ou formato invalido |
| `404` | escola ou municipio solicitado nao existe |
| `500` | falha interna inesperada |
| `503` | fonte de dados temporariamente indisponivel |

Quando uma entidade solicitada for invalida, a requisicao inteira deve falhar. A
regra de falha parcial aplica-se aos pontos temporais de entidades validas, e nao
a codigos inexistentes ou malformados.

## 9. Casos obrigatorios de validacao futura

1. Tres municipios geram tres series.
2. Uma escola e dois municipios geram quatro series.
3. Duas escolas e um municipio geram cinco series.
4. Tres escolas geram seis series.
5. Cada escola gera sua propria referencia com exclusao individual.
6. Duas escolas do mesmo municipio mantem referencias separadas.
7. Municipio manual e referencia automatica do mesmo territorio permanecem
   separados, mesmo quando os valores forem iguais.
8. O tooltip da referencia usa o municipio historico correto de cada ano.
9. Escola sem indice em um ano nao oculta uma referencia municipal valida.
10. `NULL` nao e transformado em zero.
11. Cobertura escolar exatamente em 60% nao gera alerta.
12. Cobertura escolar abaixo de 60% gera alerta sem ocultar o indice.
13. O limiar de 60% nao e aplicado automaticamente a series municipais.
14. Denominador zero retorna percentual `null`.
15. Uma falha de ponto em uma serie nao bloqueia as demais.

## 10. Criterios de aceite da BE11

- [x] Rota e formato dos parametros propostos.
- [x] Limite de tres alvos manuais formalizado.
- [x] Limite de seis series formalizado.
- [x] Referencias municipais automaticas representadas como series separadas.
- [x] Exclusao individual da escola-alvo especificada.
- [x] Municipio historico preservado por ano.
- [x] Diferenca entre municipio manual e referencia automatica documentada.
- [x] Tratamento de `null`, falhas parciais, cobertura e denominador documentado.
- [x] Casos minimos de validacao futura listados.
- [x] Implementacao funcional identificada como fora do escopo desta historia.
- [ ] Revisao multidisciplinar e atualizacao formal da REQ06 no Taiga.

## 11. Pendencias antes da implementacao funcional

1. Requisitos deve incorporar no Taiga os esclarecimentos que substituem a
   leitura antiga de exatamente tres linhas.
2. Dados deve concluir a revisao da DAD07 e confirmar os denominadores e o
   universo municipal.
3. Backend deve transformar esta proposta em contrato versionado somente depois
   da homologacao das regras.
4. Frontend deve validar legenda, diferenciacao visual e tooltip no prototipo.
5. QA deve transformar os casos da secao 9 em cenarios automatizados.

## 12. Relacao com a Sprint 4

A Sprint 4 entrega a composicao detalhada Escola x Municipio por meio de BE09,
BE10 e BE12. A comparacao multipla permanece como descoberta preparada para uma
sprint futura. Assim, a conclusao da BE11 significa que a proposta tecnica esta
documentada e revisavel, e nao que o endpoint multiplo ja exista.
