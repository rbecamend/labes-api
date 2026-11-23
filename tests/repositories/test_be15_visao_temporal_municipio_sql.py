import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, insert

from app.models.infraestrutura import dim_tp_dependencia, infraestrutura_comum
from app.repositories.infraestrutura_repository import InfraestruturaRepository
from app.schemas.infraestrutura import VisaoTemporalMunicipioInfraestruturaResponse
from app.services.infraestrutura_service import InfraestruturaService
from app.core.exceptions import SourceDataInconsistentError
from tests.routes.test_be15_visao_temporal_municipio import ROTA, _aplicacao


class _Rows:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self

    def __iter__(self):
        return iter(self._rows)

    def first(self):
        return next(iter(self._rows), None)


class _RepositorioSqlite(InfraestruturaRepository):
    def __init__(self, engine):
        self.engine = engine

    async def _execute(self, stmt):
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).mappings().all()
        return _Rows(rows)


def _linha(id_, ano, municipio, agua, biblioteca=None, rede=3):
    row = {col.name: None for col in infraestrutura_comum.columns}
    row.update(
        CO_ENTIDADE=id_,
        NU_ANO_CENSO=ano,
        CO_MUNICIPIO=municipio,
        NO_ENTIDADE=f"Escola {id_}",
        NO_MUNICIPIO=f"Municipio {municipio}",
        TP_DEPENDENCIA=rede,
        IN_AGUA_POTAVEL=agua,
        IN_BIBLIOTECA=biblioteca,
    )
    return row


@pytest.fixture
def sqlite():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.exec_driver_sql("ATTACH DATABASE ':memory:' AS silver")
        conn.exec_driver_sql("ATTACH DATABASE ':memory:' AS gold")
        infraestrutura_comum.create(conn)
        dim_tp_dependencia.create(conn)
        conn.execute(
            insert(dim_tp_dependencia),
            [
                {"co_tp_dependencia": 2, "no_tp_dependencia": "Estadual"},
                {"co_tp_dependencia": 3, "no_tp_dependencia": "Municipal"},
            ],
        )
        conn.execute(
            insert(infraestrutura_comum),
            [
                _linha(15010001, 2022, 1501402, 1, 1),
                _linha(15010002, 2022, 1501402, 0, None),
                _linha(15010003, 2022, 1501402, None, 0, rede=2),
                _linha(15010001, 2022, 1501402, 1, 1),  # duplicata fisica
                _linha(15010004, 2022, 1500800, 1, 1),  # outro municipio
                _linha(15010001, 2023, 1501402, None, None),
            ],
        )
    yield engine
    engine.dispose()


async def test_agrega_escolas_distintas_e_preserva_null(sqlite):
    repo = _RepositorioSqlite(sqlite)

    registros = await repo.find_serie_temporal_municipio(
        co_municipio=1501402,
        ano_inicio=2022,
        ano_fim=2023,
        indicadores=["in_agua_potavel", "in_biblioteca"],
    )

    assert [registro["ano"] for registro in registros] == [2022, 2023]
    assert registros[0]["quantidade_escolas"] == 3
    assert registros[0]["in_agua_potavel__presentes"] == 1
    assert registros[0]["in_agua_potavel__validos"] == 2
    assert registros[0]["in_biblioteca__presentes"] == 1
    assert registros[0]["in_biblioteca__validos"] == 2
    assert registros[1]["quantidade_escolas"] == 1
    assert registros[1]["in_agua_potavel__validos"] == 0
    assert registros[0]["quantidade_escolas_com_informacao"] == 3
    assert registros[0]["cobertura_media_percentual"] == pytest.approx(100 / 3)
    assert registros[0]["quantidade_escolas_inconsistentes"] == 0
    assert registros[1]["quantidade_escolas_com_informacao"] == 0
    assert registros[1]["cobertura_media_percentual"] is None


async def test_filtra_rede_de_ensino_sem_alterar_as_regras_de_cobertura(sqlite):
    repo = _RepositorioSqlite(sqlite)

    registros = await repo.find_serie_temporal_municipio(
        co_municipio=1501402,
        ano_inicio=2022,
        ano_fim=2022,
        indicadores=["in_agua_potavel"],
        rede_ensino=["Municipal"],
    )

    assert registros[0]["quantidade_escolas"] == 2
    assert registros[0]["in_agua_potavel__presentes"] == 1
    assert registros[0]["in_agua_potavel__validos"] == 2
    assert registros[0]["cobertura_media_percentual"] == 50


async def test_identifica_municipio_pela_observacao_mais_recente(sqlite):
    repo = _RepositorioSqlite(sqlite)

    municipio = await repo.find_identificacao_municipio(co_municipio=1501402)

    assert municipio == {
        "co_municipio": 1501402,
        "no_municipio": "Municipio 1501402",
    }


