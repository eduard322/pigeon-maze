"""Local dev server for the pygbag build.

Note: we deliberately do NOT send Cross-Origin-Embedder-Policy: require-corp.
That header blocks pygbag's cross-origin runtime files on the public CDN
(pygame-web.github.io), which hangs the loader. We only disable caching so
each rebuild is picked up immediately.

Usage: .venv/bin/python serve_web.py [port]
"""
import functools
import http.server
import socketserver
import sys

DIRECTORY = ".stage/pigeon_maze/build/web"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()


class Server(socketserver.TCPServer):
    allow_reuse_address = True


handler = functools.partial(Handler, directory=DIRECTORY)
print(f"Serving {DIRECTORY}")
print(f"  -> OPEN http://127.0.0.1:{PORT}   (use 127.0.0.1, NOT localhost:")
print("     'localhost' triggers pygbag proxy-mode and breaks the CDN package load)")
Server(("", PORT), handler).serve_forever()
