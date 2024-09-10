@ECHO off
set project=shuri

set CommitID=%1
set device_vendor=%2
set device_serial_number=%3
set device_capacity=%4
set CVFVersion=%5
set FWVersion=%6

echo %project%
echo %CommitID%
echo %device_vendor%
echo %device_serial_number%
echo %device_capacity%
echo %CVFVersion%
echo %FWVersion%

set SANDISK_CVF_HOME_X64_Path=C:\Program Files (x86)\SanDisk\CVF_3.0_x64
set LOCAL_BOT_PATH=C:\%project%\BOT


:: Check if the value starts with 'AO' (official FW)
if "%FWVersion:~0,2%"=="AO" (
    set FW_CHAR=%FWVersion:~5,3%
) else (
    set FW_CHAR=%FWVersion:~5,3%
)
echo FW_CHAR: %FW_CHAR%

@REM ER build result on KSG GFS
@REM e.g.) Atlas3 : \\ksg-op-fpgcss01.wdc.com\fpgcss_ci\atlas3\Firmware\Releases\Unofficial_Builds\12007_aba3e736\12007AKN\atlas3_dev_BOT
@REM       Shuri  : \\ksg-op-fpgcss01.wdc.com\fpgcss_ci\shuri\Firmware\Releases\Unofficial_Builds\12653_5be04572\12653ALA\shuri_asic_BOT

:GetFWChar
@REM TODO:Once all FW chars are defined, add more
if /I "%FW_CHAR%"=="ALN" (
    set PSET=shuri
)
if /I "%FW_CHAR%"=="ALG" (
    set PSET=shuri_sbm
)
if /I "%FW_CHAR%"=="ALA" (
    set PSET=shuri_asic
)
if /I "%FW_CHAR%"=="ALP" (
    set PSET=shuri_perf
)

echo PSET is %PSET%

:CVFProduction
set SANDISK_CTF_HOME_X64=C:\Program Files (x86)\SanDisk\CVF_3.0_x64

set CVF_FILE=cvf.ini
echo CVF INI file is %CVF_FILE%
copy %CONFIG_DIR%\CVFConfigFiles\%CVFVersion%\%CVF_FILE% "%SANDISK_CTF_HOME_X64%\config\cvf.ini"

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
@REM pip install pywin32

cd python
echo %cd%
:: Convert CVFVersion to a number and compare
set /a "versionNumber=%CVFVersion%"
set "PRODUCTION_ARGS=--sku_file=%LOCAL_BOT_PATH%\sku_file.txt --bot_file=%LOCAL_BOT_PATH%\CFG.bot --device_vendor=%device_vendor% --device_serial_number=%device_serial_number% --device_capacity=%device_capacity% --security_production=0 --device_adapter_type=edsff"
:: Check if CVF version is 240806 or greater
if %versionNumber% geq 240806 (
    echo Calling JSONProduction.py
    echo python JSONProduction.py --production_json_file_path="C:\Program Files (x86)\SanDisk\CVF_3.0_x64\Python\production_flow_hw_no_ram.json" %PRODUCTION_ARGS%
) else (
    echo Calling Production.py
    echo python Production.py %PRODUCTION_ARGS%
)
