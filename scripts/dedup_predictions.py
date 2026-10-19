import json
from pathlib import Path
from collections import Counter

SRC = Path("mde-entrega/data/raw_predictions/claude_results.jsonl")
DST = Path("mde-entrega/data/raw_predictions/claude_results_dedup.jsonl")

best, total = {}, 0
with SRC.open(encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        total += 1
        r = json.loads(line)
        qid = r["id_questao"]
        atual = best.get(qid)
        if atual is None or r.get("valido") or not atual.get("valido"):
            best[qid] = r

with DST.open("w", encoding="utf-8") as f:
    for qid in sorted(best):
        f.write(json.dumps(best[qid], ensure_ascii=False) + "\n")

regs = best.values()
print(f"Linhas lidas: {total} | Unicas: {len(best)}")
print(f"Invalidas: {sum(not r.get('valido') for r in regs)}")
print("Status:", dict(Counter(r.get("status") for r in regs)))
print("Confianca:", dict(sorted(Counter(
    (r.get("predicao_llm") or {}).get("confianca_modelo") for r in regs).items(),
    key=lambda x: str(x[0]))))
print(f"Fora do escopo: {sum((r.get('predicao_llm') or {}).get('pertence_ao_escopo') is False for r in regs)}")
