#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find "$ROOT_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "$ROOT_DIR" -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

echo "Cleaned Python cache files in: $ROOT_DIR"
