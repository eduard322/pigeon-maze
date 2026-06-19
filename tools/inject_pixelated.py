"""Inject nearest-neighbor (crisp) canvas CSS into a pygbag-built index.html.

pygbag renders the WASM canvas at low resolution and lets the browser upscale
it with smoothing, which blurs pixel art on HiDPI/Retina displays. Forcing
image-rendering:pixelated keeps the pixels sharp. Idempotent.

Usage: python tools/inject_pixelated.py path/to/index.html
"""
import sys

MARKER = "/* pigeon-pixel-crisp */"
CSS = (
    "<style>" + MARKER +
    "#canvas,#canvas3d{image-rendering:pixelated;"
    "image-rendering:crisp-edges;}</style>\n</head>"
)


def inject(path):
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    if MARKER in html:
        print("pixelated canvas CSS already present")
        return
    html = html.replace("</head>", CSS, 1)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("injected pixelated canvas CSS")


if __name__ == "__main__":
    inject(sys.argv[1])
