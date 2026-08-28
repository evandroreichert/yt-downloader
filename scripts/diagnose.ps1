param([switch]$CheckOnly)

. "$PSScriptRoot\common.ps1"

if ($CheckOnly) {
    Write-Output "CHECK: diagnostico em modo somente leitura"
    Write-Output "CHECK: Python da .venv e pacotes"
    Write-Output "CHECK: FFmpeg e FFprobe"
    Write-Output "CHECK: Node 22+ e Git"
    Write-Output "CHECK: CUDA e fallback CPU"
    exit 0
}

$failed = $false
$venvPython = Join-Path $Script:ProjectRoot ".venv\Scripts\python.exe"
Write-Host "`n=== Diagnostico Media Tools ===" -ForegroundColor Cyan

if (Test-Path $venvPython) {
    & $venvPython (Join-Path $Script:ProjectRoot "diagnostics.py")
    if ($LASTEXITCODE -ne 0) { $failed = $true }
    & $venvPython -m pip check
    if ($LASTEXITCODE -ne 0) { $failed = $true }
} else {
    Write-Host "FALHA Python: .venv nao encontrado. Execute instalar.bat."
    $failed = $true
}

foreach ($tool in @("node", "ffmpeg", "ffprobe")) {
    $path = Get-ToolPath $tool
    $version = Get-ToolVersion $path
    if ($path) {
        Write-Host "OK  $tool`: $version ($path)"
    } else {
        Write-Host "FALHA $tool nao encontrado no PATH."
        $failed = $true
    }
}

$drive = Get-Item $Script:ProjectRoot
$freeGb = [math]::Round($drive.PSDrive.Free / 1GB, 1)
Write-Host "INFO downloads: $(Join-Path $Script:ProjectRoot 'downloads')"
Write-Host "INFO espaco livre: $freeGb GB"

if ($failed) { exit 1 }
Write-Host "Diagnostico concluido sem falhas obrigatorias." -ForegroundColor Green
exit 0
