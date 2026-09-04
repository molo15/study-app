@echo off
REM === Quiz App - Web build pipeline ===
REM Usage (run from app\):
REM   build_web.bat                 build with base href /study-app/ (GitHub Pages)
REM   build_web.bat /               root deployment
REM   build_web.bat /some/path/     custom base href (must start and end with /)
REM Steps: flutter build web -> sw.js BUILD_ID -> dead asset cleanup
REM        -> .gz precompress -> deploy zip (with .gz)
REM Always use this script for deployment builds.

setlocal enabledelayedexpansion

REM ---------- base href (default: GitHub Pages project subpath) ----------
set "BASE_HREF=%~1"
if "%BASE_HREF%"=="" set "BASE_HREF=/study-app/"

echo.
echo ========================================
echo   Quiz App - Web Build (base-href=%BASE_HREF%)
echo ========================================
echo.

REM ---------- Step 1: flutter build web ----------
echo [1/5] flutter build web --release --no-web-resources-cdn --base-href "%BASE_HREF%"
echo.
call D:\flutter\bin\flutter.bat build web --release --no-web-resources-cdn --base-href "%BASE_HREF%"
if errorlevel 1 (
    echo.
    echo [ERROR] flutter build web failed, abort.
    exit /b 1
)
echo.
echo [OK] flutter build web done
echo.

REM ---------- Step 2: sw.js BUILD_ID fingerprint ----------
echo [2/5] inject sw.js BUILD_ID (SHA-256 prefix of main.dart.js)
echo.
python tools\post_build_sw.py
if errorlevel 1 (
    echo.
    echo [ERROR] post_build_sw.py failed, abort.
    exit /b 1
)
echo.

REM ---------- Step 3: dead asset cleanup (before gzip so dead .gz never appears) ----------
echo [3/5] cleanup: .symbols + web-dead ttf + stub SW + unused engine variants
echo.
python tools\post_build_cleanup.py
if errorlevel 1 (
    echo.
    echo [ERROR] post_build_cleanup.py failed, abort.
    exit /b 1
)
echo.

REM ---------- Step 4: .gz precompression ----------
echo [4/5] generate .gz files (nginx gzip_static; GitHub Pages auto-serves them too)
echo.
python tools\precompress.py
if errorlevel 1 (
    echo.
    echo [ERROR] precompress.py failed, abort.
    exit /b 1
)
echo.

REM ---------- Step 5: deploy zip (includes .gz) ----------
echo [5/5] package build\web-deploy-study-app.zip (includes .gz)
echo.
python tools\package_deploy.py
if errorlevel 1 (
    echo.
    echo [ERROR] package_deploy.py failed
    exit /b 1
)
echo.

REM ---------- Done ----------
echo ========================================
echo   Build finished
echo ========================================
echo.
echo Output : build\web (base-href=%BASE_HREF%)
echo Zip    : build\web-deploy-study-app.zip (upload extracted contents)
echo SW hash: injected from main.dart.js SHA-256 prefix
echo .gz    : generated (gzip_static / GitHub Pages static gzip)
echo Cleanup: .symbols / dead ttf / stub SW removed
echo.

endlocal
