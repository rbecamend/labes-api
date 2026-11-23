"""Testes de orquestração da BE10 sobre as consultas históricas BE02–BE04."""

import pytest
from app.core.exceptions import NotFoundError
from app.domain.infraestrutura import InfraestruturaRegistroBruto
from app.schemas.infraestrutura import INDICADORES_COMPARACAO_INFRAESTRUTURA
from app.services.infraestrutura_agregacao_municipal import InfraestruturaAgregacaoMunicipalService


CHAVES = INDICADORES_COMPARACAO_INFRAESTRUTURA


def reg(id_, ano, municipio, *, agua=1, biblioteca=0):
    valores = {chave: None for chave in CHAVES}
    valores.update(in_agua_potavel=agua, in_biblioteca=biblioteca)
    return InfraestruturaRegistroBruto(
        id_, f"Escola {id_}", municipio, "Municipio", ano, valores,
    )


class RepoFake:
    def __init__(self, historico=(), pares=None, existe=True):
        self.historico = list(historico)
        self.pares = pares or {}
        self.existe = existe
        self.chamadas = []

    async def find_identificacao_escola(self, *, co_entidade):
        return {"co_entidade": co_entidade} if self.existe else None

    async def find_historico_escola(self, *, co_entidade, anos_comparaveis):
        assert tuple(anos_comparaveis) == (2022, 2023, 2024, 2025)
        return list(self.historico)

    async def find_pares_municipais(self, *, co_entidade_excluida, co_municipio, ano):
        self.chamadas.append((co_entidade_excluida, co_municipio, ano))
        return self.pares.get((co_municipio, ano), [])


async def test_serie_historica_usa_municipio_do_ano_e_mantem_lacunas():
    repo = RepoFake(
        historico=[reg(1, 2022, 10), reg(1, 2024, 20, agua=None)],
        pares={(10, 2022): [reg(2, 2022, 10, agua=1)],
               (20, 2024): [reg(3, 2024, 20, agua=0), reg(4, 2024, 20, agua=None)]},
    )
    serie = await InfraestruturaAgregacaoMunicipalService(repo).calcular_serie(co_entidade=1)
    assert [p["ano"] for p in serie] == [2022, 2023, 2024, 2025]
    assert serie[0]["municipio_referencia"]["co_municipio"] == 10
    assert serie[2]["municipio_referencia"]["co_municipio"] == 20
    assert serie[1]["registro_historico_disponivel"] is False
    assert serie[1]["composicao_municipal"] is None
    assert serie[2]["registro_historico_disponivel"] is True
    assert serie[2]["composicao_municipal"]["in_agua_potavel"] == {
        "quantidade_presentes": 0, "quantidade_validos": 1,
        "quantidade_sem_dados": 1, "quantidade_escolas_referencia": 2,
        "percentual_presentes": 0.0, "cobertura_percentual": 50.0,
    }
    assert repo.chamadas == [(1, 10, 2022), (1, 20, 2024)]
    assert set(serie[0]["composicao_municipal"]) == set(CHAVES)


async def test_escola_inexistente_e_diferente_de_sem_historico():
    with pytest.raises(NotFoundError):
        await InfraestruturaAgregacaoMunicipalService(RepoFake(existe=False)).calcular_serie(co_entidade=1)
    serie = await InfraestruturaAgregacaoMunicipalService(RepoFake()).calcular_serie(co_entidade=1)
    assert len(serie) == 4
    assert all(item["composicao_municipal"] is None for item in serie)


async def test_municipio_nulo_nao_consulta_pares_ou_inventa_municipio():
    repo = RepoFake(historico=[reg(1, 2024, None)])
    serie = await InfraestruturaAgregacaoMunicipalService(repo).calcular_serie(co_entidade=1)
    assert serie[2]["registro_historico_disponivel"] is True
    assert serie[2]["municipio_referencia"] is None
    assert serie[2]["composicao_municipal"] is None
    assert repo.chamadas == []


async def test_sem_pares_retorna_composicao_zerada_e_nao_resultado_falso():
    repo = RepoFake(historico=[reg(1, 2025, 10)])
    serie = await InfraestruturaAgregacaoMunicipalService(repo).calcular_serie(co_entidade=1)
    v = serie[-1]["composicao_municipal"]["in_biblioteca"]
    assert v["quantidade_escolas_referencia"] == 0
    assert v["percentual_presentes"] is None
    assert v["cobertura_percentual"] is None


async def test_historico_duplicado_rejeitado_antes_de_consultar_pares():
    repo = RepoFake(historico=[reg(1, 2024, 10), reg(1, 2024, 10)])
    with pytest.raises(ValueError, match="duplicados"):
        await InfraestruturaAgregacaoMunicipalService(repo).calcular_serie(co_entidade=1)
    assert repo.chamadas == []


async def test_rejeita_historico_de_outra_entidade_ou_fora_do_recorte():
    with pytest.raises(ValueError, match="outra escola"):
        await InfraestruturaAgregacaoMunicipalService(RepoFake(historico=[reg(2, 2024, 10)])).calcular_serie(co_entidade=1)
    with pytest.raises(ValueError, match="fora do recorte"):
        await InfraestruturaAgregacaoMunicipalService(RepoFake(historico=[reg(1, 2026, 10)])).calcular_serie(co_entidade=1)
