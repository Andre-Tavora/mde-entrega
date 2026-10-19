$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath "C:\Users\André Tavora\Desktop\CASE IA\CASE_CARLOSANDRE\mde-entrega"
$enc = New-Object Text.UTF8Encoding $false
$pt  = [Globalization.CultureInfo]::GetCultureInfo('pt-BR')

[double]$acertos = 80
[double]$audit   = 80
[double]$z = 1.959964

[double]$p   = $acertos / $audit
[double]$den = 1.0 + ($z*$z)/$audit
[double]$cen = ($p + ($z*$z)/(2.0*$audit)) / $den
[double]$mar = $z * [math]::Sqrt(($p*(1.0-$p))/$audit + ($z*$z)/(4.0*$audit*$audit)) / $den
[double]$wlo = [math]::Max(0.0, $cen - $mar)
[double]$whi = [math]::Min(1.0, $cen + $mar)

$lo = ($wlo*100).ToString('0.0',$pt) + '%'
$hi = ($whi*100).ToString('0.0',$pt) + '%'
Write-Host "Wilson calculado: [$lo ; $hi]" -ForegroundColor Cyan
if ($wlo -ge 0.999 -or $wlo -lt 0.90) { throw "Valor suspeito ($lo). Abortado." }

foreach ($f in ".\entrega\relatorio.md", ".\entrega\previsao.txt") {
  $path = (Resolve-Path $f).Path
  $t = [IO.File]::ReadAllText($path, [Text.Encoding]::UTF8)
  $t2 = $t -replace '100,0% a 100,0%', "$lo a $hi" -replace '\[100,0% ; 100,0%\]', "[$lo ; $hi]"
  if ($t2 -ne $t) { [IO.File]::WriteAllText($path, $t2, $enc); Write-Host "[OK] $f corrigido" -ForegroundColor Green }
  else { Write-Host "[ATENCAO] nada trocado em $f" -ForegroundColor Yellow }
}
