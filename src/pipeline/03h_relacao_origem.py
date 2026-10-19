import json, csv, sys, re, collections, unicodedata
pred, temas, quest = sys.argv[1:4]

def n(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"parte\s*0*(\d+)", r"parte \1", s)
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())

R = {r["tema_id"].strip(): r for r in csv.DictReader(open(temas, encoding="utf-8"))}
par = {k: r["parent_id"].strip() for k, r in R.items()}
t2id = collections.defaultdict(list)
for k, r in R.items(): t2id[n(r["titulo"])].append(k)

def anc(x):
    out, cur = [], x
    for _ in range(10):
        p = par.get(cur)
        if not p or p not in R: break
        out.append(p); cur = p
    return set(out)

ORD = ["MESMO", "PAI_FILHO", "IRMAO", "OUTRO"]
def rel(p, o):
    if p == o: return "MESMO"
    if o in anc(p) or p in anc(o): return "PAI_FILHO"
    if par.get(p) and par.get(p) == par.get(o): return "IRMAO"
    return "OUTRO"

def origem_ids(org):
    itens = org if isinstance(org, list) else [org]
    ids = []
    for it in itens:
        for parte in [it] + str(it).split(","):
            ids += t2id.get(n(parte), [])
    return list(dict.fromkeys(ids))

Q = {}
for l in open(quest, encoding="utf-8"):
    if l.strip():
        o = json.loads(l); Q[o["id"]] = o.get("assunto_origem") or ""

c = collections.Counter(); out = []
for l in open(pred, encoding="utf-8"):
    o = json.loads(l)
    p = str(o["predicao_llm"].get("id_tema_escolhido") or "")
    if not p: continue
    org = Q.get(o["id_questao"], ""); ids = origem_ids(org)
    tag = min((rel(p, i) for i in ids), key=ORD.index) if ids else "SEM_MAPA"
    c[tag] += 1
    out.append((o["id_questao"], p, R.get(p, {}).get("titulo", "?"), str(org), tag))

for t in ("IRMAO", "OUTRO"):
    print(f"\n== {t} ==")
    for x in out:
        if x[4] == t: print(" ", " | ".join(x[:4]))
print("\nResumo:", dict(c))
sm = collections.Counter(x[3] for x in out if x[4] == "SEM_MAPA")
print("\nTop origens sem mapa:")
for k, v in sm.most_common(15): print(f"  {v:3} {k or '(vazio)'}")
