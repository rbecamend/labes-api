from fractions import Fraction
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domain.infraestrutura import (
    SituacaoComparacaoInfraestrutura,
    cobertura_indicadores_reduzida,
)

# Envelopes genéricos reaproveitados de acessibilidade (PlotlyFigure, Grafico,
# Paginacao e os blocos de dados são idênticos entre os painéis).
from app.schemas.acessibilidade import (
    AnaliseTemporalData,
    Grafico,
    Paginacao,
    PainelData,
)

__all__ = [
    "PainelData",
    "PainelResponse",
    "PainelEscolasData",
    "PainelEscolasResponse",
    "MapaPonto",
    "MapaData",
    "MapaResponse",
    "AnaliseTemporalData",
    "AnaliseTemporalResponse",
    "FiltrosVisaoTemporalMunicipioInfraestrutura",
    "IndicadorVisaoTemporalMunicipioInfraestrutura",
    "PontoVisaoTemporalMunicipioInfraestrutura",
    "VisaoTemporalMunicipioInfraestruturaData",
    "VisaoTemporalMunicipioInfraestruturaResponse",
    "ANOS_COMPARACAO_INFRAESTRUTURA",
    "INDICADORES_COMPARACAO_INFRAESTRUTURA",
    "SituacaoComparacaoInfraestrutura",
    "CodigoErroComparacaoInfraestrutura",
    "EscolaComparacaoInfraestrutura",
    "MunicipioComparacaoInfraestrutura",
    "FiltrosComparacaoInfraestrutura",
    "ComposicaoMunicipalIndicadorInfraestrutura",
    "MetodologiaComparacaoInfraestrutura",
    "PontoComparacaoInfraestrutura",
    "ComparacaoInfraestruturaData",
    "ComparacaoInfraestruturaResponse",
    "ErroComparacaoInfraestruturaResponse",
]


ANOS_COMPARACAO_INFRAESTRUTURA = (2022, 2023, 2024, 2025)

INDICADORES_COMPARACAO_INFRAESTRUTURA = (
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
    "in_auditorio",
)

CodigoErroComparacaoInfraestrutura = Literal[
    "not_found",
    "internal_error",
    "warehouse_unavailable",
]


