# BE15 — entrega da visão temporal municipal conforme REQ07

**Tarefa:** [#72 — BE15, Sprint 5](https://tree.taiga.io/project/rebecamendonca-sie-v2/us/72).
**Data:** 15/11/2026. **Estado da entrega:** implementação disponível para integração e QA; não representa homologação metodológica nem aceite final.

## O que foi corrigido

A versão inicial (`63ce24c`) retornava contagens e percentuais por indicador, mas não a média municipal necessária à linha única da REQ07. Esta entrega acrescenta o cálculo e as contagens anuais de escolas, preserva os agregados por indicador e exige pelo menos dois anos inclusivos (2023–2024 é válido; 2024–2024 retorna 422).

Referência funcional: seção de regras de cálculo do PDF **[SP5][REQ-07] Consolidar requisitos e UX da análise temporal (Escola × Município e Visão Município)**, anexado à [REQ07 #69](https://tree.taiga.io/project/rebecamendonca-sie-v2/us/69). A [proposta DAD08](DAD-08_PROPOSTA_HOMOLOGACAO_METODOLOGIA.md) examinou a implementação anterior; suas afirmações de que a BE15 não retorna média escolar descrevem aquele commit, não esta entrega. O documento original e suas evidências foram preservados. Esta atualização funcional não converte a proposta DAD08 em metodologia homologada.

## Regra implementada

1. Selecionar município, ano, rede(s) e indicadores. Sem filtro de indicadores, usar os 17 do catálogo; é necessário ao menos um. Sem filtro de rede, incluir todas as escolas do recorte. Não existe escola-alvo a excluir nesta visão.
2. Para cada escola/ano, calcular `100 × respostas 1 / respostas válidas (0 ou 1)` nos indicadores selecionados. `NULL` não significa ausência do recurso e não entra no denominador escolar.
3. Calcular a **média aritmética simples desses índices escolares**, com o mesmo peso para cada escola que tenha ao menos uma resposta válida. Escolas inteiramente sem informação ficam fora da média, mas permanecem na contagem de elegíveis.
4. Arredondar somente o resultado público final para duas casas decimais. Não arredondar os índices escolares antes da média.

Exemplo sintético discriminante: escola A `(1, NULL)` tem índice 100%; B `(0, 1)` tem 50%; C `(NULL, NULL)` não tem índice. A média municipal é **75%**, com **3 elegíveis, 2 com informação e 1 sem dados**. Não é a proporção global de respostas `2/3 = 66,67%` nem a média dos percentuais por indicador.

## Contrato para FE16 e QA09

`GET /infraestrutura/analise-temporal/municipios/{co_municipio}`

Exemplo de consulta:

```text
/infraestrutura/analise-temporal/municipios/1501402?ano_inicio=2023&ano_fim=2024&rede_ensino=Municipal&indicadores=in_agua_potavel&indicadores=in_biblioteca
```

`data.serie` contém todos os anos solicitados, em ordem crescente, inclusive lacunas. Cada ponto traz:

| Campo | Uso |
| --- | --- |
| `ano` | Ano da observação, não apenas o ano mais recente |
| `quantidade_escolas` | Escolas distintas elegíveis naquele município/ano/rede |
| `quantidade_escolas_com_informacao` | Escolas com ao menos um 0/1 nos indicadores selecionados |
| `quantidade_escolas_sem_dados` | Elegíveis menos escolas com informação |
| `cobertura_media_percentual` | Média simples dos índices escolares, de 0 a 100 ou `null` |
| `situacao` | `com_dados`, `sem_dados` ou `denominador_zero` |
| `indicadores` | Detalhamento legado por indicador, preservado para conferência |

Apesar do nome funcional `cobertura_media_percentual`, esse campo mede **disponibilidade de infraestrutura**; não deve ser confundido com a cobertura de respostas `indicadores[chave].cobertura_percentual` (válidos/elegíveis). `percentual_presentes` continua sendo presentes/válidos **daquele indicador**.

| Situação anual | Média | Apresentação prevista na REQ07 |
| --- | --- | --- |
| Nenhuma escola elegível | `null` / `denominador_zero` | Não calculada |
| Há escolas, nenhuma tem informação válida | `null` / `sem_dados` | Sem dados |
| Há informação válida e nenhum recurso presente | `0` / `com_dados` | 0%, não ausência de dados |

Os cards de resumo superior usam o último ano **selecionado**, mesmo se for uma lacuna; os cards inferiores usam o respectivo ponto anual. Não preencher lacunas copiando o ano anterior.

`data.metodologia` explicita:

```json
{
  "versao": "infraestrutura-municipio-v1-req07-provisoria",
  "homologada": false,
  "formula": "media_simples_indices_escolares",
  "avisos": [
    "Esta análise utiliza metodologia de cálculo em caráter provisório e pendente de homologação.",
    "O índice representa disponibilidade de infraestrutura, não qualidade escolar."
  ]
}
```

FE16 deve apresentar os avisos metodológicos e os estados distintos. Os campos antigos foram preservados, mas consumidores com validação estrita precisam aceitar os novos campos; consultas de um único ano deixam de ser válidas conforme REQ07.

## Integridade e ressalvas metodológicas

- Duplicatas idênticas nos indicadores selecionados contam uma vez por escola/ano. Valores conflitantes (inclusive `NULL` versus 0/1) ou fora de 0/1/NULL bloqueiam a série solicitada com **HTTP 503, `code=source_data_inconsistent`**. É uma proteção provisória: não escolhe arbitrariamente um registro nem transforma inválidos em ausência de informação. A política definitiva depende de Dados.
- HTTP 503 `warehouse_unavailable` é indisponibilidade de acesso ao banco, distinta de inconsistência na fonte. Ambos constam no OpenAPI; 404 significa município não encontrado e 422 recorte inválido.
- O cálculo segue a população disponível na Silver: registros sem código de escola continuam excluídos; redes sem correspondência na dimensão podem ficar fora quando há filtro. Diagnóstico da base real, completude da população, conflitos cadastrais de município/rede e decisão sobre exclusões permanecem com Dados/QA. A proteção implementada não certifica toda a integridade cadastral.
- Uma escola com poucos indicadores válidos recebe o mesmo peso que outra com respostas completas; não há limiar mínimo de cobertura homologado aplicado à visão municipal. Disponibilidade parcial pode afetar a interpretação.
- Mudanças de população escolar, rede e preenchimento entre anos podem alterar a média sem representar melhoria/piora na mesma coorte. Não é medida de qualidade escolar, ranking ou evidência causal.
- A seleção e equivalência semântica dos 17 indicadores entre anos, a elegibilidade e a política de avisos precisam de homologação em **DAD08 #70**. A implementação e os testes não substituem esse aceite.
- Não foram executados testes contra PostgreSQL/base real ou validação visual do frontend nesta entrega. As evidências SQL usam SQLite em memória e dados sintéticos; HTTP é exercitado em processo, sem servidor externo.

## Verificação reproduzível

Ambiente desta execução: Python 3.12.3, pytest 9.1.1, dependências da `.venv` local. Os testes DAD04 que usam comunicação entre threads foram executados fora do isolamento restrito, que os deixava em espera. Nenhuma base oficial foi alterada.

```bash
python -m pytest -q tests/repositories/test_be15_visao_temporal_municipio_sql.py tests/services/test_be15_visao_temporal_municipio.py tests/routes/test_be15_visao_temporal_municipio.py
python -m pytest -q -ra
```

Cobertura BE15: média simples versus proporção global; respostas parciais; contagens escolares; filtros de rede e indicador; 17 indicadores padrão; duplicatas; valores inválidos; arredondamento final; zero real versus dois estados de indisponibilidade; lacunas; intervalo mínimo; erros; schema/OpenAPI e fluxo HTTP → serviço → SQL → resposta.

**Resultado final:** **36/36 testes BE15 aprovados**. Suíte completa: **194 aprovados, 3 falhas preexistentes e 1 ignorado (198 coletados)**. A verificação `git diff --check` não apresentou erros de whitespace. Os percentuais por indicador também são arredondados com frações exatas, evitando divergência com a validação pública em casos como 3,175% → 3,18%.

Comparação de regressão: a base anterior `d15090e` foi exportada para uma cópia temporária e testada com o mesmo interpretador/dependências: **172 aprovados, 3 falhas, 1 ignorado (176 coletados)**. As três falhas preexistentes são:

- `tests/routes/test_dad04_conciliacao_oficial.py::test_http_compara_serie_e_oraculo_sintetico_independente`
- `tests/routes/test_dad04_conciliacao_oficial.py::test_http_preserva_ano_sem_observacao_e_sem_pares_validos`
  - Os resultados esperados não incluem campos já existentes da resposta Escola × Município, como referência municipal, disponibilidade histórica e alerta de cobertura reduzida.
- `tests/services/test_conectividade_service.py::test_escolas_hover_traz_pibid_e_ideb`
  - Divergência de tipo no `customdata` do gráfico: `'7'` versus `7`.

O teste oficial DAD03B foi ignorado por ausência de `DAD03B_PACKAGE_DIR`, o pacote restrito externo ao Git. Essas falhas não foram ocultadas nem alteradas nesta BE15; **a suíte geral não está totalmente aprovada**.

## Passagem de responsabilidade

- **BE15/Rebeca:** implementação, contrato, testes locais e evidências entregues para teste. Correções que surgirem no aceite ainda podem exigir retorno ao backend.
- **REQ07/Dados (DAD08):** confirmar critérios e homologar metodologia/população/políticas de integridade.
- **FE16 #74:** consumir o contrato, representar estados e mostrar avisos.
- **QA09 #75:** validar cenários integrados e dados reais, registrar defeitos e aceite.

Não é necessário declarar a metodologia homologada para disponibilizar o backend provisório a FE16/QA09. O estado apropriado da BE15 é **Ready for test**, não **Done** por aceite completo.
