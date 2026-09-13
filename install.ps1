<#
.SYNOPSIS
  Install the cat-visual-aptitude skill for Antigravity CLI (agy) and/or Claude Code.

.DESCRIPTION
  Default (-Mode register): points agy's global skills.json at this repo, so
  `git pull` updates the skill with no reinstall.
  -Mode copy      : copies the skill folder into the global skills root instead.
  -Mode workspace : registers it for the current repo only (.agents/skills.json).
  -Mode claude    : copies the skill into ~/.claude/skills for Claude Code.

.EXAMPLE
  .\install.ps1
  .\install.ps1 -Mode copy
  .\install.ps1 -Mode workspace
#>
param(
  [ValidateSet('register', 'copy', 'workspace', 'claude')]
  [string]$Mode = 'register'
)

$ErrorActionPreference = 'Stop'
$Repo      = $PSScriptRoot
$SkillsDir = Join-Path $Repo 'skills'
$SkillName = 'cat-visual-aptitude'
# $HOME is read-only in PowerShell, so use our own name (and honour $env:HOME,
# which also makes this script testable against a sandbox directory).
$UserHome  = if ($env:HOME) { $env:HOME } else { $HOME }

if (-not (Test-Path (Join-Path $SkillsDir "$SkillName\SKILL.md"))) {
  throw "skills\$SkillName\SKILL.md not found under $Repo - run this from the repo root."
}

function Add-Entry($ConfigPath, $EntryPath) {
  $dir = Split-Path $ConfigPath -Parent
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }

  if (Test-Path $ConfigPath) {
    $cfg = Get-Content $ConfigPath -Raw | ConvertFrom-Json
  } else {
    $cfg = [pscustomobject]@{ entries = @() }
  }
  if (-not $cfg.PSObject.Properties.Name.Contains('entries') -or $null -eq $cfg.entries) {
    $cfg | Add-Member -NotePropertyName entries -NotePropertyValue @() -Force
  }

  $existing = @($cfg.entries | Where-Object { $_.path -eq $EntryPath })
  if ($existing.Count -gt 0) {
    Write-Host "already registered: $EntryPath"
  } else {
    $cfg.entries = @($cfg.entries) + @([pscustomobject]@{ path = $EntryPath })
    # Write UTF-8 WITHOUT a BOM: PowerShell 5.1's -Encoding utf8 adds one, and
    # Go's encoding/json (which agy uses) rejects a leading BOM.
    $json = $cfg | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($ConfigPath, $json, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host "registered $EntryPath in $ConfigPath"
  }
}

switch ($Mode) {
  'register' {
    Add-Entry (Join-Path $UserHome '.gemini\config\skills.json') ($SkillsDir -replace '\\', '/')
    Write-Host "`nInstalled globally for agy. Start a new session; the skill loads"
    Write-Host "automatically and is also available as /$SkillName."
    Write-Host "Update later with: git -C `"$Repo`" pull"
  }
  'copy' {
    $dest = Join-Path $UserHome ".gemini\config\skills\$SkillName"
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Copy-Item (Join-Path $SkillsDir "$SkillName\*") $dest -Recurse -Force
    Write-Host "copied to $dest"
    Write-Host "Note: a copy does not track this repo. Re-run after a git pull."
  }
  'workspace' {
    $cwd = (Get-Location).Path
    Add-Entry (Join-Path $cwd '.agents\skills.json') ($SkillsDir -replace '\\', '/')
    Write-Host "`nRegistered for this workspace only ($cwd)."
    Write-Host "Commit .agents/skills.json to share it with the team."
  }
  'claude' {
    $dest = Join-Path $UserHome ".claude\skills\$SkillName"
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Copy-Item (Join-Path $SkillsDir "$SkillName\*") $dest -Recurse -Force
    Write-Host "copied to $dest - restart Claude Code to pick it up"
  }
}

Write-Host "`nOptional: pip install pillow    (needed only for the image scripts)"
