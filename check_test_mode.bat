@echo off
setlocal

:: Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting admin rights...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

REM Run bcdedit and search for testsigning status
for /f "tokens=2 delims==" %%A in ('bcdedit /enum {current} ^| findstr /i "testsigning"') do (
    if /i "%%A"=="Yes" (
        echo Testsigning is ON.
        goto :end
    )
)

REM If we reached here, testsigning is off
echo Testsigning is OFF.

:end
endlocal
