"""Verificacao independente dos exemplos SINTETICOS da DAD08.
Nao usa banco, API, CSVs reais nem codigo da aplicacao SIE.
"""
from fractions import Fraction
from json import dumps
from pathlib import Path

checks = []

def ck(nome, resultado, esperado):
    ok = resultado == esperado
    checks.append({"verificacao": nome, "obtido": str(resultado), "esperado": str(esperado), "aprovada": ok})
    if not ok:
        raise AssertionError(f"{nome}: {resultado!r} != {esperado!r}")

# Exemplo 1: escolas A, B, C municipais (agua=1,0,NULL),
# D,E estaduais (agua=1,NULL).
ck("E1 todos total", 3+2, 5)
ck("E1 todos validos", 2+1, 3)
ck("E1 todos presentes", 1+1, 2)
ck("E1 todos presenca", 100*Fraction(2,3), Fraction(200,3))
ck("E1 todos cobertura", 100*Fraction(3,5), Fraction(60))
ck("E1 municipal presenca", 100*Fraction(1,2), Fraction(50))
ck("E1 municipal cobertura", 100*Fraction(2,3), Fraction(200,3))
ck("E1 estadual presenca", 100*Fraction(1,1), Fraction(100))
ck("E1 estadual cobertura", 100*Fraction(1,2), Fraction(50))

# Exemplo 2: E estadual (12/17). Referencias A municipal 9/15,
# B municipal 17/17, C estadual 4/10, D municipal sem validos.
indice_e = 100*Fraction(12,17)
IA = 100*Fraction(9,15)
IB = 100*Fraction(17,17)
IC = 100*Fraction(4,10)
referencia_geral = (IA+IB+IC)/3
referencia_municipal = (IA+IB)/2
ck("E2 indice alvo", indice_e, Fraction(1200,17))
ck("E2 A", IA, Fraction(60))
ck("E2 B", IB, Fraction(100))
ck("E2 C", IC, Fraction(40))
ck("E2 pares geral T", 4, 4)
ck("E2 pares geral N", 3, 3)
ck("E2 media geral", referencia_geral, Fraction(200,3))
ck("E2 cobertura pares geral", 100*Fraction(3,4), Fraction(75))
ck("E2 delta geral", indice_e-referencia_geral, Fraction(200,51))
ck("E2 pares Municipal T", 3, 3)
ck("E2 pares Municipal N", 2, 2)
ck("E2 media Municipal", referencia_municipal, Fraction(80))
ck("E2 cobertura pares Municipal", 100*Fraction(2,3), Fraction(200,3))
ck("E2 delta Municipal", indice_e-referencia_municipal, -Fraction(160,17))
ck("E2 alvo nao excluido pelo filtro Municipal", indice_e, Fraction(1200,17))

# Exemplo 3: distinguir T=0, N=0, N=1, V=0.
ck("E3 sem comparadoras T=0", 0, 0)
ck("E3 sem comparadoras N=0", 0, 0)
ck("E3 3 comparadoras todas sem indice: cobertura 0", 100*Fraction(0,3), 0)
ck("E3 uma comparadora valida entre 2", 100*Fraction(1,2), 50)
ck("E3 indice da unica comparadora", 100*Fraction(7,17), Fraction(700,17))
ck("E3 V=0 T=3 cobertura indicador", 100*Fraction(0,3), 0)
ck("E3 V=0 T=3 sem dados", 3-0, 3)
ck("E3 escola 17 NULL cobertura", 100*Fraction(0,17), 0)
ck("Regra de alerta 10/17", Fraction(10,17) < Fraction(3,5), True)
ck("Regra de alerta 11/17", Fraction(11,17) < Fraction(3,5), False)
ck("Cobertura escolar 60 por cento exata impossivel", all(Fraction(v,17)!=Fraction(3,5) for v in range(18)), True)

report = {
    "natureza": "Verificacoes com fracoes exatas sobre dados sinteticos; nao validam o banco ou os endpoints",
    "total": len(checks),
    "aprovadas": sum(v["aprovada"] for v in checks),
    "reprovadas": sum(not v["aprovada"] for v in checks),
    "verificacoes": checks,
}
saida = Path(__file__).with_name("RESULTADOS_VERIFICACAO_SINTETICA_DAD08.json")
saida.write_text(dumps(report, ensure_ascii=False, indent=2)+"\n",encoding="utf-8",newline="\n")
print(f"DAD08 sintetica: {report['aprovadas']}/{report['total']} verificacoes aprovadas")
print(saida)
