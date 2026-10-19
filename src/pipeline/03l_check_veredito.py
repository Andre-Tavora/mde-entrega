import csv, sys, collections
raw = open(sys.argv[1], encoding="utf-8-sig").read()
sep = ";" if raw.count(";") >= raw.count(",") else ","
rows = list(csv.DictReader(raw.splitlines(), delimiter=sep))
print("separador:", repr(sep), "| colunas:", list(rows[0]))
print(collections.Counter(repr((r.get("veredito") or "")) for r in rows))
