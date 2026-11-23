"""BE-03: pares do mesmo município e ano com exclusão no SQL."""

import pytest
from sqlalchemy import create_engine, insert
from app.models.infraestrutura import infraestrutura_comum
from app.repositories.infraestrutura_repository import InfraestruturaRepository


class _Result:
    def __init__(self, rows):
        self.rows = rows
    def mappings(self):
        return self.rows


class _RepoLocal(InfraestruturaRepository):
    def __init__(self, engine):
        self.engine = engine
        self.queries = []
    async def _execute(self, query):
        self.queries.append(query)
        with self.engine.connect() as connection:
            return _Result(connection.execute(query).mappings().all())


def _row(id_, ano, cidade=1501402, agua=None):
    data = {column.name: None for column in infraestrutura_comum.columns}
    data.update(CO_ENTIDADE=id_, NU_ANO_CENSO=ano, CO_MUNICIPIO=cidade,
                NO_ENTIDADE=f"Escola {id_}", NO_MUNICIPIO="Município",
                IN_AGUA_POTAVEL=agua)
    return data


@pytest.fixture
def banco():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS silver")
        infraestrutura_comum.create(connection)
        connection.execute(insert(infraestrutura_comum), [
            _row(10, 2022, agua=0),
            _row(20, 2022, agua=None),
            _row(30, 2022, agua=1),
            _row(40, 2022, cidade=1500800, agua=1),
            _row(50, 2023, agua=1),
            _row(10, 2023, cidade=1500800, agua=0),
            _row(60, 2023, cidade=1500800, agua=1),
        ])
    yield engine
    engine.dispose()


async def test_filtro_por_municipio_ano_e_exclusao_da_propria_escola(banco):
    repo = _RepoLocal(banco)
    registros = await repo.find_pares_municipais(
        co_entidade_excluida=10, co_municipio=1501402, ano=2022
    )
    assert [r.co_entidade for r in registros] == [20, 30]
    assert all(r.nu_ano_censo == 2022 and r.co_municipio == 1501402 for r in registros)
    assert registros[0].indicadores["in_agua_potavel"] is None
    assert registros[1].indicadores["in_agua_potavel"] == 1
    stmt = str(repo.queries[0]).lower()
    assert '"co_entidade" !=' in stmt
    assert '"co_municipio" =' in stmt
    assert '"nu_ano_censo" =' in stmt


async def test_municipio_pode_mudar_entre_anos_sem_usar_a_dimensao_atual(banco):
    repo = _RepoLocal(banco)
    antigo = await repo.find_pares_municipais(
        co_entidade_excluida=10, co_municipio=1501402, ano=2022
    )
    atual = await repo.find_pares_municipais(
        co_entidade_excluida=10, co_municipio=1500800, ano=2023
    )
    assert [r.co_entidade for r in antigo] == [20, 30]
    assert [r.co_entidade for r in atual] == [60]


async def test_municipio_ausente_retorna_vazio_sem_sql(banco):
    repo = _RepoLocal(banco)
    assert await repo.find_pares_municipais(
        co_entidade_excluida=10, co_municipio=None, ano=2022
    ) == []
    assert repo.queries == []


async def test_ano_sem_outras_escolas_nao_vaza_dados(banco):
        repo = _RepoLocal(banco)
        assert await repo.find_pares_municipais(
            co_entidade_excluida=10, co_municipio=1501402, ano=2024
        ) == []
