import csv, sys, math, collections
aud = sys.argv[1]
N = {"MESMO":59,"PAI_FILHO":46,"IRMAO":64,"OUTRO":105,"SEM_MAPA":81}
def wilson(k,n,z=1.96):
    if n==0: return (0,0,0)
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return p,max(0,c-h),min(1,c+h)
rows=[r for r in csv.DictReader(open(aud,encoding="utf-8-sig"),delimiter=";") if r["veredito"].strip().upper() in ("C","E","F")]
g=collections.defaultdict(list)
for r in rows: g[r["tag"]].append(r["veredito"].strip().upper()=="C")
print(f"{'estrato':10} {'n':>3} {'acc':>6}  IC95")
tot=sum(N[t] for t in g); est=0; var=0
for t,v in g.items():
    k,n=sum(v),len(v); p,lo,hi=wilson(k,n); w=N[t]/tot
    est+=w*p; var+=w*w*p*(1-p)/max(n-1,1)*(1-n/N[t])
    print(f"{t:10} {n:3} {p:6.1%}  [{lo:.1%}, {hi:.1%}]")
se=math.sqrt(var); print(f"\nPonderada: {est:.1%}  IC95 [{est-1.96*se:.1%}, {est+1.96*se:.1%}]")
b=collections.defaultdict(list)
for r in rows:
    try: c=float(r["confianca"])
    except: continue
    b[c].append(r["veredito"].strip().upper()=="C")
print("\nPor confianca (>= limiar):")
for lim in sorted(b):
    v=[x for c,l in b.items() if c>=lim for x in l]; p,lo,hi=wilson(sum(v),len(v))
    print(f"  >= {lim:<5} n={len(v):3} acc={p:.1%} wilson_inf={lo:.1%}")
