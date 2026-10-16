from dataclasses import asdict

import pytest

from app.domain.infraestrutura import (
    InfraestruturaRegistroBruto,
    calcular_comparacao_infraestrutura_ano,
    calcular_indice_infraestrutura,
    calcular_serie_comparacao_infraestrutura,
)


INDICADORES = (
    "in_agua_potavel",
    "in_biblioteca",
    "in_quadra_esportes",
    "in_auditorio",
)


def _registro(
    co_entidade: int,
    indicadores: dict[str, int | None],
    *,
    ano: int = 2024,
    co_municipio: int = 1501402,
) -> InfraestruturaRegistroBruto:
    return InfraestruturaRegistroBruto(
        co_entidade=co_entidade,
        no_entidade=f"Escola {co_entidade}",
        co_municipio=co_municipio,
        no_municipio="Belém",
        nu_ano_censo=ano,
        indicadores=indicadores,
    )


def test_registro_bruto_preserva_identificacao_ano_e_indicadores_nulos():
    registro = InfraestruturaRegistroBruto(
        co_entidade=15012345,
        no_entidade="EMEF Exemplo",
        co_municipio=1501402,
        no_municipio="Belém",
        nu_ano_censo=2024,
        indicadores={
            "in_agua_potavel": 1,
            "in_biblioteca": 0,
            "in_auditorio": None,
        },
    )

    assert asdict(registro) == {
        "co_entidade": 15012345,
        "no_entidade": "EMEF Exemplo",
        "co_municipio": 1501402,
        "no_municipio": "Belém",
        "nu_ano_censo": 2024,
        "indicadores": {
            "in_agua_potavel": 1,
            "in_biblioteca": 0,
            "in_auditorio": None,
        },
    }


def test_indice_trata_zero_como_valido_e_exclui_nulo():
    resultado = calcular_indice_infraestrutura(
        {
            "in_agua_potavel": 1,
            "in_biblioteca": 0,
            "in_quadra_esportes": None,
        }
    )

    assert resultado.percentual == 50.0
    assert resultado.presentes == 1
    assert resultado.validos == 2
    assert resultado.total_indicadores == 3
    assert resultado.cobertura_indicadores_percentual == 66.67


def test_indice_aplica_cobertura_minima_sem_fixar_valor_global():
    indicadores = {
        "in_agua_potavel": 1,
        "in_biblioteca": None,
        "in_quadra_esportes": None,
        "in_auditorio": None,
    }

    sem_minimo = calcular_indice_infraestrutura(
        indicadores,
        indicadores_esperados=INDICADORES,
    )
    com_minimo = calcular_indice_infraestrutura(
        indicadores,
        indicadores_esperados=INDICADORES,
        cobertura_minima_percentual=50,
    )

    assert sem_minimo.percentual == 100.0
    assert sem_minimo.cobertura_indicadores_percentual == 25.0
    assert com_minimo.percentual is None


@pytest.mark.parametrize("cobertura", [-0.01, 100.01])
def test_indice_rejeita_cobertura_minima_fora_do_intervalo(cobertura):
    with pytest.raises(ValueError, match="entre 0 e 100"):
        calcular_indice_infraestrutura(
            {"in_agua_potavel": 1},
            cobertura_minima_percentual=cobertura,
        )


def test_indice_rejeita_valor_de_indicador_fora_do_contrato():
    with pytest.raises(ValueError, match="0, 1 ou None"):
        calcular_indice_infraestrutura({"in_agua_potavel": 2})


def test_comparacao_calcula_media_com_pesos_iguais_e_exclui_escola_consultada():
    escola = _registro(
        1,
        {
            "in_agua_potavel": 1,
            "in_biblioteca": 1,
            "in_quadra_esportes": 0,
            "in_auditorio": None,
        },
    )
    referencias = [
        escola,
        _registro(2, {chave: 1 for chave in INDICADORES}),
        _registro(3, {chave: 0 for chave in INDICADORES}),
        _registro(
            4,
            {chave: 1 for chave in INDICADORES},
            co_municipio=9999999,
        ),
    ]

    resultado = calcular_comparacao_infraestrutura_ano(
        escola,
        referencias,
        indicadores_esperados=INDICADORES,
    )

    assert resultado.situacao == "disponivel"
    assert resultado.indice_escola_percentual == 66.67
    assert resultado.quantidade_indicadores_presentes == 2
    assert resultado.quantidade_indicadores_validos == 3
    assert resultado.total_indicadores == 4
    assert resultado.cobertura_indicadores_percentual == 75.0
    assert resultado.media_municipal_percentual == 50.0
    assert resultado.diferenca_pontos_percentuais == 16.67
    assert resultado.quantidade_pares_validos == 2
    assert resultado.denominador_pares == 2
    assert resultado.cobertura_pares_percentual == 100.0


