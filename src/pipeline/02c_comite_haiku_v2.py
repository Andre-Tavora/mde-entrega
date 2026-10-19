from dotenv import load_dotenv
load_dotenv(r"C:\Users\André Tavora\Desktop\CASE IA\CASE_CARLOSANDRE\mde-entrega\.env")
import csv, json, os, re, sys, time
from pathlib import Path
import anthropic

Q_PATH = Path(sys.argv[1]); T_PATH = Path(sys.argv[2])
LIMITE = int(sys.argv[3]) if len(sys.argv) > 3 else 0
OUT = Path("data/raw_predictions/haiku_results_v2.jsonl")
MODELO = os.getenv("MODELO_HAIKU", "claude-haiku-5-5")
client = anthropic.Anthropic()

# ---------- Árvore ----------
with open(T_PATH, encoding="utf-8-sig", newline="") as f:
    cab = f.readline(); f.seek(0)
    delim = max([",", ";", "\t", "|"], key=cab.count)
    linhas = list(csv.DictReader(f, delimiter=delim))
print(f"Delimitador: {delim!r} | colunas: {list(linhas[0].keys())}")
cols = {c.lower(): c for c in linhas[0].keys()}
col_id = next((cols[c] for c in cols if c in ("id", "id_tema", "tema_id", "codigo")), list(linhas[0].keys())[0])
col_ativo = next((cols[c] for c in cols if "ativo" in c or "status" in c), None)

def ativo(r):
    if not col_ativo: return True
    return str(r[col_ativo]).strip().lower() in ("1", "true", "sim", "s", "ativo", "active", "yes")

nos = [r for r in linhas if ativo(r)]
IDS_ATIVOS = {int(re.search(r"\d+", r[col_id]).group()) for r in nos}
ARVORE_TXT = "\n".join(" | ".join(f"{k}={r[k]}" for k in linhas[0].keys()) for r in nos)
print(f"Árvore ativa: {len(IDS_ATIVOS)} nós | modelo: {MODELO}")

SYSTEM = [
    {"type": "text", "text":
     "Você classifica questões de concurso (Penal, Processo Penal, Legislação Especial, Criminologia) "
     "no tema MAIS ESPECÍFICO da árvore abaixo. NÃO resolva a questão. NÃO diga qual alternativa é correta. "
     "Foque no instituto jurídico cobrado pelo comando e alternativas. Atenção a subtemas irmãos: "
     "escolha o irmão errado é o pior erro; se houver dúvida entre irmãos, escolha o nó pai e reduza a confiança. "
     "Se a questão não pertence a nenhum tema, use pertence_ao_escopo=false e id_tema_escolhido=null.\n"
     "Confiança: 5=inequívoco, 4=forte, 3=plausível com alternativa próxima, 2=dúvida real, 1=chute.\n\n"
     "ÁRVORE DE TEMAS:\n" + ARVORE_TXT,
     "cache_control": {"type": "ephemeral"}}
]

TOOL = {
    "name": "classificar_tema",
    "description": "Registra a classificação temática da questão.",
    "input_schema": {
        "type": "object",
        "properties": {
            "pertence_ao_escopo": {"type": "boolean"},
            "id_tema_escolhido": {"type": ["integer", "null"]},
            "confianca": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
            "ids_extras": {"type": "array", "items": {"type": "integer"}, "maxItems": 3},
            "justificativa": {"type": "string",
                              "description": "Máx. 2 frases: por que este tema e não o irmão."}
        },
        "required": ["pertence_ao_escopo", "id_tema_escolhido", "confianca", "ids_extras", "justificativa"]
    }
}

def to_int(v):
    if isinstance(v, bool) or v is None: return None
    if isinstance(v, int): return v
    m = re.search(r"\d+", str(v)); return int(m.group()) if m else None

def texto_questao(q):
    partes = []
    for k, v in q.items():
        if k.lower() in ("id", "id_questao", "gabarito", "resposta"): continue
        if isinstance(v, (list, dict)): v = json.dumps(v, ensure_ascii=False)
        if v not in (None, ""): partes.append(f"[{k}]\n{v}")
    return "\n\n".join(partes)

def validar(p):
    if p is None: return "sem_resposta"
    if p.get("pertence_ao_escopo") is False: return "fora_escopo"
    if p.get("id_tema_escolhido") is None: return "id_nao_inteiro"
    if p["id_tema_escolhido"] not in IDS_ATIVOS: return "id_inexistente_ou_inativo"
    if p.get("confianca") not in (1, 2, 3, 4, 5): return "confianca_invalida"
    return "ok"

# ---------- Retomada ----------
feitas = {}
if OUT.exists():
    for l in OUT.read_text(encoding="utf-8").splitlines():
        r = json.loads(l)
        if r["valido"]: feitas[r["id_questao"]] = r
print(f"Retomando: {len(feitas)} válidas já processadas.")

questoes = [json.loads(l) for l in Q_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
if LIMITE: questoes = questoes[:LIMITE]
tin = tout = 0; t0 = time.time()

with open(OUT, "a", encoding="utf-8") as fo:
    for q in questoes:
        qid = q.get("id_questao") or q.get("id")
        if qid in feitas: continue
        print(f"Processando {qid}...", end=" ", flush=True)
        pred, uso = None, {}
        for tentativa in range(3):
            try:
                resp = client.messages.create(
                    model=MODELO, max_tokens=400, system=SYSTEM,
                    messages=[{"role": "user", "content": texto_questao(q) +
                               "\n\nClassifique o tema chamando classificar_tema. Não resolva a questão."}],
                    tools=[TOOL], tool_choice={"type": "tool", "name": "classificar_tema"})
                uso = {"input": resp.usage.input_tokens, "output": resp.usage.output_tokens,
                       "cache_read": getattr(resp.usage, "cache_read_input_tokens", 0) or 0,
                       "stop_reason": resp.stop_reason}
                b = next((x for x in resp.content if x.type == "tool_use"), None)
                if b:
                    pred = dict(b.input)
                    pred["id_tema_escolhido"] = to_int(pred.get("id_tema_escolhido"))
                    pred["confianca"] = to_int(pred.get("confianca"))
                    pred["ids_extras"] = [i for i in map(to_int, pred.get("ids_extras") or [])
                                          if i in IDS_ATIVOS and i != pred["id_tema_escolhido"]]
                break
            except anthropic.APIError as e:
                print(f"[erro API: {e.__class__.__name__}, retry]", end=" ", flush=True)
                time.sleep(5 * (tentativa + 1))
        st = validar(pred)
        tin += uso.get("input", 0); tout += uso.get("output", 0)
        fo.write(json.dumps({"id_questao": qid, "modelo": MODELO, "predicao_llm": pred, "status": st,
                             "uso_tokens": uso, "valido": st in ("ok", "fora_escopo"),
                             "via": "tool_use_v2"}, ensure_ascii=False) + "\n")
        fo.flush(); print(st)

print(f"\nProcessadas: {len(questoes)} | tokens in: {tin} | out: {tout} | tempo: {time.time()-t0:.0f}s")




