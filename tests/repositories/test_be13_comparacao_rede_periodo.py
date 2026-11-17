"""BE13: descoberta dos anos da Silver e filtro da rede nas referências."""

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
    def all(self):
        return self._rows
    def first(self):
        return self._rows[0] if self._rows else None


class _RepositorioSqlite(InfraestruturaRepository):
    def __init__(self, engine):
        self.engine = engine
        self.consultas = []
    async def _execute(self, stmt):
        self.consultas.append(stmt)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            if result.returns_rows:
                return _Rows(result.mappings().all())
            return _Rows([])


def _linha(id_, ano, municipio=1501402, dependencia=3, agua=1):
    row = {col.name: None for col in infraestrutura_comum.columns}
    row.update(
        CO_ENTIDADE=id_, NU_ANO_CENSO=ano, CO_MUNICIPIO=municipio,
        NO_ENTIDADE=f"Escola {id_}", NO_MUNICIPIO="Belém",
        TP_DEPENDENCIA=dependencia, IN_AGUA_POTAVEL=agua,
    )
    return row


@pytest.fixture
def banco():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.exec_driver_sql("ATTACH DATABASE ':memory:' AS silver")
        conn.exec_driver_sql("ATTACH DATABASE ':memory:' AS gold")
        infraestrutura_comum.create(conn)
        dim_tp_dependencia.create(conn)
        conn.execute(insert(dim_tp_dependencia), [
            {"co_tp_dependencia": 1, "no_tp_dependencia": "Federal"},
            {"co_tp_dependencia": 2, "no_tp_dependencia": "Estadual"},
            {"co_tp_dependencia": 3, "no_tp_dependencia": "Municipal"},
            {"co_tp_dependencia": 4, "no_tp_dependencia": "Privada"},
        ])
        conn.execute(insert(infraestrutura_comum), [
            _linha(10000001, 2022, dependencia=1),
            _linha(10000002, 2022, dependencia=2),
            _linha(10000003, 2022, dependencia=3),
            _linha(10000004, 2024, dependencia=3),
            _linha(10000005, 2024, municipio=1500800, dependencia=3),
            _linha(10000006, 2025, dependencia=4),
            _linha(None, 2025, dependencia=3),
            _linha(10000007, None, dependencia=3),
        ])
    yield engine
    engine.dispose()


async def test_be13_retorna_anos_distintos_disponiveis_no_intervalo(banco):
    repo = _RepositorioSqlite(banco)
    anos = await repo.find_anos_disponiveis(ano_inicio=2022, ano_fim=2025)
    assert anos == [2022, 2024, 2025]
    query = str(repo.consultas[0]).lower()
    assert "distinct" in query
    assert '"nu_ano_censo" between' in query


async def test_be13_filtra_somente_pares_pela_rede_selecionada(banco):
    repo = _RepositorioSqlite(banco)
    pares = await repo.find_pares_municipais(
        co_entidade_excluida=10000001,
        co_municipio=1501402,
        ano=2022,
        rede_ensino=["Municipal"],
    )
    assert [item.co_entidade for item in pares] == [10000003]
    query = str(repo.consultas[0]).lower()
    assert "dim_tp_dependencia" in query
    assert 'no_tp_dependencia in' in query
    assert '"co_entidade" !=' in query


async def test_be13_sem_filtro_de_rede_preserva_todas_as_referencias(banco):
    repo = _RepositorioSqlite(banco)
    pares = await repo.find_pares_municipais(
        co_entidade_excluida=10000001,
        co_municipio=1501402,
        ano=2022,
    )
    assert [item.co_entidade for item in pares] == [10000002, 10000003]
