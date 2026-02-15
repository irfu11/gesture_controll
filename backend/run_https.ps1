#!/usr/bin/env pwsh
# Generate cert.pem/key.pem if missing and run the backend with SSL env vars set.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $scriptDir
.
.\create_self_signed_cert.ps1
if (-Not (Test-Path cert.pem) -or -Not (Test-Path key.pem)) {
    Write-Error "cert.pem/key.pem missing. Aborting."
    Pop-Location
    exit 1
}
$env:SSL_CERT = (Join-Path $scriptDir "cert.pem")
$env:SSL_KEY = (Join-Path $scriptDir "key.pem")
$env:PORT = "8443"
Write-Host "Running backend on https://localhost:8443"
python .\app.py
Pop-Location
