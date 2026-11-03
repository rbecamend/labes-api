import pytest
from pydantic import ValidationError

from app.schemas.infraestrutura import (
    ANOS_COMPARACAO_INFRAESTRUTURA,
    INDICADORES_COMPARACAO_INFRAESTRUTURA,
    ComparacaoInfraestruturaResponse,
    ErroComparacaoInfraestruturaResponse,
    PontoComparacaoInfraestrutura,
)


def _composicao_escola(*, presentes: int = 13, validos: int = 17) -> dict:
    return {
        chave: 1 if indice < presentes else 0 if indice < validos else None
        for indice, chave in enumerate(INDICADORES_COMPARACAO_INFRAESTRUTURA)
    }


def _composicao_municipal(
    *, total: int = 94, presentes: int = 60, validos: int = 85
) -> dict:
    percentual = round(100 * presentes / validos, 2) if validos else None
    cobertura = round(100 * validos / total, 2) if total else None
    return {
        chave: {
            "quantidade_presentes": presentes,
            "quantidade_validos": validos,
            "quantidade_sem_dados": total - validos,
            "quantidade_escolas_referencia": total,
            "percentual_presentes": percentual,
            "cobertura_percentual": cobertura,
        }
        for chave in INDICADORES_COMPARACAO_INFRAESTRUTURA
    }


def _ponto(ano: int, situacao: str = "disponivel") -> dict:
    return {
        "ano": ano,
        "situacao": situacao,
        "municipio_referencia": {
            "co_municipio": 1501402,
            "no_municipio": "Belém",
        },
        "registro_historico_disponivel": True,
        "indice_escola_percentual": 76.47,
        "quantidade_indicadores_presentes": 13,
        "quantidade_indicadores_validos": 17,
        "total_indicadores": 17,
        "cobertura_indicadores_percentual": 100.0,
        "cobertura_indicadores_reduzida": False,
        "media_municipal_percentual": 64.71,
        "diferenca_pontos_percentuais": 11.76,
        "quantidade_pares_validos": 85,
        "denominador_pares": 94,
        "cobertura_pares_percentual": 90.43,
        "composicao_escola": _composicao_escola(),
        "composicao_municipal": _composicao_municipal(),
    }


def _ponto_situacao(situacao: str) -> dict:
    ponto = _ponto(2024, situacao)
    if situacao == "escola_sem_dados":
        ponto.update(
            indice_escola_percentual=None,
            quantidade_indicadores_presentes=0,
            quantidade_indicadores_validos=0,
            cobertura_indicadores_percentual=0.0,
            cobertura_indicadores_reduzida=True,
            diferenca_pontos_percentuais=None,
            composicao_escola=_composicao_escola(presentes=0, validos=0),
        )
    elif situacao == "sem_pares_validos":
        ponto.update(
            media_municipal_percentual=None,
            diferenca_pontos_percentuais=None,
            quantidade_pares_validos=0,
            cobertura_pares_percentual=0.0,
            composicao_municipal=_composicao_municipal(
                total=94,
                presentes=0,
                validos=0,
            ),
        )
    elif situacao == "sem_pares_municipio":
        ponto.update(
            media_municipal_percentual=None,
            diferenca_pontos_percentuais=None,
            quantidade_pares_validos=0,
            denominador_pares=0,
            cobertura_pares_percentual=None,
            composicao_municipal=_composicao_municipal(
                total=0,
                presentes=0,
                validos=0,
            ),
        )
    return ponto


