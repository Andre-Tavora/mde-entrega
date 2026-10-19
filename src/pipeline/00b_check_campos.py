import json, sys
n = vc = ve = va = 0
for l in open(sys.argv[1], encoding="utf-8"):
    if not l.strip(): continue
    q = json.loads(l); n += 1
    vc += not str(q.get("comando") or "").strip()
    ve += not str(q.get("enunciado_html") or "").strip()
    va += not q.get("alternativas")
print(f"total={n} | comando vazio={vc} | enunciado vazio={ve} | alternativas vazias={va}")
