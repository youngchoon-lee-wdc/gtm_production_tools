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

# Define the path to the file that stores the restart count
$restartCountFile = "$targetDirectory\restart_count.txt"

# Function to get the current restart count from the file
function Get-RestartCount {
    if (Test-Path $restartCountFile) {
        return [int](Get-Content $restartCountFile)
    } else {
        return 0
    }
}

# Function to increment and save the restart count
function Increment-RestartCount {
    $count = Get-RestartCount
    $count++
    Set-Content -Path $restartCountFile -Value $count
    return $count
}

$minimumRequiredGenSpeed = 4
$maxRestartCount = 3

# Function to send an email notification
function Send-EmailNotification {
    $smtpServer = "milrelay.sandisk.com"
    $smtpFrom = "your-email@yourdomain.com"
    $smtpTo = "youngchoon.lee@wdc.com,SangMin.Seok2@wdc.com,Jeonghwa.Kim@wdc.com,minlee.ha@wdc.com"
    $messageSubject = "GTM Machine Restart Alert"
    $messageBody = "The machine has restarted more than $maxRestartCount times due to Gen spped is less than minimum required Gen$minimumRequiredGenSpeed"

    Send-MailMessage -SmtpServer $smtpServer -From $smtpFrom -To $smtpTo -Subject $messageSubject -Body $messageBody
}


if ($pciLinkSpeed -lt $minimumRequiredGenSpeed) {
    Write-Host "Gen speed is less than $minimumRequiredGenSpeed. Restarting the machine..."
    $restartCount = Increment-RestartCount

    if ($restartCount -gt $maxRestartCount) {
        Write-Host "Restart count has exceeded $maxRestartCount. Sending email notification..."
        Send-EmailNotification
        Write-Host "Deleting the restart count file..."
        Remove-Item -Path $restartCountFile -Force
    }

    Restart-Computer -Force
} else {
    Write-Host "Value is $minimumRequiredGenSpeed or greater. No action needed."
}


