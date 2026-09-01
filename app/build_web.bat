@echo off
chcp 65001 >nul
REM === 考研刷题 App — Web 端构建脚本 ===
REM 用法：在 app\ 目录下运行 build_web.bat
REM 流程：flutter build web → 替换 sw.js BUILD_ID 指纹 → 构建后清理（死资源+调试文件+空壳SW）
REM 注意：必须运行此脚本构建后部署，直接 flutter build web 会导致 sw.js 缓存版本化失效。

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   考研刷题 App — Web 构建
echo ========================================
echo.

REM ---------- 步骤 1：flutter build web ----------
echo [1/3] flutter build web --release --no-web-resources-cdn
echo.
call D:\flutter\bin\flutter.bat build web --release --no-web-resources-cdn
if errorlevel 1 (
    echo.
    echo [ERROR] flutter build web 失败，终止构建。
    exit /b 1
)
echo.
echo [OK] flutter build web 完成
echo.

REM ---------- 步骤 2：替换 sw.js BUILD_ID 指纹 ----------
echo [2/3] 替换 sw.js BUILD_ID 指纹（main.dart.js SHA-256 前缀）
echo.
python tools\post_build_sw.py
if errorlevel 1 (
    echo.
    echo [ERROR] post_build_sw.py 失败，终止构建。
    exit /b 1
)
echo.

REM ---------- 步骤 3：构建后清理（死资源 + 调试文件 + 空壳 SW） ----------
echo [3/3] 构建后清理：canvaskit .symbols + Web端死资源ttf + Flutter空壳SW
echo.
python tools\post_build_cleanup.py
if errorlevel 1 (
    echo.
    echo [ERROR] post_build_cleanup.py 失败
    exit /b 1
)
echo.

REM ---------- 完成 ----------
echo ========================================
echo   构建完成
echo ========================================
echo.
echo 产物目录：build\web
echo sw.js 指纹：已替换为 main.dart.js SHA-256 前缀
echo 部署前请确认 build\web\sw.js 中 BUILD_ID 不为 '__BUILD_ID__'
echo.

endlocal
