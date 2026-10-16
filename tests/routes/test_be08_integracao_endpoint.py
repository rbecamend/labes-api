import json
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_infraestrutura_service
from app.schemas.infraestrutura import ComparacaoInfraestruturaResponse
from main import app


ROTA = (
    "/infraestrutura/analise-temporal/escolas/"
    "15012345/comparacao-municipio"
)
CAMINHO_EXEMPLO = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "examples"
    / "be08-comparacao-escola-municipio.json"
)


def _carregar_exemplo() -> dict:
    return json.loads(CAMINHO_EXEMPLO.read_text(encoding="utf-8"))


class _ServicoIntegracao:
    def __init__(self, resposta: dict):
        self.resposta = resposta
        self.chamadas: list[int] = []

    async def build_comparacao_municipio(self, *, co_entidade: int) -> dict:
        self.chamadas.append(co_entidade)
        return self.resposta


@pytest.fixture
async def cliente_integrado():
    servico = _ServicoIntegracao(_carregar_exemplo())

    async def substituir_servico():
        return servico

    app.dependency_overrides[get_infraestrutura_service] = substituir_servico
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://testserver",
        ) as cliente:
            yield cliente, servico
    finally:
        app.dependency_overrides.pop(get_infraestrutura_service, None)


def test_exemplo_entregue_ao_frontend_respeita_schema_publico():
    resposta = ComparacaoInfraestruturaResponse.model_validate(_carregar_exemplo())

    assert [ponto.ano for ponto in resposta.data.serie] == [2022, 2023, 2024, 2025]


async def test_endpoint_esta_integrado_na_aplicacao_completa(cliente_integrado):
    cliente, servico = cliente_integrado

    resposta = await cliente.get(ROTA)

    assert resposta.status_code == 200
    assert resposta.json() == _carregar_exemplo()
    assert servico.chamadas == [15012345]


async def test_frontend_local_e_aceito_pelo_cors(cliente_integrado):
    cliente, _ = cliente_integrado

    resposta = await cliente.options(
        ROTA,
        headers={
            "Origin": "http://localhost:4200",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert resposta.status_code == 200
    assert resposta.headers["access-control-allow-origin"] == "http://localhost:4200"


async def test_openapi_publica_contrato_e_erros_da_integracao(cliente_integrado):
    cliente, _ = cliente_integrado
    caminho = ROTA.replace("15012345", "{co_entidade}")

    resposta = await cliente.get("/openapi.json")
    operacao = resposta.json()["paths"][caminho]["get"]

    assert set(operacao["responses"]) >= {"200", "404", "422", "500", "503"}
