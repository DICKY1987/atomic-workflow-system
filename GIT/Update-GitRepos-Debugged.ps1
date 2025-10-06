# ========================================================================
# File: Update-GitRepos.ps1
# Description: Safely updates multiple Git repositories from a JSON registry.
# Requirements: PowerShell 7+, Git in PATH, AutomationSuite.psm1 module.
# Author: Debugged & Optimized by Code GPT 🧠
# ========================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Import-Module AutomationSuite.psm1 -Force

$config = Get-AutomationConfig -Environment $env:AUTOMATION_ENVIRONMENT
$envValidation = Test-AutomationEnvironment

if (-not $envValidation -or -not $envValidation.IsValid) {
    Write-StructuredLog -Level Error -Message "Environment validation failed or returned null."
    throw ([AutomationError]::new("Invalid environment state", [ErrorSeverity]::Critical, [ErrorCategory]::Configuration))
}

function Invoke-GitSafe {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$RepoPath,
        [Parameter(Mandatory)][string[]]$Args
    )

    $stdout = New-TemporaryFile
    $stderr = New-TemporaryFile

    try {
        $proc = Start-Process -FilePath "git" -ArgumentList $Args `
            -WorkingDirectory $RepoPath -NoNewWindow -Wait `
            -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru

        $out = Get-Content $stdout -Raw
        $err = Get-Content $stderr -Raw

        if ($proc.ExitCode -ne 0) {
            throw ([AutomationError]::new("git $($Args -join ' ') failed: $err", [ErrorSeverity]::High, [ErrorCategory]::External))
        }

        return $out
    } finally {
        Remove-Item $stdout, $stderr -Force -ErrorAction SilentlyContinue
    }
}

function Update-GitRepo {
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
    param(
        [pscustomobject]$Repo,
        [switch]$DryRun
    )

    if ($DryRun) { $WhatIfPreference = $true }

    $summary = [ordered]@{
        RepoPath   = $Repo.repo_path
        RepoUrl    = $Repo.repo_url
        RemoteName = $Repo.remote_name
        Branch     = $Repo.branch
        Status     = 'Pending'
        Error      = $null
    }

    try {
        if ($Repo.is_clean -and $Repo.last_synced -gt (Get-Date).AddMinutes(-10)) {
            Write-StructuredLog -Level Info -Message "Skipping clean repo: $($Repo.repo_url)"
            $summary.Status = 'Skipped'
            return [pscustomobject]$summary
        }

        if (-not (Test-Path -LiteralPath $Repo.repo_path)) {
            if ($Repo.auto_clone) {
                $parent = Split-Path -Path $Repo.repo_path -Parent
                if ($parent -and -not (Test-Path $parent)) {
                    New-Item -ItemType Directory -Path $parent -Force | Out-Null
                }
                Invoke-GitSafe -RepoPath "." -Args @("clone", $Repo.repo_url, $Repo.repo_path) | Out-Null
                $summary.Status = 'Cloned'
            } else {
                throw ([AutomationError]::new("Missing repo path and auto_clone is false: '$($Repo.repo_path)'", [ErrorSeverity]::Medium, [ErrorCategory]::FileSystem))
            }
        }

        Push-Location -LiteralPath $Repo.repo_path
        try {
            if (-not (Test-Path ".git")) {
                throw ([AutomationError]::new("Directory is not a Git repository: '$($Repo.repo_path)'", [ErrorSeverity]::High, [ErrorCategory]::FileSystem))
            }

            Invoke-GitSafe -RepoPath $Repo.repo_path -Args @("remote", "set-url", $Repo.remote_name, $Repo.repo_url) | Out-Null
            Invoke-GitSafe -RepoPath $Repo.repo_path -Args @("fetch", $Repo.remote_name, "--prune", "--tags") | Out-Null

            Invoke-GitSafe -RepoPath $Repo.repo_path -Args @("checkout", "-B", $Repo.branch, "$($Repo.remote_name)/$($Repo.branch)") | Out-Null

            if ($Repo.is_dirty -and -not $Repo.hard_sync) {
                if ($Repo.PSObject.Properties.Match("force") -and $Repo.force) {
                    Invoke-GitSafe -RepoPath $Repo.repo_path -Args @("stash", "push", "-u", "-m", "Auto-stash by automation") | Out-Null
                    $summary.Stashed = $true
                } else {
                    throw ([AutomationError]::new("Working tree has uncommitted changes.", [ErrorSeverity]::Medium, [ErrorCategory]::State))
                }
            }

            if ($Repo.hard_sync) {
                Invoke-GitSafe -RepoPath $Repo.repo_path -Args @("reset", "--hard", "$($Repo.remote_name)/$($Repo.branch)") | Out-Null
                $summary.HardSynced = $true
            }

            Invoke-GitSafe -RepoPath $Repo.repo_path -Args @("pull", "--ff-only", $Repo.remote_name, $Repo.branch) | Out-Null

            $summary.Status = if ($WhatIfPreference) { 'DRYRUN' } else { 'OK' }
        }
        finally {
            Pop-Location
        }
    }
    catch {
        $summary.Status = 'ERROR'
        $summary.Error = $_.Exception.Message
        Write-StructuredLog -Level Error -Message $_.Exception.Message -Exception $_.Exception
    }

    return [pscustomobject]$summary
}

function Update-GitReposFromRegistry {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory)][string]$RegistryPath,
        [switch]$DryRun,
        [switch]$Parallel
    )

    if (-not (Test-Path $RegistryPath)) {
        throw ([AutomationError]::new("Registry not found: $RegistryPath", [ErrorSeverity]::High, [ErrorCategory]::FileSystem))
    }

    $repos = Get-Content -Raw -LiteralPath $RegistryPath | ConvertFrom-Json
    $results = @()

    Write-StructuredLog -Level Info -Message "Starting repository updates for $($repos.Count) repositories..."

    if ($Parallel -and $PSVersionTable.PSVersion.Major -ge 7) {
        $results = $repos | ForEach-Object -Parallel {
            Update-GitRepo -Repo $_ -DryRun:$using:DryRun
        }
    } else {
        foreach ($repo in $repos) {
            Write-StructuredLog -Level Info -Message "Processing $($repo.repo_url) [$($repo.branch)]"
            $res = Update-GitRepo -Repo $repo -DryRun:$DryRun
            $results += $res
        }
    }

    $results | ConvertTo-Json -Depth 5 | Set-Content "UpdateSummary.json" -Encoding UTF8
    Write-StructuredLog -Level Info -Message "Update summary written to UpdateSummary.json"

    return ,$results
}

Write-StructuredLog -Level Info -Message "Git repository updater initialized successfully."
