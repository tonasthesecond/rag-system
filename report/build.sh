#!/usr/bin/env bash
# Render report.md to report.pdf (needs pandoc + typst; the Inter font is optional).
set -euo pipefail
cd "$(dirname "$0")"
pandoc report.md -o report.pdf --pdf-engine=typst \
  -V mainfont="Inter" -V fontsize=10pt -V papersize=a4 \
  -V margin-x=2.2cm -V margin-y=2.2cm
echo "wrote $(pwd)/report.pdf ($(pandoc report.md -t plain | wc -w) words)"
