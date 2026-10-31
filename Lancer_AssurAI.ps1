$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$assurPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (-not (Test-Path -LiteralPath $assurPython)) { throw 'Python intégré introuvable. Installer Python 3.12, les requirements, puis exécuter python run_local.py.' }
& $assurPython (Join-Path $PSScriptRoot 'run_local.py')
