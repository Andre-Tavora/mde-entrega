import csv
from collections import Counter
def rd(f):
    t = open(f, encoding="utf-8-sig").read(); s = ";" if t.split("\n")[0].count(";") > t.split("\n")[0].count(",") else ","
    return list(csv.DictReader(t.splitlines(), delimiter=s))
P = {r.get("id_questao") or r.get("id"): r for r in rd("entrega/publicacao.csv")}
tc = lambda r: (r.get("tema_central") or r.get("tema_central_id") or "").strip()
for f, col in [("output/auditoria_publicar.csv","auditoria_ok"), ("data/gold/auditoria_revisar.csv","correto"), ("relatorio/amostra_auditoria_080.csv","veredito")]:
    R = rd(f); ids = [r["id"] for r in R]
    mesmo = sum(1 for r in R if r["id"] in P and tc(P[r["id"]]) == (r.get("tema_central_id") or tc(P[r["id"]])).strip())
    dec = Counter(P[i]["decisao"] for i in ids if i in P)
    print(f"\n{f}: n={len(R)} | ids no atual={sum(i in P for i in ids)} | mesmo tema={mesmo} | decisao atual={dict(dec)}")
    print("   valores:", dict(Counter((r.get(col) or "").strip() for r in R)), "| obs preenchida:", sum(1 for r in R if (r.get("obs") or "").strip()))
