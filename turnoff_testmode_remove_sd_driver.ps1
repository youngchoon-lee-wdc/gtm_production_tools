bcdedit.exe /set testsigning off
Write-Host "Turned OFF Test mode for measuring performance"

# Define the device name or a part of the device name to search for
$deviceName = "SanDisk NVME"

# Get the device information using WMI
$driverInstance = Get-WmiObject Win32_PnPSignedDriver | Where-Object { $_.DeviceName -eq $deviceName }

if (-not $driverInstance) {
    Write-Host "Driver not found."
    exit
}

# Get the hardware ID
$hardwareId = $driverInstance.HardwareID
Write-Host "Hardware Ids: $hardwareId"

# Define the paths to the DevCon utility
$devconPath = "C:\star\star_client\discovery\miscellaneous\RawNVMeDrive\devcon.exe"

# Disable the driver with the specified hardware ID
Write-Host "Disabling driver with Hardware ID: $hardwareId"
& $devconPath remove $hardwareId

