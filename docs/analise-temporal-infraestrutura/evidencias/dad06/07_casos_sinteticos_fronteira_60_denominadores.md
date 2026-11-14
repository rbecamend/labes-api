# DAD06 — Casos sintéticos de fronteira, denominadores e exclusão

**Natureza:** exemplos fictícios para conferir aritmética; não foram executados no PostgreSQL nem na API. Não comprovam ocorrência empírica, política pública aprovada ou homologação metodológica.

## Definições e escopo do alerta

- **Cobertura da escola:** `100 × indicadores 0/1 / 17`. Somente esta cobertura recebe o aviso REQ05/BE09 quando a fração exata é **estritamente menor** que 60%; o índice continua calculável se houver dado válido.
- **Cobertura dos pares municipais:** `100 × escolas comparadoras com índice calculável / escolas comparadoras`, se o denominador for positivo. Não recebe automaticamente o aviso escolar.
- **Composição municipal de indicador:** presença `100 × respostas 1 / respostas 0/1` se houver válidas; cobertura `100 × respostas 0/1 / total de escolas` se houver escolas.

## Fronteira de 60%

| Caso | Dados sintéticos | Resultado | Interpretação |
|---|---|---|---|
| C1 | Escola: 10 válidos entre 17; 6 presentes | Cobertura `10/17 = 58,82%`; índice `6/10 = 60%` | Aviso escolar ativo; índice calculável. |
| C2 | Escola: 11 válidos entre 17; 7 presentes | Cobertura `11/17 = 64,71%`; índice `7/11 = 63,64%` | Aviso escolar inativo. |
| C3 | Função genérica com 3 válidos entre 5 indicadores **hipotéticos** | Cobertura `3/5 = 60%` exatos | Comparação `< 60%` falsa; **não é escola com 17 indicadores**. |
| C4 | Município: 3 comparadoras calculáveis entre 5 | Cobertura de pares `3/5 = 60%` exatos | Média dos três índices definida; sem alerta escolar municipal. |
| C5 | Indicador municipal: duas respostas `1`, uma `0`, duas `NULL` | Cobertura `3/5 = 60%`; presença `2/3 = 66,67%` | Grandezas diferentes; sem alerta escolar municipal. |

Com exatamente 17 indicadores, `v/17 = 60%` exigiria `v=10,2`, que não é inteiro. Não existe escola com cobertura exatamente igual a 60% nesse conjunto fixo: `10/17 = 58,82%` e `11/17 = 64,71%` são as coberturas vizinhas. C3 testa apenas a regra genérica.

## Denominadores zero

| Caso | Dados sintéticos | Resultado matemático |
|---|---|---|
| D1 | Escola-alvo única no município/ano; após excluí-la, `T=0,N=0` | Cobertura de pares `NULL`, referência `NULL`, diferença `NULL`. |
| D2 | Três comparadoras com 17 `NULL` cada; `T=3,N=0` | Cobertura de pares `0%`, referência `NULL`, diferença `NULL`. |
| D3 | Indicador com zero válidas e três `NULL`; `V=0,T=3` | Presença `NULL`, cobertura `0%`. |
| D4 | Indicador sem comparadoras; `V=0,T=0` | Presença e cobertura `NULL`. |
| D5 | Escola com 17 `NULL` | Cobertura escolar `0%`, índice `NULL`; não criar índice `0%`. |

## Exclusão individual: exercício sintético

Num grupo fictício com `T=5` escolas e `V=3` respostas válidas para um indicador:

- Se a escola excluída tinha valor válido, `T_auto=4`, `V_auto=2` e cobertura `2/4 = 50%`.
- Se a escola excluída tinha `NULL`, `T_auto=4`, `V_auto=3` e cobertura `3/4 = 75%`.

Esses resultados **não** comprovam a exclusão real de uma escola de Porto de Moz.

## Conferência aritmética

Em 13/11/2026, 14 verificações de frações exatas nesta revisão conferiram: `3/5=60%`; `10/17<60%`; `11/17>60%`; inexistência de `v/17=60%` para `0≤v≤17`; índices `6/10=60%` e `7/11=63,64%`; cobertura de pares `3/5=60%`; presença `2/3=66,67%`; `53+49=102`; `102+3=105`; Porto de Moz `53/102=51,96%` e `102/105=97,14%`; exclusões sintéticas `2/4=50%` e `3/4=75%`. **14/14 conferências passaram.** São verificações de aritmética documental, sem testes automatizados de backend e sem acesso ao PostgreSQL nesta rodada.
