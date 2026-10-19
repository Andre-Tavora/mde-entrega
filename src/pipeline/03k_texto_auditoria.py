import json, csv, sys, re, html
quest, aud = sys.argv[1:3]
Q = {}
for l in open(quest, encoding="utf-8"):
    if l.strip(): o = json.loads(l); Q[o["id"]] = o
print("Campos:", list(next(iter(Q.values())).keys()))
CH = ("enunciado","comando","texto","alternativa","questao","pergunta","body")
def limpa(v):
    if isinstance(v, list): v = " | ".join(limpa(x) for x in v)
    elif isinstance(v, dict): v = " | ".join(f"{k}) {limpa(x)}" for k, x in v.items())
    return " ".join(re.sub(r"<[^>]+>", " ", html.unescape(str(v or ""))).split())
def texto(q):
    partes = [limpa(v) for k, v in q.items() if any(c in k.lower() for c in CH)]
    return " || ".join(p for p in partes if p)[:1500]
rows = list(csv.DictReader(open(aud, encoding="utf-8-sig"), delimiter=";"))
vazios = 0
for r in rows:
    r["comando"] = texto(Q.get(r["id"], {}))
    vazios += not r["comando"]
with open(aud, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter=";"); w.writeheader(); w.writerows(rows)
print(f"Atualizado: {len(rows)} linhas | sem texto: {vazios}")
