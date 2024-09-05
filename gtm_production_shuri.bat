@ECHO off
echo %USERNAME% is logged
cd C:\Perf_Automation\gtm_production_tools
git pull
set project=shuri

@REM set path=%path%;C:\Users\%USERNAME%\.pyenv\pyenv-win\versions\2.7.14;C:\Windows\System32;
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
@REM commit_id, device_vendor, device_serial_number, device_capacity, cvf_version fw_version, )

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
if not exist "%LOCAL_BOT_PATH%" (
    mkdir "%LOCAL_BOT_PATH%"
    echo The folder was not found, so it has been created.
)

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
    set PSET=shuri_asic_perf
)

echo PSET is %PSET%
REM Check if FWVersion starts with "AO"
if "%FWVersion:~0,2%"=="AO" (
    REM If it starts with "AO", set the path as Official FW
    set GFS_FW_BOT_ROOT=\\ksg-op-fpgcss01.wdc.com\fpgcss_ci\%project%\Firmware\Releases\Official_Builds
    GOTO SetOfficialFWBotPath
) else (
    REM If not, set the path as Engineering FW
    set GFS_FW_BOT_ROOT=\\ksg-op-fpgcss01.wdc.com\fpgcss_ci\%project%\Firmware\Releases\Unofficial_Builds
    GOTO SetEngFWBotPath
)


:SetOfficialFWBotPath 
echo Official FW 
set OFFICIAL_FW_REVISION=%FWVersion:~2%
Set FW_BOT_PATH=%GFS_FW_BOT_ROOT%\%OFFICIAL_FW_REVISION%_%CommitID%\FW_Product_Build\%FWVersion%%FW_CHAR%\%PSET%_BOT
GOTO CopyCVFConfigFiles

:SetEngFWBotPath
echo Engineering FW  
REM Extract the first five characters
set ER_BUILD_JIRA_STR=%FWVersion:~0,5%
echo ER_BUILD_JIRA_STR : %ER_BUILD_JIRA_STR%
REM Convert the extracted substring to an integer
set /a ER_BUILD_JIRA_KEY=%ER_BUILD_JIRA_STR%

REM Output the result
echo Engineering build JIRA key is: %ER_BUILD_JIRA_KEY%
Set FW_BOT_PATH=%GFS_FW_BOT_ROOT%\%ER_BUILD_JIRA_KEY%_%CommitID%\%FWVersion%\%PSET%_BOT
GOTO CopyCVFConfigFiles

:CopyCVFConfigFiles
echo FW bot path : %FW_BOT_PATH%
echo Copy CVF Config Files
Set CVF_CONFIG_PATH=\\seouniip01\CSS-Firmware\Integration\FW\%project%\CVFConfigFiles\%CVFVersion%

xcopy /y %CVF_CONFIG_PATH%\cvf.ini "%SANDISK_CVF_HOME_X64_Path%\config\"
xcopy /y %CVF_CONFIG_PATH%\cvf.ini.README "%SANDISK_CVF_HOME_X64_Path%\config\"
xcopy /y %CVF_CONFIG_PATH%\systemCfg.xml "%SANDISK_CVF_HOME_X64_Path%\VTF\"
xcopy /y "%SANDISK_CVF_HOME_X64_Path%\config\MoonshotDownloadPSS.ini" "%LOCAL_BOT_PATH%"

:CopyBOT
echo Copy FW config files

xcopy /y %FW_BOT_PATH%\MoonshotDownloadPSS.ini "%LOCAL_BOT_PATH%"
xcopy /y %FW_BOT_PATH%\sku_file.txt "%LOCAL_BOT_PATH%"
xcopy /y %FW_BOT_PATH%\CFG.bot "%LOCAL_BOT_PATH%"
xcopy /y %FW_BOT_PATH%\SetDictionary.dco  "%USER_STORAGE_PATH%\rwr\"
xcopy /y %FW_BOT_PATH%\FwtDictionary.fdo  "%USER_STORAGE_PATH%\rwr\"
@REM TODO: Now, dbg.bat is not generated because it's so early project stage, so please confirm if dbg.bat file is generated
xcopy /y %FW_BOT_PATH%\dbg.bat  "C:\fw\"

echo Copy Bin Files
xcopy /y  "%FW_BOT_PATH%\*.bin"  "%LOCAL_BOT_PATH%"
goto CVFProduction

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
python Production.py --sku_file=%LOCAL_BOT_PATH%\sku_file.txt --bot_file=%LOCAL_BOT_PATH%\CFG.bot --device_vendor=%device_vendor% --device_serial_number=%device_serial_number% --device_capacity=%device_capacity% --security_production=0 --device_adapter_type=edsff
IF %ERRORLEVEL% NEQ 0 (
    EXIT /B %ERRORLEVEL%
)
@REM set path=C:\Users\%USERNAME%\.pyenv\pyenv-win\versions\2.7.14;C:\Windows\System32;
EXIT /B %ERRORLEVEL%