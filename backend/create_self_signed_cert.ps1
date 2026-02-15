#!/usr/bin/env pwsh
# Creates a self-signed certificate using OpenSSL and writes cert.pem/key.pem
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $scriptDir
if (Get-Command openssl -ErrorAction SilentlyContinue) {
    if (-Not (Test-Path cert.pem) -or -Not (Test-Path key.pem)) {
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem -subj "/CN=localhost"
        Write-Host "Created cert.pem and key.pem in $scriptDir"
    } else {
        Write-Host "cert.pem and key.pem already exist in $scriptDir"
    }
} else {
    Write-Error "OpenSSL not found. Install OpenSSL (e.g., via Git for Windows) or create cert.pem/key.pem manually in $scriptDir."
}
Pop-Location
