Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$index = Get-Content -LiteralPath (Join-Path $root "index.html") -Raw -Encoding UTF8
$builder = Get-Content -LiteralPath (Join-Path $root "build_zh.py") -Raw -Encoding UTF8
$contract = Get-Content -LiteralPath (Join-Path $PSScriptRoot "localization_contract.json") -Raw -Encoding UTF8 | ConvertFrom-Json

$hits = @($contract.forbidden | Where-Object { $index.Contains($_) })
if ($hits.Count -gt 0) {
  throw "User-visible English remains: $($hits -join ', ')"
}

foreach ($required in $contract.required) {
  if (-not $index.Contains($required)) { throw "Required localized copy missing from index.html." }
  if (-not $builder.Contains($required)) { throw "Required localized copy missing from build_zh.py." }
}

Write-Host "Analysis-page localization checks passed."
