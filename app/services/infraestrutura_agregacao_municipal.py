"""BE10: orquestra agregação por indicador com consultas históricas BE02–BE04.

Não cria/alterar rota nem envelope HTTP: integração posterior com a BE09.
"""

import asyncio
from dataclasses import asdict

from app.core.exceptions import NotFoundError
from app.domain.infraestrutura_agregacao_municipal import agregar_indicadores_municipais
from app.schemas.infraestrutura import (
    ANOS_COMPARACAO_INFRAESTRUTURA,
    INDICADORES_COMPARACAO_INFRAESTRUTURA,
)


class InfraestruturaAgregacaoMunicipalService:
    """Produz dados internos para compor `data.serie` do contrato da BE09."""

    def __init__(self, repository):
        self._repository = repository

    async def calcular_serie(self, *, co_entidade: int) -> list[dict]:
        identificacao = await self._repository.find_identificacao_escola(
            co_entidade=co_entidade
        )
        if identificacao is None:
            raise NotFoundError(f"Escola {co_entidade} não encontrada.")

        historico = await self._repository.find_historico_escola(
            co_entidade=co_entidade,
            anos_comparaveis=ANOS_COMPARACAO_INFRAESTRUTURA,
        )
        registros = {}
        for registro in historico:
            if registro.co_entidade != co_entidade:
                raise ValueError("O histórico contém outra escola.")
            if registro.nu_ano_censo not in ANOS_COMPARACAO_INFRAESTRUTURA:
                raise ValueError("O histórico contém ano fora do recorte 2022–2025.")
            if registro.nu_ano_censo in registros:
                raise ValueError("Há registros duplicados da escola selecionada no ano.")
            registros[registro.nu_ano_censo] = registro

        anos_observados = sorted(registros)
        # Busca somente os pares correspondentes ao município de cada linha anual.
        referencias = await asyncio.gather(*(
            self._repository.find_pares_municipais(
                co_entidade_excluida=co_entidade,
                co_municipio=registros[ano].co_municipio,
                ano=ano,
            )
            for ano in anos_observados
            if registros[ano].co_municipio is not None
        ))
        pares_por_ano = dict(zip(
            (ano for ano in anos_observados if registros[ano].co_municipio is not None),
            referencias,
            strict=True,
        ))

        serie = []
        for ano in ANOS_COMPARACAO_INFRAESTRUTURA:
            escola = registros.get(ano)
            if escola is None:
                serie.append({
                    "ano": ano,
                    "registro_historico_disponivel": False,
                    "municipio_referencia": None,
                    "composicao_municipal": None,
                })
                continue
            agregados = agregar_indicadores_municipais(
                escola,
                pares_por_ano.get(ano, []),
                indicadores_esperados=INDICADORES_COMPARACAO_INFRAESTRUTURA,
            )
            serie.append({
                "ano": ano,
                "registro_historico_disponivel": True,
                "municipio_referencia": (
                    {"co_municipio": escola.co_municipio, "no_municipio": escola.no_municipio}
                    if escola.co_municipio is not None else None
                ),
                "composicao_municipal": (
                    {chave: asdict(valor) for chave, valor in agregados.items()}
                    if agregados is not None else None
                ),
            })
        return serie
