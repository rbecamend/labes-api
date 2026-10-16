import pytest
from pydantic import ValidationError

from app.schemas.infraestrutura import (
    ANOS_COMPARACAO_INFRAESTRUTURA,
    INDICADORES_COMPARACAO_INFRAESTRUTURA,
    ComparacaoInfraestruturaResponse,
    ErroComparacaoInfraestruturaResponse,
)


def _ponto(ano: int, situacao: str = "disponivel") -> dict:
    return {
        "ano": ano,
        "situacao": situacao,
        "indice_escola_percentual": 76.47,
        "quantidade_indicadores_presentes": 13,
        "quantidade_indicadores_validos": 17,
        "total_indicadores": 17,
        "cobertura_indicadores_percentual": 100.0,
        "media_municipal_percentual": 64.71,
        "diferenca_pontos_percentuais": 11.76,
        "quantidade_pares_validos": 85,
        "denominador_pares": 94,
        "cobertura_pares_percentual": 90.43,
    }


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
                "versao": "infraestrutura-v2-provisoria",
                "homologada": False,
                "anos": list(ANOS_COMPARACAO_INFRAESTRUTURA),
                "indicadores": list(INDICADORES_COMPARACAO_INFRAESTRUTURA),
                "total_indicadores": 17,
                "cobertura_minima_percentual": None,
                "observacao": "Metodologia provisória e não homologada.",
            },
            "serie": [_ponto(ano) for ano in ANOS_COMPARACAO_INFRAESTRUTURA],
        },
    }


def test_schema_valida_resposta_completa_do_contrato_v2():
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
