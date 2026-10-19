$ROOT   = "C:\Users\André Tavora\Desktop\CASE IA\CASE_CARLOSANDRE\mde-entrega"
$RAW    = "$ROOT\data\raw"
$PROC   = "$ROOT\data\processed"
$PREDD  = "$ROOT\data\raw_predictions"
$GOLD   = "$ROOT\data\gold"
$PIPE   = "$ROOT\src\pipeline"
$TEMAS  = "$RAW\temas.csv"
$QUEST  = "$RAW\questoes.jsonl"
$QLIMP  = "$PROC\questoes_limpas.jsonl"
$FLAGS  = "$PROC\flags_disciplina.csv"
$PRED   = "$PREDD\claude_results_dedup.jsonl"
$PRED_C = "$PREDD\claude_results.jsonl"
$PRED_H = "$PREDD\haiku_results_v2.jsonl"
$AUDIT  = "$PROC\auditoria.csv"
$ASAMP  = "$ROOT\data\audit\audit_sample.csv"
$GREV   = "$GOLD\auditoria_revisar.csv"
$GAMOS  = "$GOLD\amostra_revisar.csv"
foreach ($v in "TEMAS","QUEST","QLIMP","PRED","PRED_H") {
  $p = (Get-Variable $v).Value
  if (-not (Test-Path -LiteralPath $p)) { Write-Warning "$v nao existe: $p" }
}
Write-Host "paths carregados" -ForegroundColor Green
