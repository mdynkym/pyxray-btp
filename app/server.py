import os
import http.server
import socketserver
import threading

from .config import PORT, FILE_PATH
from .config import PORT, FILE_PATH, SUB_PATH, SUB_TOKEN

PUBLIC_DIR = os.path.join(FILE_PATH, "public")

import os
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

from .config import PORT, FILE_PATH, SUB_PATH, SUB_TOKEN

PUBLIC_DIR = os.path.join(FILE_PATH, "public")


class BlogHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path.startswith(SUB_PATH):
            qs = parse_qs(urlparse(self.path).query)
            if not SUB_TOKEN or qs.get("token", [""])[0] != SUB_TOKEN:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Forbidden")
                return
            fp = os.path.join(FILE_PATH, 'sub.txt')
            if os.path.exists(fp):
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                with open(fp, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        if self.path == '/api/news/config':
            fp = os.path.join(FILE_PATH, 'config.json')
            if os.path.exists(fp):
                self.send_response(200)
                self.send_header('Content-Type',
                                 'application/json; charset=utf-8')
                self.end_headers()
                with open(fp, 'rb') as f:
                    self.wfile.write(f.read())
                return

        if self.path == '/api/news/log':
            fp = os.path.join(FILE_PATH, 'cloudflared.log')
            if os.path.exists(fp):
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                with open(fp, 'rb') as f:
                    self.wfile.write(f.read())
                return

        # 其它路径走静态博客
        return super().do_GET()


def start_http_server():
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    httpd = socketserver.TCPServer(('0.0.0.0', PORT), BlogHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print(f"HTTP 服务已启动，端口：{PORT}，订阅路径：{SUB_PATH}?token=***")
