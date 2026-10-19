import csv, json
from pathlib import Path
tf = next(Path("mde-entrega/data/raw").glob("tema*.csv"))
nivel = {t["tema_id"]: t["caminho"].count(">") for t in csv.DictReader(open(tf, encoding="utf-8-sig"))}
f = next(Path("mde-entrega/data").rglob("*pred*.jsonl"))
n0 = []
for l in open(f, encoding="utf-8"):
    p = json.loads(l)
    v = p.get("id_tema_escolhido")
    if v in (None, ""): continue
    tid = str(int(float(v)))
    if nivel.get(tid) == 0:
        n0.append((p.get("id"), tid, p.get("confianca_modelo")))
for x in n0: print(*x)
print("Total nivel 0:", len(n0))
