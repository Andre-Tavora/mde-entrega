import csv, sys, collections, re
R = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
cols = list(R[0].keys()); print("Colunas:", cols)
nome = cols[4]; disc = cols[2]
base = lambda s: re.sub(r"\s*\(parte.*?\)", "", s.strip().lower())
g = collections.defaultdict(list)
for r in R: g[base(r[nome])].append(f'{r[cols[0]]}:{r[disc]}')
print("\nNomes repetidos na arvore:")
for k, v in sorted(g.items()):
    if len(v) > 1: print(f"  {k} -> {v}")
