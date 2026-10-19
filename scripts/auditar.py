import csv, json, sys
from datetime import datetime
from pathlib import Path

BASE = Path("mde-entrega")
QST = BASE / "data/processed/questoes_limpas.jsonl"
TMS = BASE / "data/raw/temas.csv"
REVISAR = "--revisar" in sys.argv
argv = [a for a in sys.argv[1:] if a != "--revisar"]

def ler(p): return list(csv.DictReader(open(p, encoding="utf-8-sig"))) if p.exists() else []

temas = {r["tema_id"]: r for r in ler(TMS)}
qs = {q["id"]: q for q in (json.loads(l) for l in open(QST, encoding="utf-8") if l.strip())}

if REVISAR:
    AUD = BASE / "data/gold/auditoria_revisar.csv"
    TIPO = "tipo_acerto"
    campos = ["id","decisao","motivo","tema_central_id","extras_ids","confianca","correto","tipo_acerto","obs","auditado_em"]
    feitas = {r["id"]: r for r in ler(AUD)}
    rows = []
    for a in ler(BASE / "data/gold/amostra_revisar.csv"):
        r = {c: a.get(c, "") for c in campos}
        r.update({k: v for k, v in feitas.pop(a["id"], {}).items() if k in campos and v})
        rows.append(r)
    rows += [{c: f.get(c, "") for c in campos} for f in feitas.values()]
else:
    AUD = BASE / "output/auditoria_publicar.csv"
    TIPO = "tipo_erro"
    rows = ler(AUD); campos = list(rows[0].keys())
idx = {r["id"]: r for r in rows}

def caminho(t):
    t = str(t).strip(); return temas[t]["caminho"] if t in temas else f"?? ({t})"

def salvar():
    with open(AUD, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos, quoting=csv.QUOTE_ALL)
        w.writeheader(); w.writerows(rows)

def show(n):
    for r in [r for r in rows if r["correto"] == ""][:n]:
        q = qs.get(r["id"], {})
        print("=" * 90)
        print(f"{r['id']} | conf {r['confianca']} | {r.get('motivo','')} | origem: {q.get('disciplina_origem')} > {q.get('assunto_origem')}")
        print(q.get("texto_modelo", "(sem texto)")[:2500])
        print(f">> PREVISTO: {r['tema_central_id']} = {caminho(r['tema_central_id'])}")
        for e in filter(None, r.get("extras_ids", "").replace(";", "|").split("|")):
            print(f"   extra: {e} = {caminho(e)}")
    print(f"\nPendentes: {sum(r['correto']=='' for r in rows)}/{len(rows)}")

def stats():
    f = [r for r in rows if r["correto"] in ("0", "1", "fora")]
    ok = sum(r["correto"] == "1" for r in f)
    print(f"[{'REVISAR' if REVISAR else 'PUBLICAR'}] Feitas: {len(f)}/{len(rows)} | Acertos: {ok} | Precisao: {ok/max(len(f),1):.1%}")
    for r in f:
        if r["correto"] != "1": print(f"  {r['correto'].upper()} {r['id']}: {r[TIPO]} -> {r['obs']}")

def mark(args):
    for a in args:
        qid, v = a.split("=", 1); p = v.split(":", 2)
        r = idx.get(qid)
        if r is None: print("ID inexistente:", qid); continue
        r["correto"] = p[0]
        r[TIPO] = p[1] if len(p) > 1 else ""
        r["obs"] = p[2] if len(p) > 2 else ""
        if "auditado_em" in r: r["auditado_em"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    salvar(); stats()

cmd = argv[0] if argv else "stats"
if cmd == "show": show(int(argv[1]) if len(argv) > 1 else 5)
elif cmd == "mark": mark(argv[1:])
else: stats()
