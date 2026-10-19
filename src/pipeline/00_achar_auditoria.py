import csv, glob, re
from collections import Counter
P = re.compile(r"^(acerto|erro|fora|certo|errado|ok|correto|incorreto|sim|nao|não|1|0|true|false)$", re.I)
for f in sorted(glob.glob("**/*audit*.csv", recursive=True) + glob.glob("**/amostra*.csv", recursive=True)):
    raw = open(f, encoding="utf-8-sig", errors="replace").read()
    if not raw.strip(): print(f"\n### {f}: VAZIO"); continue
    sep = ";" if raw.splitlines()[0].count(";") > raw.splitlines()[0].count(",") else ","
    R = list(csv.DictReader(raw.splitlines(), delimiter=sep))
    print(f"\n### {f}  linhas={len(R)} sep='{sep}'")
    print("   colunas:", list(R[0].keys()) if R else [])
    for c in (R[0].keys() if R else []):
        v = Counter((r.get(c) or "").strip().lower() for r in R)
        hits = {k: n for k, n in v.items() if P.match(k)}
        if hits and not c.lower().startswith(("id", "tema", "conf")): print(f"   >> {c}: {hits}")