def _resposta() -> dict:
    return {
        "descricao": "comparacao_infraestrutura_escola_municipio",
        "data": {
            "escola": {
                "co_entidade": 15012345,
                "no_entidade": "EMEF Exemplo",
            },
            "municipio": {
                "co_municipio": 1501402,
                "no_municipio": "Belém",
            },
            "metodologia": {
                "versao": "infraestrutura-v3-provisoria",
                "homologada": False,
                "anos": list(ANOS_COMPARACAO_INFRAESTRUTURA),
                "indicadores": list(INDICADORES_COMPARACAO_INFRAESTRUTURA),
                "total_indicadores": 17,
                "cobertura_minima_percentual": None,
                "limiar_alerta_cobertura_percentual": 60.0,
                "limiar_alerta_cobertura_status": "confirmado_req05",
                "limiar_alerta_cobertura_escopo": "escola_selecionada",
                "validacao_empirica_cobertura_status": "parcial_dad06_q8b",
                "bloqueia_resultado_por_cobertura": False,
                "avisos": [
                    "Metodologia provisória.",
                    "O índice não representa qualidade escolar.",
                ],
                "observacao": "Metodologia provisória e não homologada.",
            },
            "serie": [_ponto(ano) for ano in ANOS_COMPARACAO_INFRAESTRUTURA],
        },
    }


def test_schema_valida_resposta_completa_do_contrato_v3():
    resposta = ComparacaoInfraestruturaResponse.model_validate(_resposta())

    serializada = resposta.model_dump(mode="json")
    assert serializada["data"]["metodologia"]["total_indicadores"] == 17
    assert [ponto["ano"] for ponto in serializada["data"]["serie"]] == [
        2022,
        2023,
        2024,
        2025,
    ]


def test_json_schema_expoe_metadados_anuais_no_openapi():
    schema = ComparacaoInfraestruturaResponse.model_json_schema()
    ponto = schema["$defs"]["PontoComparacaoInfraestrutura"]

    assert {
        "quantidade_indicadores_presentes",
        "quantidade_indicadores_validos",
        "total_indicadores",
        "cobertura_indicadores_percentual",
        "quantidade_pares_validos",
        "denominador_pares",
        "cobertura_pares_percentual",
        "municipio_referencia",
        "registro_historico_disponivel",
        "cobertura_indicadores_reduzida",
        "composicao_escola",
        "composicao_municipal",
    } <= set(ponto["required"])


def test_schema_rejeita_serie_com_ano_ausente():
    payload = _resposta()
    payload["data"]["serie"].pop()

    with pytest.raises(ValidationError, match="at least 4 items"):
        ComparacaoInfraestruturaResponse.model_validate(payload)


def test_schema_rejeita_lista_de_indicadores_diferente_do_contrato():
    payload = _resposta()
    payload["data"]["metodologia"]["indicadores"][-1] = "indicador_invalido"

    with pytest.raises(ValidationError, match="17 indicadores do contrato"):
        ComparacaoInfraestruturaResponse.model_validate(payload)


def test_schema_rejeita_contagens_incoerentes():
    payload = _resposta()
    payload["data"]["serie"][0]["quantidade_indicadores_presentes"] = 18

    with pytest.raises(ValidationError, match="presentes não podem superar"):
        ComparacaoInfraestruturaResponse.model_validate(payload)


@pytest.mark.parametrize(
    "situacao",
    ["disponivel", "escola_sem_dados", "sem_pares_validos", "sem_pares_municipio"],
)
def test_schema_aceita_as_quatro_situacoes_coerentes(situacao):
    ponto = _ponto_situacao(situacao)

    assert PontoComparacaoInfraestrutura.model_validate(ponto).situacao == situacao


def test_schema_aceita_escola_sem_dados_com_ou_sem_pares():
    com_pares = _ponto_situacao("escola_sem_dados")
    sem_pares_validos = _ponto_situacao("escola_sem_dados")
    sem_pares_validos.update(
        media_municipal_percentual=None,
        quantidade_pares_validos=0,
        cobertura_pares_percentual=0.0,
    )
    sem_pares = _ponto_situacao("escola_sem_dados")
    sem_pares.update(
        media_municipal_percentual=None,
        quantidade_pares_validos=0,
        denominador_pares=0,
        cobertura_pares_percentual=None,
        composicao_municipal=_composicao_municipal(
            total=0,
            presentes=0,
            validos=0,
        ),
    )

    assert PontoComparacaoInfraestrutura.model_validate(
        com_pares
    ).media_municipal_percentual == 64.71
    assert PontoComparacaoInfraestrutura.model_validate(
        sem_pares_validos
    ).cobertura_pares_percentual == 0.0
    assert PontoComparacaoInfraestrutura.model_validate(
        sem_pares
    ).cobertura_pares_percentual is None


