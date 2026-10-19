import csv, textwrap, glob
F = "entrega/auditar_lote2.csv"
TP = (glob.glob("data/raw/temas.csv") or glob.glob("**/temas.csv", recursive=True))[0]
raw = open(TP, "rb").read()
try: s = raw.decode("utf-8-sig")
except: s = raw.decode("cp1252")
T = {}
for row in csv.reader(s.splitlines()):
    if row and row[0].strip().isdigit():
        T[row[0].strip()] = {"pai": row[1].strip(), "nome": row[4].strip(), "cam": row[5].strip()}
filhos = {}
for k, v in T.items(): filhos.setdefault(v["pai"], []).append(k)
def nome(i): i = str(i).strip(); return f"{i} = {T[i]['cam']}" if i in T else f"{i} = (nao achado)"
def irmaos(i):
    i = str(i).strip()
    if i not in T: return ""
    return ", ".join(T[x]["nome"] for x in filhos.get(T[i]["pai"], []) if x != i)
def subs(i): return ", ".join(T[x]["nome"] for x in filhos.get(str(i).strip(), []))

R = list(csv.DictReader(open(F, encoding="utf-8-sig"), delimiter=";"))
rc = next(c for c in R[0] if c.lower().startswith("resultado"))
def salvar():
    with open(F, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(R[0]), delimiter=";"); w.writeheader(); w.writerows(R)
pend = [r for r in R if not r[rc].strip()]
print(f"pendentes: {len(pend)}/{len(R)} | a=acerto e=erro f=fora s=pular q=sair\n")
for n, r in enumerate(pend, 1):
    tc = r["tema_central"].strip()
    print("=" * 90)
    print(f"[{n}/{len(pend)}] id={r['id_questao']} | conf={r['confianca']}")
    print(f"PREVISTO : {nome(tc)}")
    for e in [x for x in r.get("extras", "").replace(",", "|").split("|") if x.strip()]:
        print(f"EXTRA    : {nome(e)}")
    if subs(tc): print(f"FILHOS (=acerto): {subs(tc)}")
    print(f"IRMAOS (=ERRO) : {irmaos(tc)}")
    print("-" * 90); print(textwrap.fill(r["enunciado"], 90))
    print("-" * 90); print(textwrap.fill(r["alternativas"], 90))
    while True:
        k = input("veredito [a/e/f/s/q]: ").strip().lower()
        if k in ("a", "e", "f", "s", "q"): break
    if k == "q": break
    if k == "s": continue
    r[rc] = {"a": "acerto", "e": "erro", "f": "fora"}[k]
    if k in ("e", "f"):
        r["tema_auditor"] = input("tema correto (id ou Enter): ").strip()
    salvar()
print("feitas:", sum(1 for r in R if r[rc].strip()), "/", len(R))
