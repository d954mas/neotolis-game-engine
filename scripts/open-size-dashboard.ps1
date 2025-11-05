param(
    [int]$Port = 9010,
    [string]$Root
)

if (-not $Root) {
    throw "Missing --root argument"
}

if (-not (Test-Path -Path $Root)) {
    throw "Root path '$Root' does not exist"
}

$listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
if (-not $listener) {
    Start-Process -FilePath python -ArgumentList @('-m','http.server',$Port,'--directory',$Root) -WindowStyle Hidden | Out-Null
    Start-Sleep -Seconds 1
}

$url = "http://localhost:$Port/report.html"
$chrome = Get-Command 'chrome' -ErrorAction SilentlyContinue
if ($chrome) {
    Start-Process -FilePath $chrome.Source -ArgumentList $url | Out-Null
} else {
    Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c','start', $url) | Out-Null
}
