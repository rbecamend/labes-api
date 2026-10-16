# SIE - DAD-03B | Validação empírica exploratória

**Funcionalidade:** Análise Temporal de Infraestrutura - Escola × Município  
**Recorte reportado:** 2022–2025  
**Natureza:** validação empírica exploratória concluída; não constitui homologação semântica nem autorização de publicação.

> **Atualização transversal (16/10/2026):** esta DAD-03B não testou a API. A [DAD-04 oficial](DAD-04_CONCILIACAO_API_OFICIAL.md), integrada pela [PR #12](https://github.com/rbecamend/labes-api/pull/12), conciliou depois a rota HTTP com repositório controlado; PostgreSQL real permanece pendente. As evidências empíricas abaixo não foram reescritas.

## 1. Objetivo e escopo

Registrar a seleção determinística, as populações anuais, os diagnósticos territoriais e os resultados da primeira execução e da extração complementar de Q1–Q4. A extração complementar foi concluída em 12/10/2026, conforme resultados fornecidos para esta consolidação. Não houve nova consulta ao banco nesta atualização documental.

Os resultados permanecem exploratórios. A execução e a conferência computacional dos dados brutos não homologam o significado dos indicadores, o conjunto temporal S, sua interpretação ou sua publicação. O índice não deve ser interpretado como medida de qualidade escolar nem como evidência causal. Esta DAD-03B não testou a API; a DAD-04 exercitou posteriormente somente a rota experimental.

## 2. Protocolo de segurança reportado

As execuções foram reportadas sob a conta `sie_auditoria`, usando uma única transação `REPEATABLE READ READ ONLY`, timeout de conexão de 5 segundos e `statement_timeout` de 20 segundos. O escopo de leitura ficou restrito às consultas Q1–Q4 e às relações autorizadas `silver.infraestrutura_comum` e `gold.dim_municipio`. A Q1 precedeu a construção dos 16 parâmetros tipados da Q2; Q3 e Q4 foram executadas em seguida.

Na extração complementar, o preflight foi aprovado, com zero controles reprovados. O resultado agregado foi informado; os valores individuais de cada controle não estão disponíveis no workspace e não são reproduzidos neste relatório. Nenhuma credencial é registrada.

## 3. Primeira execução

Os resultados da primeira execução cobriram os quatro anos de 2022–2025, em snapshot distinto do complementar. Foram reportadas as populações municipais, a elegibilidade das comparadoras, o índice da escola selecionada, a média municipal e a diferença em pontos percentuais. A tabela anual anterior foi retirada da versão publicável porque suas frações e contagens, combinadas com o recorte, descrevem uma escola individual mesmo sem código INEP. Os valores históricos não foram alterados; a evidência detalhada deve permanecer em armazenamento de acesso controlado, ainda a ser localizado e confirmado pela equipe.

A população de Q4 reportada foi 54 registros em 2022, 53 em 2023, 53 em 2024 e 53 em 2025, totalizando 213. Q3 retornou 16 linhas, mas somente dez foram exibidas no terminal da primeira execução.

Nenhuma linha individual de Q1/Q2, vetor de indicadores ou série de índice por escola acompanha a versão publicável.

## 4. Extração complementar

**Data informada:** 12/10/2026  
**Snapshot:** os detalhes do snapshot PostgreSQL não foram disponibilizados neste workspace. O identificador da pasta temporária da extração foi omitido da versão publicável; não comprova armazenamento estável.

Resultados reportados para a extração complementar:

| Consulta | Linhas retornadas | Estado SQL reportado |
|---|---:|---|
| Q1 | 4 | complete |
| Q2 | 155 | complete |
| Q3 | 16 | complete |
| Q4 | 4 | complete |

Os quatro anos (2022–2025) foram reportados com status `complete`; as contagens anuais de comparadoras, retiradas da versão publicável, constam da evidência detalhada a localizar. A validação matemática foi reportada como `complete`. A integridade foi reportada para dez arquivos, com zero divergências SHA-256. O preflight foi aprovado, com zero controles reprovados.

A saída ou o pacote de artefatos da extração complementar não foi localizado no workspace durante esta atualização. Assim, esses totais e estados são registrados como resultados fornecidos e verificados na revisão externa, não como verificações executadas novamente nesta sessão. Não foi possível registrar uma localização permanente comprovada para os dez artefatos ou conferir seus conteúdos e hashes localmente. Não adicionar arquivos de dados escolares ao Git.

### 4.1 Correspondência do alvo entre execuções

Para a primeira execução, município e escola selecionada foram identificados na evidência histórica restrita. Os quatro resultados da Q1 complementar, que permitiriam confrontar esses identificadores, não estão disponíveis no workspace. Portanto, a equivalência do município e da escola selecionada entre snapshots não pôde ser conferida aqui nem é demonstrada pelos identificadores editoriais deste documento.

A comparação de 16/16 resultados concordantes é registrada como reportada pela revisão externa. Sem a evidência de Q1 dos dois snapshots, este documento não caracteriza essa concordância como reprodução comprovada para o mesmo alvo. Os snapshots são tratados separadamente.

## 5. Validação computacional e conferência aritmética

A validação matemática dos indicadores brutos da extração complementar foi reportada como `complete`. Segundo a revisão externa, a conferência usou os 17 valores originais por escola/ano para recontar indicadores válidos e valores iguais a 1, recalcular os índices individuais sem arredondamento intermediário, verificar comparadoras elegíveis e exclusão da escola selecionada, recontar N e recalcular a média aritmética não ponderada e diferenças em pontos percentuais. O resultado reportado foi concordância de 16 em 16 comparações com a primeira execução.

Os valores brutos, os numeradores e denominadores por escola/ano, as quatro linhas integrais de Q1, a saída completa de Q2 e os registros de validação independente não estão presentes no workspace. A conferência é, portanto, documentada como computacionalmente concluída conforme evidência reportada, mas não reproduzida a partir dos artefatos nesta sessão. Não há divergência reportada; a ausência de artefatos locais limita a inspeção documental independente.

A conferência aritmética anual das frações foi reportada sem arredondamento intermediário. As contas por ano e escola foram retiradas da versão publicável; sua eventual reprodução depende dos vetores brutos e dos artefatos de validação em acesso controlado, cuja localização atual não foi confirmada. A referência segue definida como média aritmética não ponderada dos índices individuais das comparadoras elegíveis, excluída a escola selecionada.

## 6. Diagnósticos territoriais

Na primeira execução, Q3 retornou 16 linhas, das quais dez foram exibidas. Na extração complementar, Q3 retornou 16 linhas; o conteúdo completo dessas linhas não está disponível no workspace para reprodução neste relatório.

Q4 retornou quatro linhas agregadas na extração complementar, correspondentes a 2022–2025. A distribuição reportada na primeira execução foi 54, 53, 53 e 53 registros por ano, respectivamente, total de 213. Os quatro resultados de Q4 da extração complementar foram reportados como completos; seus valores não foram disponibilizados para uma conferência de diferenças por ano nesta sessão.

Os diagnósticos não identificam, por si sós, causas de diferenças nem demonstram comparabilidade territorial histórica.

## 7. Estados de validação e encerramento

1. **Execução SQL:** `complete`, conforme resultados reportados para a extração complementar (Q1: 4, Q2: 155, Q3: 16, Q4: 4).
2. **Validação matemática:** `complete`, conforme resultado reportado; os 17 indicadores brutos foram usados na conferência computacional descrita, mas os arquivos não estão presentes no workspace para reprodução independente nesta sessão.
3. **Preflight:** aprovado, zero controles reprovados, conforme resultado reportado. Resultados individuais dos controles não disponíveis neste workspace.
4. **Integridade dos artefatos:** dez arquivos verificados, zero divergências SHA-256, conforme resultado reportado. Localização permanente e conteúdo dos arquivos não verificados neste workspace.
5. **Concordância entre execuções:** 16/16 resultados concordantes, conforme resultado reportado. A equivalência dos identificadores de município e escola entre Q1 dos dois snapshots não pôde ser confirmada; não se afirma reprodução comprovada para o mesmo alvo.
6. **Homologação semântica e autorização de publicação:** pendentes, fora do escopo deste encerramento.

**VALIDAÇÃO EMPÍRICA EXPLORATÓRIA CONCLUÍDA.**

Este encerramento não altera os estados das etapas e decisões metodológicas:

- **DAD-01:** NÃO HOMOLOGADA.
- **DAD-02:** matriz preliminar.
- **DAD-05:** contrato metodológico condicional.
- **Conjunto S:** indicadores candidatos, sem homologação semântica.
- **Publicação de indicadores oficiais:** não autorizada.

## 8. Pendências preservadas para a integração oficial Escola × Município

O encerramento da validação empírica não homologa o método nem autoriza publicação. A lista abaixo registra os gates metodológicos do plano original. Houve desenvolvimento experimental depois desta DAD, mas a PR #44 não deve ser incorporada ao backend compartilhado. A integração oficial depende das BE-07/BE-08 e de nova validação com a rota BE-05:

1. decisão formal sobre a homologação da DAD-01 e estabilização da matriz temporal DAD-02;
2. decisão sobre o contrato metodológico condicional da DAD-05, incluindo o conjunto S, ressalvas para cobertura parcial no MVP sem corte mínimo, tratamento de ausências, exclusões, integridade e interpretação dos índices;
3. confirmação documentada de equivalência dos identificadores de escola selecionada e município entre a primeira execução e a extração complementar, se a alegação de reprodução para o mesmo alvo for necessária;
4. preservação e localização controlada das evidências completas da extração complementar fora do Git, com manifesto e hashes, caso sejam requeridas para auditoria posterior;
5. validação da implementação oficial contra o contrato HTTP BE-05 antes de qualquer alegação de funcionamento integrado.

Nenhuma API foi testada ou implementada pela DAD-03B. Não se declara indicador oficial nem autorização de publicação.
