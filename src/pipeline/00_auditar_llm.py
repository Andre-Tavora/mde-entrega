import csv, glob, json, os, re
import anthropic
F = "entrega/auditar_lote2.csv"
MODELO = os.getenv("JUIZ_MODELO", "claude-sonnet-4-5")
TP = (glob.glob("data/raw/temas.csv") or glob.glob("**/temas.csv", recursive=True))[0]
raw = open(TP, "rb").read()
try: s = raw.decode("utf-8-sig")
except: s = raw.decode("cp1252")
T = {r[0].strip(): {"pai": r[1].strip(), "nome": r[4].strip(), "cam": r[5].strip()}
     for r in csv.reader(s.splitlines()) if r and r[0].strip().isdigit()}
fil = {}
for k, v in T.items(): fil.setdefault(v["pai"], []).append(k)
def cam(i): return T.get(str(i).strip(), {}).get("cam", "?")
def lista(ids): return "\n".join(f"{x} = {T[x]['cam']}" for x in ids)

R = list(csv.DictReader(open(F, encoding="utf-8-sig"), delimiter=";"))
rc = next(c for c in R[0] if c.lower().startswith("resultado"))
for col in ("tema_auditor", "metodo_auditoria", "motivo_auditoria"):
    if col not in R[0]:
        for r in R: r[col] = ""
cli = anthropic.Anthropic()
SYS = """Voce e professor de Direito Penal auditando a classificacao de uma questao de concurso.
Regra: ACERTO se o tema previsto for o no exato, o PAI ou um FILHO do tema correto.
ERRO se o correto for um IRMAO ou outro ramo. FORA se a questao nao pertence a nenhum tema da arvore.
Se nao tiver certeza juridica, responda INCERTO. Nunca chute.
Responda SOMENTE um JSON: {"veredito":"acerto|erro|fora|incerto","tema_correto_id":"id ou vazio","motivo":"1 frase"}"""
def salvar():
    with open(F, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(R[0]), delimiter=";"); w.writeheader(); w.writerows(R)
for r in R:
    if r[rc].strip(): continue
    tc = r["tema_central"].strip(); pai = T.get(tc, {}).get("pai", "")
    irm = [x for x in fil.get(pai, []) if x != tc]
    msg = f"""QUESTAO: {r['enunciado']}
ALTERNATIVAS: {r['alternativas']}
TEMA PREVISTO: {tc} = {cam(tc)}
FILHOS DO PREVISTO (contam acerto):
{lista(fil.get(tc, [])) or '-'}
IRMAOS (contam erro):
{lista(irm) or '-'}"""
    try:
        out = cli.messages.create(model=MODELO, max_tokens=300, system=SYS,
            messages=[{"role": "user", "content": msg}])
        txt = out.content[0].text
        j = json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
    except Exception as ex:
        print(f"{r['id_questao']}: falha ({ex})"); continue
    v = str(j.get("veredito", "incerto")).lower()
    print(f"{r['id_questao']}: {v} | {j.get('motivo','')}")
    if v in ("acerto", "erro", "fora"):
        r[rc] = v; r["tema_auditor"] = str(j.get("tema_correto_id", ""))
        r["metodo_auditoria"] = f"llm-juiz:{MODELO}"; r["motivo_auditoria"] = j.get("motivo", "")
    salvar()
print("auditadas:", sum(1 for r in R if r[rc].strip()), "/", len(R))
