from decimal import Decimal

import pytest

from app.core.exceptions import NotFoundError, SourceDataInconsistentError
from app.schemas.infraestrutura import PontoVisaoTemporalMunicipioInfraestrutura
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
                "quantidade_escolas_com_informacao": 2,
                "cobertura_media_percentual": 50.0,
                "quantidade_escolas_inconsistentes": 0,
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
    assert lacuna["quantidade_escolas_com_informacao"] == 0
    assert lacuna["quantidade_escolas_sem_dados"] == 0
    assert lacuna["situacao"] == "denominador_zero"
    assert lacuna["cobertura_media_percentual"] is None
    primeiro = resposta["data"]["serie"][0]
    assert primeiro["cobertura_media_percentual"] == 50
    assert primeiro["quantidade_escolas_sem_dados"] == 1
    assert primeiro["situacao"] == "com_dados"
    assert lacuna["indicadores"]["in_agua_potavel"]["percentual_presentes"] is None
    assert lacuna["indicadores"]["in_agua_potavel"]["cobertura_percentual"] is None
    assert repo.chamadas[1][1]["rede_ensino"] == ["Municipal"]


async def test_usa_os_dezessete_indicadores_por_padrao():
    indicadores = [chave for chave, _ in METRIC_FIELDS]
    registro = {"ano": 2025, "quantidade_escolas": 1,
                "quantidade_escolas_com_informacao": 0,
                "cobertura_media_percentual": None,
                "quantidade_escolas_inconsistentes": 0}
    for indicador in indicadores:
        registro[f"{indicador}__presentes"] = 0
        registro[f"{indicador}__validos"] = 0
    repo = _Repositorio(
        identificacao={"co_municipio": 1501402, "no_municipio": "Belem"},
        registros=[registro],
    )

    resposta = await InfraestruturaService(repo).build_visao_temporal_municipio(
        co_municipio=1501402,
        ano_inicio=2024,
        ano_fim=2025,
    )

    assert resposta["data"]["filtros"]["indicadores"] == indicadores
    assert len(resposta["data"]["serie"][0]["indicadores"]) == 17
    ponto = resposta["data"]["serie"][1]
    assert ponto["situacao"] == "sem_dados"
    assert ponto["quantidade_escolas_sem_dados"] == 1
    assert ponto["cobertura_media_percentual"] is None
    assert resposta["data"]["metodologia"]["homologada"] is False


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


async def test_rejeita_um_unico_ano():
    repo = _Repositorio()
    with pytest.raises(ValueError, match="dois anos"):
        await InfraestruturaService(repo).build_visao_temporal_municipio(
            co_municipio=1501402, ano_inicio=2024, ano_fim=2024,
        )
    assert repo.chamadas == []


async def test_nao_publica_percentual_sobre_fonte_inconsistente():
    repo = _Repositorio(
        identificacao={"co_municipio": 1501402, "no_municipio": "Belem"},
        registros=[{"quantidade_escolas_inconsistentes": 1}],
    )
    with pytest.raises(SourceDataInconsistentError):
        await InfraestruturaService(repo).build_visao_temporal_municipio(
            co_municipio=1501402, ano_inicio=2023, ano_fim=2024,
        )


@pytest.mark.parametrize("presentes,validos,campo", [
    (127, 4000, "percentual_presentes"),
    (127, 127, "cobertura_percentual"),
])
def test_arredondamento_dos_agregados_coincide_com_contrato(presentes, validos, campo):
    ponto = InfraestruturaService._compor_ponto_temporal_municipio(
        ano=2024, indicadores=["in_agua_potavel"],
        registro={
            "quantidade_escolas": 4000,
            "quantidade_escolas_com_informacao": validos,
            "cobertura_media_percentual": Decimal(100 * presentes) / validos,
            "in_agua_potavel__presentes": presentes,
            "in_agua_potavel__validos": validos,
        },
    )
    assert ponto["indicadores"]["in_agua_potavel"][campo] == 3.18
    PontoVisaoTemporalMunicipioInfraestrutura.model_validate(ponto)
