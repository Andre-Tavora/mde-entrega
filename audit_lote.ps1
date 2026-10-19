param([switch]$Exportar, [int]$N = 10, [string]$Importar)
. "C:\Users\André Tavora\Desktop\CASE IA\CASE_CARLOSANDRE\mde-entrega\paths.ps1"
$enc  = New-Object Text.UTF8Encoding $false
$rows = @(Import-Csv -LiteralPath $AUDIT -Delimiter ";" -Encoding UTF8)

if ($Exportar) {
  $txt = @{}
  Get-Content -LiteralPath $QLIMP -Encoding UTF8 | Where-Object { $_.Trim() } | ForEach-Object {
    $q = $_ | ConvertFrom-Json; $txt[$q.id] = $q.texto_modelo
  }
  $lote = @($rows | Where-Object { -not $_.veredito } | Select-Object -First $N)
  $out = foreach ($r in $lote) {
    $t = $txt[$r.id]; if (-not $t) { $t = $r.comando }
    if ($t.Length -gt 1800) { $t = $t.Substring(0, 1800) + " [...]" }
    "### $($r.id) | tag=$($r.tag)`nORIGEM: $($r.origem)`nPREVISTO: $($r.pred) - $($r.pred_titulo)`n$t`n"
  }
  ($out -join "`n") | Set-Clipboard
  Write-Host "[OK] $($lote.Count) questoes copiadas. Cole no chat." -ForegroundColor Green
}

if ($Importar) {
  $map = @{}
  foreach ($p in $Importar -split ";") {
    $k, $v = $p.Trim() -split "="
    if ($k -and $v -and $v.Trim().ToUpper() -in "C","E","F") { $map[$k.Trim()] = $v.Trim().ToUpper() }
  }
  $n = 0
  foreach ($r in $rows) { if ($map.ContainsKey($r.id)) { $r.veredito = $map[$r.id]; $n++ } }
  [IO.File]::WriteAllLines($AUDIT, ($rows | ConvertTo-Csv -Delimiter ";" -NoTypeInformation), $enc)
  $pend = @($rows | Where-Object { -not $_.veredito }).Count
  Write-Host "[OK] $n vereditos gravados | pendentes: $pend" -ForegroundColor Green
}