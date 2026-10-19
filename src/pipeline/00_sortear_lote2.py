import csv, json, glob, random, re, html
random.seed(42)
def rd(f):
    t = open(f, encoding="utf-8-sig").read(); s = ";" if t.split("\n")[0].count(";") > t.split("\n")[0].count(",") else ","
    return list(csv.DictReader(t.splitlines(), delimiter=s))
P = rd("entrega/publicacao.csv"); k = "id_questao" if "id_questao" in P[0] else "id"
Pm = {p[k]: p for p in P}
falta = open("entrega/falta_auditar_publicar.txt").read().split()
# estratifica por confianca (tercis) -> 15 de cada
falta.sort(key=lambda i: float(Pm[i].get("confianca") or 0))
n = len(falta); sel = []
for a, b in [(0, n//3), (n//3, 2*n//3), (2*n//3, n)]:
    sel += random.sample(falta[a:b], min(15, b-a))
# enunciados do JSONL
Q = {}
for f in glob.glob("data/**/*.jsonl", recursive=True):
    for l in open(f, encoding="utf-8"):
        try: d = json.loads(l)
        except: continue
        i = str(d.get("id") or d.get("id_questao") or "")
        if i and i not in Q: Q[i] = d
limpa = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(str(s or "")))).strip()
T = {}
for r in rd(glob.glob("data/**/temas.csv", recursive=True)[0]):
    T[str(r.get("id") or r.get("tema_id"))] = " > ".join(v for c, v in r.items() if c and c.lower() in ("disciplina","tema","subtema") and v)
with open("entrega/auditar_lote2.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["id_questao","confianca","tema_central","caminho","extras","enunciado","alternativas","resultado(acerto/erro/fora)","tema_auditor","obs"])
    for i in sel:
        p, d = Pm[i], Q.get(i, {}); tc = p.get("tema_central") or p.get("tema_central_id", "")
        w.writerow([i, p.get("confianca"), tc, T.get(str(tc), ""), p.get("extras", ""),
                    limpa(d.get("enunciado") or d.get("comando") or d.get("html"))[:1500],
                    limpa(d.get("alternativas"))[:800], "", "", ""])
print(f"sorteadas={len(sel)} | com texto={sum(i in Q for i in sel)} -> entrega/auditar_lote2.csv")
