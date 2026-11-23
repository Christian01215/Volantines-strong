<#
.SYNOPSIS
Carga las variables de .env en Vercel (Production + Preview) sin imprimir secretos.

USO
  1) Copiá .env.example a .env y completá todos los valores.
  2) Desde la raíz del proyecto:
       powershell -File scripts/sync_vercel_env.ps1
  3) Después:
       vercel deploy --prod --yes

NOTA
  Las variables VERCEL_* se omiten porque son sólo para la CLI local.
#>

param(
    [string]$EnvFile = ".env"
)

if (-not (Test-Path -LiteralPath $EnvFile)) {
    Write-Error "No existe $EnvFile. Copiá .env.example a .env y completalo primero."
    exit 1
}

$skip = @('VERCEL_TOKEN', 'VERCEL_ORG_ID', 'VERCEL_PROJECT_ID', 'ALLOWED_HOST')

Write-Host "Limpiando variables obsoletas..."
vercel env remove ALLOWED_HOST --confirm-name ALLOWED_HOST 2>$null | Out-Null
vercel env remove SUPABASE_KEY --environment development --confirm-name SUPABASE_KEY 2>$null | Out-Null

Get-Content -LiteralPath $EnvFile | ForEach-Object {
    $line = $_.Trim()

    if (-not $line -or $line.StartsWith('#')) { return }
    if ($line -notmatch '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$') { return }

    $name = $Matches[1]
    $value = $Matches[2]

    if ($skip -contains $name) { return }

    # Quitar comillas envolventes si el usuario las puso en .env
    if ($value.Length -ge 2) {
        $first = $value.Substring(0, 1)
        $last = $value.Substring($value.Length - 1, 1)
        if (($first -eq '"' -and $last -eq '"') -or ($first -eq "'" -and $last -eq "'")) {
            $value = $value.Substring(1, $value.Length - 2)
        }
    }

    foreach ($target in @('production', 'preview')) {
        $value | vercel env add $name -e $target --sensitive --force --yes | Out-Null
    }

    Write-Host "Actualizada: $name"
}

Write-Host ""
Write-Host "Listo. Ahora ejecutá: vercel deploy --prod --yes"
