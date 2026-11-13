import pytest

from app.core.exceptions import NotFoundError
from app.services.infraestrutura_service import (
    METRIC_FIELDS,
    InfraestruturaService,
)


class _Repositorio:
    def __init__(self, *, identificacao=None, registros=None):
        self.identificacao = identificacao
        self.registros = registros or []
        self.chamadas = []

    async def find_identificacao_municipio(self, *, co_municipio):
        self.chamadas.append(("identificacao", co_municipio))
        return self.identificacao

    async def find_serie_temporal_municipio(self, **kwargs):
        self.chamadas.append(("serie", kwargs))
        return self.registros


async def test_monta_intervalo_com_lacunas_e_preserva_denominadores():
    repo = _Repositorio(
        identificacao={
            "co_municipio": 1501402,
            "no_municipio": "Belem",
        },
        registros=[
            {
                "ano": 2022,
                "quantidade_escolas": 3,
                "in_agua_potavel__presentes": 1,
                "in_agua_potavel__validos": 2,
            }
        ],
    )

    resposta = await InfraestruturaService(repo).build_visao_temporal_municipio(
        co_municipio=1501402,
        rede_ensino=["Municipal"],
        ano_inicio=2022,
        ano_fim=2024,
        indicadores=["in_agua_potavel"],
    )

    assert resposta["descricao"] == "analise_temporal_infraestrutura_municipio"
    assert [ponto["ano"] for ponto in resposta["data"]["serie"]] == [
        2022,
        2023,
        2024,
    ]
    agua = resposta["data"]["serie"][0]["indicadores"]["in_agua_potavel"]
    assert agua == {
        "quantidade_presentes": 1,
        "quantidade_validos": 2,
        "quantidade_sem_dados": 1,
        "percentual_presentes": 50.0,
        "cobertura_percentual": 66.67,
    }
    lacuna = resposta["data"]["serie"][1]
    assert lacuna["quantidade_escolas"] == 0
    assert lacuna["indicadores"]["in_agua_potavel"]["percentual_presentes"] is None
    assert lacuna["indicadores"]["in_agua_potavel"]["cobertura_percentual"] is None
    assert repo.chamadas[1][1]["rede_ensino"] == ["Municipal"]


async def test_usa_os_dezessete_indicadores_por_padrao():
    indicadores = [chave for chave, _ in METRIC_FIELDS]
    registro = {"ano": 2025, "quantidade_escolas": 1}
    for indicador in indicadores:
        registro[f"{indicador}__presentes"] = 0
        registro[f"{indicador}__validos"] = 0
    repo = _Repositorio(
        identificacao={"co_municipio": 1501402, "no_municipio": "Belem"},
        registros=[registro],
    )

    resposta = await InfraestruturaService(repo).build_visao_temporal_municipio(
        co_municipio=1501402,
        ano_inicio=2025,
        ano_fim=2025,
    )

    assert resposta["data"]["filtros"]["indicadores"] == indicadores
    assert len(resposta["data"]["serie"][0]["indicadores"]) == 17


async def test_municipio_inexistente_retorna_not_found_sem_consultar_serie():
    repo = _Repositorio(identificacao=None)

    with pytest.raises(NotFoundError, match="1501402"):
        await InfraestruturaService(repo).build_visao_temporal_municipio(
            co_municipio=1501402,
            ano_inicio=2022,
            ano_fim=2025,
        )

    assert repo.chamadas == [("identificacao", 1501402)]


async def test_rejeita_intervalo_invertido_antes_de_consultar_repositorio():
    repo = _Repositorio()

    with pytest.raises(ValueError, match="ano inicial"):
        await InfraestruturaService(repo).build_visao_temporal_municipio(
            co_municipio=1501402,
            ano_inicio=2025,
            ano_fim=2022,
        )

    assert repo.chamadas == []
