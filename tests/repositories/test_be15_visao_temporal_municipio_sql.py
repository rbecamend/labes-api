import pytest
from sqlalchemy import create_engine, insert

from app.models.infraestrutura import dim_tp_dependencia, infraestrutura_comum
from app.repositories.infraestrutura_repository import InfraestruturaRepository


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


async def test_identifica_municipio_pela_observacao_mais_recente(sqlite):
    repo = _RepositorioSqlite(sqlite)

    municipio = await repo.find_identificacao_municipio(co_municipio=1501402)

    assert municipio == {
        "co_municipio": 1501402,
        "no_municipio": "Municipio 1501402",
    }
