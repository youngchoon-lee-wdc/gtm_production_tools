@ECHO OFF

C:\Windows\System32\pnputil.exe /enable-device "PCI\VEN_15B7&DEV_5015&SUBSYS_501515B7&REV_00\4&2498E50C&0&0030"
echo enabled NVMe Controller driver successfully
echo %ERRORLEVEL%
