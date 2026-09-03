. "$PSScriptRoot\common.ps1"

try {
    Set-Location $Script:ProjectRoot
    $git = Get-ToolPath "git"
    if ($git -and (Test-Path (Join-Path $Script:ProjectRoot ".git"))) {
        $changes = & $git status --porcelain
        if ([string]::IsNullOrWhiteSpace(($changes -join ""))) {
            Write-Step "Atualizando codigo"
            Invoke-Checked $git @("pull", "--ff-only")
        } else {
            Write-Warning "Codigo local alterado; git pull foi ignorado para preservar seu trabalho."
        }
    } else {
        Write-Warning "Git indisponivel ou pasta sem .git; atualizando apenas dependencias."
    }

    $venvPython = Join-Path $Script:ProjectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        throw "Ambiente .venv ausente. Execute instalar.bat primeiro."
    }
    Write-Step "Atualizando dependencias"
    Invoke-Checked $venvPython @("-m", "pip", "install", "--upgrade", "pip", "yt-dlp[default]")
    Invoke-Checked $venvPython @("-m", "pip", "install", "--upgrade", "-r", (Join-Path $Script:ProjectRoot "requirements.txt"))
    & "$PSScriptRoot\diagnose.ps1"
    exit $LASTEXITCODE
} catch {
    Write-Error $_
    exit 1
}
