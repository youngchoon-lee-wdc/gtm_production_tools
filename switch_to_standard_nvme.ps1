# Define SanDisk NVME driver package (.inf file)
$sdDriverPath = "C:\Program Files (x86)\SanDisk\CVF_2.0_x64\Driver\SDdriver_64bitWinXX\package\SdNvmeDriver.inf"
pnputil.exe /delete-driver $sdDriverPath /force

Check if the disable command was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully removed SanDisk NVME driver with Hardware ID: $hardwareId"
} else {
    Write-Host "Failed to remove SanDisk NVME driver with Hardware ID: $hardwareId"
    exit 1
}

# Define Standard NVME driver package (.inf file)
$standardDriverPath = "C:\Windows\INF\stornvme.inf"

# Add the driver using PnPUtil
Write-Host "Adding driver from: $standardDriverPath"
pnputil /add-driver $standardDriverPath /install

# Check if the add driver command was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully Switched driver successfully (SanDisk NVMe --> Standard NVM Express Controller)"
} else {
    Write-Host "Failed to switch driver (SanDisk NVMe --> Standard NVM Express Controller)"
    exit 1
}

