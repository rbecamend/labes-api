from collections.abc import Collection, Iterable
from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

# TotalEscolas é genérico (apenas um inteiro) — reaproveitado de acessibilidade
# em vez de duplicar.
from app.domain.acessibilidade import TotalEscolas

__all__ = [
    "InfraestruturaMunicipio",
    "InfraestruturaTemporal",
    "TotalEscolas",
    "InfraestruturaDependencia",
    "InfraestruturaLocalizacao",
    "InfraestruturaEscola",
    "InfraestruturaRegistroBruto",
    "IndiceInfraestrutura",
    "ComparacaoInfraestruturaAno",
    "SituacaoComparacaoInfraestrutura",
    "calcular_indice_infraestrutura",
    "calcular_comparacao_infraestrutura_ano",
    "calcular_serie_comparacao_infraestrutura",
    "InfraestruturaTemporalDependencia",
]


SituacaoComparacaoInfraestrutura = Literal[
    "disponivel",
    "escola_sem_dados",
    "sem_pares_validos",
    "sem_pares_municipio",
]


@dataclass(frozen=True)
class InfraestruturaMunicipio:
    """
    Percentual de escolas por município que possuem a(s) métrica(s) de
    infraestrutura selecionada(s), sobre o total de escolas do município no
    recorte (ano + filtros de rede/localização).

    Fonte: silver.infraestrutura_comum (município já presente na silver via
    CO_MUNICIPIO/NO_MUNICIPIO). Valor de `percentual` em 0.0 - 100.0, com 2 casas.
    """

    codigo_municipio: int
    municipio: str
    percentual: float
    total_escolas: int


@dataclass(frozen=True)
class InfraestruturaTemporal:
    """
    Percentual de escolas com a métrica de infraestrutura selecionada, por
    (ano censo, tipo de localização). Alimenta o gráfico de evolução temporal
    por tipo de localização (urbana/rural).

    Fonte: silver.infraestrutura_comum + gold.dim_tp_localizacao.
    """

    ano: int
    codigo_localizacao: int
    localizacao: str
    percentual: float


@dataclass(frozen=True)
class InfraestruturaDependencia:
    """
    Percentual de escolas por tipo de dependência administrativa com a métrica
    de infraestrutura selecionada = 1, sobre o total de escolas daquela
    dependência no recorte filtrado.

    Fonte: silver.infraestrutura_comum + gold.dim_tp_dependencia.
    """

    codigo_dependencia: int
    dependencia: str
    percentual: float
    total_escolas: int


@dataclass(frozen=True)
class InfraestruturaLocalizacao:
    """
    Percentual de escolas por tipo de localização (Urbana/Rural) com a métrica
    de infraestrutura selecionada = 1, sobre o total de escolas daquela
    localização no recorte filtrado.

    Fonte: silver.infraestrutura_comum + gold.dim_tp_localizacao.
    """

    codigo_localizacao: int
    localizacao: str
    percentual: float
    total_escolas: int


@dataclass(frozen=True)
class InfraestruturaEscola:
    """
    Uma escola com o valor (0/1) de cada uma das 17 métricas de
    infraestrutura e o score (soma das 17). Quando o filtro de `ano` não é
    informado, representa o censo mais recente disponível para a escola.

    Fonte: silver.infraestrutura_comum. Alimenta o gráfico de barras
    empilhadas "Métricas de infraestrutura por escola" do painel.
    """

    co_entidade: int
    no_entidade: str
    nu_ano_censo: int
    metricas: dict[str, int]
    score: int


@dataclass(frozen=True)
class InfraestruturaRegistroBruto:
    """Registro de infraestrutura de uma escola em um ano do Censo Escolar.

    Este é o formato de entrada para as consultas da análise Escola × Município.
    Diferentemente dos objetos usados pelos gráficos atuais, os indicadores não
    são binarizados, agregados ou usados para calcular score nesta etapa. O valor
    ``None`` vindo de ``silver.infraestrutura_comum`` é preservado para que a
    camada de serviço possa distinguir ausência de dado de valor zero.
    """

    co_entidade: int
    no_entidade: str
    co_municipio: int
    no_municipio: str
    nu_ano_censo: int
    indicadores: dict[str, int | None]


