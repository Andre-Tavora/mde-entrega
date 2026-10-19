import math, re
from pathlib import Path

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    m = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return max(0, c-m), min(1, c+m)

pct = lambda x: f"{x*100:.1f}%".replace(".", ",")
lo1, hi1 = wilson(87, 87)
lo2, hi2 = wilson(87, 359)
print("Precisao:", pct(lo1), pct(hi1), "| Cobertura:", pct(lo2), pct(hi2))

f = Path("output/previsao.txt")
out = []
for ln in f.read_text(encoding="utf-8-sig").splitlines():
    s = ln.strip()
    if s.startswith("IC 95% (Wilson):"):
        ln = f"   IC 95% (Wilson): [{pct(lo1)} ; {pct(hi1)}]"
    elif s.startswith("Compromisso:"):
        ln = f"   Compromisso: precisao >= {pct(lo1)} (limite inferior), acima da regua de 95%."
    elif s.startswith("IC 95% (Wilson, projecao"):
        ln = f"   IC 95% (Wilson, projecao para lotes futuros): [{pct(lo2)} ; {pct(hi2)}]"
    out.append(ln)
f.write_text("\n".join(out) + "\n", encoding="utf-8")
