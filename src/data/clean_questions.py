"""Sanitiza as questoes. Ordem do texto p/ o modelo: enunciado > alternativas > comando (auxiliar)."""
import json
import re
import sys
import unicodedata
import warnings
from pathlib import Path

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def html_para_texto(s):
    if not s:
        return ""
    s = str(s).replace("\\n", "\n")
    soup = BeautifulSoup(s, "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    t = soup.get_text()
    t = unicodedata.normalize("NFC", t).replace("\xa0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r" ?\n ?", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def tipo_questao(alts):
    return "certo_errado" if set(alts) == {"C", "E"} else "multipla_escolha"


def comando_suspeito(tipo, comando):
    if not comando or tipo != "certo_errado":
        return False
    return not re.search(r"julgue|marque|assinale|certo|errado", comando, re.I)


def clean_questions(inp="data/raw/questoes.jsonl",
                    out="data/processed/questoes_limpas.jsonl"):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    ok, erros = 0, []
    with open(inp, encoding="utf-8-sig") as fin, open(out, "w", encoding="utf-8") as fout:
        for i, linha in enumerate(fin, 1):
            linha = linha.strip()
            if not linha:
                continue
            try:
                q = json.loads(linha)
            except json.JSONDecodeError as e:
                erros.append((i, str(e)))
                continue

            alts_raw = q.get("alternativas") or {}
            alts = {k: html_para_texto(v) for k, v in alts_raw.items()}
            tipo = tipo_questao(alts)
            enun = html_para_texto(q.get("enunciado_html"))
            cmd = html_para_texto(q.get("comando"))

            blocos = [f"ENUNCIADO:\n{enun}"]
            if tipo == "multipla_escolha":
                blocos.append("ALTERNATIVAS:\n" + "\n".join(f"({k}) {v}" for k, v in alts.items()))
            else:
                blocos.append("FORMATO: item para julgar como Certo ou Errado.")
            if cmd and cmd.lower() not in enun.lower():
                blocos.append(f"COMANDO (auxiliar, pode nao corresponder ao item):\n{cmd}")

            fout.write(json.dumps({
                "id": q["id"],
                "tipo": tipo,
                "enunciado": enun,
                "comando": cmd,
                "comando_vazio": not cmd,
                "comando_suspeito": comando_suspeito(tipo, cmd),
                "alternativas": alts,
                "texto_modelo": "\n\n".join(blocos),
                "disciplina_origem": (q.get("disciplina_origem") or "").strip(),
                "assunto_origem": (q.get("assunto_origem") or "").strip(),
            }, ensure_ascii=False) + "\n")
            ok += 1
    print(f"Questoes limpas: {ok} | linhas com erro de JSON: {len(erros)}")
    for ln, e in erros[:5]:
        print(f"  linha {ln}: {e}")


if __name__ == "__main__":
    clean_questions(*sys.argv[1:3])