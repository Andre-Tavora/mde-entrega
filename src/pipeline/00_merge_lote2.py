import csv
t = open("entrega/auditar_lote2.csv", "rb").read()
try: s = t.decode("utf-8-sig")
except: s = t.decode("cp1252")
h = s.splitlines()[0]; sep = ";" if h.count(";") > h.count(",") else ","
L = list(csv.DictReader(s.splitlines(), delimiter=sep))
rc = next(c for c in L[0] if c.lower().startswith("resultado"))
A = list(csv.DictReader(open("entrega/amostra_auditoria.csv", encoding="utf-8-sig")))
idx = {a["id_questao"]: a for a in A}; base = {c: "" for c in A[0]}
for r in L:
    v = (r[rc] or "").strip().lower()
    if not v: continue
    i = r["id_questao"].strip()
    if i in idx: idx[i].update(resultado=v, tema_auditor=r.get("tema_auditor", ""))
    else:
        n = {**base, "id_questao": i, "decisao": "publicar", "tema_central": r.get("tema_central", ""), "caminho": r.get("caminho", ""), "confianca": r.get("confianca", ""), "tema_auditor": r.get("tema_auditor", ""), "resultado": v}
        A.append(n); idx[i] = n
with open("entrega/amostra_auditoria.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(A[0])); w.writeheader(); w.writerows(A)
print("ok:", sum(1 for a in A if a["resultado"] and a["decisao"] == "publicar"), "publicar auditadas")
