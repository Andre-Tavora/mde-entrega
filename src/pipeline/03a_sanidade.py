import json, csv, sys, collections
pred, temas = sys.argv[1], sys.argv[2]
norm = lambda x: str(x).strip() if x is not None else None
arv = {norm(r["tema_id"]): r for r in csv.DictReader(open(temas, encoding="utf-8"))}
ativos = {k for k, r in arv.items() if r.get("status", "").lower() in ("", "ativo", "active")}
linhas = [json.loads(l) for l in open(pred, encoding="utf-8") if l.strip()]
print("Chaves topo:", list(linhas[0].keys()))
idk = next((k for k in ("id", "questao_id", "id_questao", "qid", "codigo") if k in linhas[0]), None)
dk = next((k for k in ("disciplina", "disciplina_original") if k in linhas[0]), None)
conf, escopo = collections.Counter(), collections.Counter()
inval, inativo, extras_inval, disc_div, exemplos = [], [], 0, 0, []
for o in linhas:
    p = o["predicao_llm"]; qid = o.get(idk)
    conf[p.get("confianca")] += 1; escopo[p.get("pertence_ao_escopo")] += 1
    t = norm(p.get("id_tema_escolhido"))
    if p.get("pertence_ao_escopo") and t:
        if t not in arv: inval.append((qid, t))
        elif t not in ativos: inativo.append((qid, t))
        else:
            d = (o.get(dk) or "").strip().lower() if dk else ""
            if d and d not in arv[t]["disciplina"].lower() and arv[t]["disciplina"].lower() not in d:
                disc_div += 1
                if len(exemplos) < 5: exemplos.append((qid, d, arv[t]["disciplina"]))
    extras_inval += sum(1 for e in (p.get("ids_extras") or []) if norm(e) not in arv)
print(f"Campo ID: {idk} | Campo disciplina: {dk}")
print("Confiança:", dict(sorted(conf.items(), key=lambda x: str(x[0]))))
print("Escopo:", dict(escopo))
print(f"ID inexistente: {len(inval)} {inval[:5]}")
print(f"ID inativo: {len(inativo)} {inativo[:5]}")
print(f"Extras inválidos: {extras_inval}")
print(f"Disciplina divergente: {disc_div} {exemplos}")