@dataclass(frozen=True)
class IndiceInfraestrutura:
    """Resultado intermediário do índice de uma escola em um ano.

    ``presentes`` conta indicadores iguais a 1 e ``validos`` conta indicadores
    não nulos. A cobertura de indicadores é separada da cobertura de pares
    usada na comparação municipal.
    """

    percentual: float | None
    presentes: int
    validos: int
    total_indicadores: int
    cobertura_indicadores_percentual: float | None


@dataclass(frozen=True)
class ComparacaoInfraestruturaAno:
    """Comparação de uma escola com as demais escolas do município em um ano."""

    ano: int
    situacao: SituacaoComparacaoInfraestrutura
    indice_escola_percentual: float | None
    quantidade_indicadores_presentes: int
    quantidade_indicadores_validos: int
    total_indicadores: int
    cobertura_indicadores_percentual: float | None
    media_municipal_percentual: float | None
    diferenca_pontos_percentuais: float | None
    quantidade_pares_validos: int
    denominador_pares: int
    cobertura_pares_percentual: float | None


def _validar_cobertura_minima(cobertura_minima_percentual: float | None) -> None:
    if cobertura_minima_percentual is not None and not (
        0 <= cobertura_minima_percentual <= 100
    ):
        raise ValueError("A cobertura mínima deve estar entre 0 e 100.")


def _percentual_arredondado(proporcao: Fraction) -> float:
    """Arredonda uma proporção exata apenas ao produzir o percentual público."""
    return float(round(100 * proporcao, 2))


def _indice_exato(indice: IndiceInfraestrutura) -> Fraction | None:
    """Reusa elegibilidade e contagens do índice, sem arredondamento intermediário."""
    if indice.percentual is None:
        return None
    return Fraction(indice.presentes, indice.validos)


def calcular_indice_infraestrutura(
    indicadores: dict[str, int | None],
    *,
    indicadores_esperados: Collection[str] | None = None,
    cobertura_minima_percentual: float | None = None,
) -> IndiceInfraestrutura:
    """Calcula ``100 × presentes / válidos`` preservando a ausência de dados.

    Valores 0 e 1 são válidos, enquanto ``None`` é excluído do denominador.
    Quando uma lista de indicadores esperados é informada, chaves ausentes no
    registro são tratadas como nulas. A cobertura mínima é configurável para
    que a regra possa ser usada antes da homologação de um percentual oficial.
    """

    _validar_cobertura_minima(cobertura_minima_percentual)

    chaves = tuple(
        indicadores.keys()
        if indicadores_esperados is None
        else indicadores_esperados
    )
    if len(chaves) != len(set(chaves)):
        raise ValueError("A lista de indicadores esperados contém duplicatas.")
    valores = [indicadores.get(chave) for chave in chaves]

    invalidos = [valor for valor in valores if valor not in (0, 1, None)]
    if invalidos:
        raise ValueError("Indicadores de infraestrutura devem ser 0, 1 ou None.")

    total_indicadores = len(chaves)
    validos = sum(valor is not None for valor in valores)
    presentes = sum(valor == 1 for valor in valores)
    cobertura = (
        _percentual_arredondado(Fraction(validos, total_indicadores))
        if total_indicadores
        else None
    )

    percentual: float | None = None
    atende_cobertura = (
        cobertura_minima_percentual is None
        or (cobertura is not None and cobertura >= cobertura_minima_percentual)
    )
    if validos and atende_cobertura:
        percentual = _percentual_arredondado(Fraction(presentes, validos))

    return IndiceInfraestrutura(
        percentual=percentual,
        presentes=presentes,
        validos=validos,
        total_indicadores=total_indicadores,
        cobertura_indicadores_percentual=cobertura,
    )


