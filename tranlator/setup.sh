#!/bin/bash
# ============================================
# DonaTrust Sign Translator - 环境安装脚本
# 适用于 macOS / Linux
# ============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

echo "=========================================="
echo "  DonaTrust Sign Translator 环境配置"
echo "=========================================="

# ---------- 检测 Python 版本 ----------
find_python() {
    # 优先寻找 3.10 ~ 3.12 的 Python
    for cmd in python3.10 python3.11 python3.12 python3; do
        if command -v "$cmd" &>/dev/null; then
            ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" -eq 3 ] && [ "$minor" -ge 9 ] && [ "$minor" -le 12 ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done

    # macOS 框架安装路径
    for minor in 10 11 12; do
        fwk="/Library/Frameworks/Python.framework/Versions/3.${minor}/bin/python3"
        if [ -x "$fwk" ]; then
            echo "$fwk"
            return 0
        fi
    done

    return 1
}

PYTHON_CMD=$(find_python) || {
    echo "❌ 未找到 Python 3.9~3.12。"
    echo "   mediapipe 0.10.14 不支持 Python 3.13+。"
    echo "   请从 https://www.python.org/downloads/ 安装 Python 3.10。"
    exit 1
}

echo "✅ 找到 Python: $PYTHON_CMD ($($PYTHON_CMD --version))"

# ---------- 创建虚拟环境 ----------
if [ -d "$VENV_DIR" ]; then
    echo "⚠️  虚拟环境已存在: $VENV_DIR"
    read -rp "   是否重新创建? (y/N): " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
        echo "   已删除旧虚拟环境"
    else
        echo "   保留现有环境，仅安装依赖"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 正在创建虚拟环境..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    echo "✅ 虚拟环境已创建: $VENV_DIR"
fi

# ---------- 安装依赖 ----------
echo "📦 正在安装依赖..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$REQ_FILE"

# ---------- 验证 ----------
echo ""
echo "🔍 正在验证安装..."
"$VENV_DIR/bin/python3" -c "
import cv2
import mediapipe as mp
assert hasattr(mp, 'solutions'), 'mediapipe.solutions 不可用'
print('  ✅ opencv-python:', cv2.__version__)
print('  ✅ mediapipe:', mp.__version__)
print('  ✅ mp.solutions.hands 可用')
"

echo ""
echo "=========================================="
echo "  ✅ 安装完成！"
echo "=========================================="
echo ""
echo "运行手语翻译器："
echo "  $VENV_DIR/bin/python3 $SCRIPT_DIR/sign_translator.py"
echo ""
echo "或者先激活虚拟环境："
echo "  source $VENV_DIR/bin/activate"
echo "  python sign_translator.py"
echo ""
