<#
    mantener_despierto.ps1
    Evita que Windows suspenda el equipo mientras el tunel publico esta activo.

    Uso:
        powershell -ExecutionPolicy Bypass -File scripts\mantener_despierto.ps1

    Deja la ventana abierta mientras quieras que el enlace siga funcionando.
    Para detenerlo pulsa Ctrl+C.

    Nota: este script impide la suspension por inactividad. Si el equipo es una
    laptop, mantenla enchufada y con la tapa abierta: cerrar la tapa o quedarse
    sin bateria si puede suspenderla.
#>

$ErrorActionPreference = 'Stop'

Add-Type @"
using System;
using System.Runtime.InteropServices;

public class EstadoEnergia {
    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    public static extern uint SetThreadExecutionState(uint esFlags);

    public const uint ES_CONTINUOUS       = 0x80000000;
    public const uint ES_SYSTEM_REQUIRED  = 0x00000001;
    public const uint ES_DISPLAY_REQUIRED = 0x00000002;

    public static void Activar() {
        SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED);
    }

    public static void Liberar() {
        SetThreadExecutionState(ES_CONTINUOUS);
    }
}
"@

try {
    [EstadoEnergia]::Activar()
    Write-Host 'Equipo marcado como "en uso": no se suspenderá por inactividad.' -ForegroundColor Green
    Write-Host 'Deja esta ventana abierta. Ctrl+C para detener.' -ForegroundColor Cyan
    Write-Host ''

    while ($true) {
        Start-Sleep -Seconds 60
    }
} finally {
    [EstadoEnergia]::Liberar()
    Write-Host 'Listo: Windows vuelve a su comportamiento normal de suspension.' -ForegroundColor Yellow
}
