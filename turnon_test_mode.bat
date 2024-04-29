@ECHO OFF
bcdedit.exe /set testsigning on
echo Turned ON Test mode for CVF production 

C:\Windows\System32\pnputil.exe /disable-device "PCI\VEN_15B7&DEV_5015&SUBSYS_501515B7&REV_00\4&22F77229&0&0008"
echo Disabled NVMe Controller driver successfully

echo It's about to restart machine after CVF production..
echo %ERRORLEVEL%
shutdown /r /t 5
