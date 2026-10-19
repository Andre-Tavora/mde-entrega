import json, csv, sys, re, random, difflib, collections, unicodedata, html
pred, temas, quest, saida = sys.argv[1:5]
def n(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii","ignore").decode().lower()
    s = re.sub(r"parte\s*0*(\d+)", r"parte \1", s)
    return " ".join(re.sub(r"[^a-z0-9 ]"," ",s).split())
sp = lambda s: re.sub(r"\s*parte \d+", "", s).strip()
R = {r["tema_id"].strip(): r for r in csv.DictReader(open(temas, encoding="utf-8"))}
par = {k: r["parent_id"].strip() for k,r in R.items()}
t2id = collections.defaultdict(list)
for k,r in R.items(): t2id[n(r["titulo"])].append(k); t2id[sp(n(r["titulo"]))].append(k)
def anc(x):
    o=set()
    while par.get(x) in R and len(o)<10: x=par[x]; o.add(x)
    return o
ORD=["MESMO","PAI_FILHO","IRMAO","OUTRO"]
def rel(p,o):
    if p==o: return "MESMO"
    if o in anc(p) or p in anc(o): return "PAI_FILHO"
    if par.get(p) and par.get(p)==par.get(o): return "IRMAO"
    return "OUTRO"
def mapa(org):
    ids, via = [], "exato"
    for it in (org if isinstance(org,list) else [org]):
        for x in [it]+str(it).split(","):
            k=n(x)
            if not k: continue
            ids += t2id.get(k,[]) or t2id.get(sp(k),[])
            if not ids:
                m=difflib.get_close_matches(sp(k), list(t2id), n=1, cutoff=0.85)
                if m: ids+=t2id[m[0]]; via="fuzzy"
    return list(dict.fromkeys(ids)), via
Q={}
for l in open(quest,encoding="utf-8"):
    if l.strip(): o=json.loads(l); Q[o["id"]]=o
rows=[]; c=collections.Counter()
for l in open(pred,encoding="utf-8"):
    o=json.loads(l); P=o["predicao_llm"]; p=str(P.get("id_tema_escolhido") or "")
    q=Q.get(o["id_questao"],{}); org=q.get("assunto_origem") or ""
    ids,via=mapa(org)
    tag = "SEM_TEMA" if not p else (min((rel(p,i) for i in ids),key=ORD.index) if ids else "SEM_MAPA")
    c[tag]+=1
    cmd=re.sub(r"<[^>]+>"," ",html.unescape(str(q.get("comando",""))))[:300]
    rows.append(dict(id=o["id_questao"],tag=tag,via=via,pred=p,pred_titulo=R.get(p,{}).get("titulo",""),
        confianca=P.get("confianca"),origem=str(org),comando=" ".join(cmd.split()),veredito=""))
print("Resumo:",dict(c))
random.seed(42); g=collections.defaultdict(list)
for r in rows: g[r["tag"]].append(r)
amostra=[]
for t,quota in {"MESMO":8,"PAI_FILHO":8,"IRMAO":15,"OUTRO":15,"SEM_MAPA":14}.items():
    amostra+=random.sample(g[t],min(quota,len(g[t])))
with open(saida,"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=";"); w.writeheader(); w.writerows(amostra)
print("Amostra:",len(amostra),"->",saida)
