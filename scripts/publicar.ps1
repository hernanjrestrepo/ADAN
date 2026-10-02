# Publica ADÁN temporalmente en internet desde este equipo (Windows), sin cuenta ni dominio.
# Uso, desde cualquier carpeta:  powershell -ExecutionPolicy Bypass -File <repo>\scripts\publicar.ps1
# Hace todo: trae main, levanta Docker, espera a ADÁN y abre un túnel público (Pinggy por el puerto 443,
# que pasa por redes corporativas; si falla, Cloudflare). Deja esta ventana abierta: al cerrarla, el link muere.
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
Write-Host "ADÁN en $repo" -ForegroundColor Cyan

git fetch origin main
git checkout main
git pull --ff-only origin main
docker compose up --build -d

Write-Host 'Esperando a que ADÁN responda en http://127.0.0.1:5174 ...'
$ok = $false
for ($i = 0; $i -lt 90; $i++) {
    try { if ((Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5174/ -TimeoutSec 3).StatusCode -eq 200) { $ok = $true; break } } catch {}
    Start-Sleep -Seconds 2
}
if (-not $ok) { docker compose ps; throw 'ADÁN no respondió en el puerto 5174 (revisa docker compose logs frontend).' }
Write-Host 'ADÁN está arriba.' -ForegroundColor Green

Write-Host "`nAbriendo el túnel público. Copia el link https://...pinggy.link que aparece abajo." -ForegroundColor Cyan
ssh -p 443 -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes `
    -R0:127.0.0.1:5174 free.pinggy.io
if ($LASTEXITCODE -ne 0 -and (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    Write-Host 'Pinggy no conectó; probando Cloudflare.' -ForegroundColor Yellow
    cloudflared tunnel --url http://127.0.0.1:5174
}
