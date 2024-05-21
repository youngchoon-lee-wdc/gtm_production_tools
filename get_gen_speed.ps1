# Ensure the target directory exists
$GenSpeedResultDir = "C:\GenSpeedResult"
if (-not (Test-Path -Path $GenSpeedResultDir)) {
    New-Item -ItemType Directory -Path $GenSpeedResultDir
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
$filename = "$GenSpeedResultDir\$timestamp.txt"

# Save the PCI current link speed to the file
$genSpeedStr | Out-File -FilePath $filename

# Output the result
Write-Host "PCI current link speed saved to $filename"

# Define the path to the file that stores the restart count
$restartCountFile = "$GenSpeedResultDir\restart_count.txt"

# Function to get the current restart count from the file
function Get-RestartCount {
    Write-Host "Getting restart count from $restartCountFile file..."
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
    $smtpFrom = "svc-ep-jenm01@wdc.com"
    $smtpTo = "Young Choon Lee <YoungChoon.Lee@wdc.com>", "JeongHwa Kim <Jeonghwa.Kim@wdc.com>", "Minlee Ha <minlee.ha@wdc.com>", "SangMin Seok <SangMin.Seok2@wdc.com>"
    $hostname = (Get-ComputerInfo).CsName
    $messageSubject = "GTM Machine($hostname) Restart Alert - Genspeed is less than minimum required Gen$minimumRequiredGenSpeed "
    $messageBody = @"
    <html>
    <body>
        <h1>GTM Machine($hostname) Restart Alert</h1>
        <p>The machine($hostname) has restarted more than $maxRestartCount times due to Genspeed was <font color=red>Gen$pciLinkSpeed</font>.</p>
        <p>It is less than minimum required <font color=blue>Gen$minimumRequiredGenSpeed</font>.</p>
        <p>So please check Genspeed on the machine.</p>
    </body>
    </html>
"@    
    Write-Host $messageBody   
    Send-MailMessage -SmtpServer $smtpServer -From $smtpFrom -To $smtpTo -Subject $messageSubject -Body $messageBody -BodyAsHtml
}


if ($pciLinkSpeed -lt $minimumRequiredGenSpeed) {
    Write-Host "Gen speed is less than $minimumRequiredGenSpeed. Restarting the machine..."
    $restartCount = Increment-RestartCount

    if ($restartCount -gt $maxRestartCount) {
        Write-Host "Restart count has exceeded $maxRestartCount. Sending email notification..."
        Send-EmailNotification
        Write-Host "Deleting the restart count file..."
        Remove-Item -Path $restartCountFile -Force
        exit 1
    }

    # Restart-Computer -Force
} else {
    Write-Host "Value is $minimumRequiredGenSpeed or greater. No action needed."
}

$keepFileDays = 7
$currentDate = Get-Date
$timeSpan = New-TimeSpan -Days $keepFileDays

# Get all .txt files in the specified folder
$txtFiles = Get-ChildItem -Path $GenSpeedResultDir -Filter *.txt

foreach ($file in $txtFiles) {
    # Calculate the age of the file
    $fileAge = $currentDate - $file.CreationTime
    
    # Check if the file is older than one week
    if ($fileAge -gt $timeSpan) {
        Write-Host "Deleting file: $($file.FullName)"
        Remove-Item -Path $file.FullName -Force
    }
}


