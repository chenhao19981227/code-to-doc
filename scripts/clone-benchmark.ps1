# Re-create the Kill Bill benchmark clones under benchmark/ (shallow, small).
#
# The repo does NOT ship the third-party Kill Bill sources/docs (~164 MB).
# Run this once after cloning code-to-doc to reproduce the benchmark environment.
#
# Usage:
#   pwsh -File scripts/clone-benchmark.ps1
#   pwsh -File scripts/clone-benchmark.ps1 -Proxy http://127.0.0.1:7897
#   pwsh -File scripts/clone-benchmark.ps1 -NoProxy          # direct connection

param(
    [string]$Proxy = "http://127.0.0.1:7897",
    [switch]$NoProxy
)

$ErrorActionPreference = "Stop"

$root  = Split-Path -Parent $PSScriptRoot
$bench = Join-Path $root "benchmark"
New-Item -ItemType Directory -Force -Path $bench | Out-Null

# Revision the benchmark results in docs/ were produced against.
$KILLBILL_SHA = "cb60779c171391be558cd7aebb1eafea60ad2b82"
$DOCS_SHA     = "c57d61b8a7bf2ba11cd553b6b97a6beb9ed3644d"

$useProxy = (-not $NoProxy) -and $Proxy
if ($useProxy) {
    $env:HTTPS_PROXY = $Proxy
    $env:HTTP_PROXY  = $Proxy
}
$env:GIT_TERMINAL_PROMPT = "0"
$env:GIT_PAGER = "cat"

$gitc = @()
if ($useProxy) { $gitc = @("-c", "http.proxy=$Proxy", "-c", "https.proxy=$Proxy") }

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    & git @gitc @Args
    if ($LASTEXITCODE -ne 0) { throw "git $($Args -join ' ') failed with exit code $LASTEXITCODE" }
}

$kbDir   = Join-Path $bench "killbill"
$docsDir = Join-Path $bench "killbill-docs"

if (-not (Test-Path $kbDir)) {
    Write-Host "==> cloning killbill (shallow) ..."
    Invoke-Git clone --depth 1 https://github.com/killbill/killbill.git $kbDir
} else {
    Write-Host "==> killbill already present, skipping clone"
}

if (-not (Test-Path $docsDir)) {
    Write-Host "==> cloning killbill-docs (shallow, branch v3) ..."
    Invoke-Git clone --depth 1 --branch v3 https://github.com/killbill/killbill-docs.git $docsDir
} else {
    Write-Host "==> killbill-docs already present, skipping clone"
}

$kbHead   = (& git -C $kbDir rev-parse HEAD).Trim()
$docsHead = (& git -C $docsDir rev-parse HEAD).Trim()

Write-Host ""
Write-Host "killbill      HEAD = $kbHead"
Write-Host "  expected         = $KILLBILL_SHA"
Write-Host "killbill-docs HEAD = $docsHead"
Write-Host "  expected         = $DOCS_SHA"

if ($kbHead -ne $KILLBILL_SHA) {
    Write-Warning "killbill HEAD differs from the pinned revision; L4 numbers may shift."
}
if ($docsHead -ne $DOCS_SHA) {
    Write-Warning "killbill-docs HEAD differs from the pinned revision; the answer key may shift."
}

Write-Host ""
Write-Host "done. Next: python -m pip install -r eval/requirements.txt"
