import json, csv, sys, collections
pred, quest, temas = sys.argv[1], sys.argv[2], sys.argv[3]
norm = lambda x: str(x).strip() if x is not None else None
arv = {norm(r["tema_id"]): r for r in csv.DictReader(open(temas, encoding="utf-8"))}
Q = [json.loads(l) for l in open(quest, encoding="utf-8") if l.strip()]
print("Chaves questoes:", list(Q[0].keys()))
qk = next(k for k in ("id_questao", "id", "questao_id") if k in Q[0])
dk = next((k for k in ("disciplina_origem", "disciplina", "disciplina_original") if k in Q[0]), None)
disc = {norm(q[qk]): (q.get(dk) or "").strip().lower() for q in Q} if dk else {}
cruz, div, ex = collections.Counter(), 0, []
for l in open(pred, encoding="utf-8"):
    o = json.loads(l); p = o["predicao_llm"]; qid = norm(o["id_questao"])
    t = norm(p.get("id_tema_escolhido"))
    if t not in arv: continue
    d_orig, d_pred = disc.get(qid, ""), arv[t]["disciplina"].strip().lower()
    cruz[(d_orig, d_pred)] += 1
    if d_orig and d_orig not in d_pred and d_pred not in d_orig:
        div += 1
        if len(ex) < 8: ex.append((qid, d_orig, d_pred, p.get("confianca")))
print(f"Campo disciplina: {dk} | Divergentes: {div}")
for e in ex: print("  ", e)
print("Matriz original -> predita:")
for (a, b), n in cruz.most_common(): print(f"  {n:4d}  {a}  ->  {b}")

