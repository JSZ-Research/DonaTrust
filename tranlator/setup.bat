@echo off
REM ============================================
REM DonaTrust Sign Translator - Windows 环境安装脚本
REM ============================================

echo ==========================================
echo   DonaTrust Sign Translator 环境配置
echo ==========================================

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "REQ_FILE=%SCRIPT_DIR%requirements.txt"

REM ---------- 检测 Python ----------
set "PYTHON_CMD="

REM 尝试 py launcher (Windows 推荐)
where py >nul 2>&1
if %errorlevel%==0 (
    for /f "tokens=*" %%i in ('py -3.10 --version 2^>nul') do set "PYTHON_CMD=py -3.10"
    if not defined PYTHON_CMD (
        for /f "tokens=*" %%i in ('py -3.11 --version 2^>nul') do set "PYTHON_CMD=py -3.11"
    )
    if not defined PYTHON_CMD (
        for /f "tokens=*" %%i in ('py -3.12 --version 2^>nul') do set "PYTHON_CMD=py -3.12"
    )
)

REM 回退到 python3 / python
if not defined PYTHON_CMD (
    where python3 >nul 2>&1
    if %errorlevel%==0 set "PYTHON_CMD=python3"
)
if not defined PYTHON_CMD (
    where python >nul 2>&1
    if %errorlevel%==0 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo ❌ 未找到 Python。
    echo    请从 https://www.python.org/downloads/ 安装 Python 3.10。
    pause
    exit /b 1
)

echo ✅ 使用 Python: %PYTHON_CMD%

REM ---------- 创建虚拟环境 ----------
if exist "%VENV_DIR%" (
    echo ⚠️  虚拟环境已存在: %VENV_DIR%
    set /p choice="   是否重新创建? (y/N): "
    if /i "%choice%"=="y" (
        rmdir /s /q "%VENV_DIR%"
        echo    已删除旧虚拟环境
    )
)

if not exist "%VENV_DIR%" (
    echo 📦 正在创建虚拟环境...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    echo ✅ 虚拟环境已创建
)

REM ---------- 安装依赖 ----------
echo 📦 正在安装依赖...
"%VENV_DIR%\Scripts\pip.exe" install --upgrade pip -q
"%VENV_DIR%\Scripts\pip.exe" install -r "%REQ_FILE%"

REM ---------- 验证 ----------
echo.
echo 🔍 正在验证安装...
"%VENV_DIR%\Scripts\python.exe" -c "import cv2; import mediapipe as mp; assert hasattr(mp, 'solutions'); print('  ✅ 安装验证通过: mediapipe', mp.__version__, '/ opencv', cv2.__version__)"

echo.
echo ==========================================
echo   ✅ 安装完成！
echo ==========================================
echo.
echo 运行手语翻译器：
echo   %VENV_DIR%\Scripts\python.exe %SCRIPT_DIR%sign_translator.py
echo.
echo 或者先激活虚拟环境：
echo   %VENV_DIR%\Scripts\activate.bat
echo   python sign_translator.py
echo.
pause
