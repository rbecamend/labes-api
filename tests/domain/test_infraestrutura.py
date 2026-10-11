from dataclasses import asdict

from app.domain.infraestrutura import InfraestruturaRegistroBruto


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