def calcular_comparacao_infraestrutura_ano(
    escola: InfraestruturaRegistroBruto,
    referencias: Iterable[InfraestruturaRegistroBruto],
    *,
    indicadores_esperados: Collection[str] | None = None,
    cobertura_minima_percentual: float | None = None,
) -> ComparacaoInfraestruturaAno:
    """Compara uma escola com pares do mesmo município e ano.

    A escola consultada é sempre excluída das referências. Cada escola de
    referência com índice válido tem o mesmo peso na média municipal.
    """

    indice_escola = calcular_indice_infraestrutura(
        escola.indicadores,
        indicadores_esperados=indicadores_esperados,
        cobertura_minima_percentual=cobertura_minima_percentual,
    )
    indice_escola_exato = _indice_exato(indice_escola)

    pares = [
        registro
        for registro in referencias
        if registro.co_entidade != escola.co_entidade
        and registro.co_municipio == escola.co_municipio
        and registro.nu_ano_censo == escola.nu_ano_censo
    ]
    identificadores = [registro.co_entidade for registro in pares]
    if len(identificadores) != len(set(identificadores)):
        raise ValueError("Há escolas de referência duplicadas para o mesmo ano.")

    indices_pares = [
        _indice_exato(
            calcular_indice_infraestrutura(
                registro.indicadores,
                indicadores_esperados=indicadores_esperados,
                cobertura_minima_percentual=cobertura_minima_percentual,
            )
        )
        for registro in pares
    ]
    indices_validos = [indice for indice in indices_pares if indice is not None]

    denominador_pares = len(pares)
    quantidade_pares_validos = len(indices_validos)
    cobertura_pares = (
        _percentual_arredondado(
            Fraction(quantidade_pares_validos, denominador_pares)
        )
        if denominador_pares
        else None
    )
    media_municipal_exata = (
        sum(indices_validos, Fraction()) / quantidade_pares_validos
        if quantidade_pares_validos
        else None
    )
    media_municipal = (
        _percentual_arredondado(media_municipal_exata)
        if media_municipal_exata is not None
        else None
    )

    if indice_escola.percentual is None:
        situacao: SituacaoComparacaoInfraestrutura = "escola_sem_dados"
    elif denominador_pares == 0:
        situacao = "sem_pares_municipio"
    elif quantidade_pares_validos == 0:
        situacao = "sem_pares_validos"
    else:
        situacao = "disponivel"

    diferenca = (
        _percentual_arredondado(indice_escola_exato - media_municipal_exata)
        if indice_escola_exato is not None and media_municipal_exata is not None
        else None
    )

    return ComparacaoInfraestruturaAno(
        ano=escola.nu_ano_censo,
        situacao=situacao,
        indice_escola_percentual=indice_escola.percentual,
        quantidade_indicadores_presentes=indice_escola.presentes,
        quantidade_indicadores_validos=indice_escola.validos,
        total_indicadores=indice_escola.total_indicadores,
        cobertura_indicadores_percentual=(
            indice_escola.cobertura_indicadores_percentual
        ),
        media_municipal_percentual=media_municipal,
        diferenca_pontos_percentuais=diferenca,
        quantidade_pares_validos=quantidade_pares_validos,
        denominador_pares=denominador_pares,
        cobertura_pares_percentual=cobertura_pares,
    )


def calcular_serie_comparacao_infraestrutura(
    registros_escola: Iterable[InfraestruturaRegistroBruto],
    referencias: Iterable[InfraestruturaRegistroBruto],
    *,
    indicadores_esperados: Collection[str] | None = None,
    cobertura_minima_percentual: float | None = None,
) -> list[ComparacaoInfraestruturaAno]:
    """Calcula a série anual em ordem crescente de ano do Censo Escolar."""

    registros = list(registros_escola)
    anos = [registro.nu_ano_censo for registro in registros]
    if len(anos) != len(set(anos)):
        raise ValueError("Há mais de um registro da escola para o mesmo ano.")

    referencias_materializadas = list(referencias)
    return [
        calcular_comparacao_infraestrutura_ano(
            escola,
            referencias_materializadas,
            indicadores_esperados=indicadores_esperados,
            cobertura_minima_percentual=cobertura_minima_percentual,
        )
        for escola in sorted(registros, key=lambda registro: registro.nu_ano_censo)
    ]


@dataclass(frozen=True)
class InfraestruturaTemporalDependencia:
    """
    Percentual de escolas com a métrica de infraestrutura selecionada,
    por (ano censo, tipo de dependência administrativa). Alimenta o
    gráfico de evolução temporal por dependência no endpoint
    /analise-temporal.

    Fonte: silver.infraestrutura_comum + gold.dim_tp_dependencia.
    """

    ano: int
    codigo_dependencia: int
    dependencia: str
    percentual: float
