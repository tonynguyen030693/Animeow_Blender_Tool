@echo off
chcp 65001 > nul
echo ==================================================
echo       ANIMEOW MAYA SCENE PERFORMANCE DEBUGGER
echo ==================================================
echo.

if "%~1"=="" (
    echo [LOI] Vui long keo tha file Maya .ma hoac .mb vao day.
    echo [ERROR] Please drag and drop a Maya file .ma or .mb here.
    echo.
    pause
    exit /b
)

:: Tim kiem mayabatch.exe o cac phien ban Maya thong dung
set "MAYA_EXE_PATH="
for %%v in (2020 2022 2023 2024 2025) do (
    if exist "C:\Program Files\Autodesk\Maya%%v\bin\mayabatch.exe" (
        set "MAYA_EXE_PATH=C:\Program Files\Autodesk\Maya%%v\bin\mayabatch.exe"
        goto :FOUND
    )
)

:FOUND
if "%MAYA_EXE_PATH%"=="" (
    echo [LOI] Khong tim thay mayabatch.exe tren may cua ban.
    echo [ERROR] Could not find mayabatch.exe on your system.
    echo.
    pause
    exit /b
)

echo Dang su dung Maya Batch: %MAYA_EXE_PATH%
echo File dang phan tich: %~1
echo.

:: Dat bien moi truong cho kich ban Python doc duoc
set "MAYA_DEBUG_FILE=%~1"
set "MAYA_DEBUG_SCRIPT=%~dp0scripts\run_debug.py"

echo --------------------------------------------------
"%MAYA_EXE_PATH%" -command "python(""import os; execfile(os.environ['MAYA_DEBUG_SCRIPT'])"")"
if %ERRORLEVEL% NEQ 0 (
    echo --------------------------------------------------
    echo.
    echo ==================================================
    echo         [THAT BAI / FAILED]
    echo   Tien trinh Maya bi dung hoac crash dot ngot!
    echo   Ma loi - Exit Code: %ERRORLEVEL%
    echo ==================================================
    echo.
    echo Nhap phim bat ky de dong cua so CMD.
    pause
    exit /b %ERRORLEVEL%
)

echo --------------------------------------------------
echo.
echo ==================================================
echo         [HOAN THANH / DONE]
echo   Qua trinh kiem tra hoan toan ket thuc!
echo ==================================================
echo.
echo Nhap phim bat ky de dong cua so CMD.
pause
