@ECHO OFF
echo %USERNAME% is logged
set path=%path%;C:\Users\%USERNAME%\.pyenv\pyenv-win\versions\2.7.14;C:\Windows\System32;

bcdedit.exe /set testsigning on
echo Turned ON Test mode for next CVF production 

C:\Windows\System32\pnputil.exe /add-driver "C:\Program Files (x86)\SanDisk\CVF_2.0_x64\Driver\SDdriver_64bitWinXX\package\SdNvmeDriver.inf" /install
echo Switched driver successfully (Standard NVM Standard NVM Express Controller --> SanDisk NVMe) 

setlocal
@REM Windows error code 3010 indicates that a reboot is necessary to complete the installation process
if %errorlevel%==3010 (
    echo Warning: The operation completed successfully, but a restart is required.
    
    REM Reset the errorlevel to 0
    shutdown /r /t 5
    exit /b 0
    
)
echo %errorlevel%
shutdown /r /t 5
exit /b %errorlevel%
