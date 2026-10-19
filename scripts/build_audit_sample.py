import json, csv, random, re, html
from pathlib import Path
from collections import Counter

RAW = Path("mde-entrega/data/raw")
PRED = Path("mde-entrega/data/raw_predictions/claude_results_dedup.jsonl")
OUT = Path("mde-entrega/data/audit/audit_sample.csv")
QUOTAS = {5: 30, 4: 30, 3: 20, 2: 10}
random.seed(42)

def limpa(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", str(t or "")))).strip()

def achar(d, *chaves):
    for k in chaves:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None

# Temas
temas = {r["tema_id"]: r for r in csv.DictReader(
    open(next(RAW.glob("tema*.csv")), encoding="utf-8-sig"))}
print("Status temas:", dict(Counter(t["status"] for t in temas.values())))

# Questoes
qfile = next(RAW.glob("ques*.jsonl"))
questoes = [json.loads(l) for l in open(qfile, encoding="utf-8") if l.strip()]
print("Campos questao:", list(questoes[0].keys()))
qmap = {str(achar(q, "id_questao", "id", "questao_id")): q for q in questoes}

# Predicoes
preds = [json.loads(l) for l in open(PRED, encoding="utf-8")]
print("Campos predicao_llm:", list((preds[0].get("predicao_llm") or {}).keys()))

def tema_pred(p):
    llm = p.get("predicao_llm") or {}
    v = achar(llm, "id_tema_escolhido", "tema_id"); return str(int(float(v))) if v not in (None, "") else ""

# Amostragem estratificada
por_conf = {}
for p in preds:
    c = (p.get("predicao_llm") or {}).get("confianca_modelo")
    por_conf.setdefault(c, []).append(p)
amostra = [p for p in preds if p.get("status") == "fora_escopo"]
for c, n in QUOTAS.items():
    pool = [p for p in por_conf.get(c, []) if p not in amostra]
    amostra += random.sample(pool, min(n, len(pool)))

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["id_questao", "confianca", "status", "disciplina_orig", "assunto_orig",
                "tema_id_pred", "caminho_pred", "justificativa", "enunciado",
                "alternativas", "veredito(ACERTO/ERRO/FORA)", "tema_correto", "obs"])
    for p in amostra:
        q = qmap.get(str(p["id_questao"]), {})
        llm = p.get("predicao_llm") or {}
        tid = tema_pred(p)
        alts = achar(q, "alternativas", "opcoes", "options") or ""
        if isinstance(alts, list):
            alts = " | ".join(limpa(a if isinstance(a, str) else json.dumps(a, ensure_ascii=False)) for a in alts)
        w.writerow([p["id_questao"], llm.get("confianca_modelo"), p.get("status"),
                    achar(q, "disciplina_origem"), achar(q, "assunto_origem"), tid,
                    temas.get(tid, {}).get("caminho", "??"),
                    limpa(achar(llm, "raciocinio_juridico", "justificativa"))[:400],
                    (limpa(achar(q, "enunciado_html")) + " || COMANDO: " + limpa(achar(q, "comando")))[:1800],
                    limpa(alts)[:1500], "", "", ""])

print(f"Amostra: {len(amostra)} -> {OUT}")
print("Por confianca:", dict(Counter((p.get('predicao_llm') or {}).get('confianca_modelo') for p in amostra)))
print("Tema pred nao encontrado:", sum(temas.get(tema_pred(p)) is None for p in amostra))

