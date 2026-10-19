# Case VDE - Classificacao de Topicos

## Reproduzir (PowerShell)
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:ANTHROPIC_API_KEY="..."
$env:ANTHROPIC_MODEL="claude-haiku-5-5"
python .\fix_previsao.py
python .\hiper.py
python .\scripts\auditar.py
python .\scripts\build_audit_sample.py
python .\scripts\calibrar.py
python .\scripts\check_inactive.py
python .\scripts\check_nivel0.py
python .\scripts\dedup_predictions.py
python .\scripts\gerar_previsao.py
python .\src\data\clean_questions.py
python .\src\data\parse_taxonomia.py
python .\src\data\profile_data.py
python .\src\pipeline\00_achar_auditoria.py
python .\src\pipeline\00_auditar_llm.py
python .\src\pipeline\00_auditar_terminal.py
python .\src\pipeline\00_diag_lote2.py
python .\src\pipeline\00_merge_auditorias.py
python .\src\pipeline\00_merge_lote2.py
python .\src\pipeline\00_sortear_lote2.py
python .\src\pipeline\00_validar_auditorias.py
python .\src\pipeline\00b_check_campos.py
python .\src\pipeline\02_classificacao_llm.py
python .\src\pipeline\02b_comite_haiku.py
python .\src\pipeline\02c_comite_haiku_v2.py
python .\src\pipeline\02d_normaliza_campos.py
python .\src\pipeline\03_gating.py
python .\src\pipeline\03a_sanidade.py
python .\src\pipeline\03b_diag_discordancia.py
python .\src\pipeline\03b_disciplina.py
python .\src\pipeline\03c_flags_disciplina.py
python .\src\pipeline\03d_ids_invalidos.py
python .\src\pipeline\03e_inspeciona.py
python .\src\pipeline\03f_duplicados.py
python .\src\pipeline\03g_impacto_dup.py
python .\src\pipeline\03h_relacao_origem.py
python .\src\pipeline\03i_auditoria.py
python .\src\pipeline\03j_resultado_auditoria.py
python .\src\pipeline\03k_texto_auditoria.py
python .\src\pipeline\03l_check_veredito.py
python .\src\pipeline\03m_normaliza_veredito.py
python .\src\pipeline\04_previsao.py
python .\src\pipeline\gating.py
python .\src\pipeline\listar_modelos.py
python .\src\pipeline\schema.py
python .\wilson.py
```

## Entregaveis
- entrega/publicacao.csv
- entrega/previsao.txt
- entrega/relatorio.md

## Execucao
- Modelo: claude-haiku-5-5 | Roteamento: sem embedding: arvore ativa completa no system prompt (prompt caching)
- Custo: US$ 0,40 | Tempo: 25 min | Tokens: input=300867 | cache_read=5054844 | output=200263
- Resultado: publicar=81, revisar=277, fora=1 | cobertura=22,6%
- Precisao (conservadora): 93,0% [IC95% 85,6% - 100,0%]