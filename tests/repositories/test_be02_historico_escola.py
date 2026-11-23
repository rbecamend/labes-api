"""BE-02: SELECT real em SQLite, com esquema Silver temporário."""

import pytest
from sqlalchemy import create_engine, insert

from app.models.infraestrutura import infraestrutura_comum
from app.repositories.infraestrutura_repository import InfraestruturaRepository, METRIC_KEYS


class _Rows:
    def __init__(self, rows):
        self._rows = rows
    def mappings(self):
        return self._rows


class _RepoLocal(InfraestruturaRepository):
    def __init__(self, engine):
        self.engine = engine
        self.executions = 0
    async def _execute(self, stmt):
        self.executions += 1
        with self.engine.connect() as connection:
            return _Rows(connection.execute(stmt).mappings().all())


def _registro(codigo, ano, municipio=1501402, **indicadores):
    base = {col.name: None for col in infraestrutura_comum.columns}
    base.update({
        "CO_ENTIDADE": codigo,
        "NO_ENTIDADE": f"Escola {codigo}",
        "CO_MUNICIPIO": municipio,
        "NO_MUNICIPIO": "Belém" if municipio == 1501402 else "Outra cidade",
        "NU_ANO_CENSO": ano,
    })
    base.update(indicadores)
    return base


@pytest.fixture
def banco():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.exec_driver_sql("ATTACH DATABASE ':memory:' AS silver")
        infraestrutura_comum.create(conn)
        conn.execute(insert(infraestrutura_comum), [
            _registro(11, 2024, IN_AGUA_POTAVEL=0, IN_BANHEIRO=1),
            _registro(11, 2022, IN_AGUA_POTAVEL=None, IN_BANHEIRO=1),
            _registro(12, 2022, IN_AGUA_POTAVEL=1),
            _registro(11, 2018, IN_AGUA_POTAVEL=1),
        ])
    yield engine
    engine.dispose()


async def test_historico_ordenado_com_17_indicadores_e_null_original(banco):
    historico = await _RepoLocal(banco).find_historico_escola(
        co_entidade=11, anos_comparaveis=[2024, 2022]
    )
    assert [r.nu_ano_censo for r in historico] == [2022, 2024]
    assert [r.co_entidade for r in historico] == [11, 11]
    assert historico[0].no_entidade == "Escola 11"
    assert historico[0].co_municipio == 1501402
    assert len(historico[0].indicadores) == len(METRIC_KEYS) == 17
    assert historico[0].indicadores["in_agua_potavel"] is None
    assert historico[1].indicadores["in_agua_potavel"] == 0
    assert historico[1].indicadores["in_banheiro"] == 1


async def test_sem_filtro_retorna_anos_observados_sem_supor_homologacao(banco):
    dados = await _RepoLocal(banco).find_historico_escola(co_entidade=11)
    assert [r.nu_ano_censo for r in dados] == [2018, 2022, 2024]


async def test_lista_de_anos_vazia_nao_abre_consulta(banco):
    repo = _RepoLocal(banco)
    assert await repo.find_historico_escola(co_entidade=11, anos_comparaveis=[]) == []
    assert repo.executions == 0


async def test_escola_inexistente_gera_serie_vazia(banco):
    assert await _RepoLocal(banco).find_historico_escola(co_entidade=999) == []


async def test_duplicatas_na_fonte_sao_preservadas_para_verificacao_no_dominio(banco):
    with banco.begin() as conn:
        conn.execute(insert(infraestrutura_comum), [_registro(11, 2022)])
    registros = await _RepoLocal(banco).find_historico_escola(
        co_entidade=11, anos_comparaveis=[2022]
    )
    assert len(registros) == 2
