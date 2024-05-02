@ECHO off
echo %USERNAME% is logged
set path=%path%;C:\Users\%USERNAME%\.pyenv\pyenv-win\versions\2.7.14;C:\Windows\System32;

set CommitID=%1
set Product=%2
set device_vendor=%3
set device_serial_number=%4
set device_capacity=%5
set project=%6
set CVFVersion=%7

set SHARED_BOT_DIR=\\seouniip01\SSD_Builds\%project%\Firmware\Releases\Unofficial_Builds\%CommitID%\%Product%\_out\%Product%\BOT
set CONFIG_DIR=\\seouniip01\CSS-Firmware\Integration\FW\%project%

echo %SHARED_BOT_DIR%
echo Copying BOT files
xcopy /y %SHARED_BOT_DIR%\CFG.bot "C:\%project%\BOT\"
xcopy /y %SHARED_BOT_DIR%\MoonshotDownload.ini "C:\%project%\BOT\"
xcopy /y %SHARED_BOT_DIR%\sku_file.txt "C:\%project%\BOT\"
xcopy /y  "%SHARED_BOT_DIR%\*.bin"  "C:\%project%\BOT\"
echo Copied BOT files 

set SANDISK_CTF_HOME_X64=C:\Program Files (x86)\SanDisk\CVF_2.0_x64

set CVF_FILE=cvf.ini
echo CVF INI file is %CVF_FILE%
copy %CONFIG_DIR%\CVFConfigFiles\%CVFVersion%\%CVF_FILE% "%SANDISK_CTF_HOME_X64%\config\cvf.ini"

C:\Windows\System32\pnputil.exe /add-driver "C:\Program Files (x86)\SanDisk\CVF_2.0_x64\Driver\SDdriver_64bitWinXX\package\SdNvmeDriver.inf" /install
echo Switched driver successfully (Standard NVM Standard NVM Express Controller --> SanDisk NVMe) 

set PYTHONHOME=C:\Users\%USERNAME%\.pyenv\pyenv-win\versions\2.7.14
set SANDISK_CTF_HOME=%SANDISK_CTF_HOME_X64%
set PATH=%PYTHONHOME%;%PYTHONHOME%\Scripts;%SANDISK_CTF_HOME_X64%;%SANDISK_CTF_HOME_X64%\Python;%SANDISK_CTF_HOME_X64%\Dlls;%SANDISK_CTF_HOME_X64%\Dlls\ESS;
set PYTHONPATH=%SANDISK_CTF_HOME_X64%\Python;%SANDISK_CTF_HOME_X64%\Dlls;%SANDISK_CTF_HOME_X64%\SDR5\SystemTests\;%PYTHONHOME%\Lib;%PYTHONHOME%\DLLs;%PYTHONHOME%\Lib\lib-tk;%PYTHONHOME%

set OPENSSL_CONF=%SANDISK_CTF_HOME_X64%\config\SecurityProduction\OpenSSL\openssl.cnf
cd %SANDISK_CTF_HOME%

echo CURRENT_INSTALLATION_FOLDER is %CURRENT_INSTALLATION_FOLDER%
echo PYTHONHOME is %PYTHONHOME%
echo PYTHONPATH is %PYTHONPATH% 

python Python\Production.py --device_vendor=%device_vendor% --device_serial_number=%device_serial_number% --device_capacity=%device_capacity%  --security_production=1 --sku_file=C:\Atlas3\BOT\sku_file.txt --bot_file=C:\Atlas3\BOT\CFG.bot --security_production_secrets_config_file="C:\Program Files (x86)\SanDisk\CVF_2.0_x64\config\MoonshotDownloadPSS.ini" --set_tlp_payload_size=1 --disable_enable_root_node_rom=1

set path=C:\Users\%USERNAME%\.pyenv\pyenv-win\versions\2.7.14;C:\Windows\System32;

bcdedit.exe /set testsigning off
echo Turned OFF Test mode for measuring performance

C:\Windows\System32\pnputil.exe /delete-driver "C:\Program Files (x86)\SanDisk\CVF_2.0_x64\Driver\SDdriver_64bitWinXX\package\SdNvmeDriver.inf" /force
C:\Windows\System32\pnputil.exe /add-driver "C:\Windows\INF\stornvme.inf" /install
echo Switched driver successfully (SanDisk NVMe --> Standard NVM Express Controller) 

echo It's about to restart machine after CVF production..

echo %ERRORLEVEL%