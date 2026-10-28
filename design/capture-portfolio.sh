#!/bin/sh
# Genera las capturas del portafolio en landing/static/landing/portfolio/ (JPEG 1200x750).
set -e
cd "$(dirname "$0")/.."
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=landing/static/landing/portfolio
mkdir -p "$OUT"
for s in dental telefono salientes restaurante reservas empresa ventas automatizacion; do
  "$C" --headless=new --disable-gpu --hide-scrollbars --window-size=1200,750 \
    --screenshot="$OUT/$s.png" "file://$PWD/design/portfolio-mockups.html#$s" >/dev/null 2>&1
  sips -s format jpeg -s formatOptions 82 "$OUT/$s.png" --out "$OUT/$s.jpg" >/dev/null
  rm "$OUT/$s.png"
  echo "  $OUT/$s.jpg"
done
