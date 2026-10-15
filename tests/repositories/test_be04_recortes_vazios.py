"""BE-04: consultas vazias não são confundidas com falhas no banco."""

import pytest
from sqlalchemy import create_engine, insert
from sqlalchemy.exc import OperationalError

from app.domain.infraestrutura import calcular_comparacao_infraestrutura_ano
from app.models.infraestrutura import infraestrutura_comum
from app.repositories.infraestrutura_repository import InfraestruturaRepository


class _Result:
    def __init__(self, rows):
        self.rows = rows
    def mappings(self):
        return self
    def first(self):
        return self.rows[0] if self.rows else None
    def __iter__(self):
        return iter(self.rows)


class _RepoLocal(InfraestruturaRepository):
    def __init__(self, engine):
        self.engine = engine
    async def _execute(self, query):
        with self.engine.connect() as conn:
            return _Result(conn.execute(query).mappings().all())


def _row(id_, ano, cidade=1501402, water=None):
    data = {column.name: None for column in infraestrutura_comum.columns}
    data.update(CO_ENTIDADE=id_, NO_ENTIDADE=f"Escola {id_}",
                CO_MUNICIPIO=cidade, NO_MUNICIPIO="Município",
                NU_ANO_CENSO=ano, IN_AGUA_POTAVEL=water)
    return data


@pytest.fixture
def banco():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.exec_driver_sql("ATTACH DATABASE ':memory:' AS silver")
        infraestrutura_comum.create(conn)
        conn.execute(insert(infraestrutura_comum), [
            _row(10, 2020, water=1),
            _row(10, 2021, cidade=1500800, water=0),
            _row(20, 2024, water=1),
            _row(30, 2024, water=None),
            _row(40, 2024, cidade=None, water=1),
            _row(50, 2024, cidade=1500800, water=1),
        ])
    yield engine
    engine.dispose()


async def test_escola_inexistente_vs_escola_sem_anos_comparaveis(banco):
    repo = _RepoLocal(banco)
    assert await repo.find_identificacao_escola(co_entidade=999) is None
    existente = await repo.find_identificacao_escola(co_entidade=10)
    assert existente == {
        "co_entidade": 10, "no_entidade": "Escola 10",
        "co_municipio": 1500800, "no_municipio": "Município",
        "nu_ano_censo": 2021,
    }
    assert await repo.find_historico_escola(co_entidade=999, anos_comparaveis=[2024]) == []
    assert await repo.find_historico_escola(co_entidade=10, anos_comparaveis=[2024]) == []


async def test_municipio_sem_pares_retorna_apenas_a_escola(banco):
    repo = _RepoLocal(banco)
    escola = (await repo.find_historico_escola(co_entidade=50, anos_comparaveis=[2024]))[0]
    pares = await repo.find_pares_municipais(
        co_entidade_excluida=50, co_municipio=escola.co_municipio, ano=escola.nu_ano_censo
    )
    assert pares == []
    result = calcular_comparacao_infraestrutura_ano(escola, pares)
    assert result.situacao == "sem_pares_municipio"
    assert result.media_municipal_percentual is None


async def test_pares_sem_indicadores_validos_sao_previsiveis(banco):
    repo = _RepoLocal(banco)
    escola = (await repo.find_historico_escola(co_entidade=20, anos_comparaveis=[2024]))[0]
    pares = await repo.find_pares_municipais(
        co_entidade_excluida=20, co_municipio=escola.co_municipio, ano=2024
    )
    assert [p.co_entidade for p in pares] == [30]
    resultado = calcular_comparacao_infraestrutura_ano(escola, pares)
    assert resultado.situacao == "sem_pares_validos"
    assert resultado.denominador_pares == 1
    assert resultado.quantidade_pares_validos == 0


async def test_municipio_ausente_na_fonte_nao_busca_pares_aleatorios(banco):
    repo = _RepoLocal(banco)
    escola = (await repo.find_historico_escola(co_entidade=40, anos_comparaveis=[2024]))[0]
    assert escola.co_municipio is None
    assert await repo.find_pares_municipais(
        co_entidade_excluida=40, co_municipio=escola.co_municipio, ano=2024
    ) == []


async def test_falha_real_de_banco_propaga_em_vez_de_virar_serie_vazia(banco):
    repo = _RepoLocal(banco)
    with banco.begin() as conn:
        infraestrutura_comum.drop(conn)
    with pytest.raises(OperationalError):
        await repo.find_historico_escola(co_entidade=10)
    with pytest.raises(OperationalError):
        await repo.find_identificacao_escola(co_entidade=10)


async def test_identificacao_com_ano_nulo_nao_impede_existencia(banco):
    with banco.begin() as conn:
        conn.execute(insert(infraestrutura_comum), [_row(60, None, water=None)])
    repo = _RepoLocal(banco)
    assert (await repo.find_identificacao_escola(co_entidade=60))["co_entidade"] == 60
    assert await repo.find_historico_escola(co_entidade=60, anos_comparaveis=[2024]) == []
