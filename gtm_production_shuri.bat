@ECHO off
echo %USERNAME% is logged
@REM set path=%path%;C:\Users\%USERNAME%\.pyenv\pyenv-win\versions\2.7.14;C:\Windows\System32;

set CommitID=%1
set Product=%2
set device_vendor=%3
set device_serial_number=%4
set device_capacity=%5
set project=%6
set CVFVersion=%7

REM Run bcdedit and search for testsigning status
for /f "tokens=2 delims==" %%A in ('bcdedit /enum {current} ^| findstr /i "testsigning"') do (
    if /i "%%A"=="Yes" (
        echo Testsigning is ON.
        goto :RUN_PRODUCTION
    ) else (
        REM If we reached here, testsigning is off
        echo Testsigning is OFF. Please turn on Test mode on the machine!
        EXIT /B %ERRORLEVEL% 
    )
)

:RUN_PRODUCTION
set SHARED_BOT_DIR=\\seouniip01\SSD_Builds\%project%\Firmware\Releases\Unofficial_Builds\%CommitID%\%Product%\_out\%Product%\BOT
set CONFIG_DIR=\\seouniip01\CSS-Firmware\Integration\FW\%project%

echo %SHARED_BOT_DIR%
echo Copying BOT files
xcopy /y %SHARED_BOT_DIR%\CFG.bot "C:\%project%\BOT\"
xcopy /y %SHARED_BOT_DIR%\MoonshotDownload.ini "C:\%project%\BOT\"
xcopy /y %SHARED_BOT_DIR%\sku_file.txt "C:\%project%\BOT\"
xcopy /y  "%SHARED_BOT_DIR%\*.bin"  "C:\%project%\BOT\"
echo Copied BOT files 

set SANDISK_CTF_HOME_X64=C:\Program Files (x86)\SanDisk\CVF_3.0_x64

set CVF_FILE=cvf.ini
echo CVF INI file is %CVF_FILE%
copy %CONFIG_DIR%\CVFConfigFiles\%CVFVersion%\%CVF_FILE% "%SANDISK_CTF_HOME_X64%\config\cvf.ini"

:CVFProduction
@REM TODO: set security_production=1
SET PYTHONHOME=%SANDISK_CVF_HOME_X64_Path%\Python38_x64\

::Setting python path
SET PYTHONPATH=%SANDISK_CVF_HOME_X64_Path%\Python38_x64\

SET SANDISK_CTF_HOME=%SANDISK_CVF_HOME_X64_Path%
SET PYTHONPATH=%PYTHONPATH%;%SANDISK_CTF_HOME%\Python;%SANDISK_CTF_HOME%\Dlls;%PYTHONHOME%
SET PYTHONPATH=%SANDISK_CTF_HOME%\SDR5\SystemTests\;%PYTHONPATH%
if not defined OPENSSL_CONF set OPENSSL_CONF=%SANDISK_CTF_HOME%\config\SecurityProduction\OpenSSL\openssl.cnf
cls
cd %SANDISK_CTF_HOME%
GOTO SETPATH

:SETPATH
SET PATH=%PYTHONHOME%;%PYTHONHOME%Scripts\;%PATH%; /M
echo CURRENT_INSTALLATION_FOLDER is %CURRENT_INSTALLATION_FOLDER%
echo PYTHONHOME is %PYTHONHOME%
echo PYTHONPATH is %PYTHONPATH%
pip install pywin32

cd python
echo %cd%
python Production.py --sku_file=C:\Shuri\BOT\sku_file.txt --bot_file=C:\Shuri\BOT\CFG.bot --device_vendor=%device_vendor% --device_serial_number=%device_serial_number% --device_capacity=%device_capacity% --security_production=0 --device_adapter_type=edsff
IF %ERRORLEVEL% NEQ 0 (
    EXIT /B %ERRORLEVEL%
)
@REM set path=C:\Users\%USERNAME%\.pyenv\pyenv-win\versions\2.7.14;C:\Windows\System32;
echo %ERRORLEVEL%