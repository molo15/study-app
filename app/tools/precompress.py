# -*- coding: utf-8 -*-
"""生产预压缩脚本：对 build/web 下 wasm/js/css/json/html 等生成 .gz 静态文件，
配合 nginx gzip_static / brotli_static 零 CPU 直发（生产推荐 brotli_static）。

用法：python tools/precompress.py [root]      # 默认 build/web
"""
import gzip
import os
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'build/web')
EXTS = {'.wasm', '.js', '.json', '.css', '.html', '.txt', '.svg'}

n = 0
saved = 0
for dirpath, _, files in os.walk(ROOT):
    for f in files:
        if os.path.splitext(f)[1] not in EXTS:
            continue
        p = os.path.join(dirpath, f)
        gz = p + '.gz'
        data = open(p, 'rb').read()
        comp = gzip.compress(data, 9)
        if len(comp) < len(data):
            with open(gz, 'wb') as out:
                out.write(comp)
            saved += len(data) - len(comp)
            n += 1
print(f'precompressed {n} files, saved ~{saved // 1024}KB')
