"""Gera reports/profiling.json com os numeros exatos para o relatorio."""
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    return re.sub(r"\s+", " ", "".join(ch for ch in s if not unicodedata.combining(ch))).lower().strip()


DISCIPLINAS_ALVO = ("penal", "processo penal", "legislacao", "criminologia")


def main(arv="data/processed/arvore_taxonomia.json",
         qs="data/processed/questoes_limpas.jsonl",
         out="reports/profiling.json"):
    A = json.loads(Path(arv).read_text(encoding="utf-8"))
    nos = {int(k): v for k, v in A["nos"].items()}
    ativos = [nos[i] for i in A["ativos"]]
    Q = [json.loads(l) for l in Path(qs).read_text(encoding="utf-8").splitlines() if l.strip()]

    por_titulo = defaultdict(list)
    for n in ativos:
        por_titulo[norm(n["titulo"])].append(n)
    homonimos = {t: [{"id": n["tema_id"], "caminho": n["caminho"]} for n in v]
                 for t, v in por_titulo.items()
                 if len(v) > 1 and len({n["parent_id"] for n in v}) > 1}
    parte_n = [{"id": n["tema_id"], "caminho": n["caminho"]} for n in ativos
               if re.search(r"parte\s*\d+", norm(n["titulo"]))]
    sem_desc = [n["tema_id"] for n in ativos if not n["descricao"]]
    folhas = [n for n in ativos if not n["filhos"]]
    tem_contagem = any(n["n_questoes"] is not None for n in ativos)
    zero_q = [n["tema_id"] for n in ativos if n["n_questoes"] == 0] if tem_contagem else None
    top_lixeiras = sorted(
        ({"id": n["tema_id"], "caminho": n["caminho"], "n_questoes": n["n_questoes"]}
         for n in ativos if n["n_questoes"]),
        key=lambda x: -x["n_questoes"])[:10] if tem_contagem else None

    disc = Counter(q["disciplina_origem"] or "(vazio)" for q in Q)
    fora_alvo = {d: c for d, c in disc.items()
                 if d == "(vazio)" or not any(k in norm(d) for k in DISCIPLINAS_ALVO)}
    rep = {
        "arvore": {
            "total_nos": len(nos), "ativos": len(ativos), "inativos": A["inativos"],
            "por_nivel_ativos": dict(Counter(n["nivel"] for n in ativos)),
            "folhas_ativas": len(folhas),
            "homonimos_entre_ramos": homonimos,
            "nos_parte_n": parte_n,
            "ativos_sem_descricao": {"qtd": len(sem_desc), "ids": sem_desc},
            "temas_com_zero_questoes": zero_q,
            "top10_lixeiras": top_lixeiras,
            "problemas_integridade": A["problemas"],
        },
        "questoes": {
            "total": len(Q),
            "tipo": dict(Counter(q["tipo"] for q in Q)),
            "n_alternativas": dict(Counter(len(q["alternativas"]) for q in Q)),
            "comando_vazio": sum(q["comando_vazio"] for q in Q),
            "comando_suspeito_CE": [q["id"] for q in Q if q["comando_suspeito"]],
            "disciplina_origem": dict(disc),
            "disciplina_origem_fora_das_4_ou_vazia": fora_alvo,
            "assunto_origem_vazio": sum(1 for q in Q if not q["assunto_origem"]),
            "enunciado_curto_lt_80_chars": [q["id"] for q in Q if len(q["enunciado"]) < 80],
            "ids_duplicados": [i for i, c in Counter(q["id"] for q in Q).items() if c > 1],
        },
    }
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    a, q = rep["arvore"], rep["questoes"]
    print(f"Arvore: {a['total_nos']} nos | ativos {a['ativos']} | inativos {a['inativos']}")
    print(f"Homonimos entre ramos: {len(a['homonimos_entre_ramos'])} | nos 'Parte N': {len(a['nos_parte_n'])}"
          f" | ativos sem descricao: {a['ativos_sem_descricao']['qtd']}")
    print(f"Questoes: {q['total']} | C/E: {q['tipo'].get('certo_errado', 0)} | comando vazio: {q['comando_vazio']}"
          f" | comando suspeito (C/E): {len(q['comando_suspeito_CE'])}")
    print(f"Disciplina de origem fora das 4 ou vazia: {sum(fora_alvo.values())}")


if __name__ == "__main__":
    main()