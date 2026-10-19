param([int]$N = 40, [int]$Seed = 42)
. "$PSScriptRoot\paths.ps1"
$enc = New-Object Text.UTF8Encoding $false
$PUB = "$ROOT\output\publicacao.csv"

function Ler($p) {
  $h = Get-Content -LiteralPath $p -TotalCount 1 -Encoding UTF8
  $d = if ($h -match ";") { ";" } else { "," }
  @(Import-Csv -LiteralPath $p -Delimiter $d -Encoding UTF8)
}
function Col($cols, $re, $not) {
  $cols | Where-Object { $_ -match $re -and (-not $not -or $_ -notmatch $not) } | Select-Object -First 1
}

$pub  = Ler $PUB
$cols = $pub[0].PSObject.Properties.Name
$cId   = Col $cols '^(id|quest)'
$cDec  = Col $cols 'decis'
$cTema = Col $cols 'tema' 'extra'
$cConf = Col $cols 'confi'
if (-not ($cId -and $cDec -and $cTema)) { throw "Colunas nao detectadas: $($cols -join ', ')" }

# titulos dos temas
$tm = Ler $TEMAS; $tc = $tm[0].PSObject.Properties.Name
$tId = Col $tc '^(id|tema_id|codigo)'; $tTit = Col $tc '(titulo|nome|tema)' '^(id|tema_id)'
$tit = @{}; if ($tId -and $tTit) { $tm | ForEach-Object { $tit[$_.$tId] = $_.$tTit } }

$aud = @(Import-Csv -LiteralPath $AUDIT -Delimiter ";" -Encoding UTF8)
$ja = @{}; $aud | ForEach-Object { $ja[$_.id] = 1 }

$pool = @($pub | Where-Object { $_.$cDec -match '^\s*publicar' -and -not $ja[$_.$cId] })
$rng = New-Object Random $Seed
$sel = @($pool | Sort-Object { $rng.Next() } | Select-Object -First $N)

$novos = foreach ($r in $sel) {
  $p = ($r.$cTema -replace '^\D*(\d+).*$', '$1')
  [pscustomobject]@{ id=$r.$cId; tag='ALEAT_PUB'; via='aleatorio'; pred=$p
    pred_titulo=$tit[$p]; confianca=$(if ($cConf) { $r.$cConf }); origem=''; comando=''; veredito='' }
}
$all = @($aud) + @($novos)
[IO.File]::WriteAllLines($AUDIT, ($all | ConvertTo-Csv -Delimiter ";" -NoTypeInformation), $enc)

$nPub = @($pub | Where-Object { $_.$cDec -match '^\s*publicar' }).Count
Write-Host "[OK] colunas: id=$cId dec=$cDec tema=$cTema conf=$cConf" -ForegroundColor Cyan
Write-Host "[OK] publicar total: $nPub | pool nao auditado: $($pool.Count) | adicionadas: $($novos.Count)" -ForegroundColor Green
