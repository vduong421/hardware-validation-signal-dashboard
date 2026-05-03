@echo off
setlocal

cd /d "%~dp0"

echo =====================================
echo   Hardware Validation Dashboard
echo =====================================

echo [1] Checking Python...
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python not found.
    pause
    exit /b 1
)

echo [2] Creating venv if not exists...
if not exist ".venv\Scripts\activate.bat" (
    python -m venv .venv
)

echo [3] Activating venv...
call .venv\Scripts\activate.bat

echo [4] Upgrading pip...
python -m pip install --upgrade pip

echo [5] Installing dependencies...
if exist requirements.txt (
    python -m pip install -r requirements.txt
) else (
    echo No requirements.txt found. Standard library project.
)

echo [6] Generating sample dataset...
python generate_samples.py

echo [7] Running analyzer with local AI...
python analyzer.py sample_validation_results.csv --use-ai

echo [8] Starting web dashboard...
start "Validation Backend" cmd /k "cd /d "%~dp0" && call .venv\Scripts\activate.bat && python server.py"

timeout /t 2 >nul
start http://localhost:8006/

echo.
echo Project is running at http://localhost:8006/
echo.

pause
endlocal

