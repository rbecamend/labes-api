# BE-09 - Contrato HTTP v3 da composicao detalhada Escola x Municipio

**Funcionalidade:** Analise temporal de infraestrutura - Escola x Municipio

**Responsavel:** Rebeca Mendonca

**Revisao esperada:** Backend, Dados, Requisitos, Frontend e QA

**Estado:** contrato tecnico implementado pela BE12 e validado por testes automatizados; metodologia provisoria e amostra empirica ampliada da DAD06 ainda pendentes

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

Este contrato foi elaborado e revisado a partir das seguintes fontes:

1. contrato HTTP v2 vigente e implementacao integrada da Sprint 3;
2. relatorio REQ05 anexado a historia #54 do Taiga;
3. criterios de aceite das historias REQ05, DAD06 e BE09;
4. [DAD06 - Denominadores e amostra de validacao](https://github.com/rbecamend/labes-api/blob/5af47d4/docs/analise-temporal-infraestrutura/DAD-06_DENOMINADORES_E_AMOSTRA_VALIDACAO.md);
5. [DAD06 - Relatorio tecnico final](https://github.com/rbecamend/labes-api/blob/5af47d4/docs/analise-temporal-infraestrutura/DAD-06_RELATORIO_TECNICO_FINAL.md), commit `5af47d4` e PR #14, integrada na branch compartilhada;
6. [DAD-05 - Contrato metodologico](DAD-05_CONTRATO_METODOLOGICO.md);
7. [DAD-02 - Matriz de comparabilidade temporal](DAD-02_MATRIZ_COMPARABILIDADE_TEMPORAL.md);
8. decisao operacional provisoria da Sprint 3;
9. codigo e testes vigentes na branch compartilhada da Sprint 3;
10. implementacao da agregacao municipal da BE10, integrada pela PR #15;
11. implementacao final da composicao detalhada da BE12, integrada pela PR #18;
12. cenarios automatizados de QA06, com 33 testes aprovados na PR #3 do repositorio de QA.

Em caso de divergencia, a implementacao nao deve escolher uma regra
silenciosamente. A divergencia deve permanecer registrada ate a revisao dos
responsaveis.

## 3. Decisao consolidada sobre o alerta de cobertura

As fontes atuais concordam que:

- `cobertura_minima_percentual` permanece `null`;
- baixa cobertura nao torna o indice indisponivel;
- o resultado continua visivel e recebe um aviso informativo;
- `null` nao entra no denominador valido.

Os registros anteriores apresentavam estados diferentes para o valor do alerta:

| Fonte | Registro atual |
|---|---|
| Relatorio REQ05 | Apresenta `60%` como limiar oficial do aviso de precisao reduzida para a escola. |
| DAD06 | A auditoria Q8B encontrou 5.644 cenarios abaixo de `60%`, nenhum exatamente igual a `60%` e 228.344 acima. A evidencia sustenta o uso informativo do limiar, mas nao homologa o valor nem cobre o caso exato de fronteira. |
| Wiki da Sprint 4 | Foi conciliada com o REQ05: `60%` aplica-se somente a escola selecionada e nao bloqueia a exibicao. |
| DAD-05 | Confirma ausencia de corte minimo, mas nao define um limiar visual. |

Decisao consolidada para este contrato:

- `60.0` e o limiar confirmado por Requisitos para a cobertura dos indicadores da escola selecionada;
- a DAD06 valida empiricamente a aplicacao da regra e os denominadores agregados, mas nao altera o valor sem uma nova decisao de Requisitos;
- o alerta usa somente a cobertura da escola e nao e aplicado automaticamente a cobertura municipal por indicador;
- a regra nao bloqueia o calculo nem remove dados;
- o caso exatamente igual a `60%` nao apareceu na amostra Q8B, mas foi coberto por testes sinteticos de Backend e QA;
- denominador zero tambem foi coberto sinteticamente e preserva `null` na saida.

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
- `data.metodologia.limiar_alerta_cobertura_escopo`;
- `data.metodologia.validacao_empirica_cobertura_status`;
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
      "limiar_alerta_cobertura_status": "confirmado_req05",
      "limiar_alerta_cobertura_escopo": "escola_selecionada",
      "validacao_empirica_cobertura_status": "parcial_dad06_q8b",
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
            "cobertura_percentual": 88.3
          },
          "in_energia_rede_publica": {
            "quantidade_presentes": 90,
            "quantidade_validos": 94,
            "quantidade_sem_dados": 0,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 95.74,
            "cobertura_percentual": 100.0
          },
          "in_esgoto_rede_publica": {
            "quantidade_presentes": 60,
            "quantidade_validos": 82,
            "quantidade_sem_dados": 12,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 73.17,
            "cobertura_percentual": 87.23
          },
          "in_lixo_servico_coleta": {
            "quantidade_presentes": 75,
            "quantidade_validos": 84,
            "quantidade_sem_dados": 10,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 89.29,
            "cobertura_percentual": 89.36
          },
          "in_banheiro": {
            "quantidade_presentes": 83,
            "quantidade_validos": 85,
            "quantidade_sem_dados": 9,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 97.65,
            "cobertura_percentual": 90.43
          },
          "in_banheiro_pne": {
            "quantidade_presentes": 55,
            "quantidade_validos": 80,
            "quantidade_sem_dados": 14,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 68.75,
            "cobertura_percentual": 85.11
          },
          "in_biblioteca": {
            "quantidade_presentes": 50,
            "quantidade_validos": 82,
            "quantidade_sem_dados": 12,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 60.98,
            "cobertura_percentual": 87.23
          },
          "in_sala_leitura": {
            "quantidade_presentes": 35,
            "quantidade_validos": 78,
            "quantidade_sem_dados": 16,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 44.87,
            "cobertura_percentual": 82.98
          },
          "in_laboratorio_ciencias": {
            "quantidade_presentes": 30,
            "quantidade_validos": 80,
            "quantidade_sem_dados": 14,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 37.5,
            "cobertura_percentual": 85.11
          },
          "in_laboratorio_informatica": {
            "quantidade_presentes": 40,
            "quantidade_validos": 83,
            "quantidade_sem_dados": 11,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 48.19,
            "cobertura_percentual": 88.3
          },
          "in_sala_multiuso": {
            "quantidade_presentes": 25,
            "quantidade_validos": 77,
            "quantidade_sem_dados": 17,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 32.47,
            "cobertura_percentual": 81.91
          },
          "in_sala_atendimento_especial": {
            "quantidade_presentes": 20,
            "quantidade_validos": 55,
            "quantidade_sem_dados": 39,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 36.36,
            "cobertura_percentual": 58.51
          },
          "in_cozinha": {
            "quantidade_presentes": 82,
            "quantidade_validos": 85,
            "quantidade_sem_dados": 9,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 96.47,
            "cobertura_percentual": 90.43
          },
          "in_refeitorio": {
            "quantidade_presentes": 65,
            "quantidade_validos": 84,
            "quantidade_sem_dados": 10,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 77.38,
            "cobertura_percentual": 89.36
          },
          "in_quadra_esportes": {
            "quantidade_presentes": 60,
            "quantidade_validos": 83,
            "quantidade_sem_dados": 11,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 72.29,
            "cobertura_percentual": 88.3
          },
          "in_patio_coberto": {
            "quantidade_presentes": 70,
            "quantidade_validos": 84,
            "quantidade_sem_dados": 10,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 83.33,
            "cobertura_percentual": 89.36
          },
          "in_auditorio": {
            "quantidade_presentes": 15,
            "quantidade_validos": 78,
            "quantidade_sem_dados": 16,
            "quantidade_escolas_referencia": 94,
            "percentual_presentes": 19.23,
            "cobertura_percentual": 82.98
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
as 17 chaves com contagens `0` e percentuais `null`. Nenhuma classificacao de
cobertura municipal e inferida.

## 10. Cobertura e alerta

O contrato diferencia duas regras:

1. cobertura minima de calculo;
2. limiar informativo de alerta.

`cobertura_minima_percentual` permanece `null`. Nenhum resultado e bloqueado por
baixa cobertura.

Para a escola selecionada:

- `limiar_alerta_cobertura_percentual` vale `60.0`;
- `limiar_alerta_cobertura_status` vale `confirmado_req05`;
- `limiar_alerta_cobertura_escopo` vale `escola_selecionada`;
- `validacao_empirica_cobertura_status` vale `parcial_dad06_q8b`, pois a auditoria agregada foi concluida e os casos ausentes foram cobertos sinteticamente, mas ela nao substitui a amostra manual pendente;
- a comparacao usa a razao exata, antes do arredondamento, e o operador
  estritamente menor que o limiar;
- cobertura exatamente igual a `60.0` nao gera alerta;
- o frontend deve exibir aviso, mas manter todos os valores disponiveis.

No ponto anual, `cobertura_indicadores_reduzida` aplica essa regra aos
indicadores validos da escola sobre o total de 17. O campo e `true` somente
quando existe registro historico e a razao exata e menor que `60%`. Sem registro
historico, o campo e `false`, pois nao existe resultado cuja precisao deva ser
classificada.

Na composicao municipal, `cobertura_percentual` continua exposta para
transparencia, mas nao recebe classificacao automatica de cobertura reduzida.
Um alerta municipal somente pode ser adicionado depois de decisao explicita de
Requisitos e validacao de Dados.

A DAD06 confirmou a reconciliacao matematica dos agregados e registrou cenarios
abaixo e acima de `60%`. O caso exatamente igual ao limiar e o denominador zero
foram cobertos por testes sinteticos de Backend e QA. A amostra manual ampliada
continua pendente como evidencia empirica complementar, sem impedir o uso do
contrato tecnico com o estado metodologico explicitamente provisorio.

### Evidencia empirica incorporada da DAD06

- 13.764 registros analisados entre 2022 e 2025;
- 12.515 registros completos e 1.249 registros com os 17 indicadores nulos;
- 1.496 agregados auditados, cobrindo 22 municipios e 17 indicadores por ano;
- nenhuma divergencia matematica, duplicidade ou valor invalido nos agregados Q8B disponibilizados;
- 5.644 cenarios abaixo de `60%`, nenhum exatamente igual a `60%` e 228.344 acima;
- o municipio `1503804` apresentou cobertura media simulada abaixo de `60%` nos quatro anos;
- nao foram observados casos sem pares nem denominadores entre uma e quatro escolas comparadoras nesse recorte.

Esses resultados validam o comportamento agregado observado, mas nao provam os
casos ausentes da amostra. Os casos de fronteira e denominador zero foram
cobertos sinteticamente. Valores invalidos e duplicidades permanecem sujeitos
a tratamento explicito, sem conversao silenciosa.

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
- `cobertura_indicadores_reduzida = false`;
- `composicao_municipal = null`;
- indice, media e diferenca valem `null`;
- as contagens da escola e dos pares valem `0`.

### Registro anual com todos os indicadores nulos

- `registro_historico_disponivel = true`;
- `municipio_referencia` e preenchido;
- as 17 chaves de `composicao_escola` valem `null`;
- `cobertura_indicadores_percentual = 0.0`;
- `cobertura_indicadores_reduzida = true`;
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
- exibir o aviso da escola quando `cobertura_indicadores_reduzida = true`;
- nao inferir alerta municipal apenas a partir de `cobertura_percentual`;
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
- [x] Limiar de `60%` confirmado pelo REQ05 para a escola selecionada.
- [x] Escopo do alerta separado da cobertura municipal por indicador.
- [x] Auditoria agregada Q8B da DAD06 revisada e incorporada ao contrato.
- [x] Caso exatamente igual a `60%` e denominador zero validados por testes sinteticos.
- [ ] Amostra manual reproduzivel de 2022 a 2025 revisada por Dados.
- [x] Exemplo completo de quatro anos validado localmente pelo Backend.
- [x] Implementacao da BE12 e testes automatizados conferidos contra este contrato.
- [ ] Integracao completa validada por Dados, Frontend e QA.
- [ ] Revisao tecnica registrada no Taiga apos a integracao desta branch.

## 17. Dependencias para conclusao

### DAD06

A auditoria agregada confirmou:

- denominador valido por indicador;
- relacao entre validos, sem dados e total de escolas;
- uso do municipio historico de cada ano;
- exclusao da escola selecionada;
- reconciliacao matematica dos agregados Q8B.

Situacao apos a revisao:

- a PR #14 foi revisada e integrada na branch compartilhada;
- a PR #16 complementa a DAD06, mas a amostra empirica ampliada continua parcial;
- cobertura exatamente igual a `60%` e denominador zero foram cobertos por testes sinteticos;
- valores invalidos e duplicidades nao devem sofrer conversao silenciosa;
- a metodologia permanece explicitamente provisoria ate homologacao final.

### Requisitos

Requisitos deve revisar o contrato e manter os textos obrigatorios consistentes
com o REQ05 e com a wiki ja conciliada.

### Frontend

Frontend deve consumir os campos implementados pela BE12, preservar a
nulabilidade e validar a apresentacao integrada com a API.

### QA

QA06 cobriu os casos sinteticos de fronteira e denominador zero. Ainda deve ser
registrada a validacao HTTP integrada da resposta v3 com o frontend.

## 18. Fora de escopo da BE09

- alterar schemas Pydantic;
- alterar dominio, service, repository ou rota;
- implementar a agregacao municipal;
- criar endpoint de comparacao multipla;
- implementar classificacao por faixas;
- alterar o conjunto de 17 indicadores;
- homologar metodologia ou base de dados.

As mudancas funcionais da composicao foram tratadas nas historias e branches
proprias BE10 e BE12. Comparacao multipla, classificacoes e homologacao
metodologica permanecem fora do escopo da BE09.
