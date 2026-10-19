# Diario de bordo: mudancas de plano (insumo do relatorio final)

## 15/10/2026: Fase 1

### Mudancas por verificacao externa
| Item | Plano v2 | Realidade verificada | Decisao |
|---|---|---|---|
| Gemini 2.0 Flash | Modelo do comite | Desligado em 01/06/2026 | Trocado por modelo vigente (Gemini 3.8 Flash segundo a documentacao do Google), via variavel GEMINI_MODEL |
| GPT-4o-mini | Modelo do comite | Status atual nao verificado | Confirmar na Fase 2; via OPENAI_MODEL |
| Custo estimado | US$ 0,70-0,90 | Baseado em modelos/precos desatualizados | Descartado; custo real medido por tokens |
| Bibliotecas | Versoes assumidas | pandas 3.0.6, beautifulsoup4 4.15.0 (4.13.0 foi retirada), python-dotenv 1.2.4, google-genai 2.31.0, openai 3.31.0 | Versoes fixadas em requirements.lock |
| SDKs de IA | Conhecimento previo (series 1.x/2.x) | Majors novas (google-genai 2.x, openai 3.x) | Consultar docs antes de escrever o codigo da Fase 2 |

### Mudancas por dados reais (profiling)
| Item | Plano v2 | Dado real |
|---|---|---|
| Temas inativos | 1 (ID 5078) | 2 (5078 e 5234) |
| Homonimos entre ramos | 3 conhecidos | 8 pares |
| Nos "Parte N" | 4 (6718-6721) | 11 |
| Ativos sem descricao | nao medido | 20 |
| Comando vazio | nao medido | 101 de 359 (28%) |
| Certo/Errado | nao medido | 58 (16%) |
| Comando suspeito em C/E | nao medido | 18 de 58 (heuristica a validar) |
| Disciplina de origem fora das 4 ou vazia | nao medido | 6 |
| Integridade da arvore | nao medido | 377 nos, 375 ativos, 0 problemas |

### Correcoes de codigo (becos sem saida e erros meus)
- Colunas do temas.csv eram suposicao: agora detectadas por aliases.
- Comando vinha antes das alternativas, contra a decisao travada: invertido (enunciado e alternativas primeiro; comando auxiliar).
- Regex de HTML trocado por BeautifulSoup.
- Caminho completo da arvore calculado pelos pais, sem depender de coluna do CSV.
- questoes_limpas.jsonl no .gitignore (repositorio publico, dado proprietario).

### Pendencias
- Esclarecer com a Carla se o nivel 0 (disciplina) conta como "pai".
- Validar manualmente o filtro de comando suspeito e questoes com comando vazio.
- Colar reports/profiling.json para fechar a Fase 1.