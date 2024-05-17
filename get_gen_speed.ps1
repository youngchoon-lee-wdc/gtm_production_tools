# Ensure the target directory exists
$targetDirectory = "C:\GenSpeedResult"
if (-not (Test-Path -Path $targetDirectory)) {
    New-Item -ItemType Directory -Path $targetDirectory
}

$deviceName = "Standard NVM Express Controller"

# Get the device information using WMI
$device = Get-WmiObject Win32_PnPEntity | Where-Object { $_.Name -like "*$deviceName*" }

# Check if the device is found
if ($device) {
    $pciLinkSpeed = $device.GetDeviceProperties("DEVPKEY_PciDevice_CurrentLinkSpeed").deviceProperties.data
    
    # Check if hardware IDs are available
    if ($pciLinkSpeed) {
        Write-Output $pciLinkSpeed
    } else {
        Write-Output "No PCI Current Link speed found for the specified device."
    }
} else {
    Write-Output "Device not found."
    exit 1
}

# Format the result as Gen[last index of the value]
$genSpeedStr = "Connected Gen speed : Gen" + $pciLinkSpeed

# Output the result
Write-Output $genSpeedStr


# Create a timestamped filename
$timestamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
$filename = "$targetDirectory\$timestamp.txt"

# Save the PCI current link speed to the file
$genSpeedStr | Out-File -FilePath $filename

# Output the result
Write-Host "PCI current link speed saved to $filename"
