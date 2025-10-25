param(
  [int]$Port = 8000,
  [string]$Root,
  [switch]$NoWait
)

$ErrorActionPreference = 'Stop'

# Диагностика: убедимся, что исполняется именно этот файл
Write-Host "SERVE-SANDBOX.PS1 ACTIVE"
Write-Host "PORT: $Port"
Write-Host "ROOT: $Root"

if (-not (Test-Path $Root)) {
  Write-Error "Sandbox output not found at '$Root'. Run the build first."
  exit 1
}

$pidFile = Join-Path $Root '.wasm_server.pid'
if (Test-Path $pidFile) {
  $oldPid = (Get-Content $pidFile | Select-Object -First 1)
  if ($oldPid) { try { Stop-Process -Id ([int]$oldPid) -Force -ErrorAction Stop } catch {} }
  Remove-Item $pidFile -ErrorAction SilentlyContinue
}

$py = Get-Command py -ErrorAction SilentlyContinue
$python = Get-Command python -ErrorAction SilentlyContinue
if     ($py)     { $exe = $py.Source;     $pyArgs = @('-m','http.server',$Port,'--directory',$Root) }
elseif ($python) { $exe = $python.Source; $pyArgs = @('-m','http.server',$Port,'--directory',$Root) }
else { Write-Error 'Python not found in PATH (neither py nor python).'; exit 1 }

Write-Host "PYTHON: $exe"

$server = Start-Process -FilePath $exe -ArgumentList $pyArgs -NoNewWindow -PassThru
$server.Id.ToString() | Set-Content $pidFile

Start-Sleep -Seconds 1

# ВАЖНО: открываем URL, а не локальный файл
$url = "http://localhost:$Port/"
Write-Host "SERVER READY $url (PID $($server.Id))"

if ($NoWait) {
  exit 0
}

try { Wait-Process -Id $server.Id } finally { Remove-Item $pidFile -ErrorAction SilentlyContinue }
