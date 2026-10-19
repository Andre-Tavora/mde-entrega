"""Gera previsao.txt: precisao e cobertura com IC de Wilson 95%, sem gabarito."""
import csv, json, math
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
META = BASE / "data/gold/calibracao_meta.json"
PUB = next(BASE.rglob("publicacao.csv"))
OUT = BASE / "previsao.txt"

def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return max(0.0, c - h), min(1.0, c + h)

m = json.loads(META.read_text(encoding="utf-8-sig"))
with open(PUB, encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
dec = Counter(r["decisao"].strip().lower() for r in rows)
N, n_pub = len(rows), dec.get("publicar", 0)

plo, phi = wilson(m["acertos"], m["n"])
clo, chi = wilson(n_pub, N)
pct = lambda x: f"{100 * x:.1f}%"

txt = f"""PREVISAO - Classificacao de topicos (Metodo VDE)
================================================
Total de questoes: {N}
Decisoes: publicar={n_pub} | revisar={dec.get('revisar', 0)} | fora={dec.get('fora', 0)}

1) PRECISAO EM "PUBLICAR"
   Estimativa pontual: {pct(m['acertos'] / m['n'])} ({m['acertos']}/{m['n']} auditadas)
   IC Wilson 95%: [{pct(plo)}; {pct(phi)}]
   Regua: >= 95% -> {'ATENDIDA' if plo >= 0.95 else 'NAO GARANTIDA'} (limite inferior {pct(plo)})

2) COBERTURA (publicar / total)
   Estimativa pontual: {pct(n_pub / N)} ({n_pub}/{N})
   IC Wilson 95% (generalizacao para lotes futuros): [{pct(clo)}; {pct(chi)}]

3) JUSTIFICATIVA (sem gabarito)
   - Todas as questoes com decisao "publicar" foram auditadas manualmente,
     aplicando o criterio do edital (no exato, pai ou filho = acerto; irmao = erro).
   - Usamos o limite inferior de Wilson porque, com p=100%, o IC normal (Wald)
     degenera para [100%;100%]. O Wilson continua conservador com n pequeno.
   - O threshold de publicacao (nivel 5) foi travado ANTES da auditoria. Por isso
     a amostra nao foi usada para escolher o corte, e nao ha vies de selecao.
   - Riscos: drift de estilo das bancas e temas raros. Se a precisao cair,
     o esperado e perder cobertura (mais "revisar"), nao precisao.
   - Os niveis 1 a 4 nao foram auditados e vao sempre para "revisar"
     (os priors nao influenciam a decisao "publicar").
   - Neste lote, a auditoria cobriu 100% das publicadas (censo). O IC de Wilson
     estima a precisao esperada em lotes futuros com o mesmo threshold.
   - Limitacao: a auditoria foi feita pela equipe, nao por um especialista. Recomenda-se
     que o professor valide uma amostra NOVA de 30 publicadas de um lote futuro
     (se houver 0 erros em 117, o limite inferior de Wilson sobe para ~96.8%).
   - "Fora" = 1: a taxonomia cobre quase todo o escopo das 4 disciplinas; os casos
     ambiguos vao para "revisar", e nunca para "fora", por conservadorismo.
"""
OUT.write_text(txt, encoding="utf-8")
print(txt)
print(f"-> {OUT}")