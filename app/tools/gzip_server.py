# -*- coding: utf-8 -*-
"""开发期压缩模拟服务器（多线程 + 静态 .gz 优先，近似 nginx gzip_static）：
- 若存在 <file>.gz 静态预压缩文件则直发（零 CPU，接近生产）
- 否则对 wasm/js/css/json/html 动态 gzip
生产由 nginx brotli/gzip 负责。

用法：python tools/gzip_server.py [port] [root]
默认 port=8732, root=build/web
"""
import gzip
import http.server
import os
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8732
ROOT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'build', 'web')

GZIP_EXTS = {'.wasm', '.js', '.json', '.css', '.html', '.txt', '.svg'}


class GzipHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header('Vary', 'Accept-Encoding')
        super().end_headers()

    def do_GET(self):
        ae = self.headers.get('Accept-Encoding', '')
        if 'gzip' in ae:
            path = self.translate_path(self.path)
            if os.path.isfile(path):
                ext = os.path.splitext(path)[1]
                if ext in GZIP_EXTS:
                    gz_path = path + '.gz'
                    if os.path.isfile(gz_path):
                        data = open(gz_path, 'rb').read()
                    else:
                        data = gzip.compress(open(path, 'rb').read(), 6)
                    if len(data) < os.path.getsize(path):
                        self.send_response(200)
                        self.send_header('Content-Type', self.guess_type(path))
                        self.send_header('Content-Encoding', 'gzip')
                        self.send_header('Content-Length', str(len(data)))
                        self.end_headers()
                        self.wfile.write(data)
                        return
        super().do_GET()


if __name__ == '__main__':
    os.chdir(ROOT)
    with socketserver.ThreadingTCPServer(('', PORT), GzipHandler) as httpd:
        print(f'gzip server on :{PORT} root={ROOT}')
        httpd.serve_forever()
