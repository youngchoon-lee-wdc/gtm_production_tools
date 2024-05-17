@ECHO OFF
echo %USERNAME% is logged
set path=%path%;C:\Users\%USERNAME%\.pyenv\pyenv-win\versions\2.7.14;C:\Windows\System32;

set hostname=%1
set webclicker_command=%2

bcdedit.exe /set testsigning off
echo Turned OFF Test mode for measuring performance

REM Specify the path to the INF file of the target driver
set "SD_DRIVER=C:\Program Files (x86)\SanDisk\CVF_2.0_x64\Driver\SDdriver_64bitWinXX\package\SdNvmeDriver.inf"
:: Delete the driver using PnPUtil
pnputil.exe /delete-driver "%SD_DRIVER%" /uninstall /force

:: Check if the command succeeded
if %errorlevel% equ 0 (
    echo Driver successfully deleted.
) else (
    echo Failed to delete the driver.
)

C:\Windows\System32\pnputil.exe /add-driver "C:\Windows\INF\stornvme.inf" /install
echo Switched driver successfully (SanDisk NVMe --> Standard NVM Express Controller) 

echo It's about to restart machine after CVF production..
@REM TIMEOUT /T 5
@REM python "C:\Perf_Automation\gtm_production_tools\GTM_cold_boot.py" %hostname% %webclicker_command%
popd
echo %ERRORLEVEL%
@REM shutdown /r /t 5