async def test_media_simples_difere_de_proporcao_global_com_respostas_parciais(sqlite):
    # A: 1/1=100%, B: 1/2=50%, C: sem respostas. Media=75%, nao 2/3.
    with sqlite.begin() as conn:
        conn.execute(insert(infraestrutura_comum), [
            _linha(15020001, 2024, 1501402, 1, None),
            _linha(15020002, 2024, 1501402, 0, 1),
            _linha(15020003, 2024, 1501402, None, None),
            _linha(15020001, 2024, 1501402, 1, None),
        ])
    service = InfraestruturaService(_RepositorioSqlite(sqlite))
    resposta = await service.build_visao_temporal_municipio(
        co_municipio=1501402, ano_inicio=2024, ano_fim=2025,
        indicadores=["in_agua_potavel", "in_biblioteca"],
    )
    contrato = VisaoTemporalMunicipioInfraestruturaResponse.model_validate(resposta)
    ponto = contrato.data.serie[0]
    assert ponto.cobertura_media_percentual == 75
    assert ponto.quantidade_escolas == 3
    assert ponto.quantidade_escolas_com_informacao == 2
    assert ponto.quantidade_escolas_sem_dados == 1
    assert ponto.situacao == "com_dados"
    assert contrato.data.serie[1].situacao == "denominador_zero"
    # A escolha dos indicadores altera tanto o indice como as escolas validas.
    biblioteca = await service.build_visao_temporal_municipio(
        co_municipio=1501402, ano_inicio=2024, ano_fim=2025,
        indicadores=["in_biblioteca"],
    )
    assert biblioteca["data"]["serie"][0]["cobertura_media_percentual"] == 100
    assert biblioteca["data"]["serie"][0]["quantidade_escolas_com_informacao"] == 1


async def test_zero_real_sem_dados_e_rede_sem_escolas_sao_distintos(sqlite):
    service = InfraestruturaService(_RepositorioSqlite(sqlite))
    sem_respostas = await service.build_visao_temporal_municipio(
        co_municipio=1501402, ano_inicio=2022, ano_fim=2023,
        indicadores=["in_biblioteca"], rede_ensino=["Estadual"],
    )
    pontos = sem_respostas["data"]["serie"]
    assert pontos[0]["cobertura_media_percentual"] == 0
    assert pontos[0]["situacao"] == "com_dados"
    assert pontos[1]["cobertura_media_percentual"] is None
    assert pontos[1]["situacao"] == "denominador_zero"
    todas = await service.build_visao_temporal_municipio(
        co_municipio=1501402, ano_inicio=2022, ano_fim=2023,
    )
    assert todas["data"]["serie"][1]["situacao"] == "sem_dados"
    vazia = await service.build_visao_temporal_municipio(
        co_municipio=1501402, ano_inicio=2022, ano_fim=2023,
        rede_ensino=["Federal"],
    )
    assert all(p["situacao"] == "denominador_zero" for p in vazia["data"]["serie"])


async def test_uniao_de_redes_inclui_todas_sem_exclusao_de_escola(sqlite):
    repo = _RepositorioSqlite(sqlite)
    registros = await repo.find_serie_temporal_municipio(
        co_municipio=1501402, ano_inicio=2022, ano_fim=2023,
        indicadores=["in_agua_potavel", "in_biblioteca"],
        rede_ensino=["Municipal", "Estadual"],
    )
    assert registros[0]["quantidade_escolas"] == 3
    assert registros[0]["cobertura_media_percentual"] == pytest.approx(100 / 3)


@pytest.mark.parametrize("valor", [0, None, 2])
async def test_conflitos_ou_valores_invalidos_nao_viram_percentual_normal(sqlite, valor):
    with sqlite.begin() as conn:
        conn.execute(insert(infraestrutura_comum), _linha(15010001, 2022, 1501402, valor, 1))
    with pytest.raises(SourceDataInconsistentError):
        await InfraestruturaService(_RepositorioSqlite(sqlite)).build_visao_temporal_municipio(
            co_municipio=1501402, ano_inicio=2022, ano_fim=2023,
            indicadores=["in_agua_potavel"],
        )


async def test_media_arredondada_somente_depois_da_agregacao(sqlite):
    escola_a = _linha(15020001, 2024, 1501402, 1, 0)
    escola_a["IN_AUDITORIO"] = 0  # 1/3; escola B tem 1/2.
    with sqlite.begin() as conn:
        conn.execute(insert(infraestrutura_comum), [
            escola_a, _linha(15020002, 2024, 1501402, 1, 0),
        ])
    servico = InfraestruturaService(_RepositorioSqlite(sqlite))
    resposta = await servico.build_visao_temporal_municipio(
        co_municipio=1501402, ano_inicio=2024, ano_fim=2025,
        indicadores=["in_agua_potavel", "in_biblioteca", "in_auditorio"],
    )
    assert resposta["data"]["serie"][0]["cobertura_media_percentual"] == 41.67


async def test_http_executa_repositorio_sql_servico_e_contrato(sqlite):
    app = _aplicacao(InfraestruturaService(_RepositorioSqlite(sqlite)))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resposta = await client.get(
            ROTA, params=[("ano_inicio", 2022), ("ano_fim", 2023),
                          ("indicadores", "in_agua_potavel"),
                          ("indicadores", "in_biblioteca")],
        )
    assert resposta.status_code == 200
    data = resposta.json()["data"]
    assert data["serie"][0]["cobertura_media_percentual"] == 33.33
    assert data["serie"][1]["situacao"] == "sem_dados"
    assert data["metodologia"]["homologada"] is False


async def test_valor_invalido_sem_duplicata_bloqueia_so_indicador_selecionado(sqlite):
    with sqlite.begin() as conn:
        conn.execute(insert(infraestrutura_comum), _linha(15020001, 2024, 1501402, 2, 1))
    servico = InfraestruturaService(_RepositorioSqlite(sqlite))
    with pytest.raises(SourceDataInconsistentError):
        await servico.build_visao_temporal_municipio(
            co_municipio=1501402, ano_inicio=2024, ano_fim=2025,
            indicadores=["in_agua_potavel"],
        )
    resposta = await servico.build_visao_temporal_municipio(
        co_municipio=1501402, ano_inicio=2024, ano_fim=2025,
        indicadores=["in_biblioteca"],
    )
    assert resposta["data"]["serie"][0]["cobertura_media_percentual"] == 100
