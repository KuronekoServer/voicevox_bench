@echo off
chcp 65001 > nul
echo ========================================
echo    VOICEVOX ベンチマークツール
echo ========================================
echo.

REM Pythonが利用可能かチェック
python --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Pythonがインストールされていません。
    echo https://www.python.org/ からPythonをインストールしてください。
    pause
    exit /b 1
)

REM requestsライブラリをチェック
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo requestsライブラリをインストールしています...
    pip install requests
    if errorlevel 1 (
        echo エラー: requestsライブラリのインストールに失敗しました。
        pause
        exit /b 1
    )
)

echo ベンチマークを開始します...
echo.
python bench.py

echo.
echo ベンチマーク完了！
pause
