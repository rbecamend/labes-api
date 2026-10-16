"""DAD-04: conciliação HTTP da rota oficial com contas externas ao domínio.

O pacote DAD-03B é lido somente quando DAD03B_PACKAGE_DIR aponta para sua
pasta de acesso controlado. Nenhum registro real integra este arquivo.
"""

import hashlib
import json
import os
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError

from app.core.dependencies import get_infraestrutura_repository
from app.domain.infraestrutura import InfraestruturaRegistroBruto
from main import app

# Contrato de QA declarado aqui, sem importar a lista nem os cálculos de produção.
INDICATORS = (
    "in_agua_potavel",
    "in_energia_rede_publica",
    "in_esgoto_rede_publica",
    "in_lixo_servico_coleta",
    "in_banheiro",
    "in_banheiro_pne",
    "in_biblioteca",
    "in_sala_leitura",
    "in_laboratorio_ciencias",
    "in_laboratorio_informatica",
    "in_sala_multiuso",
    "in_sala_atendimento_especial",
    "in_cozinha",
    "in_refeitorio",
    "in_quadra_esportes",
    "in_patio_coberto",
    "in_auditorio",
)
YEARS = (2022, 2023, 2024, 2025)
SCHOOL = 99000001  # Identificador fictício destes testes.
ROUTE = "/infraestrutura/analise-temporal/escolas/{}/comparacao-municipio"


def row(school, year, municipality, values, *, name=None, city=None):
    assert len(values) == len(INDICATORS)
    return {
        "co_entidade": school,
        "no_entidade": name or f"Escola sintética {school}",
        "co_municipio": municipality,
        "no_municipio": city or f"Município sintético {municipality}",
        "nu_ano_censo": year,
        "indicadores": dict(zip(INDICATORS, values, strict=True)),
    }


def rounded_percent(value):
    return float(round(value * 100, 2)) if value is not None else None


def raw_index(record):
    if record is None:
        return 0, 0, None
    values = [record["indicadores"].get(key) for key in INDICATORS]
    assert all(value in (0, 1, None) for value in values)
    yes = values.count(1)
    valid = sum(value is not None for value in values)
    return yes, valid, Fraction(yes, valid) if valid else None


def independent_point(records, selected_id, year):
    selected = [
        r
        for r in records
        if r["co_entidade"] == selected_id and r["nu_ano_censo"] == year
    ]
    assert len(selected) <= 1
    school = selected[0] if selected else None
    yes, valid, school_index = raw_index(school)
    peers = [
        r
        for r in records
        if school is not None
        and r["co_entidade"] != selected_id
        and r["nu_ano_censo"] == year
        and r["co_municipio"] == school["co_municipio"]
    ]
    exact_peer_indices = [raw_index(peer)[2] for peer in peers]
    eligible = [value for value in exact_peer_indices if value is not None]
    mean = sum(eligible, Fraction(0)) / len(eligible) if eligible else None
    if school_index is None:
        situation = "escola_sem_dados"
    elif not peers:
        situation = "sem_pares_municipio"
    elif not eligible:
        situation = "sem_pares_validos"
    else:
        situation = "disponivel"
    return {
        "ano": year,
        "situacao": situation,
        "indice_escola_percentual": rounded_percent(school_index),
        "quantidade_indicadores_presentes": yes,
        "quantidade_indicadores_validos": valid,
        "total_indicadores": len(INDICATORS),
        "cobertura_indicadores_percentual": rounded_percent(
            Fraction(valid, len(INDICATORS))
        ),
        "media_municipal_percentual": rounded_percent(mean),
        "diferenca_pontos_percentuais": rounded_percent(school_index - mean)
        if school_index is not None and mean is not None
        else None,
        "quantidade_pares_validos": len(eligible),
        "denominador_pares": len(peers),
        "cobertura_pares_percentual": rounded_percent(
            Fraction(len(eligible), len(peers))
        )
        if peers
        else None,
    }


class ControlledRepository:
    def __init__(self, records, *, failure=None):
        self.records = records
        self.failure = failure
        self.peer_queries = []

    async def find_identificacao_escola(self, *, co_entidade):
        if self.failure:
            raise self.failure
        matches = [r for r in self.records if r["co_entidade"] == co_entidade]
        return max(matches, key=lambda r: r["nu_ano_censo"]) if matches else None

    async def find_historico_escola(self, *, co_entidade, anos_comparaveis):
        return [
            InfraestruturaRegistroBruto(**r)
            for r in self.records
            if r["co_entidade"] == co_entidade and r["nu_ano_censo"] in anos_comparaveis
        ]

    async def find_pares_municipais(self, *, co_entidade_excluida, co_municipio, ano):
        self.peer_queries.append((co_entidade_excluida, co_municipio, ano))
        return [
            InfraestruturaRegistroBruto(**r)
            for r in self.records
            if r["co_entidade"] != co_entidade_excluida
            and r["co_municipio"] == co_municipio
            and r["nu_ano_censo"] == ano
        ]


