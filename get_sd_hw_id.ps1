# Define the device name or a part of the device name to search for
$deviceName = "SanDisk NVME"

# Get the device information using WMI
$device = Get-WmiObject Win32_PnPEntity | Where-Object { $_.Name -like "*$deviceName*" }

# Check if the device is found
if ($device) {
    # Retrieve the hardware IDs
    $hardwareIds = $device.GetDeviceProperties("DEVPKEY_Device_HardwareIds")
    
    # Check if hardware IDs are available
    if ($hardwareIds) {
        # Get the first hardware ID
        $firstHardwareId = $hardwareIds[0].Data
        Write-Output "The first Hardware ID is: $firstHardwareId"
    } else {
        Write-Output "No Hardware IDs found for the specified device."
    }
} else {
    Write-Output "Device not found."
}

Write-Output "Hardware Ids: $firstHardwareId"
