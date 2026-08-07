$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m ruff check src tests

if (Test-Path dist) { Remove-Item dist -Recurse -Force }
python -m PyInstaller --clean --noconfirm ChromeDiagnostic.spec

$exe = Join-Path $PWD 'dist\ChromeDiagnostic.exe'
if (-not (Test-Path $exe)) { throw 'PyInstaller did not produce ChromeDiagnostic.exe' }

$innoCandidates = @(
  "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
  "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
)
$inno = $innoCandidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

if (-not $inno) {
  Write-Warning 'Inno Setup not found. EXE build completed; installer was not created.'
} else {
  & $inno 'installer\ChromeDiagnostic.iss'
}

$checksumLines = @()
Get-ChildItem 'dist' -File | Where-Object { $_.Extension -eq '.exe' } | ForEach-Object {
  $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  $checksumLines += "$hash  $($_.Name)"
}
$checksumLines | Set-Content 'dist\SHA256SUMS.txt' -Encoding ascii
