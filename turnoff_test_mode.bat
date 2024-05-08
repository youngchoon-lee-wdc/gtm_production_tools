@ECHO OFF
echo %USERNAME% is logged
set path=%path%;C:\Users\%USERNAME%\.pyenv\pyenv-win\versions\2.7.14;C:\Windows\System32;

set hostname=%1
set webclicker_command=%2

bcdedit.exe /set testsigning off
echo Turned OFF Test mode for measuring performance

C:\Windows\System32\pnputil.exe /delete-driver "C:\Program Files (x86)\SanDisk\CVF_2.0_x64\Driver\SDdriver_64bitWinXX\package\SdNvmeDriver.inf" /force
C:\Windows\System32\pnputil.exe /add-driver "C:\Windows\INF\stornvme.inf" /install
echo Switched driver successfully (SanDisk NVMe --> Standard NVM Express Controller) 

echo It's about to restart machine after CVF production..
REM Delete the task scheduler Star_Client_Service_EventId-4634
C:\Windows\System32\schtasks.exe /end /tn Star_Client_Service

TIMEOUT /T 5

python "C:\Perf_Automation\gtm_production_tools\GTM_cold_boot.py" %hostname% %webclicker_command%
echo %ERRORLEVEL%
@REM shutdown /r /t 5
