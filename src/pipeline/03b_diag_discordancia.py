import csv, json, collections
from pathlib import Path
R = Path(__file__).resolve().parents[2]
T = {}
for r in csv.DictReader((R/"data/raw/temas.csv").open(encoding="utf-8-sig")):
    T[int(r["tema_id"])] = (int(r["parent_id"]) if r["parent_id"] else None, int(r["nivel"]), r["disciplina"])
def anc(i):
    out = []
    while T[i][0] is not None: i = T[i][0]; out.append(i)
    return out
ld = lambda p: {d["id_questao"]: d for d in map(json.loads, p.open(encoding="utf-8-sig")) if d}
S = ld(R/"data/raw_predictions/claude_results_dedup.jsonl"); H = ld(R/"data/raw_predictions/haiku_results_v2.jsonl")
P = {r["id_questao"]: r for r in csv.DictReader((R/"entrega/publicacao.csv").open(encoding="utf-8-sig"))}
c = collections.Counter(); conf = collections.Counter()
for q, r in P.items():
    if r["motivo"] != "discordancia": continue
    a = S[q]["predicao_llm"]["id_tema_escolhido"]; b = H[q]["predicao_llm"]["id_tema_escolhido"]
    if a in anc(b) or b in anc(a): k = "ancestral_distante"
    elif T[a][0] == T[b][0]: k = "irmao"
    elif T[a][2] != T[b][2]: k = "outra_disciplina"
    else: k = "mesma_disc_ramo_diferente"
    c[k] += 1; conf[(k, S[q]["predicao_llm"].get("confianca_modelo"))] += 1
print(dict(c)); print(sorted(conf.items()))
