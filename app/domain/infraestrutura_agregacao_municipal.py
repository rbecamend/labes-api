"""BE10: composição municipal por indicador a partir dos registros históricos.

Esta função não publica contrato HTTP. A BE09 define a composição na API;
a BE10 fornece as contagens e percentuais auditáveis para cada indicador.
"""

from collections.abc import Collection, Iterable
from dataclasses import dataclass
from fractions import Fraction

from app.domain.infraestrutura import InfraestruturaRegistroBruto


@dataclass(frozen=True)
class AgregadoIndicadorMunicipal:
    """Campos previstos para `composicao_municipal[indicador]` na BE09."""

    quantidade_presentes: int
    quantidade_validos: int
    quantidade_sem_dados: int
    quantidade_escolas_referencia: int
    percentual_presentes: float | None
    cobertura_percentual: float | None


def agregar_indicadores_municipais(
    escola: InfraestruturaRegistroBruto,
    referencias: Iterable[InfraestruturaRegistroBruto],
    *,
    indicadores_esperados: Collection[str],
) -> dict[str, AgregadoIndicadorMunicipal] | None:
    """Apura presença/cobertura por indicador entre outras escolas do ano/município.

    T = quantidade de outras escolas do mesmo município histórico e ano.
    Para cada indicador, p=#1, a=#0, u=#NULL, v=p+a.
    Presença = 100*p/v (quando v>0); cobertura = 100*v/T (quando T>0).
    Usa Fraction e round(..., 2) como o domínio atual; não arredonda antes
    da divisão e não transforma nulo em zero.

    Município histórico ausente torna a composição indisponível (None).
    Duplicidade, identificador ausente e valor inesperado não são descartados
    silenciosamente: sinalizam erro de integridade para a camada chamadora.
    """
    chaves = tuple(indicadores_esperados)
    if not chaves or len(chaves) != len(set(chaves)):
        raise ValueError("A lista de indicadores deve ser não vazia e sem duplicatas.")

    if escola.co_municipio is None:
        return None

    pares = [
        registro for registro in referencias
        if registro.nu_ano_censo == escola.nu_ano_censo
        and registro.co_municipio == escola.co_municipio
        and registro.co_entidade != escola.co_entidade
    ]
    codigos = [registro.co_entidade for registro in pares]
    if any(codigo is None for codigo in codigos):
        raise ValueError("Existe escola de referência sem identificador.")
    if len(codigos) != len(set(codigos)):
        raise ValueError("Existem escolas de referência duplicadas no mesmo ano.")

    total = len(pares)
    resultado = {}
    for chave in chaves:
        presentes = ausentes = sem_dados = 0
        for par in pares:
            if chave not in par.indicadores:
                raise ValueError(f"Indicador ausente no registro da escola {par.co_entidade}: {chave}")
            valor = par.indicadores[chave]
            if valor is None:
                sem_dados += 1
            elif type(valor) is int and valor == 1:
                presentes += 1
            elif type(valor) is int and valor == 0:
                ausentes += 1
            else:
                raise ValueError(
                    f"Valor inválido para {chave} na escola {par.co_entidade}: {valor!r}"
                )
        validos = presentes + ausentes
        resultado[chave] = AgregadoIndicadorMunicipal(
            quantidade_presentes=presentes,
            quantidade_validos=validos,
            quantidade_sem_dados=sem_dados,
            quantidade_escolas_referencia=total,
            percentual_presentes=(
                float(round(Fraction(100 * presentes, validos), 2))
                if validos else None
            ),
            cobertura_percentual=(
                float(round(Fraction(100 * validos, total), 2))
                if total else None
            ),
        )
    return resultado
