Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$indexPath = Join-Path (Split-Path -Parent $PSScriptRoot) "index.html"
$source = Get-Content -LiteralPath $indexPath -Raw -Encoding UTF8

$unsupportedReportTranslate = [regex]::Matches(
  $source,
  'report\s*\([^)]*\btranslate\s*:\s*true'
)

if ($unsupportedReportTranslate.Count -ne 0) {
  throw "WCL GraphQL ReportData.report does not support the translate argument."
}

if ($source -notmatch 'masterData\s*\(\s*translate\s*:\s*true\s*\)') {
  throw "The supported masterData(translate:true) localization query was removed."
}

Write-Host "GraphQL contract checks passed."
