#!/usr/bin/env python3
"""构建后清理：删除 Web 构建产物中的死资源和调试文件。

在 `flutter build web --release` + `post_build_sw.py` 之后运行。
清理项：
  - canvaskit/**/*.symbols（调试符号，生产不需要，约 8.18MB）
  - assets/assets/fonts/NotoSansSC-subset.ttf（Web 端只用 woff2，ttf 仅 io 端用，约 7.1MB）
  - flutter_service_worker.js（Flutter 生成的注销空壳，本项目使用自定义 sw.js，未注册）
  - canvaskit 下永不加载的引擎变体：skwasm/skwasm_heavy/wimp（仅 dart2wasm 的 skwasm
    渲染器使用）与 webparagraph/（仅显式开启 preferWebParagraph 时使用）。本项目固定
    dart2js + canvaskit 渲染器，这些文件不会被任何设备请求，删除约省 16MB。

清理后部署体积显著下降（减少浏览器永不请求的死重），不影响运行时功能
（浏览器不会请求被删除的文件）。

用法：
    python tools/post_build_cleanup.py
"""
import os
import shutil
import sys

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(APP_ROOT, 'build', 'web')


def remove(rel_path):
    """删除构建产物中的文件或目录，rel_path 为相对于 build/web 的路径。"""
    p = os.path.join(BUILD, rel_path)
    if not os.path.exists(p):
        print('  跳过（不存在）: %s' % rel_path)
        return 0
    size = 0
    if os.path.isdir(p):
        for root, _, files in os.walk(p):
            for f in files:
                size += os.path.getsize(os.path.join(root, f))
        shutil.rmtree(p)
    else:
        size = os.path.getsize(p)
        os.remove(p)
    print('  已删除: %s (%.2f MB)' % (rel_path, size / (1024 * 1024)))
    return size


def main():
    if not os.path.isdir(BUILD):
        print('ERROR: %s 不存在，请先运行 flutter build web' % BUILD)
        return 1

    total = 0
    print('=== Web 构建产物清理 ===')
    print()

    # 1. canvaskit .symbols 调试符号（遍历 canvaskit 目录）
    print('[1/4] 清理 canvaskit .symbols 调试符号')
    canvaskit_dir = os.path.join(BUILD, 'canvaskit')
    if os.path.isdir(canvaskit_dir):
        for root, _, files in os.walk(canvaskit_dir):
            for f in files:
                if f.endswith('.symbols'):
                    rel = os.path.relpath(os.path.join(root, f), BUILD)
                    total += remove(rel)
    else:
        print('  跳过（canvaskit 目录不存在）')
    print()

    # 2. Web 端死资源 ttf（Web 端只用 woff2）
    print('[2/4] 清理 Web 端死资源 NotoSansSC-subset.ttf')
    total += remove('assets/assets/fonts/NotoSansSC-subset.ttf')
    print()

    # 3. Flutter 空壳 Service Worker
    print('[3/4] 清理 flutter_service_worker.js（Flutter 注销空壳）')
    total += remove('flutter_service_worker.js')
    print()

    # 4. canvaskit 下永不加载的引擎变体（仅 dart2js+canvaskit 固定配置下安全）
    print('[4/4] 清理永不加载的引擎变体（skwasm/wimp/webparagraph）')
    bootstrap = os.path.join(BUILD, 'flutter_bootstrap.js')
    cfg = ''
    if os.path.exists(bootstrap):
        with open(bootstrap, 'r', encoding='utf-8', errors='ignore') as fh:
            cfg = fh.read()
    # 注意：引擎压缩代码里本身出现 "preferWebParagraph" 字段名，不能据此判断；
    # 只以 buildConfig 是否产出 dart2wasm 作为 skwasm 系列可能被使用的依据。
    uses_wasm = '"compileTarget":"dart2wasm"' in cfg
    if uses_wasm:
        print('  跳过：检测到 dart2wasm 构建，skwasm 系列可能被使用，保留')
    else:
        # webparagraph 仅当 load config 显式传 preferWebParagraph:true 才启用，本项目未传
        for rel in ('canvaskit/skwasm.js', 'canvaskit/skwasm.wasm',
                    'canvaskit/skwasm_heavy.js', 'canvaskit/skwasm_heavy.wasm',
                    'canvaskit/wimp.js', 'canvaskit/wimp.wasm',
                    'canvaskit/webparagraph'):
            total += remove(rel)
    print()

    print('=== 清理完成 ===')
    print('共释放: %.2f MB' % (total / (1024 * 1024)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
