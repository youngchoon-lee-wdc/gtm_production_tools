@ECHO OFF
echo %USERNAME% is logged
set path=%path%;C:\Users\%USERNAME%\.pyenv\pyenv-win\versions\2.7.14;C:\Windows\System32;

set hostname=%1
set webclicker_command=%2

bcdedit.exe /set testsigning off
echo Turned OFF Test mode for measuring performance

@REM Add specific Sandisk driver's HW ID using devcon because of the following error
@REM error : Failed to delete driver package: One or more devices are presently installed using the specified INF.
C:\star\star_client\discovery\miscellaneous\RawNVMeDrive\devcon.exe remove "PCI\VEN_15B7&DEV_5049&SUBSYS_504915B7&REV_00"
C:\Windows\System32\pnputil.exe /delete-driver "C:\Program Files (x86)\SanDisk\CVF_2.0_x64\Driver\SDdriver_64bitWinXX\package\SdNvmeDriver.inf" /force
C:\Windows\System32\pnputil.exe /add-driver "C:\Windows\INF\stornvme.inf" /install
echo Switched driver successfully (SanDisk NVMe --> Standard NVM Express Controller) 

echo It's about to restart machine after CVF production..
@REM TIMEOUT /T 5
@REM python "C:\Perf_Automation\gtm_production_tools\GTM_cold_boot.py" %hostname% %webclicker_command%
popd
echo %ERRORLEVEL%
@REM shutdown /r /t 5
