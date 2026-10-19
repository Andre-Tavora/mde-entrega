# Relatorio - Classificacao de Topicos (Metodo VDE)

## 1. Raciocinio e hipoteses descartadas
- Pipeline: HTML limpo -> enunciado + alternativas (comando como auxiliar) -> claude-haiku-5-5 com a arvore ativa inteira no prompt (cache) -> saida estruturada via tool_use -> votacao -> gate.
- Descartado: assunto_origem como gabarito (rotulos incompletos e fragmentados).
- Descartado: classificacao nivel a nivel (erro na disciplina se propaga).
- Descartado: retrieval top-K por embedding (a arvore de 377 nos cabe no prompt; cache torna o custo marginal baixo e elimina erro de recall).
- Descartado: confianca verbal do LLM sozinha (nao calibrada); substituida por concordancia entre votos.

## 2. Diagnostico dos dados e lixeiras
- 18 questoes sem assunto_origem.
- Assuntos fragmentados: "Acao Penal" / "(Parte 01)" / "(Parte 02)" = 58 questoes; idem "Teoria da Pena".
- "Concurso de Crimes" = 44 questoes (12%); temas 4703/4704/4708 concentram 30 revisoes: confusao tipica entre subtemas irmaos.
- Resultado: publicar=81 (22,6%), revisar=277, fora=1.

## 3. Producao para 50k questoes/semana
- Batch API assincrona (-50% de custo) + prompt caching da arvore.
- Este lote: US$ 0,40 em 25 min (input=300867 | cache_read=5054844 | output=200263). Extrapolacao linear: ~US$ 56/semana (antes do desconto de batch).
- Correcoes do professor viram rotulos -> recalibracao mensal por tema -> liberar 4/5 votos em temas ja validados.
- Monitoramento: amostra aleatoria de 1% das publicadas/semana; alarme se o limite inferior de Wilson < 95%.

## 4. Memo executivo (professor)
Das 359 questoes, o sistema publicou 81 e encaminhou 277 para sua revisao; 1 ficaram fora da arvore.
Na auditoria, 80 de 80 publicadas estavam corretas; para lotes futuros esperamos ~93% (IC 86-97%), por isso ha monitoramento continuo.
A maior fonte de duvida e Concurso de Crimes, onde os subtemas se sobrepoem: revisar a arvore nesse ponto e o que mais aumenta a cobertura.
Cada correcao sua alimenta a recalibracao: a fila de revisao deve diminuir a cada ciclo.