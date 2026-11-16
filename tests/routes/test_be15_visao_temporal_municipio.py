import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.dependencies import get_infraestrutura_service
from app.core.exceptions import AppError, NotFoundError, SourceDataInconsistentError, app_error_handler
from app.routes.infraestrutura import router
from app.schemas.infraestrutura import (
    ErroVisaoTemporalMunicipioInfraestruturaResponse,
    VisaoTemporalMunicipioInfraestruturaResponse,
)
from app.services.infraestrutura_service import AVISOS_METODOLOGIA_COMPARACAO


ROTA = "/infraestrutura/analise-temporal/municipios/1501402"


def _resposta_valida() -> dict:
    return {
        "descricao": "analise_temporal_infraestrutura_municipio",
        "data": {
            "municipio": {
                "co_municipio": 1501402,
                "no_municipio": "Belem",
            },
            "filtros": {
                "rede_ensino": ["Municipal"],
                "ano_inicio": 2023,
                "ano_fim": 2024,
                "indicadores": ["in_agua_potavel"],
            },
            "metodologia": {
                "versao": "infraestrutura-municipio-v1-req07-provisoria",
                "homologada": False,
                "formula": "media_simples_indices_escolares",
                "avisos": list(AVISOS_METODOLOGIA_COMPARACAO),
            },
            "serie": [
                {
                    "ano": ano,
                    "quantidade_escolas": 2,
                    "quantidade_escolas_com_informacao": 2,
                    "quantidade_escolas_sem_dados": 0,
                    "cobertura_media_percentual": 50.0,
                    "situacao": "com_dados",
                    "indicadores": {
                        "in_agua_potavel": {
                            "quantidade_presentes": 1,
                            "quantidade_validos": 2,
                            "quantidade_sem_dados": 0,
                            "percentual_presentes": 50.0,
                            "cobertura_percentual": 100.0,
                        }
                    },
                }
                for ano in (2023, 2024)
            ],
        },
    }


class _Servico:
    def __init__(self, *, resposta=None, erro=None):
        self.resposta = resposta
        self.erro = erro
        self.chamadas = []

    async def build_visao_temporal_municipio(self, **kwargs):
        self.chamadas.append(kwargs)
        if self.erro is not None:
            raise self.erro
        return self.resposta


def _aplicacao(servico: _Servico) -> FastAPI:
    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(router)

    async def substituir_servico():
        return servico

    app.dependency_overrides[get_infraestrutura_service] = substituir_servico
    return app


async def _get(servico: _Servico, caminho: str):
    async with AsyncClient(
        transport=ASGITransport(
            app=_aplicacao(servico),
            raise_app_exceptions=False,
        ),
        base_url="http://testserver",
    ) as cliente:
        return await cliente.get(caminho)


async def test_rota_encaminha_filtros_e_retorna_contrato():
    servico = _Servico(resposta=_resposta_valida())
    caminho = (
        f"{ROTA}?rede_ensino=Municipal&ano_inicio=2023&ano_fim=2024"
        "&indicadores=in_agua_potavel"
    )

    resposta = await _get(servico, caminho)

    assert resposta.status_code == 200
    assert resposta.json() == _resposta_valida()
    assert servico.chamadas == [
        {
            "co_municipio": 1501402,
            "rede_ensino": ["Municipal"],
            "ano_inicio": 2023,
            "ano_fim": 2024,
            "indicadores": ["in_agua_potavel"],
        }
    ]


async def test_rota_rejeita_codigo_municipal_fora_do_formato():
    servico = _Servico(resposta=_resposta_valida())

    resposta = await _get(
        servico,
        "/infraestrutura/analise-temporal/municipios/123",
    )

    assert resposta.status_code == 422
    assert servico.chamadas == []


async def test_rota_rejeita_intervalo_invertido():
    servico = _Servico(resposta=_resposta_valida())

    resposta = await _get(
        servico,
        f"{ROTA}?ano_inicio=2025&ano_fim=2022",
    )

    assert resposta.status_code == 422
    assert servico.chamadas == []


@pytest.mark.parametrize(
    ("erro", "status_code", "code"),
    [
        (NotFoundError("Municipio nao encontrado."), 404, "not_found"),
        (SQLAlchemyError("warehouse offline"), 503, "warehouse_unavailable"),
        (SourceDataInconsistentError("Conflito."), 503, "source_data_inconsistent"),
        (RuntimeError("falha inesperada"), 500, "internal_error"),
    ],
)
async def test_rota_mapeia_erros_controlados(erro, status_code, code):
    resposta = await _get(_Servico(erro=erro), ROTA)

    assert resposta.status_code == status_code
    assert resposta.json()["code"] == code
    ErroVisaoTemporalMunicipioInfraestruturaResponse.model_validate(resposta.json())


async def test_openapi_documenta_parametros_contrato_e_erros():
    resposta = await _get(
        _Servico(resposta=_resposta_valida()),
        "/openapi.json",
    )
    caminho = ROTA.replace("1501402", "{co_municipio}")
    operacao = resposta.json()["paths"][caminho]["get"]

    assert {item["name"] for item in operacao["parameters"]} == {
        "co_municipio",
        "rede_ensino",
        "ano_inicio",
        "ano_fim",
        "indicadores",
    }
    assert set(operacao["responses"]) >= {"200", "404", "422", "500", "503"}
    schemas = resposta.json()["components"]["schemas"]
    ponto = schemas["PontoVisaoTemporalMunicipioInfraestrutura"]
    assert set(ponto["required"]) >= {
        "cobertura_media_percentual", "situacao", "quantidade_escolas",
        "quantidade_escolas_com_informacao", "quantidade_escolas_sem_dados",
    }
    assert schemas["MetodologiaVisaoTemporalMunicipioInfraestrutura"]["properties"]["homologada"]["const"] is False
    erro = schemas["ErroVisaoTemporalMunicipioInfraestruturaResponse"]
    assert "source_data_inconsistent" in erro["properties"]["code"]["enum"]
    assert operacao["responses"]["503"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ErroVisaoTemporalMunicipioInfraestruturaResponse"
    )


@pytest.mark.parametrize("query", [
    "ano_inicio=2024&ano_fim=2024",
    "indicadores=",
    "indicadores=inventado",
    "rede_ensino=Inexistente",
])
async def test_rejeita_recortes_invalidos_antes_de_chamar_servico(query):
    servico = _Servico(resposta=_resposta_valida())
    resposta = await _get(servico, f"{ROTA}?{query}")
    assert resposta.status_code == 422
    assert servico.chamadas == []


@pytest.mark.parametrize("alteracao", [
    {"quantidade_escolas_sem_dados": 1},
    {"situacao": "sem_dados"},
    {"cobertura_media_percentual": None},
    {"cobertura_media_percentual": 101},
])
def test_contrato_rejeita_contagens_estado_ou_media_incoerentes(alteracao):
    resposta = _resposta_valida()
    resposta["data"]["serie"][0].update(alteracao)
    with pytest.raises(ValidationError):
        VisaoTemporalMunicipioInfraestruturaResponse.model_validate(resposta)
