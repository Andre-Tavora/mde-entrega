import json, csv, sys
pred, temas = sys.argv[1:3]
arv = {str(r["tema_id"]).strip() for r in csv.DictReader(open(temas, encoding="utf-8"))}
for o in map(json.loads, open(pred, encoding="utf-8")):
    p = o["predicao_llm"]; t = p.get("id_tema_escolhido")
    ts = str(t).strip() if t is not None else ""
    if ts not in arv:
        tipo = "SEM_TEMA" if ts in ("", "None", "null") else "INVENTADO"
        print(o["id_questao"], tipo, repr(t), "| escopo:", p.get("dentro_do_escopo", p.get("fora_do_escopo")), "| conf:", p.get("confianca"))