async def request(repository, school=SCHOOL):
    async def replace_repository():
        return repository

    app.dependency_overrides[get_infraestrutura_repository] = replace_repository
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://testserver",
        ) as client:
            return await client.get(ROUTE.format(school))
    finally:
        app.dependency_overrides.pop(get_infraestrutura_repository, None)


async def test_http_compara_serie_e_oraculo_sintetico_independente():
    a, b = 9990001, 9990002
    records = [
        row(SCHOOL, 2022, a, [1, 1, 0] + [None] * 14),
        row(99000002, 2022, a, [1, 0, 0] + [None] * 14),
        row(99000003, 2022, a, [None] * 17),
        row(99000004, 2022, b, [1] * 17),
        row(SCHOOL, 2023, a, [None] * 17),
        row(99000005, 2023, a, [1] * 17),
        row(SCHOOL, 2024, b, [1] * 17),
        row(99000006, 2024, b, [0] * 17),
        row(99000007, 2024, b, [1, 1, 0] + [None] * 14),
        row(SCHOOL, 2025, b, [0] * 17),
    ]
    repository = ControlledRepository(records)
    response = await request(repository)

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["metodologia"]["indicadores"] == list(INDICATORS)
    assert body["data"]["metodologia"]["cobertura_minima_percentual"] is None
    assert body["data"]["metodologia"]["homologada"] is False
    assert body["data"]["municipio"]["co_municipio"] == b  # Identificação mais recente.
    assert body["data"]["serie"] == [
        independent_point(records, SCHOOL, year) for year in YEARS
    ]
    assert set(repository.peer_queries) == {
        (SCHOOL, a, 2022),
        (SCHOOL, a, 2023),
        (SCHOOL, b, 2024),
        (SCHOOL, b, 2025),
    }
    assert body["data"]["serie"][0]["diferenca_pontos_percentuais"] == 33.33
    assert body["data"]["serie"][2]["media_municipal_percentual"] == 33.33


async def test_http_preserva_ano_sem_observacao_e_sem_pares_validos():
    records = [
        row(SCHOOL, 2022, 9990001, [1] * 17),
        row(99000002, 2022, 9990001, [None] * 17),
        row(SCHOOL, 2024, 9990001, [0] * 17),
        row(99000003, 2024, 9990001, [1] * 17),
    ]
    repository = ControlledRepository(records)
    response = await request(repository)
    assert response.status_code == 200
    assert response.json()["data"]["serie"] == [
        independent_point(records, SCHOOL, year) for year in YEARS
    ]
    assert [point["situacao"] for point in response.json()["data"]["serie"]] == [
        "sem_pares_validos",
        "escola_sem_dados",
        "disponivel",
        "escola_sem_dados",
    ]
    assert {query[2] for query in repository.peer_queries} == {2022, 2024}


@pytest.mark.parametrize(
    "path, expected",
    [
        (ROUTE.format(123), 422),
        (ROUTE.format("abc"), 422),
    ],
)
async def test_http_rejeita_identificador_invalido(path, expected):
    repository = ControlledRepository([])

    async def replace_repository():
        return repository

    app.dependency_overrides[get_infraestrutura_repository] = replace_repository
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            response = await client.get(path)
    finally:
        app.dependency_overrides.pop(get_infraestrutura_repository, None)
    assert response.status_code == expected
    assert repository.peer_queries == []


async def test_http_distingue_404_e_503():
    missing = await request(ControlledRepository([]))
    unavailable = await request(
        ControlledRepository([], failure=SQLAlchemyError("offline"))
    )
    assert (missing.status_code, missing.json()["code"]) == (404, "not_found")
    assert (unavailable.status_code, unavailable.json()["code"]) == (
        503,
        "warehouse_unavailable",
    )


@pytest.mark.parametrize(
    "records",
    [
        [row(SCHOOL, 2022, 9990001, [2] + [0] * 16)],
        [row(SCHOOL, 2022, 9990001, [1] * 17)] * 2,
        [
            row(SCHOOL, 2022, 9990001, [1] * 17),
            row(99000002, 2022, 9990001, [2] + [0] * 16),
        ],
        [row(SCHOOL, 2022, 9990001, [1] * 17)]
        + [row(99000002, 2022, 9990001, [0] * 17)] * 2,
    ],
    ids=[
        "valor_invalido_escola",
        "duplicata_escola",
        "valor_invalido_par",
        "duplicata_par",
    ],
)
async def test_http_bloqueia_integridade_com_erro_atual(records):
    response = await request(ControlledRepository(records))
    assert response.status_code == 500
    assert response.json()["code"] == "internal_error"
    assert set(response.json()) == {"code", "message"}


def _read_json(package, name):
    return json.loads((package / name).read_text(encoding="utf-8"))


