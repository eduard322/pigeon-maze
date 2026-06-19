#!/usr/bin/env bash
# Build the Pigeon Maze web bundle from a clean staging copy so pygbag only
# packages the game (main.py, game/, assets/) and not the venv/tests/docs.
# Output: .stage/pigeon_maze/build/web  (index.html + pigeon_maze.apk)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
STAGE="$ROOT/.stage/pigeon_maze"

rm -rf "$ROOT/.stage"
mkdir -p "$STAGE"
cp "$ROOT/main.py" "$STAGE/"
cp -R "$ROOT/game" "$STAGE/game"
cp -R "$ROOT/assets" "$STAGE/assets"
find "$STAGE" -name __pycache__ -type d -prune -exec rm -rf {} +

"$ROOT/.venv/bin/python" -m pygbag --build --title "Pigeon Maze" "$STAGE/main.py"

# Post-build: force nearest-neighbor (crisp) scaling of the WASM canvas.
# pygbag renders at low res and lets the browser upscale with smoothing, which
# blurs pixel art and text on HiDPI/Retina displays. This makes it pixel-sharp.
"$ROOT/.venv/bin/python" - "$STAGE/build/web/index.html" <<'PY'
import sys
p = sys.argv[1]
html = open(p, encoding="utf-8").read()
marker = "/* pigeon-pixel-crisp */"
if marker not in html:
    css = (
        "<style>" + marker +
        "#canvas,#canvas3d{image-rendering:pixelated;"
        "image-rendering:crisp-edges;}</style>\n</head>"
    )
    html = html.replace("</head>", css, 1)
    open(p, "w", encoding="utf-8").write(html)
    print("injected pixelated canvas CSS")
else:
    print("pixelated canvas CSS already present")
PY

echo "----------------------------------------"
echo "Web bundle ready: $STAGE/build/web"
ls -la "$STAGE/build/web"
