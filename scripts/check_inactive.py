import json
from pathlib import Path
INAT = {"5078", "5234"}
f = next(Path("mde-entrega/data").rglob("*pred*.jsonl"))
n = 0
for l in open(f, encoding="utf-8"):
    p = json.loads(l)
    v = p.get("id_tema_escolhido")
    ids = {str(int(float(v)))} if v not in (None, "") else set()
    ids |= {str(int(float(x))) for x in (p.get("ids_extras") or [])}
    if ids & INAT:
        n += 1
        print(p.get("id"), ids & INAT, p.get("confianca_modelo"))
print("Total em temas inativos:", n)
