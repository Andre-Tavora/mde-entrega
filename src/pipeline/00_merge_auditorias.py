import csv
def rd(f):
    t = open(f, encoding="utf-8-sig").read(); s = ";" if t.split("\n")[0].count(";") > t.split("\n")[0].count(",") else ","
    return list(csv.DictReader(t.splitlines(), delimiter=s))
V = {}
for r in rd("data/gold/auditoria_revisar.csv"): V[r["id"]] = "acerto" if r["correto"].strip()=="1" else "erro"
for r in rd("relatorio/amostra_auditoria_080.csv"): V.setdefault(r["id"], {"C":"acerto","E":"erro"}.get(r["veredito"].strip(), ""))
P = rd("entrega/publicacao.csv"); k = "id_questao" if "id_questao" in P[0] else "id"
A = rd("entrega/amostra_auditoria.csv"); ids = {r["id_questao"] for r in A}
for r in A: r["resultado"] = r["resultado"].strip() or V.get(r["id_questao"], "")
base = {c: "" for c in A[0]}
for p in P:
    if p[k] in V and p[k] not in ids:
        A.append({**base, "id_questao": p[k], "decisao": p["decisao"], "tema_central": p.get("tema_central",""), "confianca": p.get("confianca",""), "resultado": V[p[k]]})
with open("entrega/amostra_auditoria.csv","w",newline="",encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(A[0])); w.writeheader(); w.writerows(A)
pub = [p[k] for p in P if p["decisao"]=="publicar"]; feitos = {r["id_questao"] for r in A if r["resultado"]}
falta = [i for i in pub if i not in feitos]
print(f"publicar total={len(pub)} | auditadas={len(pub)-len(falta)} | faltam={len(falta)}")
with open("entrega/falta_auditar_publicar.txt","w") as f: f.write("\n".join(falta))
