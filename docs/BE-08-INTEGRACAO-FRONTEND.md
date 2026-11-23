# BE-08 — Integração da comparação Escola × Município

## Endpoint

```http
GET /infraestrutura/analise-temporal/escolas/{co_entidade}/comparacao-municipio
```

`co_entidade` é o código INEP da escola com exatamente oito dígitos. A rota
retorna sempre os anos `2022`, `2023`, `2024` e `2025`, nessa ordem.

Em desenvolvimento, considerando a API em `http://localhost:8000`:

```bash
curl http://localhost:8000/infraestrutura/analise-temporal/escolas/15012345/comparacao-municipio
```

O arquivo [de exemplo](examples/be08-comparacao-escola-municipio.json) contém
uma resposta completa validada automaticamente pelo mesmo schema utilizado
pela API.

## Configuração do frontend

- URL local da API: `http://localhost:8000`.
- Swagger: `http://localhost:8000/docs`.
- OpenAPI: `http://localhost:8000/openapi.json`.
- `http://localhost:4200` e `http://127.0.0.1:4200` são aceitos pelo CORS.
- Outras origens devem ser informadas em `ALLOW_ORIGINS`, separadas por vírgula.

Exemplo:

```env
ALLOW_ORIGINS=https://frontend.exemplo.br,https://homolog.exemplo.br
```

## Regras de consumo

- `null` significa ausência de dado; não deve ser convertido em zero.
- A série já vem ordenada e com as lacunas de 2022–2025 preenchidas.
- `situacao` pode ser `disponivel`, `escola_sem_dados`,
  `sem_pares_validos` ou `sem_pares_municipio`.
- O frontend não deve ligar pontos separados por `indice_escola_percentual = null`.
- Os cartões devem usar o último ano da série conforme a decisão de interface.
- A metodologia é provisória e não homologada, como indicado nos metadados.

## Erros

| HTTP | Código/corpo | Tratamento esperado |
|---:|---|---|
| `404` | `not_found` | Escola não encontrada na fonte consultada. |
| `422` | Erro de validação do FastAPI | Código vazio, malformado ou fora de oito dígitos. |
| `500` | `internal_error` | Falha interna inesperada. |
| `503` | `warehouse_unavailable` | Warehouse temporariamente indisponível. |

Erros controlados possuem o formato:

```json
{
  "code": "warehouse_unavailable",
  "message": "Não foi possível consultar os dados de infraestrutura."
}
```

## Evidência da integração

O teste `tests/routes/test_be08_integracao_endpoint.py` garante que:

1. a rota está registrada na aplicação completa;
2. o exemplo entregue ao frontend é aceito pelo schema público;
3. a resposta atravessa o endpoint sem alteração de contrato;
4. o CORS permite o frontend local;
5. o OpenAPI documenta `200`, `404`, `422`, `500` e `503`.
