<#
    publicar_tunel.ps1
    Publica TechTrack SATE en internet con un tunel temporal de Cloudflare.

    Uso:
        powershell -ExecutionPolicy Bypass -File scripts\publicar_tunel.ps1

    El script:
      1. Comprueba si la aplicacion ya responde en 127.0.0.1:5000.
      2. Si no responde, la arranca en una ventana nueva.
      3. Descarga cloudflared si hace falta.
      4. Abre el tunel y muestra la URL publica https://algo.trycloudflare.com

    La URL solo funciona mientras esta ventana y la PC sigan encendidas.
#>

$ErrorActionPreference = 'Stop'

$raiz = Split-Path -Parent $PSScriptRoot
$puerto = 5000
$destinoCloudflared = Join-Path $env:LOCALAPPDATA 'Temp\opencode\cloudflared.exe'

function Probar-Puerto {
    param([int]$Puerto)
    try {
        $cliente = New-Object System.Net.Sockets.TcpClient
        $cliente.Connect('127.0.0.1', $Puerto)
        $cliente.Close()
        return $true
    } catch {
        return $false
    }
}

Write-Host '== TechTrack SATE: publicacion con tunel ==' -ForegroundColor Cyan

# 1. Aplicacion local
if (Probar-Puerto -Puerto $puerto) {
    Write-Host "La aplicacion ya responde en http://127.0.0.1:$puerto" -ForegroundColor Green
} else {
    Write-Host "La aplicacion no responde. Arrancandola en una ventana nueva..." -ForegroundColor Yellow
    Start-Process -FilePath 'powershell' -WorkingDirectory $raiz -ArgumentList @(
        '-NoExit',
        '-Command',
        "python app.py"
    )
    $intentos = 0
    while (-not (Probar-Puerto -Puerto $puerto) -and $intentos -lt 30) {
        Start-Sleep -Seconds 1
        $intentos++
    }
    if (-not (Probar-Puerto -Puerto $puerto)) {
        throw "La aplicacion no arranco en el puerto $puerto. Revisa la ventana nueva y el archivo .env"
    }
    Write-Host "Aplicacion lista en http://127.0.0.1:$puerto" -ForegroundColor Green
}

# 2. Cliente de Cloudflare
if (-not (Test-Path $destinoCloudflared)) {
    Write-Host 'Descargando cloudflared...' -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destinoCloudflared) | Out-Null
    Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' `
        -OutFile $destinoCloudflared -UseBasicParsing
}

# 3. Tunel
Write-Host ''
Write-Host 'Abriendo el tunel. La URL publica aparece abajo, en la linea' -ForegroundColor Cyan
Write-Host '  https://algo.trycloudflare.com' -ForegroundColor Cyan
Write-Host 'Comparte esa direccion. Para cerrar la publicacion pulsa Ctrl+C.' -ForegroundColor Cyan
Write-Host ''

& $destinoCloudflared tunnel --url "http://127.0.0.1:$puerto" --no-autoupdate
