import json, csv, sys, collections
pred, quest, temas, out = sys.argv[1:5]
norm = lambda x: str(x).strip() if x is not None else ""
MAPA = {"direito penal":"penal","penal":"penal",
        "processo penal":"processo penal","direito processual penal":"processo penal",
        "criminologia":"criminologia",
        "direito penal - legislação especial":"direito penal - legislação especial"}
arv = {norm(r["tema_id"]): r for r in csv.DictReader(open(temas, encoding="utf-8"))}
Q = {norm(q["id"]): q for q in map(json.loads, open(quest, encoding="utf-8")) if q}
rows, cat = [], collections.Counter()
for o in map(json.loads, open(pred, encoding="utf-8")):
    p = o["predicao_llm"]; qid = norm(o["id_questao"]); t = norm(p.get("id_tema_escolhido"))
    orig = norm(Q.get(qid, {}).get("disciplina_origem")).lower()
    dp = arv[t]["disciplina"].strip().lower() if t in arv else ""
    if t not in arv: c = "id_invalido"
    elif not orig: c = "origem_vazia"
    elif orig not in MAPA: c = "origem_fora"
    elif MAPA[orig] == dp: c = "coerente"
    else: c = "divergente"
    cat[c] += 1
    rows.append({"id_questao":qid,"categoria_disc":c,"origem":orig,"predita":dp,
                 "tema_id":t,"tema":arv.get(t,{}).get("tema",""),"confianca":p.get("confianca"),
                 "assunto_origem":Q.get(qid,{}).get("assunto_origem","")})
with open(out,"w",newline="",encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(dict(cat))
