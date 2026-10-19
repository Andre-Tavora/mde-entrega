import json, sys
src = sys.argv[1]
ALIAS = {"justificativa": "raciocinio_juridico", "confianca": "confianca_modelo"}
out, vazias = [], 0
with open(src, encoding="utf-8") as f:
    for linha in f:
        if not linha.strip():
            continue
        o = json.loads(linha)
        p = o.get("predicao_llm") or {}
        if not p:
            vazias += 1
        for novo, antigo in ALIAS.items():
            if novo in p and antigo not in p:
                p[antigo] = p[novo]
        o["predicao_llm"] = p
        out.append(json.dumps(o, ensure_ascii=False))
with open(src, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print(f"Linhas: {len(out)} | predicao_llm vazio: {vazias}")
