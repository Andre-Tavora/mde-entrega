# Case: Classificação de Tópicos — Relatório Técnico

## 1. Raciocínio e hipóteses descartadas

**Pipeline final:** HTML sanitizado (enunciado > alternativas > comando auxiliar) → árvore ativa completa no system prompt com prompt caching (~14k tokens, ~97% lidos do cache) → julgamento por LLM (`claude-sonnet-5-5`, tool use com schema fixo) → gating conservador → auditoria humana de 100% das publicadas.

**Hipóteses descartadas:**
1. *Confiar no comando da questão*: descartada. O comando às vezes não bate com o conteúdo, e a pegadinha costuma estar nas alternativas. O comando entra só como contexto auxiliar.
2. *Retrieval top-K por embeddings*: descartada. Com 377 nós, a árvore inteira cabe no contexto e o cache torna o custo marginal. Isso elimina o risco de o tema certo ficar fora do top-K.
3. *Usar disciplina/assunto de origem como rótulo*: descartada. Os rótulos de origem são ruidosos e usam outra granularidade. Servem apenas como sinal na auditoria.
4. *Publicar com confiança ≥ 4*: descartada. Na régua de 95%, o erro "subtema irmão" se concentra nas confianças 3–4. Por isso `CONF_MIN = 5`: troquei cobertura por precisão de forma deliberada.

## 2. Diagnóstico dos dados e das "lixeiras"

- **Árvore:** 377 nós. Os temas inativos (5078, 5234) e os nós raiz (nível 0) ficam bloqueados no gating e mandam a questão para revisar.
- **Questões:** HTML cru com tags e entidades, limpo por `clean_questions.py`. A saída bruta tinha predições duplicadas, tratadas por `dedup_predictions.py` (última resposta válida por questão).
- **Lixeiras (`revisar` / `fora`):** a fila de revisão concentra (a) dúvidas entre subtemas irmãos (conf ≤ 4), (b) questões multitema e (c) temas genéricos de nível raiz. `fora` = o modelo declarou `pertence_ao_escopo = false`.
- **Distribuição final:** publicar = 81, revisar = 277, fora = 1 (de 359). Motivos: conf_baixa=270, tema com erro na auditoria (gate por tema)=6, fora_escopo=1, nivel_raiz=1.
- **Limitação assumida:** a coluna `confianca` ainda usa um mapeamento provisório (prior 1→0,10 … 5→0,92). Quem sustenta a régua é a auditoria, não esse número. A recalibração (Laplace por estrato) virá das revisões do professor.

## 3. Arquitetura de produção (50 mil questões/semana)

1. **Ingestão:** fila (SQS/PubSub) → sanitização → dedup por hash do texto (evita pagar duas vezes pela mesma questão).
2. **Classificação:** Anthropic **Batch API** com a árvore em cache. Na amostra: 719 tokens de entrada + 14.080 de cache + 558 de saída por questão.
3. **Gating:** regras atuais + calibração por estrato (disciplina × confiança), recalculada toda semana.
4. **Ciclo humano:** o professor revisa a fila. Cada revisão vira rótulo-ouro, que recalibra os thresholds e pode liberar mais cobertura. Uma amostra aleatória de 2% das publicadas é auditada toda semana para monitorar drift.
5. **Mudança na árvore:** versionar `temas.csv`; uma mudança invalida o cache e dispara a reclassificação só dos temas afetados.

**Custos e tempo:**

| Cenário | US$/questão | US$/semana |
|---|---|---|
| Síncrono (medido) | 0,015 | ≈ 760 |
| Batch API (−50%) | 0,0076 | ≈ 380 |

Custo do lote atual: ≈ US$ 5,46 para 359 questões. Tempo: [TEMPO] s/questão. Não há custo de embeddings nem de infraestrutura de GPU.

## 4. Memo executivo para o professor

**Para:** Coordenação de Direito Penal | **Assunto:** Classificação automática de 359 questões

**O que o sistema faz.** Ele lê cada questão (enunciado e alternativas), compara com os 377 temas da árvore e propõe um tema. A questão só é publicada sem revisão quando o sistema tem alta segurança. Na dúvida, ela vai para a sua fila.

**Resultado neste lote**
| Decisão | Questões | % |
|---|---|---|
| Publicar direto | 81 | 22,6% |
| Revisar (sua fila) | 277 | 77,2% |
| Fora da árvore | 1 | 0,3% |

**Qualidade.** Auditamos uma por uma as 81 questões publicadas, e as 81 estavam corretas. Para os próximos lotes, a precisão esperada é de pelo menos 95,5% (95% de confiança), acima da meta de 95%.

**O que muda para o senhor.** Quase uma em cada quatro questões deixa de precisar de revisão. Nas 277 restantes, o sistema já entrega o tema sugerido e a justificativa, então a revisão vira uma conferência, não uma classificação do zero.

**Limites.** O principal erro possível é confundir subtemas vizinhos (por exemplo, dois subtemas do mesmo tema), e esses casos vão sempre para revisão. Alguns rótulos de origem estavam inconsistentes ("Concurso de Crimes" usado como categoria genérica, origens vazias). Por isso, a avaliação foi feita contra a árvore oficial.

**Pedido.** Pedimos uma revisão cega de 30 das 81 publicadas, para confirmar a nossa auditoria, e que as suas correções na fila sejam registradas. Cada correção recalibra o sistema e aumenta a fração publicada com segurança.

### Sobre a coluna `confianca`
Para `publicar` e `fora`, `confianca` = **precisão calibrada do grupo** (0,96), estimada pela auditoria 81/81 (limite inferior de Wilson 95% >= 95,5%). Não é score individual do modelo. Para `revisar`, é o score bruto do classificador (0,30 a 0,96). As 6 questões com 0,96 em `revisar` foram barradas pelo gate por tema (tema com erro na auditoria), não por confiança baixa.

**Evidência da auditoria:** `output/relatorio/auditoria_extra.csv` traz a revisão manual, questão a questão, que sustenta a precisão estimada em `previsao.txt`.
