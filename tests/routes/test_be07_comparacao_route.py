import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
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


def _cliente(servico: _Servico) -> TestClient:
    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(router)
    app.dependency_overrides[get_infraestrutura_service] = lambda: servico
    return TestClient(app, raise_server_exceptions=False)


def test_rota_retorna_contrato_v2_e_chama_servico():
    servico = _Servico(resposta=_resposta_valida())

    resposta = _cliente(servico).get(ROTA)

    assert resposta.status_code == 200
    assert resposta.json()["data"]["metodologia"]["total_indicadores"] == 17
    assert servico.chamadas == [15012345]


def test_rota_rejeita_codigo_inep_sem_oito_digitos():
    servico = _Servico(resposta=_resposta_valida())

    resposta = _cliente(servico).get(
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
def test_rota_mapeia_erros_controlados(erro, status_code, code):
    resposta = _cliente(_Servico(erro=erro)).get(ROTA)

    assert resposta.status_code == status_code
    assert resposta.json()["code"] == code
    assert set(resposta.json()) == {"code", "message"}


def test_openapi_documenta_resposta_e_erros_da_rota():
    cliente = _cliente(_Servico(resposta=_resposta_valida()))

    operacao = cliente.get("/openapi.json").json()["paths"][ROTA.replace(
        "15012345", "{co_entidade}"
    )]["get"]

    assert set(operacao["responses"]) >= {"200", "404", "422", "500", "503"}
