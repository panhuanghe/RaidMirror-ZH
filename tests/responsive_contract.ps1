Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$index = Get-Content -LiteralPath (Join-Path $root "index.html") -Raw -Encoding UTF8

if ($index -notmatch '(?s)@media\(max-width:1640px\)\s*\{\s*\.hero-gnome\s*\{\s*display:none\s*!important;') {
  throw "Hero artwork must hide before it overlaps the summary cards at 1366px."
}

Write-Host "Responsive layout checks passed."
