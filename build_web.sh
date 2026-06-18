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

echo "----------------------------------------"
echo "Web bundle ready: $STAGE/build/web"
ls -la "$STAGE/build/web"
