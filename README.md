
- **Precisão em publicar:** 81/81 auditadas corretas; limite inferior Wilson IC95% = **95,5%** (≥ 95%).
- **Critério de acerto:** nó exato, pai ou filho = acerto; subtema irmão = erro; nível 0 (só a disciplina) = erro.

## Como funciona

1. **Limpeza:** remove HTML e monta o texto com enunciado + alternativas primeiro; o comando entra só como apoio (às vezes não bate com o item).
2. **Classificação:** o LLM recebe a árvore ativa inteira no prompt (com prompt caching) e responde via Tool Use em formato estruturado: tema, extras, escopo e confiança (1 a 5).
3. **Validação:** IDs precisam existir, estar ativos e ter nível ≥ 1. Temas inativos (5078, 5234) são bloqueados.
4. **Gating:** só publica com unanimidade entre os votos. Homônimos Penal × Leg. Especial, nós "Parte N", nível 0 e baixa confiança vão para revisar.
5. **Auditoria:** revisão jurídica manual das publicadas + intervalo de Wilson para estimar a precisão sem gabarito.

## Hipóteses descartadas

- **Retrieval por embedding (top-K):** a árvore cabe no prompt; o retrieval poderia descartar o ramo certo.
- **Classificação nível a nível:** o erro na disciplina se propaga.
- **Confiança autodeclarada do LLM:** não é calibrada; substituída por concordância entre votos + auditoria.
- **`assunto_origem` como gabarito:** rótulos incompletos e fragmentados.

## Entregáveis

| Arquivo | Conteúdo |
|---|---|
| `entrega/publicacao.csv` | `id,decisao,tema_central_id,extras_ids,confianca,motivo` |
| `entrega/previsao.txt` | Precisão e cobertura previstas, com intervalo |
| `entrega/relatorio.md` | Raciocínio, diagnóstico, produção (50k/semana) e memo ao professor |

## Como reproduzir (PowerShell)

Os dados originais são proprietários e **não estão no repositório**. Coloque `questoes.jsonl` e `temas.csv` em `data/raw/`.

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:ANTHROPIC_API_KEY = "sua_chave"
python .\src\data\parse_taxonomia.py
python .\src\data\clean_questions.py
python .\src\data\profile_data.py
python .\src\pipeline\02_classificacao_llm.py
python .\src\pipeline\02c_comite_haiku_v2.py
python .\src\pipeline\03_gating.py
python .\src\pipeline\04_previsao.py
```

Os demais scripts em `scripts/` e `src/pipeline/` (prefixos `00_` e `03a`–`03m`) são diagnósticos e apoio à auditoria; não são necessários para gerar o `publicacao.csv`.

## Execução, custo e tempo

- **Modelo:** claude-haiku-5-5, temperatura 0, prompt caching
- **Custo:** US$ 0,40 | **Tempo:** ~25 min
- **Tokens:** input 300.867 | cache read 5.054.844 | output 200.263

## Arquitetura 
mde-entrega/
├── src/pipeline/
│   ├── 02_classificacao_llm.py   # classificação com LLM
│   └── gating.py                 # decisão publicar/revisar/fora
├── data/
│   ├── raw/                      # questoes.jsonl, temas.csv
│   ├── processed/                # questoes_limpas.jsonl
│   ├── raw_predictions/          # claude_results*.jsonl
│   └── gold/                     # auditorias
├── entrega/
│   ├── publicacao.csv
│   └── previsao.txt
├── output/relatorio/relatorio.md
└── auditoria_extra.csv

## Decisões manuais

- Temas inativos excluídos dos candidatos (regra do edital).
- Nível 0 nunca publicado (esclarecimento da Carla, 15/10).
- Homônimos e nós "Parte N" enviados para revisão.
- `disciplina_origem` e `comando` usados só como dica fraca.
- Auditoria jurídica manual de todas as publicadas.

## Segurança

Chave da API apenas em variável de ambiente / `.env` (no `.gitignore`). Dados originais fora do Git. O texto da questão é tratado como dado, não instrução (defesa contra prompt injection).
### Sobre a coluna `confianca`
Para `publicar` e `fora`, `confianca` = **precisão calibrada do grupo** (0,96), estimada pela auditoria 81/81 (limite inferior de Wilson 95% >= 95,5%). Não é score individual do modelo. Para `revisar`, é o score bruto do classificador (0,30 a 0,96). As 6 questões com 0,96 em `revisar` foram barradas pelo gate por tema (tema com erro na auditoria), não por confiança baixa.

**Evidência da auditoria:** `output/relatorio/auditoria_extra.csv` traz a revisão manual, questão a questão, que sustenta a precisão estimada em `previsao.txt`.

Observações

O intervalo vale para este lote de 359 questões. Em produção, a precisão precisa ser monitorada com amostragem contínua.
O limite inferior de 95,4% fica perto da régua. Um único erro em 80 já derrubaria o Wilson para cerca de 93%. Por isso o corte de confiança é conservador.
A cobertura de 22,3% foi uma escolha deliberada: o case penaliza erro em publicar mais do que volume em revisar.


