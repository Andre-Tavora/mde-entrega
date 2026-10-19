import csv, math, collections
from pathlib import Path
R = Path(__file__).resolve().parents[2]; E = R / "entrega"
def wilson(k, n, z=1.96):
    if n == 0: return (0, 0, 0)
    p = k/n; d = 1 + z*z/n; c = (p + z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return p, max(0, c-h), min(1, c+h)
A = [r for r in csv.DictReader((E/"amostra_auditoria.csv").open(encoding="utf-8-sig")) if r["resultado"].strip()]
P = list(csv.DictReader((E/"publicacao.csv").open(encoding="utf-8-sig")))
N = len(P); tot = collections.Counter(r["decisao"] for r in P)
g = collections.defaultdict(collections.Counter)
for r in A: g[r["decisao"]][r["resultado"].strip().lower()] += 1
pub = g["publicar"]; n = sum(pub.values()); k = pub["acerto"]
if n < 30: raise SystemExit(f'Auditoria insuficiente: {n} questoes publicar auditadas (minimo 30, alvo 80).')
p, lo, hi = wilson(k, n)
cov, clo, chi = wilson(tot["publicar"], N)
rev = g["revisar"]; nr = sum(rev.values())
txt = f"""PREVISAO - Classificacao de Topicos (sem gabarito)
Metodo: auditoria manual de amostra aleatoria estratificada (seed=42), IC de Wilson 95%.

PRECISAO em 'publicar': {p:.1%}  IC95% [{lo:.1%} ; {hi:.1%}]  (auditadas {n}/{tot['publicar']}, acertos {k})
COBERTURA (publicar/total): {tot['publicar']}/{N} = {cov:.1%}  IC95% [{clo:.1%} ; {chi:.1%}]
Distribuicao: {dict(tot)}
Taxa de acerto do top-1 em 'revisar' (fila do professor): {rev['acerto']}/{nr} = {(rev['acerto']/nr if nr else 0):.1%}
Regua >=95%: {'ATENDIDA (limite inferior >= 95%)' if lo >= .95 else 'ESTIMATIVA PONTUAL >= 95%, limite inferior abaixo' if p >= .95 else 'NAO ATENDIDA - subir CONF_MIN'}

Justificativa: publica-se apenas com consenso Sonnet+Haiku (mesmo no / pai-filho), confianca Sonnet >= 4,
no abaixo da raiz. Amostra de {n} de {tot['publicar']} (fracao {n/max(1,tot['publicar']):.0%}); sem correcao de populacao finita -> IC conservador.
Lacunas da arvore (Org. Criminosa, RDD, LEP) roteadas para revisar/fora.
"""
(E/"previsao.txt").write_text(txt, encoding="utf-8"); print(txt)