@pytest.mark.parametrize(
    ("presentes", "validos", "indice", "cobertura"),
    [
        (0, 0, None, 0.0),
        (0, 3, 0.0, 17.65),
        (1, 3, 33.33, 17.65),
        (2, 3, 66.67, 17.65),
        (13, 17, 76.47, 100.0),
    ],
)
def test_schema_aceita_indice_e_cobertura_coerentes(
    presentes, validos, indice, cobertura
):
    situacao = "escola_sem_dados" if validos == 0 else "sem_pares_municipio"
    ponto = _ponto_situacao(situacao)
    ponto.update(
        indice_escola_percentual=indice,
        quantidade_indicadores_presentes=presentes,
        quantidade_indicadores_validos=validos,
        cobertura_indicadores_percentual=cobertura,
        cobertura_indicadores_reduzida=validos * 5 < 17 * 3,
        composicao_escola=_composicao_escola(
            presentes=presentes,
            validos=validos,
        ),
    )

    validado = PontoComparacaoInfraestrutura.model_validate(ponto)
    assert validado.indice_escola_percentual == indice
    assert validado.cobertura_indicadores_percentual == cobertura


def test_schema_aceita_anos_sinteticos_sem_observacao():
    payload = _resposta()
    for indice in (1, 3):
        ponto = _ponto_situacao("escola_sem_dados")
        ponto.update(
            ano=ANOS_COMPARACAO_INFRAESTRUTURA[indice],
            municipio_referencia=None,
            registro_historico_disponivel=False,
            media_municipal_percentual=None,
            quantidade_pares_validos=0,
            denominador_pares=0,
            cobertura_pares_percentual=None,
            cobertura_indicadores_reduzida=False,
            composicao_municipal=None,
        )
        payload["data"]["serie"][indice] = ponto

    serie = ComparacaoInfraestruturaResponse.model_validate(payload).data.serie
    assert [serie[indice].indice_escola_percentual for indice in (1, 3)] == [
        None,
        None,
    ]


@pytest.mark.parametrize(
    ("situacao", "alteracoes", "mensagem"),
    [
        (
            "escola_sem_dados",
            {"indice_escola_percentual": 0.0},
            "nulo sem indicadores válidos",
        ),
        (
            "disponivel",
            {
                "quantidade_indicadores_validos": 0,
                "quantidade_indicadores_presentes": 0,
                "cobertura_indicadores_percentual": 0.0,
                "cobertura_indicadores_reduzida": True,
                "composicao_escola": _composicao_escola(
                    presentes=0,
                    validos=0,
                ),
            },
            "nulo sem indicadores válidos",
        ),
        (
            "disponivel",
            {"indice_escola_percentual": None},
            "Índice da escola não corresponde às contagens",
        ),
        (
            "disponivel",
            {"indice_escola_percentual": 76.46},
            "Índice da escola não corresponde às contagens",
        ),
        (
            "disponivel",
            {"cobertura_indicadores_percentual": None},
            "Cobertura dos indicadores não corresponde às contagens",
        ),
        (
            "disponivel",
            {"cobertura_indicadores_percentual": 99.99},
            "Cobertura dos indicadores não corresponde às contagens",
        ),
        (
            "escola_sem_dados",
            {"cobertura_indicadores_percentual": 1.0},
            "Cobertura dos indicadores não corresponde às contagens",
        ),
    ],
)
def test_schema_rejeita_indice_ou_cobertura_incoerentes(
    situacao, alteracoes, mensagem
):
    ponto = _ponto_situacao(situacao)
    ponto.update(alteracoes)

    with pytest.raises(ValidationError, match=mensagem):
        PontoComparacaoInfraestrutura.model_validate(ponto)