def _verify_checksums(package):
    lines = (package / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    entries = []
    for line in lines:
        match = re.match(r"^([0-9a-fA-F]{64})\s+\*?(.+)$", line)
        if match:
            digest, name = match.groups()
            path = package / name
            assert path.parent == package and path.is_file()
            assert (
                hashlib.sha256(path.read_bytes()).hexdigest().casefold()
                == digest.casefold()
            )
            entries.append(name)
    assert len(entries) == 10 and len(set(entries)) == 10


async def test_http_concilia_pacote_dad03b_no_mesmo_snapshot():
    path = os.getenv("DAD03B_PACKAGE_DIR")
    if not path:
        pytest.skip(
            "Definir DAD03B_PACKAGE_DIR para acessar pacote restrito fora do Git"
        )
    package = Path(path).resolve(strict=True)
    _verify_checksums(package)
    manifest = _read_json(package, "manifest.json")
    q1 = _read_json(package, "q1.json")
    q2 = _read_json(package, "q2.json")
    independent = _read_json(package, "independent_calculations.json")
    assert manifest["snapshot_id"] and all(
        item["snapshot_id"] == manifest["snapshot_id"] for item in (q1, q2, independent)
    )
    assert (manifest["q1_rows"], manifest["q2_rows"]) == (4, 155)
    assert (q1["row_count"], q2["row_count"]) == (4, 155)
    assert len(q2["parameters"]) == manifest["q2_parameter_count"] == 16
    assert q1["query_sha256"] == manifest["query_sha256"]["Q1"]
    assert q2["query_sha256"] == manifest["query_sha256"]["Q2"]
    assert independent["indicator_count"] == 17
    assert [entry["year"] for entry in q1["rows"]] == list(YEARS)
    assert [entry["year"] for entry in independent["years"]] == list(YEARS)
    assert independent["mapping_errors"] == []

    target_ids = {entry["selected_school_id"] for entry in q1["rows"]}
    assert len(target_ids) == 1  # Identidade do alvo anual, sem expor o código.
    selected_id = next(iter(target_ids))
    assert all(
        sum(
            source["year"] == year
            and source["is_selected_school"]
            and source["school_id"] == selected_id
            for source in q2["rows"]
        )
        == 1
        for year in YEARS
    )
    rows = []
    for source in q2["rows"]:
        if not source["row_in_reference_municipality"]:
            continue
        reference = next(item for item in q1["rows"] if item["year"] == source["year"])
        assert source["municipality_code"] == reference["reference_municipality_code"]
        assert source["source_rows_for_key"] == 1
        assert not source["key_has_invalid_value"]
        values = [source[key.upper()] for key in INDICATORS]
        assert all(value in (0, 1, None) for value in values)
        rows.append(
            row(
                source["school_id"],
                source["year"],
                source["municipality_code"],
                values,
                name=source["school_name"],
                city=source["municipality_name"],
            )
        )
    assert (
        Counter((r["nu_ano_censo"], r["co_entidade"]) for r in rows).most_common(1)[0][
            1
        ]
        == 1
    )
    assert all(
        sum(r["co_entidade"] == selected_id and r["nu_ano_censo"] == year for r in rows)
        == 1
        for year in YEARS
    )
    assert all(
        sum(r["nu_ano_censo"] == year for r in rows)
        == next(item for item in q1["rows"] if item["year"] == year)[
            "reference_identified_school_year_keys"
        ]
        for year in YEARS
    )

    response = await request(ControlledRepository(rows), school=selected_id)
    assert response.status_code == 200
    series = response.json()["data"]["serie"]
    assert series == [independent_point(rows, selected_id, year) for year in YEARS]
    for year, reference, point in zip(YEARS, independent["years"], series, strict=True):
        assert reference["year"] == year and reference["status"] == "complete"
        assert reference["selected_excluded_from_reference"] is True
        assert not reference["errors"] and not reference["integrity_blockers"]
        assert not reference["availability_blockers"]
        selected = next(
            r
            for r in rows
            if r["nu_ano_censo"] == year and r["co_entidade"] == selected_id
        )
        school_exact = raw_index(selected)[2]
        assert school_exact == Fraction(reference["selected_index_percent"]) / 100
        peers = {
            r["co_entidade"]: r
            for r in rows
            if r["nu_ano_censo"] == year and r["co_entidade"] != selected_id
        }
        eligible = {school_id: raw_index(peer)[2] for school_id, peer in peers.items()}
        eligible = {
            school_id: value
            for school_id, value in eligible.items()
            if value is not None
        }
        historical_eligible = {
            comparator["school_id"]
            for comparator in reference["comparators"]
            if comparator["decision"] == "eligible"
        }
        # Só comparar os resultados históricos após comprovar a mesma população.
        assert eligible.keys() == historical_eligible
        assert len(eligible) == reference["N"] == point["quantidade_pares_validos"]
        for comparator in reference["comparators"]:
            if comparator["decision"] == "eligible":
                assert (
                    eligible[comparator["school_id"]]
                    == Fraction(comparator["individual_index_percent"]) / 100
                )
        mean_exact = sum(eligible.values(), Fraction(0)) / len(eligible)
        assert mean_exact == Fraction(reference["reference_percent"]) / 100
        assert school_exact - mean_exact == Fraction(reference["difference_pp"]) / 100
        assert point["indice_escola_percentual"] == rounded_percent(school_exact)
        assert point["media_municipal_percentual"] == rounded_percent(mean_exact)
        assert point["diferenca_pontos_percentuais"] == rounded_percent(
            school_exact - mean_exact
        )
