$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Get-ChildItem -Path $root -Directory -Recurse -Filter "__pycache__" |
    Remove-Item -Recurse -Force

Get-ChildItem -Path $root -File -Recurse -Include "*.pyc", "*.pyo" |
    Remove-Item -Force

Write-Host "Cleaned Python cache files in: $root"
