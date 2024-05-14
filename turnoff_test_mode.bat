@ECHO OFF
echo %USERNAME% is logged
set path=%path%;C:\Users\%USERNAME%\.pyenv\pyenv-win\versions\2.7.14;C:\Windows\System32;

set hostname=%1
set webclicker_command=%2

bcdedit.exe /set testsigning off
echo Turned OFF Test mode for measuring performance

@REM Add specific Sandisk driver's HW ID using devcon because of the following error
@REM error : Failed to delete driver package: One or more devices are presently installed using the specified INF.

setlocal enabledelayedexpansion

REM Specify the path to the INF file of the target driver
set "SD_DRIVER=C:\Program Files (x86)\SanDisk\CVF_2.0_x64\Driver\SDdriver_64bitWinXX\package\SdNvmeDriver.inf"
set "INF_TEMP_DIR=C:\Temp"
set "HW_ID="
rem Export the driver's INF file using pnputil.
pnputil /export-driver %DRIVER_NAME% /outfile "%INF_TEMP_DIR%\driver.inf"

rem Parse the INF file and extract the 'Hardware Ids' property.
for /f "tokens=2 delims=:" %%a in ('findstr /i "Hardware Ids" "%INF_TEMP_DIR%\driver.inf"') do (
    set "HW_ID=%%a"
    goto :Found_HW_ID
)
:Found_HW_ID

rem Get the first index of 'Hardware Ids'.
set "FIRST_HW_ID="
for /f "tokens=1" %%b in ("%HW_ID%") do set "FIRST_HW_ID=%%b"

echo The first Hardware Ids property: %FIRST_HW_ID%

C:\star\star_client\discovery\miscellaneous\RawNVMeDrive\devcon.exe remove "%FIRST_HW_ID%"
C:\Windows\System32\pnputil.exe /delete-driver %SD_DRIVER% /force
C:\Windows\System32\pnputil.exe /add-driver "C:\Windows\INF\stornvme.inf" /install
echo Switched driver successfully (SanDisk NVMe --> Standard NVM Express Controller) 

echo It's about to restart machine after CVF production..
@REM TIMEOUT /T 5
@REM python "C:\Perf_Automation\gtm_production_tools\GTM_cold_boot.py" %hostname% %webclicker_command%
popd
echo %ERRORLEVEL%
@REM shutdown /r /t 5