class _ContratoComparacaoInfraestrutura(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PainelResponse(BaseModel):
    """Resposta do painel: descrição + bloco de dados com gráficos e filtros."""

    descricao: str = Field(..., description="Identificador semântico do painel.")
    data: PainelData


class PainelEscolasData(BaseModel):
    grafico: Grafico = Field(..., description="Gráfico de métricas por escola (página atual).")
    paginacao: Paginacao = Field(..., description="Metadados de paginação.")


class PainelEscolasResponse(BaseModel):
    """Resposta paginada do gráfico de métricas por escola."""

    descricao: str = Field(..., description="Identificador semântico do recurso.")
    data: PainelEscolasData


class MapaPonto(BaseModel):
    """Escola por ano censo com as 17 métricas de infraestrutura e o score/
    classificação calculados on-the-fly a partir de silver.infraestrutura_comum
    (não há tabela pré-computada gold, notebook cell-9).

    O `score_infraestrutura` é a soma binária das 17 métricas (0–17). A
    classificação segue as faixas do notebook (`classificar_infraestrutura`) e,
    diferente dos outros painéis, NÃO tem faixa "Excelente"."""

    co_entidade: int
    nu_ano_censo: int
    pibid: int | None
    in_agua_potavel: float
    in_energia_rede_publica: float
    in_esgoto_rede_publica: float
    in_lixo_servico_coleta: float
    in_banheiro: float
    in_banheiro_pne: float
    in_biblioteca: float
    in_sala_leitura: float
    in_laboratorio_ciencias: float
    in_laboratorio_informatica: float
    in_sala_multiuso: float
    in_sala_atendimento_especial: float
    in_cozinha: float
    in_refeitorio: float
    in_quadra_esportes: float
    in_patio_coberto: float
    in_auditorio: float
    score_infraestrutura: int = Field(..., ge=0, le=17)
    classificacao_infraestrutura: Literal["Boa", "Média", "Baixa", "Inexistente"]


class MapaData(BaseModel):
    pontos: list[MapaPonto]


class MapaResponse(BaseModel):
    """Resposta do mapa: descrição + lista de pontos com score/classificação."""

    descricao: str = Field(..., description="Identificador semântico do mapa.")
    data: MapaData


class AnaliseTemporalResponse(BaseModel):
    """Resposta da análise temporal por tipo de localização e dependência."""

    descricao: str = Field(..., description="Identificador semântico do recurso.")
    data: AnaliseTemporalData


class EscolaComparacaoInfraestrutura(_ContratoComparacaoInfraestrutura):
    """Identificação da escola consultada."""

    co_entidade: int = Field(
        ..., ge=10_000_000, le=99_999_999, description="Código INEP da escola."
    )
    no_entidade: str = Field(..., min_length=1, description="Nome da escola.")


class MunicipioComparacaoInfraestrutura(_ContratoComparacaoInfraestrutura):
    """Município do registro mais recente da escola, usado para identificação."""

    co_municipio: int = Field(..., gt=0, description="Código IBGE do município.")
    no_municipio: str = Field(..., min_length=1, description="Nome do município.")


class FiltrosVisaoTemporalMunicipioInfraestrutura(
    _ContratoComparacaoInfraestrutura
):
    """Recorte aplicado a serie municipal."""

    rede_ensino: list[
        Literal["Federal", "Estadual", "Municipal", "Privada"]
    ] = Field(default_factory=list)
    ano_inicio: int = Field(..., ge=2000, le=2100)
    ano_fim: int = Field(..., ge=2000, le=2100)
    indicadores: list[str] = Field(..., min_length=1, max_length=17)

    @model_validator(mode="after")
    def validar_intervalo_e_indicadores(self) -> Self:
        if self.ano_inicio > self.ano_fim:
            raise ValueError("O ano inicial nao pode ser posterior ao ano final.")
        if len(self.indicadores) != len(set(self.indicadores)):
            raise ValueError("A lista de indicadores nao pode conter repeticoes.")
        if any(
            indicador not in INDICADORES_COMPARACAO_INFRAESTRUTURA
            for indicador in self.indicadores
        ):
            raise ValueError("A lista contem um indicador nao suportado.")
        return self


class IndicadorVisaoTemporalMunicipioInfraestrutura(
    _ContratoComparacaoInfraestrutura
):
    """Agregado anual de um indicador nas escolas do municipio."""

    quantidade_presentes: int = Field(..., ge=0)
    quantidade_validos: int = Field(..., ge=0)
    quantidade_sem_dados: int = Field(..., ge=0)
    percentual_presentes: float | None = Field(..., ge=0, le=100)
    cobertura_percentual: float | None = Field(..., ge=0, le=100)

    @model_validator(mode="after")
    def validar_percentuais(self) -> Self:
        if self.quantidade_presentes > self.quantidade_validos:
            raise ValueError("Presentes nao podem superar os valores validos.")

        percentual_esperado = (
            float(
                round(
                    Fraction(
                        100 * self.quantidade_presentes,
                        self.quantidade_validos,
                    ),
                    2,
                )
            )
            if self.quantidade_validos
            else None
        )
        total = self.quantidade_validos + self.quantidade_sem_dados
        cobertura_esperada = (
            float(round(Fraction(100 * self.quantidade_validos, total), 2))
            if total
            else None
        )
        if self.percentual_presentes != percentual_esperado:
            raise ValueError("Percentual de presenca nao corresponde as contagens.")
        if self.cobertura_percentual != cobertura_esperada:
            raise ValueError("Cobertura nao corresponde as contagens.")
        return self


class PontoVisaoTemporalMunicipioInfraestrutura(
    _ContratoComparacaoInfraestrutura
):
    """Composicao agregada do municipio em um ano."""

    ano: int = Field(..., ge=2000, le=2100)
    quantidade_escolas: int = Field(..., ge=0)
    indicadores: dict[str, IndicadorVisaoTemporalMunicipioInfraestrutura]

    @model_validator(mode="after")
    def validar_denominadores(self) -> Self:
        for agregado in self.indicadores.values():
            if (
                agregado.quantidade_validos + agregado.quantidade_sem_dados
                != self.quantidade_escolas
            ):
                raise ValueError(
                    "Validos e sem dados devem totalizar as escolas do ano."
                )
        return self


class VisaoTemporalMunicipioInfraestruturaData(
    _ContratoComparacaoInfraestrutura
):
    municipio: MunicipioComparacaoInfraestrutura
    filtros: FiltrosVisaoTemporalMunicipioInfraestrutura
    serie: list[PontoVisaoTemporalMunicipioInfraestrutura]

    @model_validator(mode="after")
    def validar_serie(self) -> Self:
        anos_esperados = list(
            range(self.filtros.ano_inicio, self.filtros.ano_fim + 1)
        )
        if [ponto.ano for ponto in self.serie] != anos_esperados:
            raise ValueError("A serie deve conter todos os anos do intervalo.")
        chaves_esperadas = set(self.filtros.indicadores)
        if any(
            set(ponto.indicadores) != chaves_esperadas
            for ponto in self.serie
        ):
            raise ValueError(
                "Cada ponto deve conter exatamente os indicadores solicitados."
            )
        return self


class VisaoTemporalMunicipioInfraestruturaResponse(
    _ContratoComparacaoInfraestrutura
):
    descricao: Literal["analise_temporal_infraestrutura_municipio"]
    data: VisaoTemporalMunicipioInfraestruturaData


class FiltrosComparacaoInfraestrutura(_ContratoComparacaoInfraestrutura):
    """Filtros temporais e rede aplicados à comparação Escola × Município."""

    rede_ensino: list[Literal["Federal", "Estadual", "Municipal", "Privada"]] = Field(
        default_factory=list,
        description="Redes de ensino usadas para selecionar as escolas de referência.",
    )
    ano_inicio: int = Field(..., ge=2000, le=2100)
    ano_fim: int = Field(..., ge=2000, le=2100)

    @model_validator(mode="after")
    def validar_intervalo_minimo(self) -> Self:
        if self.ano_fim - self.ano_inicio < 2:
            raise ValueError("O intervalo solicitado deve abranger pelo menos dois anos completos.")
        return self


class MetodologiaComparacaoInfraestrutura(_ContratoComparacaoInfraestrutura):
    """Metadados da metodologia provisória usada no cálculo."""

    versao: Literal["infraestrutura-v3-provisoria"] = Field(
        ..., description="Versão da metodologia aplicada."
    )
    homologada: Literal[False] = Field(
        ..., description="Indica que a metodologia ainda não foi homologada."
    )
    anos: list[int] = Field(
        ..., description="Anos efetivamente disponíveis no banco dentro do período solicitado."
    )
    indicadores: list[str] = Field(
        ...,
        min_length=17,
        max_length=17,
        description="Indicadores considerados no índice de infraestrutura.",
    )
    total_indicadores: Literal[17] = Field(
        ..., description="Total esperado de indicadores."
    )
    cobertura_minima_percentual: None = Field(
        ..., description="Sem corte mínimo de cobertura neste MVP."
    )
    limiar_alerta_cobertura_percentual: Literal[60.0] = Field(
        ..., description="Limiar informativo de cobertura da escola."
    )
    limiar_alerta_cobertura_status: Literal["confirmado_req05"] = Field(
        ..., description="Origem da decisão sobre o limiar informativo."
    )
    limiar_alerta_cobertura_escopo: Literal["escola_selecionada"] = Field(
        ..., description="Escopo do alerta, sem classificação municipal."
    )
    validacao_empirica_cobertura_status: Literal["parcial_dad06_q8b"] = Field(
        ..., description="Estado da validação empírica da regra de cobertura."
    )
    bloqueia_resultado_por_cobertura: Literal[False] = Field(
        ..., description="Baixa cobertura não bloqueia nem oculta os resultados."
    )
    avisos: list[str] = Field(
        ..., min_length=2, description="Ressalvas para exibição ao usuário."
    )
    observacao: str = Field(
        ..., min_length=1, description="Ressalva metodológica para exibição."
    )

    @field_validator("anos")
    @classmethod
    def validar_anos(cls, anos: list[int]) -> list[int]:
        if any(type(ano) is not int or ano < 2000 or ano > 2100 for ano in anos):
            raise ValueError("Os anos disponíveis devem ser inteiros válidos.")
        if anos != sorted(set(anos)):
            raise ValueError("Os anos disponíveis devem ser únicos e crescentes.")
        return anos

    @field_validator("indicadores")
    @classmethod
    def validar_indicadores(cls, indicadores: list[str]) -> list[str]:
        if tuple(indicadores) != INDICADORES_COMPARACAO_INFRAESTRUTURA:
            raise ValueError(
                "A lista deve conter os 17 indicadores do contrato, nessa ordem."
            )
        return indicadores


class ComposicaoMunicipalIndicadorInfraestrutura(
    _ContratoComparacaoInfraestrutura
):
    """Contagens auditáveis de um indicador entre os pares municipais."""

    quantidade_presentes: int = Field(..., ge=0)
    quantidade_validos: int = Field(..., ge=0)
    quantidade_sem_dados: int = Field(..., ge=0)
    quantidade_escolas_referencia: int = Field(..., ge=0)
    percentual_presentes: float | None = Field(..., ge=0, le=100)
    cobertura_percentual: float | None = Field(..., ge=0, le=100)

    @model_validator(mode="after")
    def validar_contagens_e_percentuais(self) -> Self:
        if self.quantidade_presentes > self.quantidade_validos:
            raise ValueError("Presentes não podem superar os valores válidos.")
        if (
            self.quantidade_validos + self.quantidade_sem_dados
            != self.quantidade_escolas_referencia
        ):
            raise ValueError(
                "Válidos e sem dados devem totalizar as escolas de referência."
            )

        percentual_esperado = (
            float(
                round(
                    Fraction(
                        100 * self.quantidade_presentes,
                        self.quantidade_validos,
                    ),
                    2,
                )
            )
            if self.quantidade_validos
            else None
        )
        if self.percentual_presentes != percentual_esperado:
            raise ValueError("Percentual de presença não corresponde às contagens.")

        cobertura_esperada = (
            float(
                round(
                    Fraction(
                        100 * self.quantidade_validos,
                        self.quantidade_escolas_referencia,
                    ),
                    2,
                )
            )
            if self.quantidade_escolas_referencia
            else None
        )
        if self.cobertura_percentual != cobertura_esperada:
            raise ValueError("Cobertura municipal não corresponde às contagens.")
        return self


class PontoComparacaoInfraestrutura(_ContratoComparacaoInfraestrutura):
    """Resultado da comparação Escola × Município em um ano do contrato."""

    ano: int = Field(..., ge=2000, le=2100, description="Ano do Censo Escolar disponível.")
    situacao: SituacaoComparacaoInfraestrutura = Field(
        ..., description="Disponibilidade do ponto anual."
    )
    municipio_referencia: MunicipioComparacaoInfraestrutura | None = Field(
        ..., description="Município histórico usado no ponto anual."
    )
    registro_historico_disponivel: bool = Field(
        ..., description="Distingue uma linha histórica de uma lacuna anual."
    )
    indice_escola_percentual: float | None = Field(
        ..., ge=0, le=100, description="Índice calculado para a escola."
    )
    quantidade_indicadores_presentes: int = Field(
        ..., ge=0, description="Indicadores da escola iguais a 1."
    )
    quantidade_indicadores_validos: int = Field(
        ..., ge=0, description="Indicadores da escola iguais a 0 ou 1."
    )
    total_indicadores: Literal[17] = Field(
        ..., description="Total esperado de indicadores."
    )
    cobertura_indicadores_percentual: float | None = Field(
        ..., ge=0, le=100, description="Cobertura dos indicadores da escola."
    )
    cobertura_indicadores_reduzida: bool = Field(
        ..., description="Alerta informativo para cobertura escolar abaixo de 60%."
    )
    media_municipal_percentual: float | None = Field(
        ..., ge=0, le=100, description="Média simples dos pares válidos."
    )
    diferenca_pontos_percentuais: float | None = Field(
        ...,
        ge=-100,
        le=100,
        description="Índice da escola menos a média municipal.",
    )
    quantidade_pares_validos: int = Field(
        ..., ge=0, description="Pares efetivamente usados na média."
    )
    denominador_pares: int = Field(
        ..., ge=0, description="Outras escolas encontradas no município e ano."
    )
    cobertura_pares_percentual: float | None = Field(
        ..., ge=0, le=100, description="Cobertura dos pares municipais."
    )
    composicao_escola: dict[str, Literal[0, 1] | None] = Field(
        ..., description="Valores dos 17 indicadores da escola."
    )
    composicao_municipal: dict[
        str, ComposicaoMunicipalIndicadorInfraestrutura
    ] | None = Field(
        ..., description="Contagens por indicador entre os pares municipais."
    )

    @field_validator("composicao_escola", mode="before")
    @classmethod
    def validar_composicao_escola(
        cls, composicao: dict[str, int | None]
    ) -> dict[str, int | None]:
        if not isinstance(composicao, dict):
            raise ValueError("A composição da escola deve ser um objeto.")
        if set(composicao) != set(INDICADORES_COMPARACAO_INFRAESTRUTURA):
            raise ValueError(
                "A composição da escola deve conter exatamente os 17 indicadores."
            )
        if any(
            type(valor) is not int and valor is not None
            for valor in composicao.values()
        ):
            raise ValueError("Indicadores da escola devem ser 0, 1 ou nulos.")
        if any(valor not in (0, 1, None) for valor in composicao.values()):
            raise ValueError("Indicadores da escola devem ser 0, 1 ou nulos.")
        return composicao

    @field_validator("composicao_municipal", mode="before")
    @classmethod
    def validar_chaves_composicao_municipal(cls, composicao):
        if composicao is not None and set(composicao) != set(
            INDICADORES_COMPARACAO_INFRAESTRUTURA
        ):
            raise ValueError(
                "A composição municipal deve conter exatamente os 17 indicadores."
            )
        return composicao

    @model_validator(mode="after")
    def validar_contagens(self) -> Self:
        if (
            self.quantidade_indicadores_presentes
            > self.quantidade_indicadores_validos
        ):
            raise ValueError("Indicadores presentes não podem superar os válidos.")
        if self.quantidade_indicadores_validos > self.total_indicadores:
            raise ValueError("Indicadores válidos não podem superar o total.")
        if self.quantidade_pares_validos > self.denominador_pares:
            raise ValueError(
                "Pares válidos não podem superar o denominador de pares."
            )

        valores_escola = list(self.composicao_escola.values())
        if (
            sum(valor == 1 for valor in valores_escola)
            != self.quantidade_indicadores_presentes
        ):
            raise ValueError("A composição da escola não corresponde aos presentes.")
        if (
            sum(valor is not None for valor in valores_escola)
            != self.quantidade_indicadores_validos
        ):
            raise ValueError("A composição da escola não corresponde aos válidos.")

        if not self.registro_historico_disponivel:
            if self.municipio_referencia is not None:
                raise ValueError(
                    "Lacuna histórica não pode informar município de referência."
                )
            if any(valor is not None for valor in valores_escola):
                raise ValueError("Lacuna histórica deve ter composição escolar nula.")
            if self.composicao_municipal is not None:
                raise ValueError("Lacuna histórica não pode ter composição municipal.")
            if self.cobertura_indicadores_reduzida:
                raise ValueError("Lacuna histórica não recebe alerta de cobertura.")
        else:
            alerta_esperado = cobertura_indicadores_reduzida(
                self.quantidade_indicadores_validos,
                self.total_indicadores,
            )
            if self.cobertura_indicadores_reduzida != alerta_esperado:
                raise ValueError(
                    "Alerta de cobertura não corresponde ao limiar de 60%."
                )
            if (
                self.municipio_referencia is None
                and self.composicao_municipal is not None
            ):
                raise ValueError("Composição municipal exige município de referência.")

        if self.composicao_municipal is not None:
            denominadores = {
                item.quantidade_escolas_referencia
                for item in self.composicao_municipal.values()
            }
            if denominadores != {self.denominador_pares}:
                raise ValueError(
                    "A composição municipal deve usar o denominador de pares do ano."
                )

        cobertura_indicadores_esperada = float(
            round(
                Fraction(
                    100 * self.quantidade_indicadores_validos,
                    self.total_indicadores,
                ),
                2,
            )
        )
        if self.cobertura_indicadores_percentual != cobertura_indicadores_esperada:
            raise ValueError("Cobertura dos indicadores não corresponde às contagens.")

        if (
            self.quantidade_indicadores_validos == 0
            and self.indice_escola_percentual is not None
        ):
            raise ValueError(
                "Índice da escola deve ser nulo sem indicadores válidos."
            )
        elif self.quantidade_indicadores_validos > 0:
            indice_esperado = float(
                round(
                    Fraction(
                        100 * self.quantidade_indicadores_presentes,
                        self.quantidade_indicadores_validos,
                    ),
                    2,
                )
            )
            if self.indice_escola_percentual != indice_esperado:
                raise ValueError("Índice da escola não corresponde às contagens.")

        if (
            self.denominador_pares == 0
            and self.cobertura_pares_percentual is not None
        ):
            raise ValueError("Cobertura dos pares deve ser nula sem pares.")
        elif self.denominador_pares > 0:
            cobertura_esperada = float(
                round(
                    Fraction(
                        100 * self.quantidade_pares_validos,
                        self.denominador_pares,
                    ),
                    2,
                )
            )
            if self.cobertura_pares_percentual != cobertura_esperada:
                raise ValueError("Cobertura dos pares não corresponde às contagens.")

        if (self.media_municipal_percentual is None) != (
            self.quantidade_pares_validos == 0
        ):
            raise ValueError("Média municipal deve refletir os pares válidos.")

        if self.situacao == "disponivel":
            if (
                self.indice_escola_percentual is None
                or self.media_municipal_percentual is None
                or self.diferenca_pontos_percentuais is None
                or self.quantidade_pares_validos == 0
                or self.denominador_pares == 0
            ):
                raise ValueError("Situação disponivel exige índice e comparação.")
        elif self.situacao == "escola_sem_dados":
            if (
                self.indice_escola_percentual is not None
                or self.diferenca_pontos_percentuais is not None
            ):
                raise ValueError(
                    "Situação escola_sem_dados exige índice e diferença nulos."
                )
        elif self.situacao == "sem_pares_validos":
            if (
                self.indice_escola_percentual is None
                or self.denominador_pares == 0
                or self.quantidade_pares_validos != 0
                or self.media_municipal_percentual is not None
                or self.diferenca_pontos_percentuais is not None
            ):
                raise ValueError(
                    "Situação sem_pares_validos exige escola e pares sem índice."
                )
        elif self.situacao == "sem_pares_municipio" and (
                self.indice_escola_percentual is None
                or self.denominador_pares != 0
                or self.quantidade_pares_validos != 0
                or self.media_municipal_percentual is not None
                or self.diferenca_pontos_percentuais is not None
            ):
                raise ValueError(
                    "Situação sem_pares_municipio exige ausência de pares."
                )
        return self


class ComparacaoInfraestruturaData(_ContratoComparacaoInfraestrutura):
    escola: EscolaComparacaoInfraestrutura = Field(
        ..., description="Escola consultada."
    )
    municipio: MunicipioComparacaoInfraestrutura = Field(
        ..., description="Município mais recente para identificação."
    )
    filtros: FiltrosComparacaoInfraestrutura = Field(
        ..., description="Rede de referência e intervalo temporal solicitados."
    )
    metodologia: MetodologiaComparacaoInfraestrutura = Field(
        ..., description="Metodologia aplicada ao cálculo."
    )
    serie: list[PontoComparacaoInfraestrutura] = Field(
        ...,
        description="Série dos anos efetivamente disponíveis no banco dentro do intervalo.",
    )

    @model_validator(mode="after")
    def validar_serie(self) -> Self:
        anos_metodologia = self.metodologia.anos
        anos_serie = [ponto.ano for ponto in self.serie]
        if anos_serie != anos_metodologia:
            raise ValueError("A série deve corresponder aos anos disponíveis informados na metodologia.")
        if any(
            ano < self.filtros.ano_inicio or ano > self.filtros.ano_fim
            for ano in anos_serie
        ):
            raise ValueError("A série contém ano fora do intervalo solicitado.")
        return self


class ComparacaoInfraestruturaResponse(_ContratoComparacaoInfraestrutura):
    """Resposta da comparação temporal entre uma escola e seu município."""

    descricao: Literal["comparacao_infraestrutura_escola_municipio"] = Field(
        ..., description="Identificador semântico do recurso."
    )
    data: ComparacaoInfraestruturaData


class ErroComparacaoInfraestruturaResponse(_ContratoComparacaoInfraestrutura):
    """Erro controlado da rota de comparação Escola × Município."""

    code: CodigoErroComparacaoInfraestrutura = Field(
        ..., description="Código estável do erro."
    )
    message: str = Field(
        ..., min_length=1, description="Mensagem legível do erro."
    )
