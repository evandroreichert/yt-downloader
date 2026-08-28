$ErrorActionPreference = "Stop"
$Script:ProjectRoot = Split-Path -Parent $PSScriptRoot

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Get-ToolPath {
    param([string]$Name)
    $command = Get-Command $Name -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $command) { return $null }
    return $command.Source
}

function Get-ToolVersion {
    param([string]$Path)
    if (-not $Path) { return $null }
    try {
        $output = & $Path --version 2>&1
        if ($LASTEXITCODE -ne 0) { return $null }
        $text = $output | Select-Object -First 1
        return "$text"
    } catch {
        return $null
    }
}

function Test-MinimumVersion {
    param([string]$VersionText, [string]$Minimum)
    if (-not $VersionText) { return $false }
    $match = [regex]::Match($VersionText, "(\d+)\.(\d+)")
    if (-not $match.Success) { return $false }
    $actual = [version]"$($match.Groups[1].Value).$($match.Groups[2].Value)"
    return $actual -ge [version]$Minimum
}

function Confirm-Install {
    param([string]$Label, [switch]$AssumeYes)
    if ($AssumeYes) { return $true }
    $answer = Read-Host "$Label nao foi encontrado. Instalar pelo winget? [S/n]"
    return [string]::IsNullOrWhiteSpace($answer) -or $answer -match "^[SsYy]"
}

function Install-WingetPackage {
    param([string]$PackageId)
    $winget = Get-ToolPath "winget"
    if (-not $winget) {
        throw "winget nao encontrado. Instale o App Installer pela Microsoft Store."
    }
    & $winget install --exact --id $PackageId --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar $PackageId pelo winget." }
    $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" +
        [Environment]::GetEnvironmentVariable("PATH", "User")
}

function Invoke-Checked {
    param([string]$FilePath, [string[]]$Arguments)
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Comando falhou ($LASTEXITCODE): $FilePath $($Arguments -join ' ')"
    }
}
