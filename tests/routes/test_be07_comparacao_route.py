import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError

from app.core.dependencies import get_infraestrutura_service
from app.core.exceptions import AppError, NotFoundError, app_error_handler
from app.routes.infraestrutura import router
from app.schemas.infraestrutura import (
    ANOS_COMPARACAO_INFRAESTRUTURA,
    INDICADORES_COMPARACAO_INFRAESTRUTURA,
)


ROTA = (
    "/infraestrutura/analise-temporal/escolas/"
    "15012345/comparacao-municipio"
)


def _ponto(ano: int) -> dict:
    return {
        "ano": ano,
        "situacao": "sem_pares_municipio",
        "indice_escola_percentual": 76.47,
        "quantidade_indicadores_presentes": 13,
        "quantidade_indicadores_validos": 17,
        "total_indicadores": 17,
        "cobertura_indicadores_percentual": 100.0,
        "media_municipal_percentual": None,
        "diferenca_pontos_percentuais": None,
        "quantidade_pares_validos": 0,
        "denominador_pares": 0,
        "cobertura_pares_percentual": None,
    }


def _resposta_valida() -> dict:
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


class _Servico:
    def __init__(self, *, resposta=None, erro=None):
        self.resposta = resposta
        self.erro = erro
        self.chamadas = []

    async def build_comparacao_municipio(self, *, co_entidade):
        self.chamadas.append(co_entidade)
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
    transport = ASGITransport(
        app=_aplicacao(servico),
        raise_app_exceptions=False,
    )
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as cliente:
        return await cliente.get(caminho)


async def test_rota_retorna_contrato_v2_e_chama_servico():
    servico = _Servico(resposta=_resposta_valida())

    resposta = await _get(servico, ROTA)

    assert resposta.status_code == 200
    assert resposta.json()["data"]["metodologia"]["total_indicadores"] == 17
    assert servico.chamadas == [15012345]


async def test_rota_rejeita_codigo_inep_sem_oito_digitos():
    servico = _Servico(resposta=_resposta_valida())

    resposta = await _get(
        servico,
        "/infraestrutura/analise-temporal/escolas/123/comparacao-municipio"
    )

    assert resposta.status_code == 422
    assert servico.chamadas == []


@pytest.mark.parametrize(
    ("erro", "status_code", "code"),
    [
        (NotFoundError("Escola não encontrada."), 404, "not_found"),
        (SQLAlchemyError("warehouse offline"), 503, "warehouse_unavailable"),
        (RuntimeError("falha inesperada"), 500, "internal_error"),
    ],
)
async def test_rota_mapeia_erros_controlados(erro, status_code, code):
    resposta = await _get(_Servico(erro=erro), ROTA)

    assert resposta.status_code == status_code
    assert resposta.json()["code"] == code
    assert set(resposta.json()) == {"code", "message"}


async def test_openapi_documenta_resposta_e_erros_da_rota():
    resposta = await _get(
        _Servico(resposta=_resposta_valida()),
        "/openapi.json",
    )
    operacao = resposta.json()["paths"][ROTA.replace(
        "15012345", "{co_entidade}"
    )]["get"]

    assert set(operacao["responses"]) >= {"200", "404", "422", "500", "503"}
