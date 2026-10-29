# BE-09 - Contrato HTTP v3 da composicao detalhada Escola x Municipio

**Funcionalidade:** Analise temporal de infraestrutura - Escola x Municipio

**Responsavel:** Rebeca Mendonca

**Revisao esperada:** Backend, Dados, Requisitos, Frontend e QA

**Estado:** rascunho tecnico iniciado em 29/10/2026; nao autoriza implementacao antes da validacao da DAD-06

**Versao proposta:** `infraestrutura-v3-provisoria`

**Contrato anterior:** `infraestrutura-v2-provisoria`

**Historia do Taiga:** BE09 (#56)

## 1. Objetivo

Versionar o contrato da rota oficial da comparacao Escola x Municipio para
acrescentar a composicao detalhada dos 17 indicadores da escola e da referencia
municipal, sem remover os campos de indice, media e diferenca entregues na
Sprint 3.

O contrato permite que o frontend apresente, para cada ano:

- o valor individual de cada indicador da escola como `1`, `0` ou `null`;
- o municipio historico usado como referencia naquele ano;
- as contagens municipais de presentes, validos e sem dados por indicador;
- o percentual de presenca e a cobertura por indicador;
- um aviso de cobertura reduzida que nunca bloqueia a exibicao do resultado.

Esta versao permanece provisoria. O conjunto dos 17 indicadores e a metodologia
nao devem ser apresentados como indicadores oficiais ou homologados.

## 2. Fontes e precedencia

Este rascunho foi elaborado a partir das seguintes fontes:

1. contrato HTTP v2 vigente e implementacao integrada da Sprint 3;
2. relatorio REQ05 anexado a historia #54 do Taiga;
3. criterios de aceite das historias REQ05, DAD06 e BE09;
4. [DAD-05 - Contrato metodologico](DAD-05_CONTRATO_METODOLOGICO.md);
5. [DAD-02 - Matriz de comparabilidade temporal](DAD-02_MATRIZ_COMPARABILIDADE_TEMPORAL.md);
6. decisao operacional provisoria da Sprint 3;
7. codigo e testes vigentes na branch compartilhada da Sprint 3.

Em caso de divergencia, a implementacao nao deve escolher uma regra
silenciosamente. A divergencia deve permanecer registrada ate a revisao dos
responsaveis.

## 3. Divergencia aberta sobre o alerta de cobertura

As fontes atuais concordam que:

- `cobertura_minima_percentual` permanece `null`;
- baixa cobertura nao torna o indice indisponivel;
- o resultado continua visivel e recebe um aviso informativo;
- `null` nao entra no denominador valido.

Existe, porem, uma divergencia sobre o valor do alerta:

| Fonte | Registro atual |
|---|---|
| Relatorio REQ05 | Apresenta `60%` como limiar oficial do aviso de precisao reduzida. |
| Wiki da Sprint 4 e criterios da DAD06 | Tratam o valor exato como pendente de validacao empirica por Dados. |
| DAD-05 | Confirma ausencia de corte minimo, mas nao homologa um limiar visual de `60%`. |

Decisao deste rascunho:

- `60.0` aparece como proposta provisoria no contrato;
- o campo de status informa que a decisao depende da DAD06;
- a regra nao bloqueia o calculo nem remove dados;
- a BE09 nao pode ser encerrada enquanto a DAD06 nao confirmar ou substituir o valor.

## 4. Rota oficial

```http
GET /infraestrutura/analise-temporal/escolas/{co_entidade}/comparacao-municipio
```

### Parametro de caminho

| Parametro | Tipo | Obrigatorio | Regra |
|---|---|---:|---|
| `co_entidade` | inteiro | Sim | Codigo INEP da escola com exatamente oito digitos. |

Nao sao adicionados filtros de periodo. A resposta continua contendo exatamente
os anos `2022`, `2023`, `2024` e `2025`, nesta ordem.

## 5. Compatibilidade com a versao 2

A estrutura da versao 3 evolui de forma aditiva:

- a rota permanece a mesma;
- `descricao` permanece `comparacao_infraestrutura_escola_municipio`;
- `data.escola`, `data.municipio`, `data.metodologia` e `data.serie` permanecem;
- todos os campos anuais da versao 2 permanecem com a mesma semantica;
- os quatro estados anuais vigentes permanecem;
- os corpos de erro `404`, `422`, `500` e `503` permanecem;
- a lista dos 17 indicadores permanece na mesma ordem.

O valor de `data.metodologia.versao` muda de
`infraestrutura-v2-provisoria` para `infraestrutura-v3-provisoria`. Portanto,
clientes que validam esse valor como literal precisam ser atualizados, mesmo
que ignorem os novos campos.

Campos adicionados na versao 3:

- `data.metodologia.limiar_alerta_cobertura_percentual`;
- `data.metodologia.limiar_alerta_cobertura_status`;
- `data.metodologia.bloqueia_resultado_por_cobertura`;
- `data.metodologia.avisos`;
- `data.serie[].municipio_referencia`;
- `data.serie[].registro_historico_disponivel`;
- `data.serie[].cobertura_indicadores_reduzida`;
- `data.serie[].composicao_escola`;
- `data.serie[].composicao_municipal`.

Consumidores que rejeitam campos desconhecidos precisam atualizar seus modelos.
Consumidores que ignoram campos adicionais podem continuar usando os campos da
versao 2.

## 6. Estrutura de sucesso

### `200 OK`

O exemplo abaixo abrevia `serie` para um ponto anual, apenas para explicar os
campos. A resposta real sempre contem os quatro anos e cada objeto de composicao
sempre contem as 17 chaves listadas em `metodologia.indicadores`.

```json
{
  "descricao": "comparacao_infraestrutura_escola_municipio",
  "data": {
    "escola": {
      "co_entidade": 15012345,
      "no_entidade": "EMEF Exemplo"
    },
    "municipio": {
      "co_municipio": 1501402,
      "no_municipio": "Belem"
    },
    "metodologia": {
      "versao": "infraestrutura-v3-provisoria",
      "homologada": false,
      "anos": [2022, 2023, 2024, 2025],
      "indicadores": [
        "in_agua_potavel",
        "in_energia_rede_publica",
        "in_esgoto_rede_publica",
        "in_lixo_servico_coleta",
        "in_banheiro",
        "in_banheiro_pne",
        "in_biblioteca",
        "in_sala_leitura",
        "in_laboratorio_ciencias",
        "in_laboratorio_informatica",
        "in_sala_multiuso",
        "in_sala_atendimento_especial",
        "in_cozinha",
        "in_refeitorio",
        "in_quadra_esportes",
        "in_patio_coberto",
        "in_auditorio"
      ],
      "total_indicadores": 17,
      "cobertura_minima_percentual": null,
      "limiar_alerta_cobertura_percentual": 60.0,
      "limiar_alerta_cobertura_status": "provisorio_pendente_dad06",
      "bloqueia_resultado_por_cobertura": false,
      "avisos": [
        "Esta analise utiliza metodologia de calculo em carater provisorio e pendente de homologacao.",
        "O indice representa disponibilidade de infraestrutura, nao qualidade escolar."
      ],
      "observacao": "Metodologia provisoria e nao homologada. Os resultados nao sao indicadores oficiais."
    },
    "serie": [
      {
        "ano": 2022,
        "situacao": "disponivel",
        "municipio_referencia": {
          "co_municipio": 1501402,
          "no_municipio": "Belem"
        },
        "registro_historico_disponivel": true,
        "indice_escola_percentual": 76.47,
        "quantidade_indicadores_presentes": 13,
        "quantidade_indicadores_validos": 17,
        "total_indicadores": 17,
        "cobertura_indicadores_percentual": 100.0,
        "cobertura_indicadores_reduzida": false,
        "media_municipal_percentual": 64.71,
        "diferenca_pontos_percentuais": 11.76,
        "quantidade_pares_validos": 85,
        "denominador_pares": 94,
        "cobertura_pares_percentual": 90.43,
        "composicao_escola": {
          "in_agua_potavel": 1,
          "in_energia_rede_publica": 1,
          "in_esgoto_rede_publica": 1,
          "in_lixo_servico_coleta": 1,
          "in_banheiro": 1,
          "in_banheiro_pne": 1,
          "in_biblioteca": 1,
          "in_sala_leitura": 0,
          "in_laboratorio_ciencias": 1,
          "in_laboratorio_informatica": 1,
          "in_sala_multiuso": 0,
          "in_sala_atendimento_especial": 0,
          "in_cozinha": 1,
          "in_refeitorio": 1,
          "in_quadra_esportes": 1,
          "in_patio_coberto": 1,
          "in_auditorio": 0
        },
        "composicao_municipal": {
          "in_agua_potavel": {
            "quantidade_presentes": 80,
            "quantidade_validos": 83,
            "quantidade_sem_dados": 11,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 96.39,
            "cobertura_percentual": 88.3,
            "cobertura_reduzida": false
          },
          "in_energia_rede_publica": {
            "quantidade_presentes": 90,
            "quantidade_validos": 94,
            "quantidade_sem_dados": 0,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 95.74,
            "cobertura_percentual": 100.0,
            "cobertura_reduzida": false
          },
          "in_esgoto_rede_publica": {
            "quantidade_presentes": 60,
            "quantidade_validos": 82,
            "quantidade_sem_dados": 12,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 73.17,
            "cobertura_percentual": 87.23,
            "cobertura_reduzida": false
          },
          "in_lixo_servico_coleta": {
            "quantidade_presentes": 75,
            "quantidade_validos": 84,
            "quantidade_sem_dados": 10,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 89.29,
            "cobertura_percentual": 89.36,
            "cobertura_reduzida": false
          },
          "in_banheiro": {
            "quantidade_presentes": 83,
            "quantidade_validos": 85,
            "quantidade_sem_dados": 9,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 97.65,
            "cobertura_percentual": 90.43,
            "cobertura_reduzida": false
          },
          "in_banheiro_pne": {
            "quantidade_presentes": 55,
            "quantidade_validos": 80,
            "quantidade_sem_dados": 14,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 68.75,
            "cobertura_percentual": 85.11,
            "cobertura_reduzida": false
          },
          "in_biblioteca": {
            "quantidade_presentes": 50,
            "quantidade_validos": 82,
            "quantidade_sem_dados": 12,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 60.98,
            "cobertura_percentual": 87.23,
            "cobertura_reduzida": false
          },
          "in_sala_leitura": {
            "quantidade_presentes": 35,
            "quantidade_validos": 78,
            "quantidade_sem_dados": 16,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 44.87,
            "cobertura_percentual": 82.98,
            "cobertura_reduzida": false
          },
          "in_laboratorio_ciencias": {
            "quantidade_presentes": 30,
            "quantidade_validos": 80,
            "quantidade_sem_dados": 14,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 37.5,
            "cobertura_percentual": 85.11,
            "cobertura_reduzida": false
          },
          "in_laboratorio_informatica": {
            "quantidade_presentes": 40,
            "quantidade_validos": 83,
            "quantidade_sem_dados": 11,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 48.19,
            "cobertura_percentual": 88.3,
            "cobertura_reduzida": false
          },
          "in_sala_multiuso": {
            "quantidade_presentes": 25,
            "quantidade_validos": 77,
            "quantidade_sem_dados": 17,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 32.47,
            "cobertura_percentual": 81.91,
            "cobertura_reduzida": false
          },
          "in_sala_atendimento_especial": {
            "quantidade_presentes": 20,
            "quantidade_validos": 55,
            "quantidade_sem_dados": 39,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 36.36,
            "cobertura_percentual": 58.51,
            "cobertura_reduzida": true
          },
          "in_cozinha": {
            "quantidade_presentes": 82,
            "quantidade_validos": 85,
            "quantidade_sem_dados": 9,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 96.47,
            "cobertura_percentual": 90.43,
            "cobertura_reduzida": false
          },
          "in_refeitorio": {
            "quantidade_presentes": 65,
            "quantidade_validos": 84,
            "quantidade_sem_dados": 10,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 77.38,
            "cobertura_percentual": 89.36,
            "cobertura_reduzida": false
          },
          "in_quadra_esportes": {
            "quantidade_presentes": 60,
            "quantidade_validos": 83,
            "quantidade_sem_dados": 11,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 72.29,
            "cobertura_percentual": 88.3,
            "cobertura_reduzida": false
          },
          "in_patio_coberto": {
            "quantidade_presentes": 70,
            "quantidade_validos": 84,
            "quantidade_sem_dados": 10,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 83.33,
            "cobertura_percentual": 89.36,
            "cobertura_reduzida": false
          },
          "in_auditorio": {
            "quantidade_presentes": 15,
            "quantidade_validos": 78,
            "quantidade_sem_dados": 16,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 19.23,
            "cobertura_percentual": 82.98,
            "cobertura_reduzida": false
          }
        }
      }
    ]
  }
}
```

## 7. Municipio de identificacao e municipio de referencia

`data.municipio` continua identificando o municipio do registro mais recente da
escola e permanece somente por compatibilidade com a versao 2.

`data.serie[].municipio_referencia` e a fonte normativa para o ponto anual:

- usa o codigo e o nome registrados para a escola naquele ano;
- nao e substituido silenciosamente pelo municipio mais recente;
- e `null` quando a escola nao possui registro naquele ano;
- pode existir mesmo quando todos os 17 indicadores da escola sao `null`.

O frontend deve exibir o municipio do ponto anual, nao assumir que
`data.municipio` vale para toda a serie.

## 8. Composicao da escola

`composicao_escola` e um objeto com exatamente as 17 chaves de
`metodologia.indicadores`.

| Valor | Significado | Exibicao esperada |
|---:|---|---|
| `1` | Recurso presente | Sim, verde |
| `0` | Recurso ausente | Nao, vermelho |
| `null` | Informacao indisponivel ou indeterminada | Sem dados, cinza |

Regras:

- uma chave ausente no dado bruto e tratada como `null`;
- `null` nunca e convertido em `0`;
- quando nao existe registro anual, as 17 chaves continuam presentes com
  valor `null`;
- `registro_historico_disponivel` diferencia ausencia da linha historica de
  uma linha existente com todos os indicadores nulos;
- a ordem visual e definida por `metodologia.indicadores`.

## 9. Composicao municipal por indicador

`composicao_municipal` possui exatamente as mesmas 17 chaves quando o municipio
historico e conhecido. A escola selecionada e excluida antes das contagens.

| Campo | Tipo | Pode ser `null`? | Regra |
|---|---|---:|---|
| `quantidade_presentes` | inteiro | Nao | Pares cujo indicador e `1`. |
| `quantidade_validos` | inteiro | Nao | Pares cujo indicador e `0` ou `1`. |
| `quantidade_sem_dados` | inteiro | Nao | Pares cujo indicador e `null`. |
| `quantidade_escolas_referencia` | inteiro | Nao | Total de outras escolas encontradas no municipio e ano. |
| `percentual_presentes` | numero | Sim | `100 * presentes / validos`; `null` quando `validos = 0`. |
| `cobertura_percentual` | numero | Sim | `100 * validos / escolas_referencia`; `null` quando nao ha escolas. |
| `cobertura_reduzida` | booleano | Nao | Verdadeiro quando a cobertura e menor que o limiar provisorio. |

Invariantes obrigatorias:

```text
0 <= quantidade_presentes <= quantidade_validos
quantidade_validos + quantidade_sem_dados = quantidade_escolas_referencia
quantidade_escolas_referencia = denominador_pares
```

O percentual territorial e uma proporcao por indicador. Ele nao substitui a
`media_municipal_percentual`, que continua sendo a media aritmetica dos indices
individuais das escolas com indice calculavel.

Quando nao existe registro anual da escola e, portanto, nao existe municipio
historico seguro, `composicao_municipal` e `null`.

Quando o municipio e conhecido, mas nao existem outras escolas, o objeto possui
as 17 chaves com contagens `0`, percentuais `null` e cobertura reduzida `false`.

## 10. Cobertura e alerta

O contrato diferencia duas regras:

1. cobertura minima de calculo;
2. limiar informativo de alerta.

`cobertura_minima_percentual` permanece `null`. Nenhum resultado e bloqueado por
baixa cobertura.

Enquanto a divergencia da secao 3 estiver aberta:

- `limiar_alerta_cobertura_percentual` vale `60.0` apenas como proposta;
- `limiar_alerta_cobertura_status` vale `provisorio_pendente_dad06`;
- a comparacao usa a razao exata, antes do arredondamento, e o operador
  estritamente menor que o limiar;
- cobertura exatamente igual a `60.0` nao gera alerta;
- cobertura `null` por ausencia de denominador nao e classificada como reduzida;
- o frontend deve exibir aviso, mas manter todos os valores disponiveis.

No ponto anual, `cobertura_indicadores_reduzida` aplica essa regra aos
indicadores validos da escola sobre o total de 17. Em cada item de
`composicao_municipal`, `cobertura_reduzida` aplica a mesma regra aos registros
validos do indicador sobre `quantidade_escolas_referencia`.

A DAD06 deve confirmar o valor, o escopo do alerta e a amostra de validacao
antes de este documento ser marcado como pronto.

## 11. Precisao e arredondamento

- contagens sao inteiras e nunca sofrem arredondamento;
- proporcoes intermediarias permanecem exatas;
- percentuais sao arredondados para duas casas somente na saida;
- `percentual_presentes = round(100 * presentes / validos, 2)`;
- `cobertura_percentual = round(100 * validos / escolas_referencia, 2)`;
- nao se usa percentual ja arredondado para calcular outro valor;
- `2/3 - 1/3` deve resultar em `33.33`, nao `33.34`;
- a media de `0` e `2/3` deve resultar em `33.33`.

## 12. Situacoes anuais e campos novos

Os quatro valores de `situacao` permanecem:

- `disponivel`;
- `escola_sem_dados`;
- `sem_pares_validos`;
- `sem_pares_municipio`.

### Sem registro anual da escola

- `registro_historico_disponivel = false`;
- `municipio_referencia = null`;
- as 17 chaves de `composicao_escola` valem `null`;
- `composicao_municipal = null`;
- indice, media e diferenca valem `null`;
- as contagens da escola e dos pares valem `0`.

### Registro anual com todos os indicadores nulos

- `registro_historico_disponivel = true`;
- `municipio_referencia` e preenchido;
- as 17 chaves de `composicao_escola` valem `null`;
- a composicao municipal pode ser calculada;
- o indice da escola e a diferenca permanecem `null`.

### Escola com indice e sem pares

- a composicao da escola permanece disponivel;
- a composicao municipal possui as 17 chaves com contagens zero;
- percentuais municipais valem `null`;
- media e diferenca valem `null`.

## 13. Escola inexistente e escola existente sem historico

Escola inexistente continua retornando `404 Not Found`:

```json
{
  "code": "not_found",
  "message": "Escola 15012345 nao encontrada."
}
```

Escola existente sem registros entre 2022 e 2025 retorna `200 OK`:

- os metadados de `data.escola` permanecem preenchidos;
- `data.serie` contem os quatro anos;
- todos os pontos usam `situacao = "escola_sem_dados"`;
- `registro_historico_disponivel = false`;
- nenhuma composicao municipal e inventada.

## 14. Demais erros

| HTTP | Codigo ou formato | Significado |
|---:|---|---|
| `422` | Validacao padrao do FastAPI | Codigo INEP malformado ou fora de oito digitos. |
| `500` | `internal_error` | Falha interna inesperada. |
| `503` | `warehouse_unavailable` | Dependencia de dados indisponivel. |

Os corpos e as mensagens permanecem iguais aos da versao 2.

## 15. Orientacao ao frontend

- consumir somente a rota oficial da secao 4;
- usar `metodologia.indicadores` para ordenar os paineis;
- exibir `1`, `0` e `null` como Sim, Nao e Sem dados;
- usar `municipio_referencia` do ano selecionado;
- mostrar `quantidade_presentes` de `quantidade_validos` e o percentual;
- disponibilizar `quantidade_sem_dados` e `cobertura_percentual` no tooltip;
- exibir o aviso quando `cobertura_reduzida = true`;
- nunca ocultar os dados por causa do aviso;
- nao apresentar `percentual_presentes = null` como `0%`;
- exibir os dois avisos metodologicos de `metodologia.avisos`;
- nao apresentar a versao provisoria como indicador oficial.

## 16. Criterios de aceite da BE09

- [x] Rota e compatibilidade com a versao 2 documentadas.
- [x] Municipio historico por ano exposto no contrato.
- [x] Composicao individual dos 17 indicadores documentada.
- [x] Agregacao municipal por indicador documentada.
- [x] Presencas, validos, sem dados, percentual e cobertura definidos.
- [x] Preservacao de `null` documentada.
- [x] Escola selecionada excluida da referencia municipal.
- [x] Escola inexistente diferenciada de escola existente sem historico.
- [x] Precisao e arredondamento documentados.
- [x] Regras e avisos metodologicos expostos nos metadados.
- [ ] Limiar de alerta confirmado ou substituido pela DAD06.
- [ ] Exemplo completo de quatro anos validado por Dados, Frontend e QA.
- [ ] Revisao tecnica registrada no Taiga.

## 17. Dependencias para conclusao

### DAD06

Dados deve confirmar:

- denominador valido por indicador;
- relacao entre validos, sem dados e total de escolas;
- aplicacao do limiar de `60%` ou valor substituto;
- amostra manual de 2022 a 2025;
- tratamento de integridade para valores fora de `0`, `1` e `null`;
- evidencia de que a escola selecionada foi excluida.

### Requisitos

Requisitos deve confirmar que o relatorio REQ05 e a wiki foram conciliados
quanto ao limiar de alerta e aos textos obrigatorios.

### Frontend

Frontend deve revisar nomes, nulabilidade e consumo dos novos campos antes da
implementacao da BE10.

### QA

QA deve revisar as invariantes, os casos de borda e os exemplos de precisao.

## 18. Fora de escopo da BE09

- alterar schemas Pydantic;
- alterar dominio, service, repository ou rota;
- implementar a agregacao municipal;
- criar endpoint de comparacao multipla;
- implementar classificacao por faixas;
- alterar o conjunto de 17 indicadores;
- homologar metodologia ou base de dados.

Essas mudancas devem ocorrer em historias e branches proprias depois da revisao
deste contrato.
