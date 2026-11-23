"""Testes unitários da BE10, sem consultar warehouse."""

import pytest
from app.domain.infraestrutura import InfraestruturaRegistroBruto
from app.domain.infraestrutura_agregacao_municipal import agregar_indicadores_municipais


INDICADORES = ("in_agua_potavel", "in_biblioteca")


def registro(codigo, ano=2024, municipio=1501402, agua=None, biblioteca=None):
    return InfraestruturaRegistroBruto(
        co_entidade=codigo, no_entidade=str(codigo), co_municipio=municipio,
        no_municipio="Município", nu_ano_censo=ano,
        indicadores={"in_agua_potavel": agua, "in_biblioteca": biblioteca},
    )


def agregar(pares, escola=None):
    return agregar_indicadores_municipais(
        escola or registro(1), pares, indicadores_esperados=INDICADORES,
    )


def test_agregacao_independente_por_indicador_e_nulos():
    a = agregar([
        registro(1, agua=1, biblioteca=1),  # alvo deve ser excluído
        registro(2, agua=1, biblioteca=0),
        registro(3, agua=0, biblioteca=None),
        registro(4, agua=None, biblioteca=1),
        registro(5, ano=2023, agua=1, biblioteca=1),
        registro(6, municipio=1500800, agua=1, biblioteca=1),
    ])
    agua = a["in_agua_potavel"]
    biblioteca = a["in_biblioteca"]
    assert (agua.quantidade_presentes, agua.quantidade_validos,
            agua.quantidade_sem_dados, agua.quantidade_escolas_referencia) == (1, 2, 1, 3)
    assert agua.percentual_presentes == 50.0
    assert agua.cobertura_percentual == 66.67
    assert (biblioteca.quantidade_presentes, biblioteca.quantidade_validos,
            biblioteca.quantidade_sem_dados) == (1, 2, 1)
    assert biblioteca.percentual_presentes == 50.0
    assert biblioteca.cobertura_percentual == 66.67


def test_sem_pares_tem_contagens_zero_e_percentuais_indisponiveis():
    a = agregar([])
    assert all((v.quantidade_escolas_referencia, v.quantidade_validos) == (0, 0)
               for v in a.values())
    assert all(v.percentual_presentes is None and v.cobertura_percentual is None
               for v in a.values())


def test_todos_nulos_nao_viram_zero_porcento():
    a = agregar([registro(2), registro(3)])
    assert a["in_agua_potavel"].quantidade_sem_dados == 2
    assert a["in_agua_potavel"].percentual_presentes is None
    assert a["in_agua_potavel"].cobertura_percentual == 0.0


def test_percentual_0_e_100_sao_respostas_validas():
    zeros = agregar([registro(2, agua=0, biblioteca=0)])
    uns = agregar([registro(2, agua=1, biblioteca=1)])
    assert zeros["in_agua_potavel"].percentual_presentes == 0.0
    assert uns["in_agua_potavel"].percentual_presentes == 100.0
    assert zeros["in_agua_potavel"].cobertura_percentual == 100.0


def test_precisao_dois_decimais_e_contagens_inteiras():
    a = agregar([registro(2, agua=1), registro(3, agua=0), registro(4, agua=0)])
    assert a["in_agua_potavel"].percentual_presentes == 33.33
    assert a["in_agua_potavel"].cobertura_percentual == 100.0
    assert a["in_biblioteca"].cobertura_percentual == 0.0
    assert a["in_biblioteca"].percentual_presentes is None


def test_municipio_historico_ausente_impede_agregacao():
    assert agregar([registro(2)], escola=registro(1, municipio=None)) is None


def test_rejeita_duplicados_sem_descartar_duplicidade():
    with pytest.raises(ValueError, match="duplicadas"):
        agregar([registro(2), registro(2)])


def test_rejeita_codigo_ausente_e_valores_invalidos():
    with pytest.raises(ValueError, match="identificador"):
        agregar([registro(None)])
    with pytest.raises(ValueError, match="inválido"):
        agregar([registro(2, agua=2)])
    with pytest.raises(ValueError, match="inválido"):
        agregar([registro(2, agua=True)])


def test_rejeita_indicadores_sem_chave_ou_repetidos():
    with pytest.raises(ValueError, match="ausente no registro"):
        agregar_indicadores_municipais(registro(1), [registro(2)], indicadores_esperados=("in_outro",))
    with pytest.raises(ValueError, match="duplicatas"):
        agregar_indicadores_municipais(registro(1), [], indicadores_esperados=("in_biblioteca", "in_biblioteca"))
