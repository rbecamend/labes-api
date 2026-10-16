import pytest

from app.core.exceptions import NotFoundError
from app.domain.infraestrutura import InfraestruturaRegistroBruto
from app.schemas.infraestrutura import ComparacaoInfraestruturaResponse
from app.services.infraestrutura_service import (
    ANOS_COMPARACAO,
    METRIC_FIELDS,
    InfraestruturaService,
)


INDICADORES = tuple(chave for chave, _ in METRIC_FIELDS)


def _registro(
    co_entidade: int,
    ano: int,
    valores: list[int | None],
    *,
    co_municipio: int = 1501402,
) -> InfraestruturaRegistroBruto:
    return InfraestruturaRegistroBruto(
        co_entidade=co_entidade,
        no_entidade=f"Escola {co_entidade}",
        co_municipio=co_municipio,
        no_municipio="Belém",
        nu_ano_censo=ano,
        indicadores=dict(zip(INDICADORES, valores, strict=True)),
    )


class _RepositorioComparacao:
    def __init__(self, *, identificacao, historico=None, pares=None):
        self.identificacao = identificacao
        self.historico = historico or []
        self.pares = pares or {}
        self.chamadas_pares = []
        self.anos_consultados = None

    async def find_identificacao_escola(self, *, co_entidade):
        return self.identificacao

    async def find_historico_escola(self, *, co_entidade, anos_comparaveis):
        self.anos_consultados = anos_comparaveis
        return self.historico

    async def find_pares_municipais(
        self, *, co_entidade_excluida, co_municipio, ano
    ):
        self.chamadas_pares.append(
            {
                "co_entidade_excluida": co_entidade_excluida,
                "co_municipio": co_municipio,
                "ano": ano,
            }
        )
        return self.pares.get((co_municipio, ano), [])


def _identificacao():
    return {
        "co_entidade": 15012345,
        "no_entidade": "EMEF Exemplo",
        "co_municipio": 1501402,
        "no_municipio": "Belém",
        "nu_ano_censo": 2024,
    }


async def test_servico_monta_serie_fixa_com_calculos_e_lacunas():
    escola_2022 = _registro(15012345, 2022, [1] * 13 + [0] * 4)
    escola_2024 = _registro(15012345, 2024, [None] * 17)
    pares = {
        (1501402, 2022): [
            _registro(15000001, 2022, [1] * 17),
            _registro(15000002, 2022, [0] * 17),
        ],
        (1501402, 2024): [_registro(15000003, 2024, [1] * 17)],
    }
    repositorio = _RepositorioComparacao(
        identificacao=_identificacao(),
        historico=[escola_2022, escola_2024],
        pares=pares,
    )

    envelope = await InfraestruturaService(
        repositorio
    ).build_comparacao_municipio(co_entidade=15012345)
    resposta = ComparacaoInfraestruturaResponse.model_validate(envelope)
    serie = resposta.model_dump(mode="json")["data"]["serie"]

    assert [ponto["ano"] for ponto in serie] == list(ANOS_COMPARACAO)
    assert serie[0]["situacao"] == "disponivel"
    assert serie[0]["indice_escola_percentual"] == 76.47
    assert serie[0]["quantidade_indicadores_presentes"] == 13
    assert serie[0]["quantidade_indicadores_validos"] == 17
    assert serie[0]["media_municipal_percentual"] == 50.0
    assert serie[0]["quantidade_pares_validos"] == 2
    assert serie[1]["situacao"] == "escola_sem_dados"
    assert serie[1]["denominador_pares"] == 0
    assert serie[2]["situacao"] == "escola_sem_dados"
    assert serie[2]["media_municipal_percentual"] == 100.0
    assert serie[3]["situacao"] == "escola_sem_dados"
    assert repositorio.anos_consultados == ANOS_COMPARACAO
    assert [chamada["ano"] for chamada in repositorio.chamadas_pares] == [
        2022,
        2024,
    ]


async def test_servico_retorna_quatro_lacunas_para_escola_sem_anos_do_mvp():
    repositorio = _RepositorioComparacao(identificacao=_identificacao())

    envelope = await InfraestruturaService(
        repositorio
    ).build_comparacao_municipio(co_entidade=15012345)
    serie = envelope["data"]["serie"]

    assert [ponto["ano"] for ponto in serie] == list(ANOS_COMPARACAO)
    assert all(ponto["situacao"] == "escola_sem_dados" for ponto in serie)
    assert all(ponto["total_indicadores"] == 17 for ponto in serie)
    assert repositorio.chamadas_pares == []
    ComparacaoInfraestruturaResponse.model_validate(envelope)


async def test_servico_distingue_escola_inexistente_de_historico_vazio():
    repositorio = _RepositorioComparacao(identificacao=None)

    with pytest.raises(NotFoundError, match="15012345"):
        await InfraestruturaService(repositorio).build_comparacao_municipio(
            co_entidade=15012345
        )
