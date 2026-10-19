import json, csv, sys, re, collections
pred, temas, quest = sys.argv[1:4]
R = list(csv.DictReader(open(temas, encoding="utf-8")))
info = {r["tema_id"].strip(): r for r in R}
base = lambda s: re.sub(r"\s*\(parte.*?\)", "", s.strip().lower())
grp = collections.defaultdict(set)
for r in R: grp[base(r["titulo"])].add(r["tema_id"].strip())
cl = {i: k for k, v in grp.items() if len(v) > 1 for i in v}
Q = {}
for l in open(quest, encoding="utf-8"):
    if not l.strip(): continue
    o = json.loads(l); qid = o.get("id_questao") or o.get("id")
    ks = [k for k in o if "assunto" in k.lower() or "tema" in k.lower()]
    Q[qid] = str(o[ks[0]]).strip() if ks else ""
print("Campo origem detectado em exemplo:", [k for k in json.loads(open(quest,encoding="utf-8").readline())])
c = collections.Counter()
for l in open(pred, encoding="utf-8"):
    o = json.loads(l); p = str(o["predicao_llm"].get("id_tema_escolhido") or "")
    org = Q.get(o["id_questao"], "")
    if p in cl or org in cl:
        tag = "MESMO" if p == org else ("IRMAO_DUP" if cl.get(p) == cl.get(org) else "OUTRO")
        c[(cl.get(p) or cl.get(org), tag)] += 1
        if tag != "MESMO": print(o["id_questao"], "pred", p, "| origem", org, "|", tag)
print("\nResumo:"); [print(" ", k, v) for k, v in sorted(c.items())]