def test_comparacao_arredonda_diferenca_somente_apos_subtrair_indices_exatos():
    escola = _registro(1, dict(zip(INDICADORES, (1, 1, 0, None))))
    par = _registro(2, dict(zip(INDICADORES, (1, 0, 0, None))))

    resultado = calcular_comparacao_infraestrutura_ano(
        escola, [par], indicadores_esperados=INDICADORES
    )

    assert resultado.indice_escola_percentual == 66.67
    assert resultado.media_municipal_percentual == 33.33
    assert resultado.diferenca_pontos_percentuais == 33.33


def test_comparacao_calcula_media_com_indices_exatos_antes_de_arredondar():
    escola = _registro(1, {chave: 0 for chave in INDICADORES})
    pares = [
        _registro(2, {chave: 0 for chave in INDICADORES}),
        _registro(3, dict(zip(INDICADORES, (1, 1, 0, None)))),
    ]

    resultado = calcular_comparacao_infraestrutura_ano(
        escola, pares, indicadores_esperados=INDICADORES
    )

    assert resultado.media_municipal_percentual == 33.33
    assert resultado.diferenca_pontos_percentuais == -33.33


def test_comparacao_distingue_pares_existentes_sem_indice_valido():
    escola = _registro(1, {chave: 1 for chave in INDICADORES})
    referencias = [
        _registro(2, {chave: None for chave in INDICADORES}),
        _registro(3, {chave: None for chave in INDICADORES}),
    ]

    resultado = calcular_comparacao_infraestrutura_ano(
        escola,
        referencias,
        indicadores_esperados=INDICADORES,
    )

    assert resultado.situacao == "sem_pares_validos"
    assert resultado.media_municipal_percentual is None
    assert resultado.diferenca_pontos_percentuais is None
    assert resultado.quantidade_pares_validos == 0
    assert resultado.denominador_pares == 2
    assert resultado.cobertura_pares_percentual == 0.0


def test_comparacao_distingue_municipio_sem_pares():
    escola = _registro(1, {chave: 1 for chave in INDICADORES})

    resultado = calcular_comparacao_infraestrutura_ano(
        escola,
        [],
        indicadores_esperados=INDICADORES,
    )

    assert resultado.situacao == "sem_pares_municipio"
    assert resultado.quantidade_pares_validos == 0
    assert resultado.denominador_pares == 0
    assert resultado.cobertura_pares_percentual is None


def test_escola_sem_dados_tem_precedencia_sobre_ausencia_de_pares():
    escola = _registro(1, {chave: None for chave in INDICADORES})

    resultado = calcular_comparacao_infraestrutura_ano(
        escola,
        [],
        indicadores_esperados=INDICADORES,
    )

    assert resultado.situacao == "escola_sem_dados"
    assert resultado.indice_escola_percentual is None
    assert resultado.quantidade_indicadores_presentes == 0
    assert resultado.quantidade_indicadores_validos == 0
    assert resultado.total_indicadores == 4
    assert resultado.cobertura_indicadores_percentual == 0.0
    assert resultado.cobertura_pares_percentual is None


def test_cobertura_minima_remove_par_incompleto_da_media():
    escola = _registro(1, {chave: 1 for chave in INDICADORES})
    referencias = [
        _registro(2, {chave: 0 for chave in INDICADORES}),
        _registro(
            3,
            {
                "in_agua_potavel": 1,
                "in_biblioteca": None,
                "in_quadra_esportes": None,
                "in_auditorio": None,
            },
        ),
    ]

    resultado = calcular_comparacao_infraestrutura_ano(
        escola,
        referencias,
        indicadores_esperados=INDICADORES,
        cobertura_minima_percentual=50,
    )

    assert resultado.media_municipal_percentual == 0.0
    assert resultado.quantidade_pares_validos == 1
    assert resultado.denominador_pares == 2
    assert resultado.cobertura_pares_percentual == 50.0


def test_serie_e_ordenada_por_ano():
    escola_2024 = _registro(1, {chave: 1 for chave in INDICADORES}, ano=2024)
    escola_2023 = _registro(1, {chave: 1 for chave in INDICADORES}, ano=2023)

    serie = calcular_serie_comparacao_infraestrutura(
        [escola_2024, escola_2023],
        [],
        indicadores_esperados=INDICADORES,
    )

    assert [item.ano for item in serie] == [2023, 2024]
