import json, csv, sys, collections
pred, temas = sys.argv[1:3]
L = [json.loads(l) for l in open(pred, encoding="utf-8") if l.strip()]
print("Chaves predicao_llm:", sorted({k for o in L for k in o["predicao_llm"]}))
print("Chaves topo:", sorted({k for o in L for k in o}))
for qid in ("Q0014","Q0142","Q0230","Q0268"):
    o = next((x for x in L if x["id_questao"]==qid), None)
    if o: print(qid, json.dumps(o["predicao_llm"], ensure_ascii=False)[:400])
print("\nRamo 57xx / 67xx / 70xx na arvore:")
for r in csv.DictReader(open(temas, encoding="utf-8")):
    t = str(r["tema_id"]).strip()
    if t.startswith(("57","67","70","53")): print(" ", t, "|", " | ".join(str(v) for k,v in r.items() if k!="tema_id"))
