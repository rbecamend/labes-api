"""Integração BE10 com as consultas SQL reais de BE02/BE03/BE04 em SQLite.

Valida o recorte histórico e a exclusão no SQL, sem depender do warehouse.
"""

import pytest
from sqlalchemy import create_engine, insert

from app.models.infraestrutura import infraestrutura_comum
from app.repositories.infraestrutura_repository import InfraestruturaRepository
from app.services.infraestrutura_agregacao_municipal import InfraestruturaAgregacaoMunicipalService


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
        self.consultas = []

    async def _execute(self, stmt):
        self.consultas.append(stmt)
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).mappings().all()
        return _Rows(rows)


def _linha(id_, ano, municipio, agua, biblioteca=None):
    row = {col.name: None for col in infraestrutura_comum.columns}
    row.update(
        CO_ENTIDADE=id_, NU_ANO_CENSO=ano, CO_MUNICIPIO=municipio,
        NO_ENTIDADE=f"Escola {id_}", NO_MUNICIPIO=f"Municipio {municipio}",
        IN_AGUA_POTAVEL=agua, IN_BIBLIOTECA=biblioteca,
    )
    return row


@pytest.fixture
def sqlite():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.exec_driver_sql("ATTACH DATABASE ':memory:' AS silver")
        infraestrutura_comum.create(conn)
        conn.execute(insert(infraestrutura_comum), [
            _linha(15012345, 2022, 1501402, 1, 1),
            _linha(15010001, 2022, 1501402, 1, 1),
            _linha(15010002, 2022, 1501402, 0, 0),
            _linha(15010003, 2022, 1501402, None, None),
            _linha(15010004, 2022, 1500800, 1, 1),  # outra cidade
            _linha(15012345, 2023, 1500800, 0, 0),  # mudou cidade
            _linha(15010005, 2023, 1500800, 0, 1),
            _linha(15010006, 2023, 1500800, 0, 1),
            _linha(15010007, 2023, 1501402, 1, 1),  # cidade antiga
            _linha(15012345, 2024, 1500800, None, None),  # linha nula
            _linha(15010008, 2024, 1500800, 1, None),
        ])
    yield engine
    engine.dispose()


async def test_agrega_quatro_anos_e_municipio_historico_sql_real(sqlite):
    repo = _RepositorioSqlite(sqlite)
    serie = await InfraestruturaAgregacaoMunicipalService(repo).calcular_serie(
        co_entidade=15012345
    )
    assert [item["ano"] for item in serie] == [2022, 2023, 2024, 2025]
    assert serie[0]["municipio_referencia"]["co_municipio"] == 1501402
    assert serie[1]["municipio_referencia"]["co_municipio"] == 1500800
    a = serie[0]["composicao_municipal"]["in_agua_potavel"]
    assert (a["quantidade_presentes"], a["quantidade_validos"],
            a["quantidade_sem_dados"], a["quantidade_escolas_referencia"]) == (1, 2, 1, 3)
    assert a["percentual_presentes"] == 50.0
    assert a["cobertura_percentual"] == 66.67
    b = serie[1]["composicao_municipal"]["in_agua_potavel"]
    assert b["quantidade_escolas_referencia"] == 2
    assert b["percentual_presentes"] == 0.0
    assert b["cobertura_percentual"] == 100.0
    assert serie[2]["registro_historico_disponivel"] is True
    assert serie[2]["composicao_municipal"]["in_agua_potavel"]["percentual_presentes"] == 100.0
    assert serie[3]["registro_historico_disponivel"] is False
    assert serie[3]["composicao_municipal"] is None
    assert len(repo.consultas) == 5  # identificacao, historico, 3 consultas de pares
    consultas_pares = [str(q).lower() for q in repo.consultas[2:]]
    assert all('"co_entidade" !=' in sql for sql in consultas_pares)
    assert all('"nu_ano_censo" =' in sql for sql in consultas_pares)
    assert all('"co_municipio" =' in sql for sql in consultas_pares)


async def test_escola_existente_sem_historico_no_recorte_nao_cria_pares(sqlite):
    with sqlite.begin() as conn:
        conn.execute(insert(infraestrutura_comum), [
            _linha(15099999, 2021, 1501402, 1, 0),
        ])
    repo = _RepositorioSqlite(sqlite)
    serie = await InfraestruturaAgregacaoMunicipalService(repo).calcular_serie(
        co_entidade=15099999
    )
    assert len(serie) == 4
    assert all(item["registro_historico_disponivel"] is False for item in serie)
    assert len(repo.consultas) == 2
