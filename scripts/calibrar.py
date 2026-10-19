"""Calibra a confianca do nivel 5 (publicar) pela auditoria manual: limite inferior de Wilson 95%."""
import csv, json, math
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
AUD, OUT = BASE / "output/auditoria_publicar.csv", BASE / "data/gold/calibracao.json"
SIM = {"1", "s", "sim", "true", "ok", "acerto", "certo", "x"}

rows = list(csv.DictReader(open(AUD, encoding="utf-8")))
col = next((c for c in rows[0] if c.lower() in {"acerto", "ok", "correto", "status", "veredito"}), None)
if not col:
    raise SystemExit(f"Coluna de acerto nao encontrada. Colunas: {list(rows[0])}")
f = [r for r in rows if r[col].strip()]
n, k = len(f), sum(r[col].strip().lower() in SIM for r in f)
z = 1.96; p = k / n
lo = (p + z*z/(2*n) - z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))) / (1 + z*z/n)
PRIORS = {"1": 0.1, "2": 0.3, "3": 0.55, "4": 0.8}  # niveis 1-4: priors heuristicos (nao auditados -> revisar)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({**PRIORS, "5": round(lo, 3)}, indent=2), encoding="utf-8")
OUT.with_name("calibracao_meta.json").write_text(json.dumps({"n": n, "acertos": k, "p": round(p, 3), "wilson_lo95": round(lo, 3)}, indent=2), encoding="utf-8")
print(f"n={n} acertos={k} p={p:.3f} wilson_lo={lo:.3f} -> {OUT}")
