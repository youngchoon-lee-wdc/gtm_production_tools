# Define the device name or a part of the device name to search for
$deviceName = "Standard NVM Express Controller"

# Get the device information using the Win32_PnPEntity CIM class
$devices = Get-CimInstance -ClassName Win32_PnPEntity | Where-Object { $_.Name -like "*$deviceName*" }

# Check if any devices are found
if ($devices) {
    foreach ($device in $devices) {
        # Output basic properties of the device
        Write-Output "Device Name: $($device.Name)"
        $device | Format-List -Property *
    }
} else {
    Write-Output "Device not found."
}



