#!/usr/bin/env python3
"""构建后处理：把 main.dart.js 的 SHA-256 前缀写入 build/web/sw.js 的 BUILD_ID。

在 `flutter build web --release` 之后运行。每次构建 main.dart.js 内容变化，
指纹随之变化 -> sw.js 内容变化 -> 浏览器检测到 Service Worker 更新 ->
activate 阶段自动重建缓存并清理旧版本，保证发布新版本不命中旧缓存。

用法：
    python tools/post_build_sw.py
"""
import hashlib
import io
import os
import sys

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(APP_ROOT, 'build', 'web')


def main():
    main_js = os.path.join(BUILD, 'main.dart.js')
    sw_path = os.path.join(BUILD, 'sw.js')
    if not os.path.exists(main_js):
        print('ERROR: %s 不存在，请先运行 flutter build web' % main_js)
        return 1
    if not os.path.exists(sw_path):
        print('ERROR: %s 不存在（web/sw.js 未被构建复制）' % sw_path)
        return 1

    with open(main_js, 'rb') as f:
        build_id = hashlib.sha256(f.read()).hexdigest()[:12]

    with io.open(sw_path, 'r', encoding='utf-8', newline='') as f:
        content = f.read()

    if '__BUILD_ID__' not in content:
        print('WARN: build/web/sw.js 中未找到 __BUILD_ID__ 占位，跳过（可能已处理）')
        return 0

    content = content.replace('__BUILD_ID__', build_id)
    with io.open(sw_path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

    print('OK: BUILD_ID = %s -> build/web/sw.js' % build_id)
    return 0


if __name__ == '__main__':
    sys.exit(main())
