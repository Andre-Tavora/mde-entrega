import csv
t = open("entrega/auditar_lote2.csv", "rb").read()
for enc in ("utf-8-sig", "cp1252"):
    try: s = t.decode(enc); break
    except: pass
h = s.splitlines()[0]
print("encoding:", enc, "| sep:", ";" if h.count(";") > h.count(",") else ",")
print("cabecalho:", h)
R = list(csv.reader(s.splitlines(), delimiter=";" if h.count(";") > h.count(",") else ","))
col = next((j for j, c in enumerate(R[0]) if c.lower().startswith("resultado")), None)
print("coluna resultado idx:", col, "| preenchidas:", sum(1 for r in R[1:] if col is not None and len(r) > col and r[col].strip()))
