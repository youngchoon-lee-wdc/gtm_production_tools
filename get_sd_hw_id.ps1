# Define the device name or a part of the device name to search for
$deviceName = "SanDisk NVME"

# Get the device information using WMI
$driverInstance = Get-WmiObject Win32_PnPSignedDriver | Where-Object { $_.DeviceName -eq $deviceName }

if (-not $driverInstance) {
    Write-Host "Driver not found."
    exit
}

# Get the hardware ID
$hardwareIds = $driverInstance.HardwareID
Write-Host "Hardware Ids: $hardwareIds"