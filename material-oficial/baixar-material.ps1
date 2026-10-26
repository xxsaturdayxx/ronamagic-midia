# Baixa o material da pagina de parceiros de turismo do Orlando Magic
# (autorizacao de Rosa Rivas, 19/10/2026 - ver ..\autorizacoes\)
$ErrorActionPreference = 'Continue'
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$ok = 0; $falhas = @()
Get-Content (Join-Path $aqui 'lista.txt') | Where-Object { $_ -match '\|' } | ForEach-Object {
  $pasta, $url = $_.Split('|', 2)
  $destDir = Join-Path $aqui $pasta
  New-Item -ItemType Directory -Force -Path $destDir | Out-Null
  $dest = Join-Path $destDir ([IO.Path]::GetFileName($url))
  if (Test-Path $dest) { $ok++; return }
  try { Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing; $ok++; Write-Host "ok  $pasta\$([IO.Path]::GetFileName($url))" }
  catch { $falhas += $url; Write-Host "FALHOU $url" -ForegroundColor Red }
}
Write-Host "`nBaixados: $ok  Falhas: $($falhas.Count)"
$falhas | Set-Content (Join-Path $aqui 'falhas.txt')
