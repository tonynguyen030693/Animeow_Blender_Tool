@echo off
echo ======================================================
echo   TU DONG KET NOI O DIA MANG Y VA Z (ANIMEOW PIPELINE)
echo ======================================================
echo.

:: 1. Go bo o dia cu neu dang ton tai de tranh xung dot
echo [*] Dang go bo ket noi o dia cu (neu co)...
net use Z: /delete /y >nul 2>&1
net use Y: /delete /y >nul 2>&1

:: 2. Ket noi o dia Z
echo [*] Dang ket noi o dia Z: -^> \\192.168.1.239\Animeow\Project\EnjoHub\Project_Enjo
net use Z: "\\192.168.1.239\Animeow\Project\EnjoHub\Project_Enjo" /persistent:yes
if %errorlevel% equ 0 (
    echo [OK] Da ket noi o dia Z thanh cong.
) else (
    echo [LOI] Khong the ket noi o dia Z.
)

echo.

:: 3. Ket noi o dia Y
echo [*] Dang ket noi o dia Y: -^> \\192.168.1.239\Animeow\Project\EnjoHub\Project_Enjo
net use Y: "\\192.168.1.239\Animeow\Project\EnjoHub\Project_Enjo" /persistent:yes
if %errorlevel% equ 0 (
    echo [OK] Da ket noi o dia Y thanh cong.
) else (
    echo [LOI] Khong the ket noi o dia Y.
)

echo.
echo ======================================================
echo   Hoan thanh!
echo ======================================================
echo.
pause
