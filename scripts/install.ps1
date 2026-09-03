param([switch]$AssumeYes)

. "$PSScriptRoot\common.ps1"

$requirements = @(
    @{ Label = "Python 3.11+"; Command = "python"; Package = "Python.Python.3.13"; Minimum = "3.11" },
    @{ Label = "FFmpeg"; Command = "ffmpeg"; Package = "Gyan.FFmpeg"; Minimum = $null },
    @{ Label = "FFprobe"; Command = "ffprobe"; Package = "Gyan.FFmpeg"; Minimum = $null },
    @{ Label = "Node 22+"; Command = "node"; Package = "OpenJS.NodeJS.LTS"; Minimum = "22.0" },
    @{ Label = "Git"; Command = "git"; Package = "Git.Git"; Minimum = $null }
)

try {
    Write-Step "Verificando pre-requisitos"
    $installedPackages = @{}
    foreach ($item in $requirements) {
        $path = Get-ToolPath $item.Command
        $version = Get-ToolVersion $path
        $valid = $null -ne $path
        if ($valid -and $item.Minimum) {
            $valid = Test-MinimumVersion $version $item.Minimum
        }
        if ($valid) {
            Write-Host "OK  $($item.Label): $version"
            continue
        }
        if ($installedPackages.ContainsKey($item.Package)) { continue }
        if (-not (Confirm-Install $item.Label -AssumeYes:$AssumeYes)) {
            throw "Instalacao cancelada. $($item.Label) e necessario."
        }
        Install-WingetPackage $item.Package
        $installedPackages[$item.Package] = $true
    }

    $python = Get-ToolPath "python"
    if (-not $python) { $python = Get-ToolPath "py" }
    if (-not $python) { throw "Python nao foi localizado apos a instalacao." }

    $venvPython = Join-Path $Script:ProjectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        Write-Step "Criando ambiente virtual"
        Invoke-Checked $python @("-m", "venv", (Join-Path $Script:ProjectRoot ".venv"))
    } else {
        Write-Host "OK  Ambiente virtual existente sera reutilizado."
    }

    Write-Step "Instalando dependencias"
    Invoke-Checked $venvPython @("-m", "pip", "install", "--upgrade", "pip")
    Invoke-Checked $venvPython @("-m", "pip", "install", "--upgrade", "-r", (Join-Path $Script:ProjectRoot "requirements.txt"))

    $config = Join-Path $Script:ProjectRoot "config.json"
    if (-not (Test-Path $config)) {
        Copy-Item (Join-Path $Script:ProjectRoot "config.example.json") $config
        Write-Host "OK  config.json criado."
    } else {
        Write-Host "OK  config.json pessoal preservado."
    }

    Write-Step "Executando diagnostico"
    & "$PSScriptRoot\diagnose.ps1"
    if ($LASTEXITCODE -ne 0) { throw "Diagnostico final encontrou falhas." }
    Write-Host "`nInstalacao concluida. Execute iniciar.bat." -ForegroundColor Green
    exit 0
} catch {
    Write-Error $_
    exit 1
}
