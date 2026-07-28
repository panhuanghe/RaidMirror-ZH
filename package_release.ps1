Param(
  [string]$Version = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-VersionFromReadme {
  $readmePath = Join-Path $PSScriptRoot "README.md"
  if (-not (Test-Path -LiteralPath $readmePath)) {
    throw "README.md not found: $readmePath"
  }

  # Avoid locale/encoding pitfalls by parsing a generic semantic-version marker in bold text.
  $m = Select-String -Path $readmePath -Pattern "\*\*v([0-9]+\.[0-9]+\.[0-9]+)\*\*" -Encoding UTF8 | Select-Object -First 1
  if (-not $m) {
    throw "Cannot parse version from README.md. Expected pattern: **vX.Y.Z**"
  }
  return $m.Matches[0].Groups[1].Value
}

if ([string]::IsNullOrWhiteSpace($Version)) {
  $Version = Get-VersionFromReadme
}

$zipName = "zhanjing-deploy-v$Version.zip"
$zipPath = Join-Path $PSScriptRoot $zipName

$paths = @("index.html", "assets", "data", "data_core")
foreach ($p in $paths) {
  $full = Join-Path $PSScriptRoot $p
  if (-not (Test-Path -LiteralPath $full)) {
    throw "Missing required path: $full"
  }
}

Compress-Archive -Path $paths -DestinationPath $zipPath -Force

Write-Host "Created: $zipPath"
Write-Host "Size: $((Get-Item -LiteralPath $zipPath).Length) bytes"
