"""Le temas.csv, monta a arvore completa, marca inativos e exporta o que e usavel."""
import json
import sys
from pathlib import Path

import pandas as pd

ALIASES = {
    "id": ["tema_id", "id", "id_tema", "topic_id"],
    "parent": ["parent_id", "pai_id", "id_pai", "parent", "pai"],
    "titulo": ["titulo", "nome", "tema", "name", "title"],
    "nivel": ["nivel", "level", "profundidade"],
    "status": ["status", "situacao"],
    "descricao": ["descricao", "description", "desc"],
    "n_questoes": ["n_questoes", "qtd_questoes", "questoes", "num_questoes"],
}
REQUIRED = ["id", "parent", "titulo", "status"]


def resolve_cols(df):
    found = {}
    for key, options in ALIASES.items():
        for opt in options:
            if opt in df.columns:
                found[key] = opt
                break
    missing = [k for k in REQUIRED if k not in found]
    if missing:
        sys.exit(f"Colunas ausentes: {missing}\nCabecalho real: {list(df.columns)}\n"
                 "Ajuste ALIASES em parse_taxonomia.py.")
    return found


def to_int_or_none(v):
    if pd.isna(v) or str(v).strip() in ("", "nan", "None"):
        return None
    return int(float(str(v).strip()))


def parse_taxonomia(csv_path="data/raw/temas.csv",
                    out_path="data/processed/arvore_taxonomia.json"):
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    c = resolve_cols(df)

    nos = {}
    for _, r in df.iterrows():
        tid = to_int_or_none(r[c["id"]])
        if tid is None:
            continue
        if tid in nos:
            sys.exit(f"ID duplicado no temas.csv: {tid}")
        nos[tid] = {
            "tema_id": tid,
            "parent_id": to_int_or_none(r[c["parent"]]),
            "titulo": str(r[c["titulo"]]).strip(),
            "status": str(r[c["status"]]).strip().lower(),
            "nivel_csv": to_int_or_none(r[c["nivel"]]) if "nivel" in c else None,
            "descricao": str(r[c["descricao"]]).strip() if "descricao" in c else "",
            "n_questoes": to_int_or_none(r[c["n_questoes"]]) if "n_questoes" in c else None,
        }

    problemas = []
    for tid, n in nos.items():
        trilha, atual, visitados = [], tid, set()
        while atual is not None:
            if atual in visitados:
                problemas.append(f"ciclo em {tid}")
                break
            visitados.add(atual)
            no = nos.get(atual)
            if no is None:
                problemas.append(f"pai inexistente {atual} (filho {tid})")
                break
            trilha.append(no["titulo"])
            atual = no["parent_id"]
        trilha.reverse()
        n["caminho"] = " > ".join(trilha)
        n["nivel"] = len(trilha) - 1

    ativos = {t for t, n in nos.items() if n["status"] == "active"}
    for t in ativos:
        p = nos[t]["parent_id"]
        if p is not None and p not in ativos:
            problemas.append(f"no ativo {t} com pai inativo/inexistente {p}")

    for t in nos:
        nos[t]["ativo"] = t in ativos
        nos[t]["filhos"], nos[t]["irmaos"] = [], []
    for t in ativos:
        p = nos[t]["parent_id"]
        if p in ativos:
            nos[p]["filhos"].append(t)
    for t in ativos:
        p = nos[t]["parent_id"]
        if p in ativos:
            nos[t]["irmaos"] = [s for s in nos[p]["filhos"] if s != t]

    out = {"nos": {str(k): v for k, v in nos.items()},
           "ativos": sorted(ativos),
           "inativos": sorted(set(nos) - ativos),
           "problemas": problemas}
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Temas: {len(nos)} | ativos: {len(ativos)} | inativos: {len(nos) - len(ativos)}")
    print(f"Problemas de integridade: {len(problemas)}")
    for p in problemas[:10]:
        print("  -", p)


if __name__ == "__main__":
    parse_taxonomia(*sys.argv[1:3])