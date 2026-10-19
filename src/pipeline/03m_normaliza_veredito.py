import csv, sys
p = sys.argv[1]
rows = list(csv.DictReader(open(p, encoding="utf-8-sig"), delimiter=";"))
assert "veredito" in rows[0], f"colunas inesperadas: {list(rows[0])}"
for r in rows: r["veredito"] = (r.get("veredito") or "").strip().upper()[:1]
with open(p, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter=";"); w.writeheader(); w.writerows(rows)
ok = sum(r["veredito"] in ("C","E","F") for r in rows)
print(f"preenchidos: {ok} / {len(rows)}")
