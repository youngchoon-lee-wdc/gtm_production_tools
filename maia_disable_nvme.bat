@ECHO OFF

C:\Windows\System32\pnputil.exe /disable-device "PCI\VEN_15B7&DEV_5015&SUBSYS_501515B7&REV_00\4&2498E50C&0&0030"
echo Disabled NVMe Controller driver successfully
echo %ERRORLEVEL%

shutdown /r /t 5
