import csv
import json
from pathlib import Path
from schema import *

COLS = ["id", "decisao", "tema_central_id", "extras_ids", "confianca", "motivo"]
PATH_CALIB = Path(PATH_PUBLICACAO).parent.parent / "data" / "gold" / "calibracao.json"

# Provisório até o conjunto-ouro: conf bruta 1-5 -> chance estimada 0-1.
# Lido de data/gold/calibracao.json (nivel 5 = limite inferior de Wilson 95%; niveis 1-4 = priors).
CALIB_PADRAO = {"1": 0.10, "2": 0.30, "3": 0.55, "4": 0.80, "5": 0.92}


def carregar_calib():
    if PATH_CALIB.exists():
        return json.loads(PATH_CALIB.read_text(encoding="utf-8-sig"))
    return CALIB_PADRAO


def carregar_temas():
    with open(PATH_TEMAS, encoding=CSV_ENCODING) as f:
        return {r[T_ID]: r for r in csv.DictReader(f)}


def carregar_predicoes():
    """Última resposta válida por questão; se nenhuma válida, a última."""
    por_id = {}
    for l in open(PATH_PRED, encoding="utf-8"):
        if not l.strip():
            continue
        x = json.loads(l)
        ant = por_id.get(x[K_ID])
        if ant is None or x.get(K_VALIDO) or not ant.get(K_VALIDO):
            por_id[x[K_ID]] = x
    return por_id


def selecionavel(tid, T):
    t = T.get(tid)
    return t is not None and t[T_STATUS] == T_ATIVO and t[T_NIVEL] != "0"


def decidir(x, T, calib):
    p = x.get(K_PRED) or {}
    if not x.get(K_VALIDO):
        return "revisar", "", [], 0.0, "json_invalido"

    conf_bruta = int(p.get(K_CONF, 0) or 0)
    if not 1 <= conf_bruta <= 5:
        return "revisar", "", [], 0.0, "conf_fora_escala"
    c = float(calib.get(str(conf_bruta), 0.0))

    if p.get(K_ESCOPO) is False:                       # pertence_ao_escopo == false
        return "fora", "", [], c, "fora_escopo"

    tid = str(p.get(K_TEMA, ""))
    extras = [str(e) for e in p.get(K_EXTRAS, []) or []
              if str(e) != tid and selecionavel(str(e), T)]
    t = T.get(tid)
    if t is None:
        return "revisar", "", extras, c, "tema_inexistente"
    if t[T_STATUS] != T_ATIVO:
        return "revisar", "", extras, c, "inativo"
    if t[T_NIVEL] == "0":
        return "revisar", tid, extras, c, "nivel_raiz"
    if conf_bruta < CONF_MIN:
        return "revisar", tid, extras, c, "conf_baixa"
    return "publicar", tid, extras, c, ""              # motivo vazio em publicar


def main():
    T, calib, preds = carregar_temas(), carregar_calib(), carregar_predicoes()
    linhas = [(qid, *decidir(x, T, calib)) for qid, x in preds.items()]

    # Validações do contrato (falha alta, não silenciosa)
    assert len(linhas) == 359, f"esperado 359, veio {len(linhas)}"
    for qid, d, tid, ex, c, m in linhas:
        assert 0.0 <= c <= 1.0, qid
        assert d == "publicar" or m, f"{qid}: motivo vazio em {d}"
        assert d != "fora" or tid == "", f"{qid}: fora com tema"
        assert d == "fora" or d == "revisar" or tid, f"{qid}: sem tema"
        assert not {tid, *ex} & {"5078", "5234"}, f"{qid}: inativo"

    with open(PATH_PUBLICACAO, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for qid, d, tid, ex, c, m in linhas:
            w.writerow([qid, d, tid, ";".join(ex), f"{c:.2f}", m])

    from collections import Counter
    print(Counter((d, m) for _, d, _, _, _, m in linhas))


if __name__ == "__main__":
    main()