def test_schema_nao_subtrai_percentuais_arredondados_para_validar_diferenca():
    ponto = _ponto_situacao("disponivel")
    ponto.update(
        indice_escola_percentual=66.67,
        quantidade_indicadores_presentes=2,
        quantidade_indicadores_validos=3,
        cobertura_indicadores_percentual=17.65,
        media_municipal_percentual=33.33,
        diferenca_pontos_percentuais=33.33,
        quantidade_pares_validos=1,
        denominador_pares=1,
        cobertura_pares_percentual=100.0,
        cobertura_indicadores_reduzida=True,
        composicao_escola=_composicao_escola(presentes=2, validos=3),
        composicao_municipal=_composicao_municipal(
            total=1,
            presentes=1,
            validos=1,
        ),
    )

    assert (
        PontoComparacaoInfraestrutura.model_validate(ponto)
        .diferenca_pontos_percentuais
        == 33.33
    )


@pytest.mark.parametrize(
    ("situacao", "alteracoes"),
    [
        ("disponivel", {"indice_escola_percentual": None}),
        ("disponivel", {"media_municipal_percentual": None}),
        ("disponivel", {"diferenca_pontos_percentuais": None}),
        (
            "disponivel",
            {
                "quantidade_pares_validos": 0,
                "cobertura_pares_percentual": 0.0,
                "media_municipal_percentual": None,
            },
        ),
        ("escola_sem_dados", {"indice_escola_percentual": 76.47}),
        ("escola_sem_dados", {"diferenca_pontos_percentuais": 11.76}),
        ("escola_sem_dados", {"media_municipal_percentual": None}),
        ("sem_pares_validos", {"indice_escola_percentual": None}),
        (
            "sem_pares_validos",
            {"denominador_pares": 0, "cobertura_pares_percentual": None},
        ),
        (
            "sem_pares_validos",
            {
                "quantidade_pares_validos": 1,
                "cobertura_pares_percentual": 1.04,
                "media_municipal_percentual": 64.71,
            },
        ),
        ("sem_pares_validos", {"media_municipal_percentual": 64.71}),
        ("sem_pares_validos", {"diferenca_pontos_percentuais": 11.76}),
        ("sem_pares_municipio", {"indice_escola_percentual": None}),
        (
            "sem_pares_municipio",
            {"denominador_pares": 1, "cobertura_pares_percentual": 0.0},
        ),
        ("sem_pares_municipio", {"media_municipal_percentual": 64.71}),
        ("sem_pares_municipio", {"diferenca_pontos_percentuais": 11.76}),
        ("sem_pares_municipio", {"cobertura_pares_percentual": 0.0}),
        ("disponivel", {"cobertura_pares_percentual": 50.0}),
    ],
)
def test_schema_rejeita_situacoes_ou_coberturas_incoerentes(situacao, alteracoes):
    ponto = _ponto_situacao(situacao)
    ponto.update(alteracoes)

    with pytest.raises(ValidationError):
        PontoComparacaoInfraestrutura.model_validate(ponto)


@pytest.mark.parametrize(
    "code",
    ["not_found", "internal_error", "warehouse_unavailable"],
)
def test_schema_documenta_erros_controlados(code):
    erro = ErroComparacaoInfraestruturaResponse(
        code=code,
        message="Não foi possível processar a comparação.",
    )

    assert erro.code == code


def test_schema_rejeita_codigo_de_erro_fora_do_contrato():
    with pytest.raises(ValidationError):
        ErroComparacaoInfraestruturaResponse(
            code="database_error",
            message="Erro interno.",
        )
