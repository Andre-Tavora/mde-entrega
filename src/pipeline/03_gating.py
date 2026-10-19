import csv, json, random, collections
from pathlib import Path

R = Path(__file__).resolve().parents[2]
TEMAS = R / "data/raw/temas.csv"
SON = R / "data/raw_predictions/claude_results_dedup.jsonl"
HAI = R / "data/raw_predictions/haiku_results_v2.jsonl"
OUT = R / "entrega"; OUT.mkdir(exist_ok=True)
CONF_MIN, N_PUB, N_REV, SEED = 4, 80, 30, 42

def load(p):
    return {d["id_questao"]: d for d in (json.loads(l) for l in p.open(encoding="utf-8-sig") if l.strip())}

temas = {}
with TEMAS.open(encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        temas[int(r["tema_id"])] = dict(
            pai=int(r["parent_id"]) if r["parent_id"] else None,
            nivel=int(r["nivel"]), ativo=r["status"] == "active", caminho=r["caminho"])

def ok(i): return isinstance(i, int) and i in temas and temas[i]["ativo"]
def compat(a, b): return a == b or temas[a]["pai"] == b or temas[b]["pai"] == a  # regua: exato/pai/filho

def decide(s, h):
    ps = (s or {}).get("predicao_llm") or {}; ph = (h or {}).get("predicao_llm") or {}
    ts, th = ps.get("id_tema_escolhido"), ph.get("id_tema_escolhido")
    cs, ch = ps.get("confianca_modelo") or 0, ph.get("confianca") or 0
    fs, fh = ps.get("pertence_ao_escopo") is False, ph.get("pertence_ao_escopo") is False
    conf = round((cs + ch) / 10, 2)
    if fs and fh:                                  return "fora", None, conf, "ambos_fora"
    if fs or fh:                                   return "revisar", ts if ok(ts) else None, conf, "fora_divergente"
    if not (s and s.get("valido") and ok(ts)):     return "revisar", None, conf, "sonnet_invalido"
    if not (h and h.get("valido") and ok(th)):     return "revisar", ts, conf, "haiku_invalido"
    if not compat(ts, th):                         return "revisar", ts, conf, "discordancia"
    if temas[ts]["nivel"] == 0:                    return "revisar", ts, conf, "so_disciplina"
    if cs < CONF_MIN:                              return "revisar", ts, conf, "conf_baixa"
    return "publicar", ts, conf, "consenso"

S, H = load(SON), load(HAI)
linhas = []
for q in sorted(set(S) | set(H)):
    dec, t, conf, mot = decide(S.get(q), H.get(q))
    ex = [e for e in ((S.get(q) or {}).get("predicao_llm") or {}).get("ids_extras") or [] if ok(e) and e != t]
    linhas.append(dict(id_questao=q, decisao=dec, tema_central=t or "",
                       caminho=temas[t]["caminho"] if t else "", extras=";".join(map(str, ex)),
                       confianca=conf, motivo=mot))

cols = list(linhas[0])
with (OUT / "publicacao.csv").open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(linhas)

random.seed(SEED)
por = collections.defaultdict(list)
for l in linhas: por[l["decisao"]].append(l)
amostra = (random.sample(por["publicar"], min(N_PUB, len(por["publicar"])))
           + random.sample(por["revisar"], min(N_REV, len(por["revisar"]))) + por["fora"])
with (OUT / "amostra_auditoria.csv").open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, cols + ["tema_auditor", "resultado"]); w.writeheader()
    w.writerows({**a, "tema_auditor": "", "resultado": ""} for a in amostra)

print("decisao:", dict(collections.Counter(l["decisao"] for l in linhas)))
print("motivo :", dict(collections.Counter(l["motivo"] for l in linhas)))
print(f"total={len(linhas)} | amostra={len(amostra)}")
