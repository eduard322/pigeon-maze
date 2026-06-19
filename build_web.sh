#!/usr/bin/env bash
# Build the Pigeon Maze web bundle from a clean staging copy so pygbag only
# packages the game (main.py, game/, assets/) and not the venv/tests/docs.
# Output: .stage/pigeon_maze/build/web  (index.html + pigeon_maze.apk)
#
# PYTHON env var overrides the interpreter (CI uses system python).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
STAGE="$ROOT/.stage/pigeon_maze"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"

rm -rf "$ROOT/.stage"
mkdir -p "$STAGE"
cp "$ROOT/main.py" "$STAGE/"
cp -R "$ROOT/game" "$STAGE/game"
cp -R "$ROOT/assets" "$STAGE/assets"
find "$STAGE" -name __pycache__ -type d -prune -exec rm -rf {} +

"$PYTHON" -m pygbag --build --title "Pigeon Maze" "$STAGE/main.py"

# Post-build: force crisp (nearest-neighbor) scaling of the WASM canvas.
"$PYTHON" "$ROOT/tools/inject_pixelated.py" "$STAGE/build/web/index.html"

echo "----------------------------------------"
echo "Web bundle ready: $STAGE/build/web"
ls -la "$STAGE/build/web"
